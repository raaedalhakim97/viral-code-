"""
dimensions — why a word needs 1,536 dimensions to live in. 51.2s, silent.

Same contract as illusion_of_logic: no narration, beat-locked, geometry rather
than commentary, equations that breathe on the beat. Add a track in the TikTok
editor.

    BPM=150 manimgl dimensions.py Dimensions -w -r 1080x1920
    python3 dimensions.py --click 150 click.wav

4 chapters x 32 beats = 128 beats = 32 bars = 51.200s at 150 BPM.

EVERY NUMBER ON SCREEN WAS MEASURED, not asserted. The histograms in chapter 2
are real samples of cos(u, v) for random unit vectors, drawn from the same
computation, with a fixed seed so a re-render is identical:

    dims    theory std   measured   |cos| < 0.05
       2       0.7071     0.7052          3.3%
     100       0.1000     0.1003         37.6%
    1536       0.0255     0.0254         95.2%

    volume of the unit ball inside r = 0.99, in 1536 dims:  1.975e-07
    near-perpendicular directions that fit in 1536 dims:    ~1.1e10

The last figure is the standard concentration/Johnson-Lindenstrauss style
bound, exp(d * eps^2 / 2) at eps = 0.1736 (ten degrees off perpendicular). It
is a lower bound on how many you can pack, which is the honest direction for
the claim being made.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import sys

if "--click" in sys.argv:
    import wave
    import numpy as _np

    _i = sys.argv.index("--click")
    _bpm = float(sys.argv[_i + 1])
    _out = sys.argv[_i + 2] if _i + 2 < len(sys.argv) else "click.wav"
    _SR, _dur = 44100, 60.0
    _sig = _np.zeros(int(_SR * _dur), _np.float32)
    _beat = 60.0 / _bpm
    for _n in range(int(_dur / _beat)):
        _s = int(_n * _beat * _SR)
        _e = min(_s + int(0.04 * _SR), len(_sig))
        _env = _np.exp(-_np.linspace(0, 8, _e - _s))
        _f = 1600 if _n % 4 == 0 else 900
        _sig[_s:_e] += _np.sin(2 * _np.pi * _f * _np.arange(_e - _s) / _SR) * _env * 0.6
    with wave.open(_out, "wb") as _w:
        _w.setnchannels(1)
        _w.setsampwidth(2)
        _w.setframerate(_SR)
        _w.writeframes((_np.clip(_sig, -1, 1) * 32767).astype(_np.int16).tobytes())
    print(f"{_out}  {_bpm:g} bpm  {_dur:g}s")
    sys.exit(0)

import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
CHAPTERS = 4
CH_BEATS = 32

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FRAME_H = 9.0
LINE_Y  = -2.05
HEAD_Y  = 2.35
BAR_Y   = 3.22


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, w=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    return m


def poly(pts, color=WHITE_, w=2.4, op=1.0, close=True):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners(list(pts) + ([pts[0]] if close else []))
    m.set_stroke(opacity=op)
    return m


def arrow(o, vec, color=WHITE_, w=3.2, op=1.0):
    tip = o + vec
    d = vec / (np.linalg.norm(vec) + 1e-9)
    perp = np.array([-d[1], d[0], 0.0])
    head = poly([tip, tip - d * 0.24 + perp * 0.12,
                 tip - d * 0.24 - perp * 0.12], color, w * 0.7, op)
    head.set_fill(color, opacity=op)
    return VGroup(seg(o, tip, color, w, op), head)


def cos_samples(d, n=6000, seed=7):
    """cos(u, v) for random unit vectors. Real numbers, fixed seed."""
    rng = np.random.default_rng(seed)
    a = rng.normal(size=(n, d)); a /= np.linalg.norm(a, axis=1, keepdims=True)
    b = rng.normal(size=(n, d)); b /= np.linalg.norm(b, axis=1, keepdims=True)
    return np.sum(a * b, axis=1)


class Dimensions(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.hud = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.ch1_problem()
        self.ch2_measure()
        self.ch3_count()
        self.ch4_payoff()

    # ------------------------------------------------------------------
    def T(self, beats):
        self.used += beats
        return round(beats * self.B * FPS) / FPS

    def pad_to(self, target):
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(f"chapter overruns by {-rem:.2f} beats — trim it")
        if rem > 0.01:
            self.wait(self.T(rem))

    def finish(self, n, *mobs):
        """Pad on the last visual, THEN clear — never hold on black."""
        self.pad_to(n * CH_BEATS)
        for m in mobs:
            if m is not None:
                m.clear_updaters()
        self.remove(*[m for m in mobs if m is not None])

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.055):
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def chapter(self, n, title):
        if self.hud is not None:
            self.remove(self.hud)
        g = VGroup()
        w, gap = 0.7, 0.14
        total = CHAPTERS * w + (CHAPTERS - 1) * gap
        for i in range(CHAPTERS):
            r = Rectangle(width=w, height=0.055, stroke_width=0)
            r.set_fill(GOLD if i == n - 1 else WHITE_,
                       opacity=0.85 if i < n else 0.14)
            r.move_to(np.array([-total / 2 + w / 2 + i * (w + gap), BAR_Y, 0]))
            g.add(r)
        lab = txt(f"{n} / {CHAPTERS}   {title}", 19, GREY, bold=False, w=4.2)
        lab.move_to(np.array([0, BAR_Y - 0.33, 0]))
        g.add(lab)
        self.hud = g
        self.add(g)

    # ==================================================================
    # 1 — THE PROBLEM.  Flat space runs out of directions immediately.
    # ==================================================================
    def ch1_problem(self):
        self.chapter(1, "the problem")
        big = self.dance(txt("1,536", 76, GOLD).move_to(np.array([0, 1.2, 0])), 0.07)
        sub = txt("dimensions per word", 26, GREY)
        sub.move_to(np.array([0, 0.35, 0]))
        self.play(FadeIn(big, scale=1.15), run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(sub), run_time=self.T(1))
        why = txt("why so many?", 30).move_to(np.array([0, -0.8, 0]))
        self.play(FadeIn(why, shift=0.12 * UP), run_time=self.T(1))
        self.wait(self.T(3))
        self.remove(big, sub, why)
        big.clear_updaters()

        # two axes: in a plane you get exactly two perpendicular directions
        O = np.array([0, 0.0, 0])
        a1 = arrow(O, np.array([1.45, 0, 0]))
        a2 = arrow(O, np.array([0, 1.45, 0]))
        l1 = txt("cat", 22, GREY, bold=False).move_to(O + np.array([1.82, 0, 0]))
        l2 = txt("dog", 22, GREY, bold=False).move_to(O + np.array([0, 1.78, 0]))
        head = txt("in a flat plane", 26, GREY).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.play(ShowCreation(a1), FadeIn(l1), run_time=self.T(1), rate_func=rush_from)
        self.play(ShowCreation(a2), FadeIn(l2), run_time=self.T(1), rate_func=rush_from)
        two = txt("two directions. that's all.", 25)
        two.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(two), run_time=self.T(1))
        self.wait(self.T(2))

        # a third word has nowhere perpendicular to go
        a3 = arrow(O, np.array([1.03, 1.03, 0]), GOLD, 3.2)
        l3 = txt("wolf", 22, GOLD, bold=False).move_to(O + np.array([1.4, 1.28, 0]))
        self.play(ShowCreation(a3), FadeIn(l3), run_time=self.T(1), rate_func=rush_from)
        clash = txt("the third one has to overlap", 24, GOLD, w=4.2)
        clash.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(two), FadeIn(clash), run_time=self.T(1))
        self.wait(self.T(3))

        note = txt("overlapping directions = confused meanings", 22, GREY,
                   bold=False, w=4.3)
        note.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(clash), FadeIn(note), run_time=self.T(1))
        self.finish(1, head, a1, a2, a3, l1, l2, l3, note)

    # ==================================================================
    # 2 — THE MEASUREMENT.  Real samples. The spread collapses.
    # ==================================================================
    def ch2_measure(self):
        self.chapter(2, "what high dimensions do")
        head = txt("angle between two random words", 24, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        AX_Y, AX_W, AX_H = -1.35, 4.0, 2.7
        axis = seg(np.array([-AX_W / 2, AX_Y, 0]),
                   np.array([AX_W / 2, AX_Y, 0]), FAINT, 2.4)
        zero = seg(np.array([0, AX_Y - 0.14, 0]),
                   np.array([0, AX_Y + AX_H, 0]), FAINT, 2.0)
        zl = txt("perpendicular", 19, GREY, bold=False)
        zl.move_to(np.array([0, AX_Y - 0.4, 0]))
        self.play(ShowCreation(axis), ShowCreation(zero), FadeIn(zl),
                  run_time=self.T(1))

        def hist(d, color, op):
            c = cos_samples(d)
            counts, edges = np.histogram(c, bins=61, range=(-1, 1))
            counts = counts / counts.max()
            pts = []
            for i in range(len(counts)):
                x = (edges[i] + edges[i + 1]) / 2 * (AX_W / 2)
                pts.append(np.array([x, AX_Y + counts[i] * AX_H, 0]))
            m = poly(pts, color, 3.0, op, close=False)
            return m

        prev, prevlab = None, None
        for d, hold in ((2, 2), (10, 2), (100, 2), (1536, 4)):
            last = d == 1536
            h = hist(d, GOLD if last else WHITE_, 1.0 if last else 0.8)
            lab = txt(f"{d:,} dimensions", 27 if last else 25,
                      GOLD if last else WHITE_)
            lab.move_to(np.array([0, 1.55, 0]))
            anims = [ShowCreation(h), FadeIn(lab)]
            if prev is not None:
                anims += [prev.animate.set_stroke(opacity=0.16), FadeOut(prevlab)]
            self.play(*anims, run_time=self.T(1), rate_func=rush_from)
            self.wait(self.T(hold))
            if prev is not None:
                self.remove(prev)
            prev, prevlab = h, lab

        self.dance(prevlab, 0.05)
        pay = txt("95% land within 0.05 of a right angle", 23, WHITE_,
                  bold=False, w=4.3)
        pay.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(pay), run_time=self.T(1))
        self.finish(2, head, axis, zero, zl, prev, prevlab, pay)

    # ==================================================================
    # 3 — THE COUNT.  How many directions that buys you.
    # ==================================================================
    def ch3_count(self):
        self.chapter(3, "how many fit")
        head = txt("directions that barely overlap", 24, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        rows = [("2 dimensions", "2", 0.06),
                ("3 dimensions", "3", 0.09),
                ("100 dimensions", "1,600", 0.30),
                ("1,536 dimensions", "11,000,000,000", 1.0)]
        base_y, mobs = 1.15, []
        for i, (label, count, frac) in enumerate(rows):
            y = base_y - i * 0.85
            last = i == len(rows) - 1
            l = txt(label, 22, GOLD if last else GREY, bold=last)
            l.move_to(np.array([-1.25, y, 0]))
            bw = max(frac * 2.5, 0.05)
            b = Rectangle(width=bw, height=0.2, stroke_width=0)
            b.set_fill(GOLD if last else WHITE_, opacity=0.85 if last else 0.4)
            b.move_to(np.array([0.45 + bw / 2, y, 0]))
            c = txt(count, 26 if last else 22, GOLD if last else WHITE_)
            c.move_to(np.array([0, y - 0.42, 0]))
            g = VGroup(l, b, c)
            self.play(FadeIn(g, shift=0.14 * RIGHT), run_time=self.T(1),
                      rate_func=rush_from)
            self.wait(self.T(1 if not last else 2))
            mobs.append(g)
        self.dance(mobs[-1][2], 0.05)

        for line in ("every word gets its own direction",
                     "and almost none of them collide"):
            t = txt(line, 24, WHITE_, bold=False, w=4.3)
            t.move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=self.T(1))
            self.wait(self.T(2))
            self.play(FadeOut(t), run_time=self.T(1))
        self.finish(3, head, *mobs)

    # ==================================================================
    # 4 — THE PAYOFF + CLOSE
    # ==================================================================
    def ch4_payoff(self):
        self.chapter(4, "the strange part")
        head = txt("and it gets stranger", 27).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        # A 1% shell drawn to scale is two circles 0.015 apart — invisible,
        # so the idea never lands. Plot where the volume actually lives
        # instead: r^d against r. In 2D that is a gentle curve; in 1536D it is
        # flat zero until it slams into the wall at the edge.
        AX_Y, AX_W, AX_H = -1.25, 3.9, 2.7
        axis = seg(np.array([-AX_W / 2, AX_Y, 0]),
                   np.array([AX_W / 2, AX_Y, 0]), FAINT, 2.4)
        yax = seg(np.array([-AX_W / 2, AX_Y, 0]),
                  np.array([-AX_W / 2, AX_Y + AX_H, 0]), FAINT, 2.4)
        xl0 = txt("centre", 19, GREY, bold=False)
        xl0.move_to(np.array([-AX_W / 2, AX_Y - 0.36, 0]))
        xl1 = txt("edge", 19, GREY, bold=False)
        xl1.move_to(np.array([AX_W / 2, AX_Y - 0.36, 0]))
        yl = txt("volume", 19, GREY, bold=False)
        yl.move_to(np.array([-AX_W / 2 + 0.05, AX_Y + AX_H + 0.28, 0]))
        self.play(ShowCreation(axis), ShowCreation(yax),
                  FadeIn(xl0), FadeIn(xl1), FadeIn(yl), run_time=self.T(1))

        def vol_curve(d, color, w=3.0, op=1.0):
            r = np.linspace(0, 1, 300)
            v = r ** d
            return poly([np.array([-AX_W / 2 + u * AX_W, AX_Y + h * AX_H, 0])
                         for u, h in zip(r, v)], color, w, op, close=False)

        c2 = vol_curve(2, WHITE_, 2.6, 0.55)
        n2 = txt("2 dimensions", 21, GREY, bold=False)
        n2.move_to(np.array([-0.55, AX_Y + 2.05, 0]))
        self.play(ShowCreation(c2), FadeIn(n2), run_time=self.T(1),
                  rate_func=rush_from)
        self.wait(self.T(2))

        c3 = vol_curve(1536, GOLD, 3.6)
        n3 = txt("1,536 dimensions", 24, GOLD)
        n3.move_to(np.array([0.35, AX_Y + 2.35, 0]))
        self.play(ShowCreation(c3), FadeIn(n3), run_time=self.T(1),
                  rate_func=rush_from)
        self.dance(n3, 0.05)
        self.wait(self.T(2))

        pct = self.dance(txt("99.99998%", 34, GOLD)
                         .move_to(np.array([-0.35, AX_Y + 1.35, 0])), 0.06)
        of = txt("of it sits in the outer 1%", 22, WHITE_, bold=False, w=4.2)
        of.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(pct, scale=1.18), run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(of), run_time=self.T(1))
        self.wait(self.T(3))

        self.clock.clear_updaters()
        for m in (pct, n3):
            m.clear_updaters()
        self.play(FadeOut(head), FadeOut(axis), FadeOut(yax), FadeOut(xl0),
                  FadeOut(xl1), FadeOut(yl), FadeOut(c2), FadeOut(n2),
                  FadeOut(c3), FadeOut(n3), FadeOut(pct), FadeOut(of),
                  run_time=self.T(1))
        if self.hud is not None:
            self.remove(self.hud)

        end = VGroup(txt("high dimensions are mostly", 25, GREY),
                     txt("empty space", 30),
                     txt("which is exactly the point", 24, GOLD)) \
            .arrange(DOWN, buff=0.22).move_to(np.array([0, 0.9, 0]))
        for m in end:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=self.T(1),
                      rate_func=rush_from)
        self.wait(self.T(3))
        self.play(FadeOut(end), run_time=self.T(1))

        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(2))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1))
        self.pad_to(CHAPTERS * CH_BEATS - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))


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
