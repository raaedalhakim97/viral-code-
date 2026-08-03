"""Music analysis: tempo, beats, bar anchors and drops.

Only the music track goes through here. Gameplay audio is analysed in
:mod:`wtfengine.detect`, which cares about loudness rather than rhythm.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

import numpy as np

from .timeline import Marker


@dataclass
class MusicAnalysis:
    tempo: float
    beats: np.ndarray
    """Beat times in seconds."""

    strengths: np.ndarray
    """Per-beat onset strength, normalised to 0..1."""

    downbeat_offset: int
    """Index of the first beat of a bar, i.e. beat ``i`` is a downbeat when
    ``(i - downbeat_offset) % beats_per_bar == 0``."""

    beats_per_bar: int
    drop: Optional[float]
    """Best guess at the biggest energy lift in the track, or None."""

    duration: float

    def markers(self) -> List[Marker]:
        """Beats as :class:`Marker` objects, classified by position in the bar."""
        out: List[Marker] = []
        for i, t in enumerate(self.beats):
            phase = (i - self.downbeat_offset) % self.beats_per_bar
            if phase == 0:
                kind = "downbeat"
            elif phase * 2 == self.beats_per_bar:
                kind = "strong"
            else:
                kind = "beat"
            s = float(self.strengths[i]) if i < len(self.strengths) else 1.0
            out.append(Marker(time=float(t), kind=kind, strength=s))
        if self.drop is not None:
            out.append(Marker(time=float(self.drop), kind="drop", strength=1.0))
        out.sort(key=lambda m: m.time)
        return out

    def beats_of_kind(self, kind: str) -> np.ndarray:
        """Beat times matching a class.

        ``"beat"`` returns every beat; ``"strong"`` returns downbeats *and*
        mid-bar strong beats; ``"downbeat"`` returns bar starts only.
        """
        if kind == "beat":
            return self.beats
        idx = np.arange(len(self.beats))
        phase = (idx - self.downbeat_offset) % self.beats_per_bar
        if kind == "downbeat":
            keep = phase == 0
        elif kind == "strong":
            keep = (phase == 0) | (phase * 2 == self.beats_per_bar)
        else:
            raise ValueError(f"unknown beat kind {kind!r}")
        sel = self.beats[keep]
        return sel if len(sel) else self.beats


def _infer_downbeat_offset(strengths: np.ndarray, beats_per_bar: int) -> int:
    """Pick the bar phase whose beats carry the most onset energy.

    Real downbeats are usually the loudest beat in the bar, so summing onset
    strength per phase and taking the argmax is a cheap, decent estimate.
    """
    if len(strengths) < beats_per_bar:
        return 0
    sums = [
        float(strengths[phase::beats_per_bar].sum()) for phase in range(beats_per_bar)
    ]
    return int(np.argmax(sums))


def _find_drop(onset_env: np.ndarray, times: np.ndarray) -> Optional[float]:
    """Largest sustained jump in onset energy - a decent proxy for "the drop".

    Compares a trailing window against a leading window at every point and
    returns the time of the biggest lift. Returns None for tracks too short
    (or too flat) for the comparison to mean anything.
    """
    if len(onset_env) < 40:
        return None
    dt = float(np.median(np.diff(times))) if len(times) > 1 else 0.01
    win = max(4, int(round(2.0 / dt)))  # ~2 seconds either side
    if len(onset_env) < 3 * win:
        return None

    smooth = np.convolve(onset_env, np.ones(win) / win, mode="same")

    # Leading-window mean minus trailing-window mean, at every position.
    cum = np.concatenate([[0.0], np.cumsum(smooth)])
    idx = np.arange(win, len(smooth) - win)
    ahead = (cum[idx + win] - cum[idx]) / win
    behind = (cum[idx] - cum[idx - win]) / win
    lift = np.full(len(smooth), -np.inf)
    lift[idx] = ahead - behind

    best = int(np.argmax(lift))
    if not np.isfinite(lift[best]) or lift[best] <= 0:
        return None
    span = float(smooth.max() - smooth.min())
    if span <= 0 or lift[best] < 0.15 * span:
        return None  # too flat to call anything a drop
    return float(times[best])


def analyze_music(
    path: str | Path,
    beats_per_bar: int = 4,
    sr: int = 22050,
) -> MusicAnalysis:
    """Run beat tracking on a music file.

    Imports librosa lazily so that importing :mod:`wtfengine` stays cheap.
    """
    import librosa

    y, sr = librosa.load(str(path), sr=sr, mono=True)
    duration = float(len(y) / sr)

    # Beat-track on the percussive component; harmonic content smears onsets.
    y_perc = librosa.effects.percussive(y, margin=3.0)
    onset_env = librosa.onset.onset_strength(y=y_perc, sr=sr)
    tempo, beat_frames = librosa.beat.beat_track(
        onset_envelope=onset_env, sr=sr, trim=False
    )
    tempo = float(np.atleast_1d(tempo)[0])
    beats = librosa.frames_to_time(beat_frames, sr=sr)
    times = librosa.times_like(onset_env, sr=sr)

    if len(beats) == 0:
        # Pathological input (silence, or a track with no discernible pulse).
        # Fall back to a steady 120 BPM grid so downstream code still works.
        step = 0.5
        beats = np.arange(0.0, max(duration, step), step)
        strengths = np.ones(len(beats))
        return MusicAnalysis(
            tempo=120.0,
            beats=beats,
            strengths=strengths,
            downbeat_offset=0,
            beats_per_bar=beats_per_bar,
            drop=None,
            duration=duration,
        )

    # Sample the onset envelope at each beat for a per-beat strength.
    raw = np.interp(beats, times, onset_env)
    hi = float(raw.max())
    strengths = raw / hi if hi > 0 else np.ones_like(raw)

    return MusicAnalysis(
        tempo=tempo,
        beats=beats,
        strengths=strengths,
        downbeat_offset=_infer_downbeat_offset(strengths, beats_per_bar),
        beats_per_bar=beats_per_bar,
        drop=_find_drop(onset_env, times),
        duration=duration,
    )


def snap(value: float, grid: np.ndarray) -> float:
    """Nearest grid value to ``value``. Returns ``value`` for an empty grid."""
    if grid is None or len(grid) == 0:
        return float(value)
    return float(grid[int(np.argmin(np.abs(np.asarray(grid) - value)))])
