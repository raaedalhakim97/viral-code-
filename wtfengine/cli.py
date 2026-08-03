"""Command line entry point.

    python -m wtfengine make gameplay.mp4 --music song.mp3 -o out.mp4
    python -m wtfengine analyze gameplay.mp4
    python -m wtfengine plan gameplay.mp4 --music song.mp3 --edl plan.json
    python -m wtfengine render plan.json -o out.mp4
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .config import PRESETS, Config, load_preset
from .timeline import Edl


def _add_common(p: argparse.ArgumentParser) -> None:
    p.add_argument("--preset", choices=sorted(PRESETS), default="meme",
                   help="starting point for all the knobs (default: meme)")
    p.add_argument("--config", type=Path, help="JSON config file, applied over the preset")
    p.add_argument("--max-moments", type=int, dest="max_moments")
    p.add_argument("--min-gap", type=float, dest="min_gap",
                   help="minimum seconds between selected moments")
    p.add_argument("--prominence", type=float, dest="peak_prominence",
                   help="0..1; lower finds more, weaker moments")
    p.add_argument("--pre-roll", type=float, dest="pre_roll")
    p.add_argument("--post-roll", type=float, dest="post_roll")
    p.add_argument("--zoom", type=float, dest="zoom_max", help="peak punch-in factor")
    p.add_argument("--shake", type=float, dest="shake_amp")
    p.add_argument("--slowmo", type=float, dest="ramp_slowmo",
                   help="speed factor at impact; 1.0 disables")
    p.add_argument("--no-quantize", action="store_true",
                   help="do not snap cuts to the beat")
    p.add_argument("--align", choices=["beat", "strong", "downbeat"],
                   dest="align_impact_to", help="which beat the impact lands on")
    p.add_argument("--music-start", type=float, dest="music_start",
                   help="seconds into the music to start (set this to the drop)")
    p.add_argument("--start-at-drop", action="store_true",
                   help="auto-detect the drop and start the music there")
    p.add_argument("--landscape", action="store_true", help="1920x1080 instead of 1080x1920")
    p.add_argument("--size", help="explicit WxH, e.g. 1080x1350")
    p.add_argument("--fps", type=float)
    p.add_argument("--crf", type=int)
    p.add_argument("--game-audio", type=float, dest="game_audio_level",
                   help="linear gain for gameplay audio under the music (0 = off)")
    p.add_argument("--markers", type=Path,
                   help="JSON of known event times; skips automatic detection")
    p.add_argument("--duration", type=float, help="cap the output length in seconds")


def _config_from_args(args: argparse.Namespace) -> Config:
    cfg = load_preset(args.preset)
    if getattr(args, "config", None):
        cfg = Config.from_dict({**cfg.to_dict(), **json.loads(args.config.read_text())})

    overrides = {
        k: getattr(args, k, None)
        for k in (
            "max_moments", "min_gap", "peak_prominence", "pre_roll", "post_roll",
            "zoom_max", "shake_amp", "ramp_slowmo", "align_impact_to",
            "music_start", "fps", "crf", "game_audio_level",
        )
    }
    cfg = cfg.merged(**overrides)

    if getattr(args, "no_quantize", False):
        cfg.quantize = False
    if getattr(args, "landscape", False):
        cfg.out_width, cfg.out_height = 1920, 1080
    if getattr(args, "size", None):
        w, _, h = args.size.lower().partition("x")
        cfg.out_width, cfg.out_height = int(w), int(h)
    return cfg


def _analyze_music(path: Optional[Path], cfg: Config, start_at_drop: bool):
    if path is None:
        return None
    from .audio import analyze_music

    music = analyze_music(path, beats_per_bar=cfg.beats_per_bar)
    if start_at_drop and music.drop is not None:
        cfg.music_start = music.drop
        print(f"drop detected at {music.drop:.2f}s; starting music there")
    return music


def _build_plan(source: Path, music_path: Optional[Path], cfg: Config,
                start_at_drop: bool, markers_path: Optional[Path],
                duration: Optional[float]) -> Edl:
    from .detect import build_hype_curve, find_moments, load_markers, moments_from_markers
    from .plan import build_edl
    from .probe import probe

    info = probe(source)
    print(f"source: {info.width}x{info.height} @ {info.fps:.2f}fps, {info.duration:.1f}s")

    if markers_path:
        markers = load_markers(markers_path)
        print(f"using {len(markers)} supplied markers (detection skipped)")
        curve = build_hype_curve(source, cfg, info)  # still needed for framing
        moments = moments_from_markers(markers, cfg, info, curve)
    else:
        print("scanning for WTF moments...")
        moments, _ = find_moments(source, cfg, info=info)
    print(f"found {len(moments)} moments")

    music = _analyze_music(music_path, cfg, start_at_drop)
    if music:
        print(f"music: {music.tempo:.1f} BPM, {len(music.beats)} beats")

    return build_edl(
        source=str(source),
        moments=moments,
        cfg=cfg,
        info=info,
        music=music,
        music_path=str(music_path) if music_path else None,
        target_duration=duration,
    )


def cmd_analyze(args: argparse.Namespace) -> int:
    from .detect import find_moments
    from .probe import probe

    cfg = _config_from_args(args)
    info = probe(args.source)
    moments, curve = find_moments(args.source, cfg, info=info)

    print(f"{info.width}x{info.height} @ {info.fps:.2f}fps, {info.duration:.1f}s")
    print(f"{len(moments)} moments\n")
    print(f"{'#':>3}  {'impact':>9}  {'score':>5}  window")
    for i, m in enumerate(moments):
        print(f"{i:>3}  {m.impact:9.2f}  {m.score:5.2f}  {m.start:.2f}-{m.end:.2f}")

    if args.json:
        Path(args.json).write_text(
            json.dumps({"moments": [m.to_dict() for m in moments]}, indent=2) + "\n"
        )
        print(f"\nwrote {args.json}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    from .plan import describe

    cfg = _config_from_args(args)
    edl = _build_plan(args.source, args.music, cfg, args.start_at_drop,
                      args.markers, args.duration)
    print()
    print(describe(edl))
    if args.edl:
        edl.save(args.edl)
        print(f"\nwrote {args.edl}")
    return 0


def cmd_make(args: argparse.Namespace) -> int:
    from .plan import describe
    from .render import render

    cfg = _config_from_args(args)
    edl = _build_plan(args.source, args.music, cfg, args.start_at_drop,
                      args.markers, args.duration)
    print()
    print(describe(edl))
    if args.edl:
        edl.save(args.edl)
    print(f"\nrendering {edl.duration:.2f}s -> {args.out}")
    render(edl, args.out, cfg)
    print(f"done: {args.out}")
    return 0


def cmd_render(args: argparse.Namespace) -> int:
    from .render import render

    cfg = _config_from_args(args)
    edl = Edl.load(args.edl_path)
    print(f"rendering {edl.duration:.2f}s from {args.edl_path} -> {args.out}")
    render(edl, args.out, cfg)
    print(f"done: {args.out}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="wtfengine",
        description="Turn raw Dota 2 gameplay into beat-synced WTF-moment edits.",
    )
    sub = p.add_subparsers(dest="command", required=True)

    a = sub.add_parser("analyze", help="find WTF moments and print them")
    a.add_argument("source", type=Path)
    a.add_argument("--json", type=Path, help="write the moments to a JSON file")
    _add_common(a)
    a.set_defaults(func=cmd_analyze)

    pl = sub.add_parser("plan", help="build an EDL without rendering")
    pl.add_argument("source", type=Path)
    pl.add_argument("--music", type=Path)
    pl.add_argument("--edl", type=Path, help="write the EDL here")
    _add_common(pl)
    pl.set_defaults(func=cmd_plan)

    m = sub.add_parser("make", help="detect, plan and render in one go")
    m.add_argument("source", type=Path)
    m.add_argument("--music", type=Path)
    m.add_argument("-o", "--out", type=Path, default=Path("out.mp4"))
    m.add_argument("--edl", type=Path, help="also write the EDL here")
    _add_common(m)
    m.set_defaults(func=cmd_make)

    r = sub.add_parser("render", help="render a previously saved EDL")
    r.add_argument("edl_path", type=Path)
    r.add_argument("-o", "--out", type=Path, default=Path("out.mp4"))
    _add_common(r)
    r.set_defaults(func=cmd_render)

    return p


def main(argv: Optional[list] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except (FileNotFoundError, ValueError, RuntimeError, KeyError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
