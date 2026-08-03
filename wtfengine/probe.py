"""Thin ffprobe/ffmpeg wrappers."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class FFmpegMissing(RuntimeError):
    pass


def require_ffmpeg() -> None:
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise FFmpegMissing(
                f"{tool} not found on PATH. Install it "
                "(apt install ffmpeg / brew install ffmpeg) and retry."
            )


@dataclass(frozen=True)
class MediaInfo:
    path: str
    duration: float
    width: int
    height: int
    fps: float
    has_audio: bool

    @property
    def aspect(self) -> float:
        return self.width / self.height


def _parse_rate(text: str | None) -> float:
    if not text:
        return 0.0
    if "/" in text:
        num, _, den = text.partition("/")
        try:
            den_f = float(den)
            return float(num) / den_f if den_f else 0.0
        except ValueError:
            return 0.0
    try:
        return float(text)
    except ValueError:
        return 0.0


def probe(path: str | Path) -> MediaInfo:
    """Read stream metadata. Raises FileNotFoundError if the path is absent."""
    require_ffmpeg()
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(p)

    out = subprocess.run(
        [
            "ffprobe", "-v", "error",
            "-print_format", "json",
            "-show_format", "-show_streams",
            str(p),
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(out)

    video = next(
        (s for s in data.get("streams", []) if s.get("codec_type") == "video"), None
    )
    if video is None:
        raise ValueError(f"{p} has no video stream")
    has_audio = any(s.get("codec_type") == "audio" for s in data.get("streams", []))

    fps = _parse_rate(video.get("avg_frame_rate")) or _parse_rate(
        video.get("r_frame_rate")
    )
    duration = float(data.get("format", {}).get("duration") or 0.0)
    if duration <= 0:
        duration = float(video.get("duration") or 0.0)

    return MediaInfo(
        path=str(p),
        duration=duration,
        width=int(video["width"]),
        height=int(video["height"]),
        fps=fps or 30.0,
        has_audio=has_audio,
    )


def audio_duration(path: str | Path) -> float:
    """Duration of an audio-only (or any) file, in seconds."""
    require_ffmpeg()
    out = subprocess.run(
        [
            "ffprobe", "-v", "error", "-print_format", "json",
            "-show_format", str(path),
        ],
        capture_output=True, text=True, check=True,
    ).stdout
    return float(json.loads(out).get("format", {}).get("duration") or 0.0)


def extract_audio(src: str | Path, dst: str | Path, sr: int = 22050) -> Path:
    """Decode the audio track of ``src`` to a mono wav at ``dst``."""
    require_ffmpeg()
    dst = Path(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y",
            "-i", str(src),
            "-vn", "-ac", "1", "-ar", str(sr),
            "-f", "wav", str(dst),
        ],
        check=True,
    )
    return dst
