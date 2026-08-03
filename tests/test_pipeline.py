"""End-to-end tests against generated media.

These are slower than the unit tests because they encode and decode real
video. They are the ones that would catch a regression in detection accuracy,
so they check the planted event times and the framing, not just that the
pipeline runs without raising.
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.make_sample import EVENTS, make_game_audio, make_music, make_video  # noqa: E402
from wtfengine.audio import analyze_music  # noqa: E402
from wtfengine.config import load_preset  # noqa: E402
from wtfengine.detect import build_hype_curve, find_moments, moments_from_markers  # noqa: E402
from wtfengine.plan import build_edl, src_to_out  # noqa: E402
from wtfengine.probe import probe  # noqa: E402
from wtfengine.render import render  # noqa: E402
from wtfengine.timeline import Edl  # noqa: E402

pytestmark = pytest.mark.skipif(
    shutil.which("ffmpeg") is None, reason="ffmpeg not installed"
)

DURATION = 38.0


@pytest.fixture(scope="module")
def media(tmp_path_factory):
    """Generate the sample clip and music once for the whole module."""
    d = tmp_path_factory.mktemp("media")
    silent, wav = d / "silent.mp4", d / "game.wav"
    gameplay, music = d / "gameplay.mp4", d / "music.wav"

    make_video(silent, DURATION, 1280, 720, 30.0)
    make_game_audio(wav, DURATION)
    subprocess.run(
        [
            "ffmpeg", "-v", "error", "-y", "-i", str(silent), "-i", str(wav),
            "-c:v", "libx264", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-shortest", str(gameplay),
        ],
        check=True,
    )
    make_music(music, DURATION + 12.0, bpm=128.0, drop_at=8.0)
    return {"gameplay": gameplay, "music": music}


def test_probe_reads_the_stream(media):
    info = probe(media["gameplay"])
    assert (info.width, info.height) == (1280, 720)
    assert info.fps == pytest.approx(30.0, abs=0.1)
    assert info.duration == pytest.approx(DURATION, abs=0.5)
    assert info.has_audio


def test_detector_finds_every_planted_event(media):
    cfg = load_preset("meme")
    moments, _ = find_moments(media["gameplay"], cfg)
    found = sorted(m.impact for m in moments)
    truth = [e[0] for e in EVENTS]

    assert len(found) == len(truth), f"expected {len(truth)} moments, got {found}"
    for want, got in zip(truth, found):
        # One analysis sample of tolerance, plus a little for the burst ramp.
        assert got == pytest.approx(want, abs=0.35)


def test_detector_finds_nothing_spurious_in_quiet_footage(media):
    """Every detected moment should sit near a planted event, not between them."""
    cfg = load_preset("meme")
    moments, _ = find_moments(media["gameplay"], cfg)
    truth = np.array([e[0] for e in EVENTS])
    for m in moments:
        assert np.min(np.abs(truth - m.impact)) < 0.5


def test_focus_locks_onto_the_action_point(media):
    """The framing target at each impact should be the planted screen position.

    This is the test that would have caught the original centroid bug, where
    background noise dragged the focus towards the middle of the frame.
    """
    cfg = load_preset("meme")
    curve = build_hype_curve(media["gameplay"], cfg)
    for t, ex, ey in EVENTS:
        i = int(np.argmin(np.abs(curve.times - t)))
        fx, fy = curve.focus[i]
        err = float(np.hypot(fx - ex, fy - ey))
        assert err < 0.05, f"event at {t}s framed at ({fx:.3f},{fy:.3f}), want ({ex},{ey})"


def test_music_analysis_recovers_tempo_and_drop(media):
    m = analyze_music(media["music"])
    assert m.tempo == pytest.approx(128.0, rel=0.06)
    assert len(m.beats) > 50
    assert m.drop is not None
    assert m.drop == pytest.approx(8.0, abs=1.5)


def test_impacts_land_on_the_beat_grid(media):
    cfg = load_preset("meme")
    music = analyze_music(media["music"])
    info = probe(media["gameplay"])
    moments, _ = find_moments(media["gameplay"], cfg, info=info)
    edl = build_edl(str(media["gameplay"]), moments, cfg, info, music,
                    str(media["music"]))

    grid = music.beats_of_kind(cfg.align_impact_to) - cfg.music_start
    for c in edl.clips:
        impact_out = c.out_start + src_to_out(
            c.src_impact - c.src_start, c.ramp_speed, c.ramp_window
        )
        # Either on the grid, or clamped because the footage ran out.
        off_grid = float(np.min(np.abs(grid - impact_out)))
        hit_head = c.src_start <= 1e-6
        assert off_grid < 0.05 or hit_head, f"impact at {impact_out:.3f}s is off-grid"


def test_render_produces_a_playable_file(media, tmp_path):
    cfg = load_preset("meme")
    cfg.out_width, cfg.out_height = 540, 960   # smaller, for test speed
    cfg.crf, cfg.preset = 30, "ultrafast"

    music = analyze_music(media["music"])
    info = probe(media["gameplay"])
    moments, _ = find_moments(media["gameplay"], cfg, info=info)
    edl = build_edl(str(media["gameplay"]), moments, cfg, info, music,
                    str(media["music"]))

    out = tmp_path / "out.mp4"
    render(edl, out, cfg, progress=False)

    assert out.exists() and out.stat().st_size > 10_000
    rendered = probe(out)
    assert (rendered.width, rendered.height) == (540, 960)
    assert rendered.has_audio
    assert rendered.duration == pytest.approx(edl.duration, abs=0.3)


def test_render_without_music_still_works(media, tmp_path):
    cfg = load_preset("flat")
    cfg.out_width, cfg.out_height = 480, 270
    cfg.crf, cfg.preset = 30, "ultrafast"

    info = probe(media["gameplay"])
    moments, _ = find_moments(media["gameplay"], cfg, info=info)
    edl = build_edl(str(media["gameplay"]), moments[:2], cfg, info)

    out = tmp_path / "silent.mp4"
    render(edl, out, cfg, progress=False)
    assert probe(out).duration == pytest.approx(edl.duration, abs=0.3)


def test_game_audio_mixing_keeps_the_length(media, tmp_path):
    """Time-stretched gameplay audio must still line up with the video."""
    cfg = load_preset("meme")
    cfg.out_width, cfg.out_height = 480, 854
    cfg.crf, cfg.preset = 30, "ultrafast"
    cfg.game_audio_level = 0.4

    music = analyze_music(media["music"])
    info = probe(media["gameplay"])
    moments, _ = find_moments(media["gameplay"], cfg, info=info)
    edl = build_edl(str(media["gameplay"]), moments[:3], cfg, info, music,
                    str(media["music"]))

    out = tmp_path / "mixed.mp4"
    render(edl, out, cfg, progress=False)
    assert probe(out).duration == pytest.approx(edl.duration, abs=0.3)


def test_supplied_markers_bypass_detection(media):
    """The replay-marker path should use exactly the times it is given."""
    cfg = load_preset("meme")
    info = probe(media["gameplay"])
    curve = build_hype_curve(media["gameplay"], cfg, info)
    markers = [
        {"t": 11.0, "label": "Charge of Darkness", "score": 1.0},
        {"t": 20.0, "label": "kill", "score": 0.8},
        {"t": 999.0, "label": "out of range", "score": 1.0},  # dropped
    ]
    moments = moments_from_markers(markers, cfg, info, curve)
    assert [m.impact for m in moments] == [11.0, 20.0]
    assert moments[0].label == "Charge of Darkness"

    edl = build_edl(str(media["gameplay"]), moments, cfg, info)
    # A travel ability should get the whip treatment.
    assert edl.clips[0].move.kind == "whip"


def test_saved_edl_renders_identically(media, tmp_path):
    cfg = load_preset("flat")
    cfg.out_width, cfg.out_height = 320, 180
    cfg.crf, cfg.preset = 32, "ultrafast"

    info = probe(media["gameplay"])
    moments, _ = find_moments(media["gameplay"], cfg, info=info)
    edl = build_edl(str(media["gameplay"]), moments[:2], cfg, info)

    path = tmp_path / "plan.json"
    edl.save(path)
    reloaded = Edl.load(path)

    a, b = tmp_path / "a.mp4", tmp_path / "b.mp4"
    render(edl, a, cfg, progress=False)
    render(reloaded, b, cfg, progress=False)
    assert a.read_bytes() == b.read_bytes()


def test_cli_make_runs(media, tmp_path):
    from wtfengine.cli import main

    out = tmp_path / "cli.mp4"
    rc = main([
        "make", str(media["gameplay"]),
        "--music", str(media["music"]),
        "--preset", "hype",
        "--size", "360x640",
        "--crf", "32",
        "--duration", "6",
        "-o", str(out),
    ])
    assert rc == 0
    assert out.exists()
    assert probe(out).duration <= 6.5


def test_cli_reports_a_missing_file_cleanly(tmp_path):
    from wtfengine.cli import main

    assert main(["analyze", str(tmp_path / "nope.mp4")]) == 1
