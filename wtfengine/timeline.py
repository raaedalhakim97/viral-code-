"""Data model for the edit.

The renderer never re-derives anything: an :class:`Edl` fully describes the
output, so it can be dumped to JSON, hand-edited, and re-rendered.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class Moment:
    """A candidate WTF moment found in (or supplied for) the source video."""

    impact: float
    """Source timestamp of the peak - the frame the edit should land on."""

    score: float
    """0..1 hype score. Used for ranking and for scaling camera intensity."""

    start: float
    """Source timestamp where the clip should begin."""

    end: float
    """Source timestamp where the clip should end."""

    label: str = "wtf"
    """Where this came from: "wtf" (auto), or an event name from a replay."""

    focus: List[Tuple[float, float, float]] = field(default_factory=list)
    """Action-point path as ``(t, x, y)`` with x/y normalised to 0..1 in
    source-frame coordinates. May be empty, in which case the camera holds
    on frame centre."""

    @property
    def duration(self) -> float:
        return self.end - self.start

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["focus"] = [list(p) for p in self.focus]
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Moment":
        d = dict(d)
        d["focus"] = [tuple(p) for p in d.get("focus", [])]
        return cls(**d)


@dataclass
class MoveSpec:
    """A camera move attached to a clip.

    ``kind`` selects the zoom envelope; the camera module turns this into a
    per-frame crop rectangle.
    """

    kind: str = "punch"          # punch | push | hold | whip
    zoom_peak: float = 1.8
    zoom_base: float = 1.06
    punch_in: float = 0.14
    punch_out: float = 0.55
    shake_amp: float = 0.012
    shake_decay: float = 6.0
    intensity: float = 1.0
    """Scales zoom-above-base and shake. Driven by the moment's score."""

    focus_smooth: float = 0.6
    """Gaussian smoothing of the framing path, in seconds."""

    focus_lead: float = 0.0
    """Seconds the framing anticipates the action point."""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "MoveSpec":
        return cls(**d)


@dataclass
class Clip:
    """One cut in the output timeline."""

    src_start: float
    src_end: float
    src_impact: float
    """Where, in source time, the impact frame sits."""

    out_start: float
    """Where this clip begins on the output timeline."""

    out_duration: float
    """How long it occupies the output timeline, after speed ramping."""

    move: MoveSpec = field(default_factory=MoveSpec)
    focus: List[Tuple[float, float, float]] = field(default_factory=list)
    label: str = "wtf"
    score: float = 0.0
    ramp_speed: float = 1.0
    """Speed factor inside the ramp window. 1.0 means no ramp."""

    ramp_window: float = 0.0
    """Seconds of source either side of impact that get ramped."""

    @property
    def out_end(self) -> float:
        return self.out_start + self.out_duration

    @property
    def src_duration(self) -> float:
        return self.src_end - self.src_start

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["focus"] = [list(p) for p in self.focus]
        return d

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Clip":
        d = dict(d)
        d["move"] = MoveSpec.from_dict(d.get("move", {}))
        d["focus"] = [tuple(p) for p in d.get("focus", [])]
        return cls(**d)


@dataclass
class Marker:
    """A musical landmark, in music-track time."""

    time: float
    kind: str = "beat"   # beat | strong | downbeat | drop
    strength: float = 1.0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Marker":
        return cls(**d)


@dataclass
class Edl:
    """A complete, renderable edit decision list."""

    source: str
    clips: List[Clip] = field(default_factory=list)
    music: Optional[str] = None
    music_start: float = 0.0
    markers: List[Marker] = field(default_factory=list)
    tempo: float = 0.0
    fps: float = 30.0
    width: int = 1080
    height: int = 1920

    @property
    def duration(self) -> float:
        return max((c.out_end for c in self.clips), default=0.0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "source": self.source,
            "music": self.music,
            "music_start": self.music_start,
            "tempo": self.tempo,
            "fps": self.fps,
            "width": self.width,
            "height": self.height,
            "duration": self.duration,
            "clips": [c.to_dict() for c in self.clips],
            "markers": [m.to_dict() for m in self.markers],
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Edl":
        return cls(
            source=d["source"],
            clips=[Clip.from_dict(c) for c in d.get("clips", [])],
            music=d.get("music"),
            music_start=d.get("music_start", 0.0),
            markers=[Marker.from_dict(m) for m in d.get("markers", [])],
            tempo=d.get("tempo", 0.0),
            fps=d.get("fps", 30.0),
            width=d.get("width", 1080),
            height=d.get("height", 1920),
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2) + "\n")

    @classmethod
    def load(cls, path: str | Path) -> "Edl":
        return cls.from_dict(json.loads(Path(path).read_text()))
