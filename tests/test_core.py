"""Unit tests for the pure-logic parts: timing maths, camera, planning."""

from __future__ import annotations

import numpy as np
import pytest

from wtfengine.audio import MusicAnalysis, snap
from wtfengine.camera import focus_path, plan_camera, shake_offsets, zoom_envelope, move_for
from wtfengine.config import PRESETS, Config, load_preset
from wtfengine.plan import MIN_CLIP, _snap_forward, build_edl, out_to_src, src_to_out
from wtfengine.probe import MediaInfo
from wtfengine.render import _atempo_chain
from wtfengine.timeline import Edl, Moment, MoveSpec


# --------------------------------------------------------------------------
# config
# --------------------------------------------------------------------------

def test_presets_all_load():
    for name in PRESETS:
        cfg = load_preset(name)
        assert isinstance(cfg, Config)
        assert cfg.out_width > 0 and cfg.out_height > 0


def test_preset_does_not_mutate_shared_state():
    a = load_preset("meme")
    a.zoom_max = 99.0
    b = load_preset("meme")
    assert b.zoom_max != 99.0


def test_merged_ignores_none():
    cfg = Config()
    out = cfg.merged(zoom_max=None, max_moments=3)
    assert out.zoom_max == cfg.zoom_max
    assert out.max_moments == 3


def test_from_dict_rejects_unknown_keys():
    with pytest.raises(ValueError):
        Config.from_dict({**Config().to_dict(), "nonsense": 1})


# --------------------------------------------------------------------------
# ramp timing
# --------------------------------------------------------------------------

@pytest.mark.parametrize("d", [-3.0, -1.0, -0.2, 0.0, 0.2, 1.0, 3.0])
def test_ramp_roundtrip(d):
    speed, window = 0.4, 0.45
    assert out_to_src(src_to_out(d, speed, window), speed, window) == pytest.approx(d)


def test_ramp_disabled_is_identity():
    assert src_to_out(1.7, 1.0, 0.5) == pytest.approx(1.7)
    assert out_to_src(1.7, 1.0, 0.5) == pytest.approx(1.7)


def test_slowmo_stretches_output_time():
    # Half a second of source at 0.5x should occupy a full second of output.
    assert src_to_out(0.5, 0.5, 1.0) == pytest.approx(1.0)


def test_ramp_is_monotonic():
    speed, window = 0.4, 0.45
    xs = np.linspace(-4, 4, 200)
    ys = [src_to_out(x, speed, window) for x in xs]
    assert all(b > a for a, b in zip(ys, ys[1:]))


# --------------------------------------------------------------------------
# camera
# --------------------------------------------------------------------------

def _move(**kw):
    base = dict(kind="punch", zoom_peak=2.0, zoom_base=1.05, punch_in=0.15,
                punch_out=0.5, shake_amp=0.0, intensity=1.0)
    base.update(kw)
    return MoveSpec(**base)


def test_punch_peaks_at_impact():
    t = np.linspace(0, 3, 300)
    z = zoom_envelope(t, impact_rel=1.0, move=_move())
    peak_idx = int(np.argmax(z))
    assert t[peak_idx] == pytest.approx(1.0, abs=0.05)


def test_punch_rests_at_base_before_the_windup():
    t = np.linspace(0, 3, 300)
    z = zoom_envelope(t, impact_rel=1.5, move=_move(punch_in=0.15))
    early = z[t < 1.0]
    assert np.allclose(early, 1.05, atol=1e-6)


def test_punch_eases_back_out():
    t = np.linspace(0, 3, 300)
    z = zoom_envelope(t, impact_rel=1.0, move=_move(punch_out=0.5))
    assert z[-1] < z[int(np.argmax(z))]
    assert z[-1] == pytest.approx(1.05, abs=0.02)


def test_hold_is_constant():
    t = np.linspace(0, 2, 100)
    z = zoom_envelope(t, 1.0, _move(kind="hold"))
    assert np.allclose(z, 1.05)


