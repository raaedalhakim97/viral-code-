"""Find the WTF moments.

Two independent signals are combined into a single "hype curve":

* **motion** - mean absolute difference between consecutive sampled frames.
  A teamfight moves a lot of pixels; walking down a lane does not.
* **loudness** - short-time energy of the gameplay audio. Ability casts,
  deaths and your own screaming all land here.

Both are converted to a *novelty* term as well (the positive derivative),
because what makes a moment read as "wtf" is the jump, not the level.

Alongside the peak, the motion analysis produces an **action point** per
sampled frame - the centroid of where the change happened - which the camera
module later uses to decide what to zoom in on.

There is also :func:`moments_from_markers`, which takes exact event times
(e.g. parsed out of a ``.dem`` replay) and skips detection entirely. When you
have ground truth, use it - it beats any heuristic here.
"""

from __future__ import annotations

import json
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import cv2
import numpy as np
from scipy.ndimage import gaussian_filter1d
from scipy.signal import find_peaks

from .config import Config
from .probe import MediaInfo, extract_audio, probe
from .timeline import Moment


@dataclass
class HypeCurve:
    """The per-sample analysis of a source video."""

    times: np.ndarray
    hype: np.ndarray
    motion: np.ndarray
    loudness: np.ndarray
    focus: np.ndarray
    """``(N, 2)`` action points, normalised to 0..1 in frame coordinates."""

    def focus_path(self, start: float, end: float) -> List[Tuple[float, float, float]]:
        """Action points inside ``[start, end]`` as ``(t, x, y)`` triples."""
        keep = (self.times >= start) & (self.times <= end)
        return [
            (float(t), float(p[0]), float(p[1]))
            for t, p in zip(self.times[keep], self.focus[keep])
        ]


def _norm(x: np.ndarray) -> np.ndarray:
    """Scale to 0..1 using robust percentiles, so one explosion does not
    flatten everything else to zero."""
    if len(x) == 0:
        return x
    lo = float(np.percentile(x, 5))
    hi = float(np.percentile(x, 98))
    if hi - lo < 1e-9:
        return np.zeros_like(x)
    return np.clip((x - lo) / (hi - lo), 0.0, 1.0)


def _positive_delta(x: np.ndarray) -> np.ndarray:
    """Rising-edge energy: the positive part of the first difference."""
    d = np.diff(x, prepend=x[:1] if len(x) else x)
    return np.clip(d, 0.0, None)


