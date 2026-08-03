"""Render an EDL to an mp4.

Video is processed frame by frame in OpenCV and piped to ffmpeg as raw
BGR. Doing the camera in Python rather than in an ffmpeg filter graph costs
some speed, but it buys exact per-frame control over the crop path - which
is the entire point of the focus camera, and is awkward to express as a
``zoompan`` expression.

Audio is assembled separately into a single bed (music, optionally with the
original gameplay audio time-stretched to match the speed ramps and mixed
underneath) and muxed in at the end.
"""

from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Sequence

import cv2
import numpy as np

from .camera import plan_camera
from .config import Config
from .plan import out_to_src, src_to_out
from .probe import probe, require_ffmpeg
from .timeline import Clip, Edl


def _atempo_chain(speed: float) -> List[str]:
    """Decompose a speed factor into atempo stages within ffmpeg's 0.5-2.0 range."""
    if abs(speed - 1.0) < 1e-6:
        return []
    stages: List[float] = []
    remaining = float(speed)
    while remaining < 0.5:
        stages.append(0.5)
        remaining /= 0.5
    while remaining > 2.0:
        stages.append(2.0)
        remaining /= 2.0
    stages.append(remaining)
    return [f"atempo={s:.6f}" for s in stages]


def _clip_source_times(clip: Clip, fps: float) -> np.ndarray:
    """Source timestamp for each output frame of a clip."""
    n = max(1, int(round(clip.out_duration * fps)))
    out_rel = np.arange(n) / fps
    out_pre = src_to_out(
        clip.src_impact - clip.src_start, clip.ramp_speed, clip.ramp_window
    )
    src = np.asarray(
        [
            clip.src_impact + out_to_src(o - out_pre, clip.ramp_speed, clip.ramp_window)
            for o in out_rel
        ]
    )
    return np.clip(src, clip.src_start, max(clip.src_end - 1e-6, clip.src_start))


def _render_clip_frames(
    cap: cv2.VideoCapture,
    clip: Clip,
    edl: Edl,
    src_w: int,
    src_h: int,
    src_fps: float,
    seed: int,
) -> List[np.ndarray]:
    """Decode, reframe and resize every output frame for one clip."""
    src_times = _clip_source_times(clip, edl.fps)
    n = len(src_times)
    out_rel = np.arange(n) / edl.fps
    impact_out_rel = src_to_out(
        clip.src_impact - clip.src_start, clip.ramp_speed, clip.ramp_window
    )

    rects = plan_camera(
        out_rel_times=out_rel,
        impact_out_rel=impact_out_rel,
        src_times=src_times,
        move=clip.move,
        focus=clip.focus,
        src_w=src_w,
        src_h=src_h,
        out_aspect=edl.width / edl.height,
        # Camera behaviour comes from the clip, not the live config, so that
        # re-rendering a saved EDL reproduces it exactly.
        focus_smooth=clip.move.focus_smooth,
        focus_lead=clip.move.focus_lead,
        seed=seed,
    )

    wanted = np.clip(np.round(src_times * src_fps).astype(int), 0, None)

    # Seek once, then walk forward. Source indices are non-decreasing within
    # a clip, so grabbing (without decoding) is enough to skip.
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(wanted[0]))
    current = int(wanted[0]) - 1
    last: Optional[np.ndarray] = None
    frames: List[np.ndarray] = []

    for target, rect in zip(wanted, rects):
        while current < target:
            ok = cap.grab()
            if not ok:
                break
            current += 1
        if last is None or current == target:
            ok, frame = cap.retrieve()
            if ok:
                last = frame
        if last is None:
            last = np.zeros((src_h, src_w, 3), dtype=np.uint8)

        crop = last[rect.y : rect.y + rect.h, rect.x : rect.x + rect.w]
        if crop.size == 0:
            crop = last
        frames.append(
            cv2.resize(crop, (edl.width, edl.height), interpolation=cv2.INTER_LANCZOS4)
        )

    return frames


def _build_game_audio(edl: Edl, cfg: Config, workdir: Path) -> Optional[Path]:
    """Concatenate the gameplay audio of every clip, time-stretched to match.

    Each clip is cut into up to three pieces - before the ramp window, the
    ramped middle, and after - so a slow-mo impact keeps its audio in sync
    instead of drifting.
    """
    info = probe(edl.source)
    if not info.has_audio:
        return None

    pieces: List[Path] = []
    for i, clip in enumerate(edl.clips):
        if clip.ramp_speed < 1.0 and clip.ramp_window > 0:
            lo = max(clip.src_start, clip.src_impact - clip.ramp_window)
            hi = min(clip.src_end, clip.src_impact + clip.ramp_window)
            spans = [
                (clip.src_start, lo, 1.0),
                (lo, hi, clip.ramp_speed),
                (hi, clip.src_end, 1.0),
            ]
        else:
            spans = [(clip.src_start, clip.src_end, 1.0)]

        for j, (a, b, speed) in enumerate(spans):
            if b - a <= 1e-3:
                continue
            dst = workdir / f"game_{i:03d}_{j}.wav"
            filters = _atempo_chain(speed)
            cmd = [
                "ffmpeg", "-v", "error", "-y",
                "-ss", f"{a:.6f}", "-t", f"{b - a:.6f}",
                "-i", str(edl.source),
                "-vn", "-ac", "2", "-ar", "48000",
            ]
            if filters:
                cmd += ["-filter:a", ",".join(filters)]
            cmd += [str(dst)]
            subprocess.run(cmd, check=True)
            pieces.append(dst)

    if not pieces:
        return None

    listing = workdir / "game_list.txt"
    listing.write_text("".join(f"file '{p.name}'\n" for p in pieces))
    out = workdir / "game.wav"
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y",
            "-f", "concat", "-safe", "0", "-i", str(listing),
            "-ac", "2", "-ar", "48000", str(out),
        ],
        check=True, cwd=workdir,
    )
    return out