def test_push_increases_monotonically():
    t = np.linspace(0, 2, 100)
    z = zoom_envelope(t, 1.0, _move(kind="push"))
    assert np.all(np.diff(z) >= -1e-9)
    assert z[-1] > z[0]


def test_zoom_never_below_one():
    t = np.linspace(0, 3, 300)
    for kind in ("punch", "push", "hold", "whip"):
        z = zoom_envelope(t, 1.0, _move(kind=kind, zoom_base=1.0))
        assert np.all(z >= 1.0 - 1e-9)


def test_intensity_scales_peak():
    t = np.linspace(0, 3, 300)
    weak = zoom_envelope(t, 1.0, _move(intensity=0.2)).max()
    strong = zoom_envelope(t, 1.0, _move(intensity=1.0)).max()
    assert strong > weak


def test_shake_is_silent_before_impact_and_decays_after():
    t = np.linspace(0, 2, 200)
    off = shake_offsets(t, impact_rel=1.0, move=_move(shake_amp=0.02), seed=1)
    assert np.allclose(off[t < 1.0], 0.0)
    late = np.abs(off[t > 1.6]).max()
    early = np.abs(off[(t > 1.0) & (t < 1.2)]).max()
    assert late < early


def test_shake_disabled_by_zero_amplitude():
    t = np.linspace(0, 2, 50)
    assert np.allclose(shake_offsets(t, 1.0, _move(shake_amp=0.0)), 0.0)


def test_focus_path_defaults_to_centre():
    t = np.linspace(0, 1, 10)
    p = focus_path(t, [], 0.0, smooth_sigma=0.0)
    assert np.allclose(p, 0.5)


def test_focus_path_tracks_supplied_points():
    focus = [(0.0, 0.2, 0.2), (1.0, 0.8, 0.8)]
    t = np.linspace(0, 1, 21)
    p = focus_path(t, focus, 0.0, smooth_sigma=0.0)
    assert p[0] == pytest.approx([0.2, 0.2], abs=1e-6)
    assert p[-1] == pytest.approx([0.8, 0.8], abs=1e-6)
    assert p[10] == pytest.approx([0.5, 0.5], abs=0.02)


def test_focus_path_stays_in_unit_square():
    focus = [(0.0, -5.0, 9.0), (1.0, 4.0, -3.0)]
    p = focus_path(np.linspace(0, 1, 20), focus, 0.0, smooth_sigma=0.0)
    assert p.min() >= 0.0 and p.max() <= 1.0


def test_crops_stay_inside_the_source_frame():
    n = 90
    out_rel = np.linspace(0, 3, n)
    src_t = np.linspace(10.0, 13.0, n)
    # Focus deliberately pinned to a corner to exercise clamping.
    focus = [(10.0, 0.0, 0.0), (13.0, 1.0, 1.0)]
    rects = plan_camera(
        out_rel_times=out_rel, impact_out_rel=1.0, src_times=src_t,
        move=_move(shake_amp=0.05), focus=focus,
        src_w=1920, src_h=1080, out_aspect=9 / 16, focus_smooth=0.0,
    )
    assert len(rects) == n
    for r in rects:
        assert r.x >= 0 and r.y >= 0
        assert r.x + r.w <= 1920
        assert r.y + r.h <= 1080
        assert r.w >= 2 and r.h >= 2


def test_crop_matches_output_aspect():
    n = 20
    rects = plan_camera(
        out_rel_times=np.linspace(0, 1, n), impact_out_rel=0.5,
        src_times=np.linspace(0, 1, n), move=_move(shake_amp=0.0), focus=[],
        src_w=1920, src_h=1080, out_aspect=9 / 16, focus_smooth=0.0,
    )
    for r in rects:
        assert r.w / r.h == pytest.approx(9 / 16, rel=0.02)