def scan_video(path: str | Path, cfg: Config, info: Optional[MediaInfo] = None) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Sample the video and return ``(times, motion, focus)``.

    Frames are decoded sequentially and downscaled hard - this is the slow
    part of the pipeline, so it stays deliberately cheap.
    """
    info = info or probe(path)
    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        raise RuntimeError(f"could not open {path}")

    src_fps = info.fps or cap.get(cv2.CAP_PROP_FPS) or 30.0
    stride = max(1, int(round(src_fps / cfg.sample_fps)))

    times: List[float] = []
    motion: List[float] = []
    focus: List[Tuple[float, float]] = []

    prev: Optional[np.ndarray] = None
    idx = 0
    scale_w = cfg.analysis_width

    try:
        while True:
            ok = cap.grab()
            if not ok:
                break
            if idx % stride:
                idx += 1
                continue
            ok, frame = cap.retrieve()
            if not ok:
                break

            h, w = frame.shape[:2]
            scale_h = max(1, int(round(h * scale_w / w)))
            small = cv2.resize(frame, (scale_w, scale_h), interpolation=cv2.INTER_AREA)
            gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(np.float32)

            t = idx / src_fps
            if prev is None:
                motion.append(0.0)
                focus.append((0.5, 0.5))
            else:
                diff = np.abs(gray - prev)
                motion.append(float(diff.mean()))
                focus.append(_centroid(diff))
            times.append(t)
            prev = gray
            idx += 1
    finally:
        cap.release()

    if not times:
        raise RuntimeError(f"no frames decoded from {path}")

    return np.asarray(times), np.asarray(motion), np.asarray(focus, dtype=np.float32)


def _centroid(diff: np.ndarray) -> Tuple[float, float]:
    """Normalised centre of mass of the *strongest* change in a diff image.

    The threshold has to be aggressive. A loose one (say the 80th percentile)
    lets thousands of faintly-changing background pixels outvote the few
    hundred pixels that are actually the teamfight, and the centroid collapses
    towards the middle of the frame no matter what is happening. Keeping only
    the top few percent, and weighting by how far each pixel is *above* the
    threshold, locks onto the real action point.
    """
    thresh = float(np.percentile(diff, 99.0))
    if thresh <= 1e-6:
        return (0.5, 0.5)
    mask = np.clip(diff - thresh, 0.0, None)
    total = float(mask.sum())
    if total <= 1e-6:
        return (0.5, 0.5)
    h, w = mask.shape
    ys, xs = np.nonzero(mask)
    weights = mask[ys, xs]
    cx = float((xs * weights).sum() / total) / max(w - 1, 1)
    cy = float((ys * weights).sum() / total) / max(h - 1, 1)
    return (min(max(cx, 0.0), 1.0), min(max(cy, 0.0), 1.0))


def scan_loudness(path: str | Path, times: np.ndarray, sr: int = 22050) -> np.ndarray:
    """Short-time RMS of the gameplay audio, resampled onto ``times``.

    Returns zeros when the source has no audio track.
    """
    info = probe(path)
    if not info.has_audio:
        return np.zeros_like(times)

    import librosa

    with tempfile.TemporaryDirectory() as tmp:
        wav = extract_audio(path, Path(tmp) / "game.wav", sr=sr)
        y, sr = librosa.load(str(wav), sr=sr, mono=True)

    if len(y) == 0:
        return np.zeros_like(times)

    hop = 512
    rms = librosa.feature.rms(y=y, hop_length=hop)[0]
    rms_t = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
    return np.interp(times, rms_t, rms, left=0.0, right=0.0)


def build_hype_curve(path: str | Path, cfg: Config, info: Optional[MediaInfo] = None) -> HypeCurve:
    """Full analysis pass over a source video."""
    info = info or probe(path)
    times, motion_raw, focus = scan_video(path, cfg, info)
    loud_raw = scan_loudness(path, times)

    motion = _norm(motion_raw)
    loud = _norm(loud_raw)

    dt = float(np.median(np.diff(times))) if len(times) > 1 else 1.0 / cfg.sample_fps
    sigma = max(cfg.smooth_sigma / dt, 0.5) if dt > 0 else 1.0

    novelty = _norm(_positive_delta(motion) + _positive_delta(loud))

    hype = cfg.w_motion * motion + cfg.w_audio * loud + cfg.w_novelty * novelty
    total_w = max(cfg.w_motion + cfg.w_audio + cfg.w_novelty, 1e-6)
    hype = gaussian_filter1d(hype / total_w, sigma=sigma, mode="nearest")
    hype = _norm(hype)

    # Smooth the focus path, weighted by hype.
    #
    # A plain gaussian here is wrong: during quiet stretches the centroid is
    # essentially noise, and letting those samples vote equally drags the
    # camera off the action for a second either side of every impact. Weighting
    # by hype means quiet frames inherit the framing of nearby loud ones
    # instead of polluting them, so the camera is already on target when the
    # hit lands.
    if len(focus) > 2:
        # Weight by *raw* motion, squared. The hype curve is deliberately
        # smoothed, so it starts rising a beat before the event and would give
        # the pre-event (meaningless) centroids real influence; raw motion
        # steps up exactly when the action does. Squaring sharpens the
        # preference for the few frames where the centroid is trustworthy.
        w = np.clip(motion, 0.0, None) ** 2 + 1e-3
        wsum = gaussian_filter1d(w, sigma=sigma, mode="nearest")
        focus = np.stack(
            [
                gaussian_filter1d(focus[:, i] * w, sigma=sigma, mode="nearest")
                / np.maximum(wsum, 1e-9)
                for i in range(2)
            ],
            axis=1,
        )
        focus = np.clip(focus, 0.0, 1.0)

    return HypeCurve(
        times=times, hype=hype, motion=motion, loudness=loud, focus=focus
    )


def find_moments(
    path: str | Path,
    cfg: Config,
    curve: Optional[HypeCurve] = None,
    info: Optional[MediaInfo] = None,
) -> Tuple[List[Moment], HypeCurve]:
    """Detect and rank WTF moments. Returns ``(moments, curve)``."""
    info = info or probe(path)
    curve = curve or build_hype_curve(path, cfg, info)

    dt = (
        float(np.median(np.diff(curve.times)))
        if len(curve.times) > 1
        else 1.0 / cfg.sample_fps
    )
    distance = max(1, int(round(cfg.min_gap / dt))) if dt > 0 else 1

    peaks, props = find_peaks(
        curve.hype, prominence=cfg.peak_prominence, distance=distance
    )
    if len(peaks) == 0:
        # Nothing stood out. Fall back to the single hottest sample so the
        # caller still gets something renderable.
        peaks = np.asarray([int(np.argmax(curve.hype))])
        props = {"prominences": np.asarray([0.0])}

    order = np.argsort(curve.hype[peaks])[::-1][: cfg.max_moments]
    chosen = np.sort(peaks[order])

    moments: List[Moment] = []
    for p in chosen:
        impact = float(curve.times[p])
        start = max(0.0, impact - cfg.pre_roll)
        end = min(info.duration, impact + cfg.post_roll)
        if end - start < 0.4:
            continue
        moments.append(
            Moment(
                impact=impact,
                score=float(curve.hype[p]),
                start=start,
                end=end,
                label="wtf",
                focus=curve.focus_path(start, end),
            )
        )
    return moments, curve


def moments_from_markers(
    markers: Sequence[dict],
    cfg: Config,
    info: MediaInfo,
    curve: Optional[HypeCurve] = None,
) -> List[Moment]:
    """Build moments from known event times instead of detecting them.

    ``markers`` is a list of ``{"t": <seconds>, "label": <str>, "score": <0..1>}``
    dicts - the shape you get from parsing a Dota 2 replay combat log and
    offsetting game time onto video time. ``label`` and ``score`` are optional.

    When a ``curve`` is supplied the focus path is taken from it, so the
    camera still knows where to look; otherwise the camera holds centre.
    """
    out: List[Moment] = []
    for m in markers:
        t = float(m["t"])
        if t < 0 or t > info.duration:
            continue
        start = max(0.0, t - cfg.pre_roll)
        end = min(info.duration, t + cfg.post_roll)
        if end - start < 0.4:
            continue
        out.append(
            Moment(
                impact=t,
                score=float(m.get("score", 1.0)),
                start=start,
                end=end,
                label=str(m.get("label", "event")),
                focus=curve.focus_path(start, end) if curve else [],
            )
        )
    out.sort(key=lambda mm: mm.impact)
    return out


def load_markers(path: str | Path) -> List[dict]:
    """Read a marker JSON file.

    Accepts either a bare list or ``{"markers": [...]}``.
    """
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):
        data = data.get("markers", [])
    if not isinstance(data, list):
        raise ValueError("marker file must be a list, or an object with 'markers'")
    return data
