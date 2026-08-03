"""Generate synthetic "gameplay" footage and a music track.

Not a Dota replacement - just a deterministic stand-in with known event
times, so the whole pipeline can be exercised and regression-tested without
shipping a copyrighted clip. Events are bright, fast, loud bursts at known
timestamps; a correct detector should find them and nothing else.

    python tools/make_sample.py --outdir sample
"""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from pathlib import Path
from typing import List, Tuple

import cv2
import numpy as np

#: (time_seconds, x_fraction, y_fraction) of each planted event.
EVENTS: List[Tuple[float, float, float]] = [
    (6.0, 0.25, 0.35),
    (14.5, 0.75, 0.60),
    (23.0, 0.50, 0.25),
    (31.5, 0.20, 0.75),
]

SR = 48000


def make_video(path: Path, duration: float, w: int, h: int, fps: float) -> None:
    rng = np.random.default_rng(7)
    writer = cv2.VideoWriter(
        str(path), cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h)
    )
    if not writer.isOpened():
        raise RuntimeError("could not open VideoWriter")

    n = int(round(duration * fps))
    # A lazily drifting "hero" so there is always some baseline motion.
    hero = np.array([w * 0.5, h * 0.5])
    hero_v = np.array([28.0, 17.0])

    for i in range(n):
        t = i / fps
        frame = np.zeros((h, w, 3), dtype=np.uint8)
        frame[:, :] = (28, 42, 30)  # murky map green

        # Static-ish terrain so the frame is not uniform.
        for k in range(24):
            cx = int((k * 137) % w)
            cy = int((k * 89) % h)
            cv2.circle(frame, (cx, cy), 26, (34, 52, 36), -1)

        hero = hero + hero_v / fps
        for axis, limit in ((0, w), (1, h)):
            if hero[axis] < 40 or hero[axis] > limit - 40:
                hero_v[axis] *= -1
                hero[axis] = np.clip(hero[axis], 40, limit - 40)
        cv2.circle(frame, (int(hero[0]), int(hero[1])), 12, (200, 190, 120), -1)

        # Events: a short burst of bright, fast particles at a fixed spot.
        for et, ex, ey in EVENTS:
            dt = t - et
            if -0.15 < dt < 0.9:
                cx, cy = int(ex * w), int(ey * h)
                energy = float(np.exp(-3.0 * max(dt, 0.0)))
                count = int(160 * energy) + 10
                pts = rng.normal(0.0, 55.0 * (0.4 + dt if dt > 0 else 0.4), (count, 2))
                for px, py in pts:
                    x, y = int(cx + px), int(cy + py)
                    if 0 <= x < w and 0 <= y < h:
                        shade = int(120 + 135 * energy)
                        cv2.circle(frame, (x, y), 3, (shade, shade, 255), -1)
                cv2.circle(frame, (cx, cy), int(10 + 60 * energy),
                           (90, 120, 255), max(1, int(6 * energy)))

        writer.write(frame)

    writer.release()


def make_game_audio(path: Path, duration: float) -> None:
    rng = np.random.default_rng(11)
    t = np.arange(int(duration * SR)) / SR
    # Quiet ambience, so the loudness signal is not pure silence.
    sig = 0.02 * rng.normal(0.0, 1.0, len(t))
    sig += 0.01 * np.sin(2 * np.pi * 110 * t)

    for et, _, _ in EVENTS:
        idx = int(et * SR)
        span = int(0.8 * SR)
        if idx + span > len(sig):
            span = len(sig) - idx
        if span <= 0:
            continue
        env = np.exp(-np.arange(span) / (0.18 * SR))
        burst = env * (
            0.55 * np.sin(2 * np.pi * 180 * np.arange(span) / SR)
            + 0.35 * rng.normal(0.0, 1.0, span)
        )
        sig[idx : idx + span] += burst

    _write_wav(path, sig)


def make_music(path: Path, duration: float, bpm: float = 128.0,
               drop_at: float = 8.0) -> None:
    """A click track with a clear pulse, a bar accent, and a drop."""
    t = np.arange(int(duration * SR)) / SR
    sig = np.zeros_like(t)
    beat = 60.0 / bpm

    i = 0
    time = 0.0
    while time < duration:
        idx = int(time * SR)
        span = min(int(0.22 * SR), len(sig) - idx)
        if span > 0:
            k = np.arange(span) / SR
            env = np.exp(-k / 0.055)
            downbeat = (i % 4) == 0
            freq = 62.0 if downbeat else 132.0
            gain = 1.0 if downbeat else 0.55
            if time < drop_at:
                gain *= 0.42          # quieter intro so the drop is detectable
            sig[idx : idx + span] += gain * env * np.sin(2 * np.pi * freq * k)
        i += 1
        time += beat

    # Sustained bass after the drop, to give the energy lift some body.
    after = t >= drop_at
    sig[after] += 0.16 * np.sin(2 * np.pi * 55 * t[after])

    _write_wav(path, sig)


def _write_wav(path: Path, sig: np.ndarray) -> None:
    import soundfile as sf

    peak = float(np.max(np.abs(sig))) or 1.0
    sf.write(str(path), (sig / peak * 0.89).astype(np.float32), SR)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--outdir", type=Path, default=Path("sample"))
    ap.add_argument("--duration", type=float, default=38.0)
    ap.add_argument("--width", type=int, default=1280)
    ap.add_argument("--height", type=int, default=720)
    ap.add_argument("--fps", type=float, default=30.0)
    args = ap.parse_args()

    args.outdir.mkdir(parents=True, exist_ok=True)
    gameplay = args.outdir / "gameplay.mp4"
    music = args.outdir / "music.wav"

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        silent = tmp / "silent.mp4"
        game_wav = tmp / "game.wav"

        print("rendering gameplay video...")
        make_video(silent, args.duration, args.width, args.height, args.fps)
        print("rendering gameplay audio...")
        make_game_audio(game_wav, args.duration)

        subprocess.run(
            [
                "ffmpeg", "-v", "error", "-y",
                "-i", str(silent), "-i", str(game_wav),
                "-c:v", "libx264", "-crf", "20", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-b:a", "128k", "-shortest",
                str(gameplay),
            ],
            check=True,
        )

    print("rendering music...")
    make_music(music, args.duration + 12.0)

    print(f"\nwrote {gameplay}")
    print(f"wrote {music}")
    print("planted events at: " + ", ".join(f"{e[0]:.1f}s" for e in EVENTS))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
