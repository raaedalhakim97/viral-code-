"""The meme focus camera.

Given a clip and where the action is, produce a crop rectangle for every
output frame. Two things are happening at once:

* **zoom** - an envelope over clip-relative time. ``punch`` snaps in hard at
  the impact frame and eases out; ``push`` drifts in across the whole clip;
  ``hold`` sits still; ``whip`` overshoots and settles.
* **framing** - the crop is centred on the action point, so zooming in
  actually shows you the Spirit Breaker rather than the middle of the screen.

Shake is added on top as a decaying oscillation seeded per clip, so two
clips do not shake identically.

Everything is expressed in *normalised* coordinates (0..1 of the source
frame) until the last step, which converts to integer pixel rectangles.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

import numpy as np
from scipy.ndimage import gaussian_filter1d

from .timeline import MoveSpec


@dataclass(frozen=True)
class CropRect:
    """An integer crop rectangle in source pixels."""

    x: int
    y: int
    w: int
    h: int


def _ease_out_cubic(t: np.ndarray) -> np.ndarray:
    return 1.0 - np.power(1.0 - np.clip(t, 0.0, 1.0), 3.0)


def _ease_in_out(t: np.ndarray) -> np.ndarray:
    t = np.clip(t, 0.0, 1.0)
    return np.where(t < 0.5, 2 * t * t, 1.0 - np.power(-2 * t + 2, 2) / 2)


def zoom_envelope(
    rel_times: np.ndarray,
    impact_rel: float,
    move: MoveSpec,
) -> np.ndarray:
    """Zoom factor per frame for a clip.

    ``rel_times`` are seconds from the clip's first frame, ``impact_rel`` is
    where the impact sits within that span.
    """
    base = move.zoom_base
    peak = base + (move.zoom_peak - base) * max(move.intensity, 0.0)
    peak = max(peak, base)

    if move.kind == "hold":
        return np.full_like(rel_times, base)

    if move.kind == "push":
        span = max(rel_times[-1] - rel_times[0], 1e-6) if len(rel_times) else 1.0
        return base + (peak - base) * _ease_in_out((rel_times - rel_times[0]) / span)

    # punch / whip both key off the impact frame.
    before = rel_times < impact_rel
    z = np.empty_like(rel_times)

    # Ramp in over punch_in seconds ending at the impact.
    lead = max(move.punch_in, 1e-6)
    in_t = (rel_times - (impact_rel - lead)) / lead
    z_in = base + (peak - base) * _ease_out_cubic(in_t)
    z[before] = np.where(in_t[before] < 0, base, z_in[before])

    # Ease back out over punch_out seconds after the impact.
    tail = max(move.punch_out, 1e-6)
    out_t = (rel_times - impact_rel) / tail
    after = ~before
    if move.kind == "whip":
        # Overshoot then settle: a damped wobble around the resting zoom.
        wob = np.exp(-3.0 * np.clip(out_t, 0.0, None)) * np.cos(
            6.0 * np.clip(out_t, 0.0, None)
        )
        z[after] = base + (peak - base) * np.clip(wob, -0.3, 1.0)[after]
    else:
        z[after] = peak - (peak - base) * _ease_in_out(out_t)[after]

    return np.clip(z, 1.0, None)


def shake_offsets(
    rel_times: np.ndarray,
    impact_rel: float,
    move: MoveSpec,
    seed: int = 0,
) -> np.ndarray:
    """``(N, 2)`` normalised x/y offsets from an impact shake."""
    amp = move.shake_amp * max(move.intensity, 0.0)
    if amp <= 0:
        return np.zeros((len(rel_times), 2))

    since = np.clip(rel_times - impact_rel, 0.0, None)
    decay = np.exp(-move.shake_decay * since)
    decay[rel_times < impact_rel] = 0.0

    rng = np.random.default_rng(seed)
    fx, fy = rng.uniform(28.0, 44.0, size=2)
    px, py = rng.uniform(0.0, 2 * np.pi, size=2)

    ox = amp * decay * np.sin(fx * rel_times + px)
    oy = amp * decay * np.sin(fy * rel_times + py)
    return np.stack([ox, oy], axis=1)


def focus_path(
    rel_times: np.ndarray,
    focus: Sequence[Tuple[float, float, float]],
    clip_start: float,
    smooth_sigma: float,
    lead: float = 0.0,
) -> np.ndarray:
    """Resample and smooth the action-point path onto ``rel_times``.

    Falls back to frame centre when no focus data is available.
    """
    n = len(rel_times)
    if not focus:
        return np.full((n, 2), 0.5)

    ft = np.asarray([p[0] for p in focus], dtype=np.float64) - clip_start
    fx = np.asarray([p[1] for p in focus], dtype=np.float64)
    fy = np.asarray([p[2] for p in focus], dtype=np.float64)

    order = np.argsort(ft)
    ft, fx, fy = ft[order], fx[order], fy[order]

    sample_at = rel_times + lead
    x = np.interp(sample_at, ft, fx, left=fx[0], right=fx[-1])
    y = np.interp(sample_at, ft, fy, left=fy[0], right=fy[-1])

    dt = float(np.median(np.diff(rel_times))) if n > 1 else 1.0
    if smooth_sigma > 0 and dt > 0 and n > 2:
        sigma = max(smooth_sigma / dt, 0.5)
        x = gaussian_filter1d(x, sigma=sigma, mode="nearest")
        y = gaussian_filter1d(y, sigma=sigma, mode="nearest")

    return np.clip(np.stack([x, y], axis=1), 0.0, 1.0)


def plan_camera(
    out_rel_times: np.ndarray,
    impact_out_rel: float,
    src_times: np.ndarray,
    move: MoveSpec,
    focus: Sequence[Tuple[float, float, float]],
    src_w: int,
    src_h: int,
    out_aspect: float,
    focus_smooth: float = 0.6,
    focus_lead: float = 0.0,
    seed: int = 0,
) -> List[CropRect]:
    """Produce one crop rectangle per output frame of a clip.

    Two time bases are in play. The zoom envelope and shake run on
    ``out_rel_times`` (seconds from the clip's first *output* frame), because
    a punch should feel the same length on screen whether or not the shot is
    in slow motion. Framing runs on ``src_times`` (absolute source seconds),
    because that is what the action-point path is indexed by.

    The crop always has the *output* aspect ratio, so reframing a 16:9
    capture to 9:16 happens here rather than as a separate letterbox step.
    """
    zoom = zoom_envelope(out_rel_times, impact_out_rel, move)
    centres = focus_path(src_times, focus, 0.0, focus_smooth, focus_lead)
    centres = centres + shake_offsets(out_rel_times, impact_out_rel, move, seed=seed)

    # Largest window of the target aspect that fits inside the source frame.
    if src_w / src_h > out_aspect:
        base_h = float(src_h)
        base_w = base_h * out_aspect
    else:
        base_w = float(src_w)
        base_h = base_w / out_aspect

    rects: List[CropRect] = []
    for z, (cx, cy) in zip(zoom, centres):
        z = max(float(z), 1.0)
        w = base_w / z
        h = base_h / z

        # Clamp the centre so the window stays inside the frame.
        half_w, half_h = w / 2.0, h / 2.0
        px = np.clip(cx * src_w, half_w, src_w - half_w)
        py = np.clip(cy * src_h, half_h, src_h - half_h)

        x = int(round(px - half_w))
        y = int(round(py - half_h))
        w_i = max(2, int(round(w)))
        h_i = max(2, int(round(h)))
        x = max(0, min(x, src_w - w_i))
        y = max(0, min(y, src_h - h_i))
        rects.append(CropRect(x=x, y=y, w=w_i, h=h_i))

    return rects


def move_for(score: float, base: MoveSpec, label: str = "wtf") -> MoveSpec:
    """Pick and scale a camera move for a moment.

    Weak moments get a gentle push so the edit has dynamic range; strong ones
    get the full punch. Replay-sourced labels that imply a windup (a charge,
    a channel) get a whip instead, which suits a move that travels.
    """
    spec = MoveSpec(**base.to_dict())
    spec.intensity = float(np.clip(0.45 + 0.75 * score, 0.0, 1.4))

    lowered = label.lower()
    if any(k in lowered for k in ("charge", "leap", "blink", "dash", "chase")):
        spec.kind = "whip"
    elif score < 0.35:
        spec.kind = "push"
    else:
        spec.kind = "punch"
    return spec
