"""
beat_dance — math on the beat. See BEAT_DANCE.md.

Also a click-track generator, for verifying a render actually sits on the grid:

    python3 beat_dance.py --click 128 click.wav
    ffmpeg -i videos/BeatDance.mp4 -i click.wav -c:v copy -shortest check.mp4

That branch runs BEFORE manimlib is imported on purpose — manimlib parses
sys.argv at import time and rejects unknown flags, so anything reached after
the import can never see --click.
"""
import sys

if "--click" in sys.argv:
    import wave
    import numpy as _np

    _i = sys.argv.index("--click")
    _bpm = float(sys.argv[_i + 1])
    _out = sys.argv[_i + 2] if _i + 2 < len(sys.argv) else "click.wav"
    _SR, _dur = 44100, 40.0
    _sig = _np.zeros(int(_SR * _dur), _np.float32)
    _beat = 60.0 / _bpm
    for _n in range(int(_dur / _beat)):
        _s = int(_n * _beat * _SR)
        _e = min(_s + int(0.04 * _SR), len(_sig))
        _env = _np.exp(-_np.linspace(0, 8, _e - _s))
        _f = 1600 if _n % 4 == 0 else 900          # accent the bar line
        _sig[_s:_e] += _np.sin(2 * _np.pi * _f * _np.arange(_e - _s) / _SR) * _env * 0.6
    with wave.open(_out, "wb") as _w:
        _w.setnchannels(1)
        _w.setsampwidth(2)
        _w.setframerate(_SR)
        _w.writeframes((_np.clip(_sig, -1, 1) * 32767).astype(_np.int16).tobytes())
    print(f"{_out}  {_bpm:g} bpm  {_dur:g}s")
    sys.exit(0)

from manimlib import *
import numpy as np

# "MATH DANCING" - one line, moving on the beat (9:16, length set by BPM)
#
# EXPORTS SILENT, ON PURPOSE. Do not bake the song in. Two reasons:
#   1. Audio baked into the upload cannot be attributed to the sound's page,
#      and the sound page is where a trending audio's reach actually comes from.
#   2. Sounds peak in 5-14 days. Posting inside the first 24h of a sound's rise
#      is worth roughly 3x the views of posting after it peaks - so the sound
#      has to be chosen on posting day, not on render day.
# Add the sound in the TikTok editor. This file's whole job is to already be
# on the grid when you do.
#
# EVERYTHING SNAPS TO THE BEAT. Every run_time in this scene is a whole or half
# multiple of B = 60/BPM. Nothing is allowed to be 0.37s "because it looked
# right" - one off-grid animation and the whole piece drifts against the track.
#
# Set BPM to the track's tempo before rendering:
#   manimgl beat_dance.py BeatDance -w --bpm 128
#   xvfb-run -a -s "-screen 0 1600x1200x24" manimgl beat_dance.py BeatDance -w
#
# Check the sync before you trust it - this writes a click at the same BPM:
#   python3 beat_dance.py --click 128 click.wav
#   ffmpeg -i videos/BeatDance.mp4 -i click.wav -c:v copy -shortest check.mp4
# If the line's kick drifts off the click, the tempo is wrong, not the scene.

BPM = 120.0          # overridden by --bpm

# Beat budget - 64 beats = 16 bars, so the piece ends ON a bar line and loops
# clean. Change a section length and you must rebalance another to keep the
# total at 64, or the last frame lands mid-bar and the cut to the track shows.
#   wake   8B   (2 bars)
#   dance 24B   (6 bars)  12 ratios x 2B
#   build 16B   (4 bars)  2B morph + 8 harmonics x 1.5B + 2B tail
#   close 16B   (4 bars)
TOTAL_BEATS = 64

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
GOLD   = "#EBCB8B"

FRAME_H  = 9.0
SAFE_BOT = -FRAME_H / 2 + 0.22 * FRAME_H
LINE_Y   = -2.0


def _argval(flag, cast, default):
    if flag in sys.argv:
        i = sys.argv.index(flag)
        if i + 1 < len(sys.argv):
            return cast(sys.argv[i + 1])
    return default


