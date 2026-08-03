"""Turn moments + music into a renderable EDL.

The interesting work here is beat quantisation. The naive version - snap the
start of every clip to a beat - sounds wrong, because what the ear wants is
the *impact* on the beat, not the cut. So instead the planner keeps clips
butted together and flexes the pre-roll: it holds a little more or a little
less context before the hit so that the hit itself lands on a strong beat.

Speed ramps complicate this, because a slow-mo window makes source seconds
and output seconds different lengths. :func:`src_to_out` and :func:`out_to_src`
convert between the two.
"""

from __future__ import annotations

from typing import List, Optional, Sequence

import numpy as np

from .audio import MusicAnalysis
from .camera import move_for
from .config import Config
from .probe import MediaInfo
from .timeline import Clip, Edl, Moment, MoveSpec

#: Never produce a clip shorter than this on the output timeline.
MIN_CLIP = 0.30


def src_to_out(d: float, ramp_speed: float, ramp_window: float) -> float:
    """Output-timeline offset for a source offset ``d`` from the impact.

    Inside ``±ramp_window`` of the impact, playback runs at ``ramp_speed``,
    so that stretch of source occupies ``1/ramp_speed`` as much output time.
    """
    if ramp_speed >= 1.0 or ramp_window <= 0:
        return d
    sign = 1.0 if d >= 0 else -1.0
    a = abs(d)
    if a <= ramp_window:
        return sign * (a / ramp_speed)
    return sign * (ramp_window / ramp_speed + (a - ramp_window))


def out_to_src(o: float, ramp_speed: float, ramp_window: float) -> float:
    """Inverse of :func:`src_to_out`."""
    if ramp_speed >= 1.0 or ramp_window <= 0:
        return o
    sign = 1.0 if o >= 0 else -1.0
    a = abs(o)
    knee = ramp_window / ramp_speed
    if a <= knee:
        return sign * (a * ramp_speed)
    return sign * (ramp_window + (a - knee))


def _grid(music: Optional[MusicAnalysis], cfg: Config, kind: str) -> np.ndarray:
    """Beat times of ``kind``, expressed on the output timeline."""
    if music is None or not cfg.quantize:
        return np.asarray([])
    beats = music.beats_of_kind(kind) - cfg.music_start
    return beats[beats >= 0]


def _snap_forward(value: float, grid: np.ndarray, floor: float) -> float:
    """Nearest grid value to ``value`` that is at least ``floor``.

    Returns ``max(value, floor)`` when the grid is empty or exhausted.
    """
    if len(grid) == 0:
        return max(value, floor)
    usable = grid[grid >= floor]
    if len(usable) == 0:
        return max(value, floor)
    return float(usable[int(np.argmin(np.abs(usable - value)))])


