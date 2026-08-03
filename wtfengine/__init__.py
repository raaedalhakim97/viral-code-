"""wtfengine - turn raw Dota 2 gameplay into beat-synced WTF-moment edits.

Pipeline:

    gameplay.mp4 ──> detect.find_moments()  ──┐
                                              ├──> plan.build_edl() ──> render.render()
    music.mp3    ──> audio.analyze_music()  ──┘

Everything runs offline. No API keys, no GPU.
"""

from .config import Config, PRESETS, load_preset
from .timeline import Clip, Edl, Marker, Moment, MoveSpec

__version__ = "0.1.0"

__all__ = [
    "Config",
    "PRESETS",
    "load_preset",
    "Clip",
    "Edl",
    "Marker",
    "Moment",
    "MoveSpec",
    "__version__",
]
