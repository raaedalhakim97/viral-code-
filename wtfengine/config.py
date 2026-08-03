"""Tunable knobs for the whole pipeline, plus a few opinionated presets."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field, fields
from pathlib import Path
from typing import Any, Dict


@dataclass
class Config:
    # ---- analysis ----------------------------------------------------------
    sample_fps: float = 10.0
    """How many frames per second to inspect when building the hype curve.

    This is analysis resolution only; rendering always uses full frame rate.
    10 fps is plenty to spot a teamfight and keeps a 30-minute VOD scannable
    in well under a minute.
    """

    analysis_width: int = 192
    """Frames are downscaled to this width before motion analysis."""

    w_motion: float = 1.0
    """Weight of visual motion energy in the hype score."""

    w_audio: float = 1.0
    """Weight of gameplay loudness in the hype score."""

    w_novelty: float = 0.8
    """Weight of the *rate of change* of the above. Sudden jumps are what
    make a moment read as "wtf" rather than merely busy."""

    smooth_sigma: float = 0.35
    """Gaussian smoothing of the hype curve, in seconds."""

    # ---- moment selection --------------------------------------------------
    max_moments: int = 12
    min_gap: float = 4.0
    """Minimum seconds between two selected moments, so the edit does not
    pick six peaks out of the same teamfight."""

    peak_prominence: float = 0.12
    """0..1. Lower finds more (and weaker) moments."""

    pre_roll: float = 1.4
    """Seconds of context kept before the impact frame."""

    post_roll: float = 1.8
    """Seconds kept after the impact frame."""

    # ---- music -------------------------------------------------------------
    quantize: bool = True
    """Snap every cut to a musical beat."""

    align_impact_to: str = "strong"
    """Which beat class the impact frame lands on: "beat", "strong" (bar
    anchor) or "downbeat"."""

    beats_per_bar: int = 4
    music_start: float = 0.0
    """Seconds into the music track to start the edit. Set this to the drop."""

    # ---- camera ------------------------------------------------------------
    zoom_max: float = 1.85
    """Peak punch-in factor at the impact frame."""

    zoom_base: float = 1.06
    """Resting zoom. A hair above 1.0 leaves room to pan without letterboxing."""

    punch_in: float = 0.14
    """Seconds taken to snap from base zoom to peak zoom. Short = memey."""

    punch_out: float = 0.55
    """Seconds taken to ease back out."""

    focus_smooth: float = 0.6
    """Gaussian smoothing of the focus point path, in seconds. Higher is
    calmer; lower snaps to the action but can feel jittery."""

    focus_lead: float = 0.0
    """Seconds the camera anticipates the action point. Positive values make
    the camera arrive slightly early, which reads as intentional."""

    shake_amp: float = 0.012
    """Impact shake amplitude as a fraction of frame width. 0 disables."""

    shake_decay: float = 6.0
    """Higher decays the shake faster."""

    # ---- timing ------------------------------------------------------------
    ramp_slowmo: float = 0.45
    """Speed factor applied in a short window around impact. 1.0 disables."""

    ramp_window: float = 0.45
    """Seconds around impact that get the slow-mo treatment."""

    # ---- output ------------------------------------------------------------
    out_width: int = 1080
    out_height: int = 1920
    fps: float = 30.0
    crf: int = 18
    preset: str = "medium"
    game_audio_level: float = 0.0
    """Linear gain for the original gameplay audio mixed under the music.
    0 disables. Ignored when speed ramps are active (see render.py)."""

    music_level: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        known = {f.name for f in fields(cls)}
        unknown = set(data) - known
        if unknown:
            raise ValueError(f"unknown config keys: {sorted(unknown)}")
        return cls(**data)

    @classmethod
    def load(cls, path: str | Path) -> "Config":
        return cls.from_dict(json.loads(Path(path).read_text()))

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    def merged(self, **overrides: Any) -> "Config":
        """Return a copy with non-None overrides applied."""
        data = self.to_dict()
        data.update({k: v for k, v in overrides.items() if v is not None})
        return Config.from_dict(data)


#: Named starting points. ``load_preset`` returns a fresh Config each call.
PRESETS: Dict[str, Dict[str, Any]] = {
    # Hard, fast, TikTok-brained. Big punches, heavy slow-mo, lots of shake.
    "meme": {
        "zoom_max": 2.1,
        "punch_in": 0.10,
        "punch_out": 0.45,
        "shake_amp": 0.018,
        "ramp_slowmo": 0.40,
        "pre_roll": 1.1,
        "post_roll": 1.5,
        "focus_smooth": 0.45,
    },
    # Calmer. For "actually good play" montages rather than jokes.
    "cinematic": {
        "zoom_max": 1.45,
        "zoom_base": 1.02,
        "punch_in": 0.55,
        "punch_out": 1.1,
        "shake_amp": 0.0,
        "ramp_slowmo": 0.6,
        "pre_roll": 2.2,
        "post_roll": 2.6,
        "focus_smooth": 1.1,
    },
    # Maximum moments, minimum dwell. Good for 60-second "every fight" reels.
    "hype": {
        "zoom_max": 1.9,
        "punch_in": 0.12,
        "punch_out": 0.4,
        "max_moments": 20,
        "min_gap": 2.5,
        "pre_roll": 0.9,
        "post_roll": 1.2,
        "ramp_slowmo": 1.0,
    },
    # No camera work at all - just beat-quantized cuts. Useful as an A/B
    # baseline when you want to see what the camera is actually adding.
    "flat": {
        "zoom_max": 1.0,
        "zoom_base": 1.0,
        "shake_amp": 0.0,
        "ramp_slowmo": 1.0,
    },
}


def load_preset(name: str) -> Config:
    if name not in PRESETS:
        raise KeyError(f"unknown preset {name!r}; have {sorted(PRESETS)}")
    return Config.from_dict({**Config().to_dict(), **PRESETS[name]})