def build_edl(
    source: str,
    moments: Sequence[Moment],
    cfg: Config,
    info: MediaInfo,
    music: Optional[MusicAnalysis] = None,
    music_path: Optional[str] = None,
    target_duration: Optional[float] = None,
) -> Edl:
    """Lay moments out on the output timeline, quantised to the music."""
    beat_grid = _grid(music, cfg, "beat")
    impact_grid = _grid(music, cfg, cfg.align_impact_to)

    base_move = MoveSpec(
        zoom_peak=cfg.zoom_max,
        zoom_base=cfg.zoom_base,
        punch_in=cfg.punch_in,
        punch_out=cfg.punch_out,
        shake_amp=cfg.shake_amp,
        shake_decay=cfg.shake_decay,
        focus_smooth=cfg.focus_smooth,
        focus_lead=cfg.focus_lead,
    )

    ramp_speed = cfg.ramp_slowmo if cfg.ramp_slowmo < 1.0 else 1.0
    ramp_window = cfg.ramp_window if ramp_speed < 1.0 else 0.0

    # A music bed caps the edit unless the caller overrides it.
    limit = target_duration
    if limit is None and music is not None:
        limit = max(music.duration - cfg.music_start, 0.0)

    clips: List[Clip] = []
    cursor = 0.0

    for i, m in enumerate(sorted(moments, key=lambda x: x.impact)):
        nominal_pre = src_to_out(m.impact - m.start, ramp_speed, ramp_window)
        nominal_post = src_to_out(m.end - m.impact, ramp_speed, ramp_window)

        # 1. Land the impact on a beat of the requested class.
        want_impact = cursor + nominal_pre
        impact_out = _snap_forward(want_impact, impact_grid, cursor + MIN_CLIP / 2)
        out_pre = impact_out - cursor

        # 2. Convert back to source and clamp to what the footage actually has.
        src_pre = out_to_src(out_pre, ramp_speed, ramp_window)
        if src_pre > m.impact:                      # would run off the head
            src_pre = m.impact
            out_pre = src_to_out(src_pre, ramp_speed, ramp_window)
            impact_out = cursor + out_pre

        # 3. End the clip on a beat too, so the next cut is on-grid.
        want_end = impact_out + nominal_post
        out_end = _snap_forward(want_end, beat_grid, impact_out + MIN_CLIP / 2)
        out_post = out_end - impact_out

        src_post = out_to_src(out_post, ramp_speed, ramp_window)
        tail = info.duration - m.impact
        if src_post > tail:                          # would run off the tail
            src_post = tail
            out_post = src_to_out(src_post, ramp_speed, ramp_window)

        out_duration = out_pre + out_post
        if out_duration < MIN_CLIP:
            continue

        if limit is not None and cursor + out_duration > limit:
            out_duration = limit - cursor
            if out_duration < MIN_CLIP:
                break
            # Trim the tail rather than the run-up; the hit matters more.
            out_post = max(out_duration - out_pre, 0.0)
            src_post = out_to_src(out_post, ramp_speed, ramp_window)

        clips.append(
            Clip(
                src_start=max(0.0, m.impact - src_pre),
                src_end=min(info.duration, m.impact + src_post),
                src_impact=m.impact,
                out_start=cursor,
                out_duration=out_duration,
                move=move_for(m.score, base_move, m.label),
                focus=list(m.focus),
                label=m.label,
                score=m.score,
                ramp_speed=ramp_speed,
                ramp_window=ramp_window,
            )
        )
        cursor += out_duration
        if limit is not None and cursor >= limit - MIN_CLIP:
            break

    return Edl(
        source=source,
        clips=clips,
        music=music_path,
        music_start=cfg.music_start,
        markers=music.markers() if music else [],
        tempo=music.tempo if music else 0.0,
        fps=cfg.fps,
        width=cfg.out_width,
        height=cfg.out_height,
    )


def describe(edl: Edl) -> str:
    """Human-readable summary of a plan, for the CLI and for sanity checks."""
    lines = [
        f"source     {edl.source}",
        f"output     {edl.width}x{edl.height} @ {edl.fps:g}fps",
        f"duration   {edl.duration:.2f}s across {len(edl.clips)} clips",
    ]
    if edl.music:
        lines.append(f"music      {edl.music} @ {edl.tempo:.1f} BPM (from {edl.music_start:.2f}s)")
    lines.append("")
    lines.append(f"{'#':>3}  {'out':>15}  {'source':>15}  {'move':<6} {'score':>5}  label")
    for i, c in enumerate(edl.clips):
        impact_out = c.out_start + src_to_out(
            c.src_impact - c.src_start, c.ramp_speed, c.ramp_window
        )
        lines.append(
            f"{i:>3}  "
            f"{c.out_start:6.2f}-{c.out_end:<6.2f}  "
            f"{c.src_start:6.2f}-{c.src_end:<6.2f}  "
            f"{c.move.kind:<6} {c.score:5.2f}  "
            f"{c.label} (hit @ {impact_out:.2f}s)"
        )
    return "\n".join(lines)