def test_crop_centres_on_the_focus_point():
    n = 30
    focus = [(0.0, 0.25, 0.75), (1.0, 0.25, 0.75)]
    rects = plan_camera(
        out_rel_times=np.linspace(0, 1, n), impact_out_rel=0.5,
        src_times=np.linspace(0, 1, n), move=_move(shake_amp=0.0), focus=focus,
        src_w=1920, src_h=1080, out_aspect=9 / 16, focus_smooth=0.0,
    )
    mid = rects[len(rects) // 2]
    assert (mid.x + mid.w / 2) / 1920 == pytest.approx(0.25, abs=0.02)
    assert (mid.y + mid.h / 2) / 1080 == pytest.approx(0.75, abs=0.05)


def test_move_for_picks_a_whip_for_travel_abilities():
    base = MoveSpec()
    assert move_for(0.9, base, "Charge of Darkness").kind == "whip"
    assert move_for(0.9, base, "wtf").kind == "punch"
    assert move_for(0.1, base, "wtf").kind == "push"


# --------------------------------------------------------------------------
# planning
# --------------------------------------------------------------------------

def _music(bpm=120.0, duration=60.0, beats_per_bar=4):
    beat = 60.0 / bpm
    beats = np.arange(0.0, duration, beat)
    return MusicAnalysis(
        tempo=bpm, beats=beats, strengths=np.ones(len(beats)),
        downbeat_offset=0, beats_per_bar=beats_per_bar, drop=None,
        duration=duration,
    )


def _info(duration=60.0):
    return MediaInfo(path="x.mp4", duration=duration, width=1920, height=1080,
                     fps=30.0, has_audio=True)


def _moments(times, duration=60.0):
    return [
        Moment(impact=t, score=1.0, start=max(0.0, t - 1.2),
               end=min(duration, t + 1.6))
        for t in times
    ]


def test_snap_forward_respects_the_floor():
    grid = np.array([0.0, 1.0, 2.0, 3.0])
    assert _snap_forward(0.4, grid, floor=1.5) == 2.0
    assert _snap_forward(2.6, grid, floor=0.0) == 3.0
    assert _snap_forward(1.2, np.array([]), floor=0.5) == 1.2


def test_clips_are_contiguous_and_ordered():
    cfg = load_preset("meme")
    edl = build_edl("x.mp4", _moments([6, 15, 24, 33]), cfg, _info(),
                    music=_music(), music_path="m.wav")
    assert len(edl.clips) == 4
    for a, b in zip(edl.clips, edl.clips[1:]):
        assert b.out_start == pytest.approx(a.out_end, abs=1e-6)
    assert edl.clips[0].out_start == 0.0


def test_impacts_land_on_the_requested_beat_class():
    cfg = load_preset("meme")
    cfg.align_impact_to = "downbeat"
    music = _music(bpm=120.0)
    edl = build_edl("x.mp4", _moments([6, 15, 24, 33]), cfg, _info(),
                    music=music, music_path="m.wav")
    bar = 4 * 60.0 / 120.0
    for c in edl.clips:
        impact_out = c.out_start + src_to_out(
            c.src_impact - c.src_start, c.ramp_speed, c.ramp_window
        )
        assert impact_out % bar == pytest.approx(0.0, abs=1e-3) or \
               bar - (impact_out % bar) == pytest.approx(0.0, abs=1e-3)


def test_clip_source_ranges_stay_inside_the_footage():
    cfg = load_preset("meme")
    info = _info(duration=40.0)
    # Moments right at both ends, where clamping has to kick in.
    edl = build_edl("x.mp4", _moments([0.3, 39.7], duration=40.0), cfg, info,
                    music=_music(), music_path="m.wav")
    for c in edl.clips:
        assert c.src_start >= 0.0
        assert c.src_end <= info.duration + 1e-6
        assert c.src_start <= c.src_impact <= c.src_end


def test_edit_is_capped_by_the_music_length():
    cfg = load_preset("hype")
    music = _music(duration=8.0)
    edl = build_edl("x.mp4", _moments(list(range(5, 55, 5))), cfg, _info(),
                    music=music, music_path="m.wav")
    assert edl.duration <= 8.0 + 1e-6


def test_target_duration_overrides_music_length():
    cfg = load_preset("hype")
    edl = build_edl("x.mp4", _moments(list(range(5, 55, 5))), cfg, _info(),
                    music=_music(duration=120.0), music_path="m.wav",
                    target_duration=6.0)
    assert edl.duration <= 6.0 + 1e-6


def test_works_without_music():
    cfg = load_preset("meme")
    edl = build_edl("x.mp4", _moments([6, 15]), cfg, _info())
    assert len(edl.clips) == 2
    assert edl.music is None
    assert edl.duration > 0


def test_no_clip_is_shorter_than_the_minimum():
    cfg = load_preset("hype")
    edl = build_edl("x.mp4", _moments([6, 15, 24]), cfg, _info(),
                    music=_music(), music_path="m.wav")
    for c in edl.clips:
        assert c.out_duration >= MIN_CLIP


def test_quantize_off_skips_the_grid():
    cfg = load_preset("meme")
    cfg.quantize = False
    edl = build_edl("x.mp4", _moments([6, 15]), cfg, _info(),
                    music=_music(), music_path="m.wav")
    # Without quantisation the clip length is exactly the ramped window.
    c = edl.clips[0]
    expected = src_to_out(c.src_impact - c.src_start, c.ramp_speed, c.ramp_window) \
        + src_to_out(c.src_end - c.src_impact, c.ramp_speed, c.ramp_window)
    assert c.out_duration == pytest.approx(expected, abs=1e-6)


# --------------------------------------------------------------------------
# music helpers
# --------------------------------------------------------------------------

def test_beats_of_kind_partitions_the_bar():
    m = _music(bpm=120.0, duration=16.0)
    assert len(m.beats_of_kind("downbeat")) < len(m.beats_of_kind("strong"))
    assert len(m.beats_of_kind("strong")) < len(m.beats_of_kind("beat"))


def test_beats_of_kind_rejects_nonsense():
    with pytest.raises(ValueError):
        _music().beats_of_kind("chorus")


def test_markers_are_sorted_and_classified():
    marks = _music(bpm=120.0, duration=8.0).markers()
    assert marks == sorted(marks, key=lambda m: m.time)
    assert {m.kind for m in marks} == {"downbeat", "strong", "beat"}


def test_snap_picks_the_nearest_grid_value():
    grid = np.array([0.0, 0.5, 1.0])
    assert snap(0.6, grid) == 0.5
    assert snap(3.0, np.array([])) == 3.0


# --------------------------------------------------------------------------
# serialisation & misc
# --------------------------------------------------------------------------

def test_edl_survives_a_json_roundtrip(tmp_path):
    cfg = load_preset("meme")
    edl = build_edl("x.mp4", _moments([6, 15]), cfg, _info(),
                    music=_music(), music_path="m.wav")
    edl.clips[0].focus = [(5.0, 0.2, 0.3), (6.0, 0.4, 0.5)]
    p = tmp_path / "edl.json"
    edl.save(p)
    back = Edl.load(p)
    assert back.duration == pytest.approx(edl.duration)
    assert len(back.clips) == len(edl.clips)
    assert back.clips[0].focus == edl.clips[0].focus
    assert back.clips[0].move.kind == edl.clips[0].move.kind


@pytest.mark.parametrize("speed", [0.25, 0.4, 0.5, 1.0, 1.5, 3.0])
def test_atempo_chain_multiplies_back_to_the_speed(speed):
    chain = _atempo_chain(speed)
    if not chain:
        assert speed == 1.0
        return
    product = 1.0
    for stage in chain:
        value = float(stage.split("=")[1])
        assert 0.5 <= value <= 2.0
        product *= value
    assert product == pytest.approx(speed, rel=1e-4)