class BeatDance(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)

        self.bpm = _argval("--bpm", float, BPM)
        self.B = 60.0 / self.bpm

        # One clock for the whole piece. The kick, the spin and the breathing
        # are all read off it analytically rather than driven by their own
        # animations - that is what keeps them locked to each other.
        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.a = ValueTracker(1.0)      # Lissajous x frequency
        self.b = ValueTracker(1.0)      # Lissajous y frequency
        self.harm = ValueTracker(1.0)   # Fourier harmonics in play
        self.mode = ValueTracker(0.0)   # 0 = Lissajous, 1 = Fourier
        self.amp = ValueTracker(1.0)

        self.section_wake()
        self.section_dance()
        self.section_build()
        self.section_close()

    # ------------------------------------------------------------------
    # kick: a spike at every beat that decays fast. Drives stroke weight,
    # so the line visibly punches even with the sound off.
    # ------------------------------------------------------------------
    def kick(self):
        t = self.clock.get_value()
        phase = (t % self.B) / self.B
        return float(np.exp(-((phase / 0.16) ** 2)))

    def downbeat(self):
        """Same, but only on every 4th beat - the bar line."""
        t = self.clock.get_value()
        phase = (t % (4 * self.B)) / (4 * self.B)
        return float(np.exp(-((phase / 0.05) ** 2)))

    # ------------------------------------------------------------------
    # The line itself. Lissajous when mode=0, Fourier square when mode=1,
    # and a real blend in between so the section change is a morph, not a cut.
    # ------------------------------------------------------------------
    def make_line(self):
        t = self.clock.get_value()
        a = self.a.get_value()
        b = self.b.get_value()
        m = self.mode.get_value()
        H = self.harm.get_value()
        A = self.amp.get_value()
        k = self.kick()

        N = 420
        u = np.linspace(0, TAU, N)

        # Lissajous, slowly precessing so it never looks frozen
        d = 0.35 * t
        lx = 1.85 * np.sin(a * u + d)
        ly = 1.85 * np.sin(b * u)

        # Fourier square wave, H harmonics, fractional H fades the next one in
        fx = np.linspace(-2.15, 2.15, N)
        fy = np.zeros(N)
        n = 1
        while n <= int(H):
            fy += np.sin(n * (u - 0.9 * t)) / n
            n += 2
        frac = H - int(H)
        if frac > 0:
            nn = int(H) + 1 + (int(H) % 2 == 0)
            fy += frac * np.sin(nn * (u - 0.9 * t)) / nn
        fy *= 1.45

        x = (1 - m) * lx + m * fx
        y = (1 - m) * ly + m * fy
        y = y * A * (1 + 0.06 * k)
        x = x * A * (1 + 0.06 * k)

        pts = [np.array([x[i], y[i] + 0.35, 0]) for i in range(N)]
        ln = VMobject(stroke_color=WHITE_, stroke_width=3.6 + 4.4 * k)
        ln.set_points_as_corners(pts)
        ln.set_stroke(opacity=0.85 + 0.15 * k)
        return ln

    def make_ring(self):
        """A ring that snaps out on every bar line — the visual downbeat."""
        d = self.downbeat()
        r = 1.0 + 2.6 * (1 - d)
        c = Circle(radius=r, stroke_color=GOLD, stroke_width=2.4 * d)
        c.set_stroke(opacity=0.55 * d)
        c.move_to(np.array([0, 0.35, 0]))
        return c

    # ------------------------------------------------------------------
    # beats 0-7   WAKE
    # ------------------------------------------------------------------
    def section_wake(self):
        B = self.B
        dot = Dot(np.array([0, 0.35, 0]), radius=0.10, fill_color=WHITE_)
        self.play(FadeIn(dot, scale=0.3), run_time=B / 2)

        self.line = always_redraw(self.make_line)
        self.ring = always_redraw(self.make_ring)
        self.amp.set_value(0.05)
        self.add(self.line, self.ring)
        self.remove(dot)
        self.play(self.amp.animate.set_value(1.0), run_time=2 * B,
                  rate_func=rush_from)
        self.wait(B * 1.5)

        tag = Text("sin(at) , sin(bt)", color=GREY, font_size=22)
        tag.move_to(np.array([0, 2.6, 0]))
        self.play(FadeIn(tag), run_time=B / 2)
        self.tag = tag
        self.wait(B * 3.5)

    # ------------------------------------------------------------------
    # beats 8-31   DANCE - a new Lissajous ratio every 2 beats
    # ------------------------------------------------------------------
    def section_dance(self):
        B = self.B
        ratios = [(1, 2), (2, 3), (3, 2), (3, 4), (4, 3), (5, 4),
                  (4, 5), (5, 6), (3, 5), (5, 3), (2, 5), (1, 1)]
        label = None
        for (p, q) in ratios:
            new = Text(f"{p} : {q}", color=GREY, font_size=26, weight=BOLD)
            new.move_to(np.array([0, 2.6, 0]))
            anims = [self.a.animate.set_value(p), self.b.animate.set_value(q)]
            if label is None:
                anims.append(FadeOut(self.tag))
            else:
                anims.append(FadeOut(label))
            anims.append(FadeIn(new))
            self.play(*anims, run_time=2 * B, rate_func=smooth)
            label = new
        self.label = label

    # ------------------------------------------------------------------
    # beats 32-43   BUILD - one harmonic per beat, sine becomes square
    # ------------------------------------------------------------------
    def section_build(self):
        B = self.B
        head = Text("one harmonic per beat", color=GREY, font_size=23)
        head.move_to(np.array([0, 2.6, 0]))
        self.play(FadeOut(self.label), FadeIn(head),
                  self.mode.animate.set_value(1.0), run_time=2 * B,
                  rate_func=smooth)

        for h in (3, 5, 7, 9, 11, 15, 21, 31):
            n = Text(f"{h} harmonics", color=WHITE_, font_size=25, weight=BOLD)
            n.move_to(np.array([0, LINE_Y, 0]))
            self.play(self.harm.animate.set_value(h),
                      FadeIn(n, shift=0.08 * UP),
                      run_time=B, rate_func=rush_from)
            self.play(FadeOut(n), run_time=B / 2)

        sq = Text("a square wave", color=GOLD, font_size=30, weight=BOLD)
        sq.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(sq), run_time=B)
        self.play(FadeOut(head), FadeOut(sq), run_time=B)

    # ------------------------------------------------------------------
    # CLOSE - clear every updater before the fade, then the signature
    # ------------------------------------------------------------------
    def section_close(self):
        B = self.B
        self.clock.clear_updaters()
        self.line.clear_updaters()
        self.ring.clear_updaters()
        self.play(FadeOut(self.line), FadeOut(self.ring), run_time=B)

        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.3, 0])).scale(0.8)
        self.play(ShowCreation(eye), run_time=3 * B)

        words = VGroup(
            Text("PAUSE", color=WHITE_, font_size=21, weight=BOLD),
            Text("OBSERVE", color=WHITE_, font_size=21, weight=BOLD),
            Text("LEARN", color=WHITE_, font_size=21, weight=BOLD),
        ).arrange(RIGHT, buff=0.45).move_to(np.array([0, -0.6, 0]))
        for w in words:
            self.play(FadeIn(w, shift=0.08 * UP), run_time=B)

        cta = Text("Follow for the math behind AI",
                   color=WHITE_, font_size=28, weight=BOLD)
        handle = Text("@observer.collapse", color=GREY, font_size=22)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.2)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=B)
        self.wait(6 * B)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=2 * B)


# ===========================================================================
def observer_eye(color):
    grp = VGroup()
    up = VMobject(color=color, stroke_width=2.2)
    up.set_points_smoothly([np.array([x, 0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
                            for x in np.linspace(-1.6, 1.6, 20)])
    dn = VMobject(color=color, stroke_width=2.2)
    dn.set_points_smoothly([np.array([x, -0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
                            for x in np.linspace(-1.6, 1.6, 20)])
    grp.add(up, dn)
    pupil = Circle(radius=0.42, stroke_color=color, stroke_width=2.2).move_to(ORIGIN)
    pupil_fill = Dot(ORIGIN, radius=0.12, fill_color=color)
    grp.add(pupil, pupil_fill)
    rng = np.random.default_rng(2)
    for _ in range(5):
        s = rng.uniform(0.05, 0.12)
        sq = Square(side_length=s, color=color, stroke_width=1.5)
        sq.move_to([rng.uniform(1.7, 2.4), rng.uniform(-0.6, 0.6), 0])
        sq.set_fill(color, opacity=0.5)
        grp.add(sq)
    return grp