def _build_audio_bed(edl: Edl, cfg: Config, workdir: Path) -> Optional[Path]:
    """Music (from ``music_start``) with optional gameplay audio mixed under."""
    duration = edl.duration
    if duration <= 0:
        return None

    tracks: List[tuple[Path, float]] = []

    if edl.music:
        music = workdir / "music.wav"
        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y",
                "-ss", f"{edl.music_start:.6f}",
                "-t", f"{duration:.6f}",
                "-i", str(edl.music),
                "-vn", "-ac", "2", "-ar", "48000",
                "-af", "apad",           # pad if the music runs out early
                "-t", f"{duration:.6f}",
                str(music),
            ],
            check=True,
        )
        tracks.append((music, cfg.music_level))

    if cfg.game_audio_level > 0:
        game = _build_game_audio(edl, cfg, workdir)
        if game is not None:
            tracks.append((game, cfg.game_audio_level))

    if not tracks:
        return None
    if len(tracks) == 1 and abs(tracks[0][1] - 1.0) < 1e-6:
        return tracks[0][0]

    bed = workdir / "bed.wav"
    cmd = ["ffmpeg", "-v", "error", "-y"]
    for path, _ in tracks:
        cmd += ["-i", str(path)]

    parts = [f"[{i}:a]volume={gain:.4f}[a{i}]" for i, (_, gain) in enumerate(tracks)]
    joined = "".join(f"[a{i}]" for i in range(len(tracks)))
    parts.append(
        f"{joined}amix=inputs={len(tracks)}:duration=first:normalize=0[out]"
    )
    cmd += [
        "-filter_complex", ";".join(parts),
        "-map", "[out]",
        "-ac", "2", "-ar", "48000",
        "-t", f"{duration:.6f}",
        str(bed),
    ]
    subprocess.run(cmd, check=True)
    return bed


def render(
    edl: Edl,
    out_path: str | Path,
    cfg: Optional[Config] = None,
    progress: bool = True,
) -> Path:
    """Render ``edl`` to ``out_path``. Returns the written path."""
    require_ffmpeg()
    cfg = cfg or Config()
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if not edl.clips:
        raise ValueError("EDL has no clips to render")

    info = probe(edl.source)
    cap = cv2.VideoCapture(str(edl.source))
    if not cap.isOpened():
        raise RuntimeError(f"could not open {edl.source}")
    src_fps = info.fps or 30.0

    with tempfile.TemporaryDirectory() as tmp:
        workdir = Path(tmp)
        bed = _build_audio_bed(edl, cfg, workdir)

        cmd = [
            "ffmpeg", "-v", "error", "-y",
            "-f", "rawvideo", "-pix_fmt", "bgr24",
            "-s", f"{edl.width}x{edl.height}",
            "-r", f"{edl.fps}",
            "-i", "-",
        ]
        if bed is not None:
            cmd += ["-i", str(bed)]
        cmd += [
            "-map", "0:v",
            *(["-map", "1:a"] if bed is not None else []),
            "-c:v", "libx264",
            "-preset", cfg.preset,
            "-crf", str(cfg.crf),
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
        ]
        if bed is not None:
            cmd += ["-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += [str(out_path)]

        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        total = len(edl.clips)
        try:
            for i, clip in enumerate(edl.clips):
                frames = _render_clip_frames(
                    cap, clip, edl, info.width, info.height, src_fps, seed=i
                )
                for f in frames:
                    proc.stdin.write(np.ascontiguousarray(f).tobytes())
                if progress:
                    print(
                        f"  [{i + 1}/{total}] {clip.label} "
                        f"{clip.out_start:.2f}-{clip.out_end:.2f}s "
                        f"({clip.move.kind}, {len(frames)} frames)",
                        flush=True,
                    )
        finally:
            if proc.stdin:
                proc.stdin.close()
            cap.release()

        rc = proc.wait()
        if rc != 0:
            raise RuntimeError(f"ffmpeg exited with status {rc}")

    return out_path
