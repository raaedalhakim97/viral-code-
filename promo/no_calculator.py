"""
no_calculator — 47500 / 234 in your head. 48.0s.

    BPM=150 manimgl no_calculator.py NoCalculator -w -r 1080x1920
    python3 no_calculator.py --click 150 click.wav

6 chapters x 20 beats = 120 beats = 30 bars = 48.000s at 150 BPM.

THE METHOD (plain long division, verified in full)
    475 / 234 -> 2 remainder   7      234 x 2 = 468,  475 - 468 =   7
     70 / 234 -> 0 remainder  70      234 does not fit in 70
    700 / 234 -> 2 remainder 232      234 x 2 = 468,  700 - 468 = 232
    => 202 remainder 232,  232/234 = 0.9915,  so 47500/234 = 202.99145...

WHY THIS ONE IS WORTH A VIDEO
The 700 step is the whole piece. Testing 234 x 3 = 702 overshoots 700 by
exactly 2 — and that same 2 is why 234 x 203 = 47502 overshoots 47500 by 2.
The near-miss you hit halfway through the method IS the reason the answer is a
hair under 203. So the payoff is not a new fact bolted on at the end; it is the
viewer being shown that they already computed it and did not notice.

That is the only reason to pick this division over any other. A quotient like
202.99 is otherwise unremarkable, and "here is long division" is not a video.

HONESTY NOTE. The hook says 19 seconds and the stopwatch on screen runs for
19.0s of real time across chapters 3-5, stopping when the answer lands. It is a
prop timing the method being demonstrated, not a claim about the viewer.

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
CHAPTERS = 6
CH_BEATS = 20

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FRAME_H = 9.0
LINE_Y  = -2.05
HEAD_Y  = 2.35
BAR_Y   = 3.22

SOLVE_SECONDS = 19.0          # the stopwatch, and the number in the hook


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


def tick(o, color=GOLD, s=0.26):
    return poly([o + np.array([-s, 0.05, 0]), o + np.array([-s * 0.25, -s * 0.6, 0]),
                 o + np.array([s, s * 0.75, 0])], color, 3.6, close=False)


def cross(o, color=GREY, s=0.22):
    return VGroup(seg(o + np.array([-s, -s, 0]), o + np.array([s, s, 0]), color, 3.2),
                  seg(o + np.array([-s, s, 0]), o + np.array([s, -s, 0]), color, 3.2))


def calc_glyph(color=GREY, s=1.0):
    """The thing the video is asking you to put down."""
    body = Rectangle(width=0.95, height=1.35, stroke_width=2.4)
    body.set_stroke(color, opacity=0.9)
    screen = Rectangle(width=0.72, height=0.30, stroke_width=2.0)
    screen.set_stroke(color, opacity=0.65).move_to(np.array([0, 0.44, 0]))
    g = VGroup(body, screen)
    for r in range(3):
        for c in range(3):
            k = Rectangle(width=0.16, height=0.12, stroke_width=1.6)
            k.set_stroke(color, opacity=0.5)
            k.move_to(np.array([-0.26 + c * 0.26, 0.02 - r * 0.22, 0]))
            g.add(k)
    return g.scale(s)


class NoCalculator(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.hud = None
        self.timer = None
        self.t0 = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.ch1_hook()
        self.ch2_split()
        self.ch3_first_digit()
        self.ch4_zeros()
        self.ch5_payoff()
        self.ch6_answer()

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
        w, gap = 0.52, 0.12
        total = CHAPTERS * w + (CHAPTERS - 1) * gap
        for i in range(CHAPTERS):
            r = Rectangle(width=w, height=0.055, stroke_width=0)
            r.set_fill(GOLD if i == n - 1 else WHITE_,
                       opacity=0.85 if i < n else 0.14)
            r.move_to(np.array([-total / 2 + w / 2 + i * (w + gap), BAR_Y, 0]))
            g.add(r)
        lab = txt(f"{n} / {CHAPTERS}   {title}", 19, GREY, bold=False, w=3.4)
        lab.move_to(np.array([0, BAR_Y - 0.33, 0]))
        g.add(lab)
        self.hud = g
        self.add(g)

    # ------------------------------------------------------------------
    def start_timer(self):
        """Pre-built digits swapped by opacity — rebuilding a Text every frame
        would cost 1140 pango calls over the run."""
        self.t0 = self.clock.get_value()
        digits = VGroup()
        for i in range(int(SOLVE_SECONDS) + 1):
            d = txt(f"{i}s", 21, GOLD, bold=False, w=0.7)
            d.move_to(np.array([-1.98, BAR_Y - 0.33, 0]))
            digits.add(d)

        def upd(g):
            n = int(min(SOLVE_SECONDS, max(0.0, self.clock.get_value() - self.t0)))
            for i, d in enumerate(g):
                d.set_opacity(1.0 if i == n else 0.0)

        digits.add_updater(upd)
        self.timer = digits
        self.add(digits)

    def stop_timer(self):
        if self.timer is not None:
            self.timer.clear_updaters()
            self.remove(self.timer)
            self.timer = None

    def strip(self, s):
        """The quotient building up, top of frame, during the solve."""
        g = VGroup(txt("answer so far", 17, GREY, bold=False),
                   txt(s, 34, GOLD)).arrange(DOWN, buff=0.10)
        g.move_to(np.array([0, 1.72, 0]))
        return g

    # ==================================================================
    # 1 — THE HOOK
    # ==================================================================
    def ch1_hook(self):
        self.chapter(1, "put it down")
        head = txt("you won't need this", 24, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        calc = calc_glyph(GREY, 1.15).move_to(np.array([0, 0.75, 0]))
        self.play(ShowCreation(calc), run_time=self.T(2))
        x = VGroup(seg(np.array([-0.72, -0.06, 0]), np.array([0.72, 1.56, 0]), WHITE_, 4.0),
                   seg(np.array([-0.72, 1.56, 0]), np.array([0.72, -0.06, 0]), WHITE_, 4.0))
        self.play(ShowCreation(x), run_time=self.T(1), rate_func=rush_into)
        self.wait(self.T(1))
        self.play(FadeOut(calc), FadeOut(x), run_time=self.T(1))

        expr = txt("47500 ÷ 234", 46, WHITE_, w=4.5)
        expr.move_to(np.array([0, 0.75, 0]))
        self.play(FadeIn(expr, scale=1.12), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))

        pen = txt("grab a pen", 28, GREY)
        pen.move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(pen, shift=0.1 * UP), run_time=self.T(1))
        self.wait(self.T(1))

        sec = self.dance(txt(f"{int(SOLVE_SECONDS)} seconds", 32, GOLD)
                         .move_to(np.array([0, LINE_Y, 0])), 0.06)
        self.play(FadeIn(sec, scale=1.15), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))
        self.finish(1, head, expr, pen, sec)

    # ==================================================================
    # 2 — YOU DON'T DIVIDE 47500.  YOU DIVIDE 475.
    # ==================================================================
    def ch2_split(self):
        self.chapter(2, "split it")
        head = txt("nobody divides 47500", 23, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        # Built as separate glyphs from the start so the split is a move, not a
        # swap — the digits the viewer read are the digits that travel.
        parts = VGroup(txt("475", 44), txt("0", 44), txt("0", 44))
        parts.arrange(RIGHT, buff=0.06).move_to(np.array([0, 1.05, 0]))
        self.play(FadeIn(parts), run_time=self.T(1))
        self.wait(self.T(1))

        target = VGroup(parts[0].copy(), parts[1].copy(), parts[2].copy())
        target.arrange(RIGHT, buff=0.42).move_to(np.array([0, 1.05, 0]))
        self.play(*[p.animate.move_to(t.get_center())
                    for p, t in zip(parts, target)], run_time=self.T(2))
        self.play(parts[0].animate.set_color(GOLD),
                  parts[1].animate.set_opacity(0.30),
                  parts[2].animate.set_opacity(0.30), run_time=self.T(1))

        note = txt("three digits, to match 234", 22, GREY, bold=False)
        note.move_to(np.array([0, 0.30, 0]))
        d = txt("234", 34, WHITE_).move_to(np.array([0, -0.42, 0]))
        rule = seg(np.array([-0.62, -0.06, 0]), np.array([0.62, -0.06, 0]), FAINT, 2.4)
        self.play(FadeIn(note), run_time=self.T(1))
        self.play(ShowCreation(rule), FadeIn(d), run_time=self.T(1),
                  rate_func=rush_from)
        self.wait(self.T(2))

        q = self.dance(txt("how many 234s fit in 475?", 25, GOLD, w=4.3)
                       .move_to(np.array([0, LINE_Y, 0])), 0.05)
        self.play(FadeIn(q), run_time=self.T(1))
        self.wait(self.T(2))
        self.finish(2, head, parts, note, d, rule, q)

    # ==================================================================
    # 3 — FIRST DIGIT.  The stopwatch starts here.
    # ==================================================================
    def ch3_first_digit(self):
        self.chapter(3, "first digit")
        self.start_timer()
        head = txt("how many 234s in 475?", 23, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        a = txt("234 × 2 = 468", 31)
        a.move_to(np.array([0, 0.85, 0]))
        self.play(FadeIn(a, shift=0.12 * RIGHT), run_time=self.T(2),
                  rate_func=rush_from)
        ta = tick(np.array([1.55, 0.85, 0]))
        self.play(ShowCreation(ta), run_time=self.T(1), rate_func=rush_from)

        b = txt("234 × 3 = 702", 29, GREY)
        b.move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(b, shift=0.12 * RIGHT), run_time=self.T(1),
                  rate_func=rush_from)
        xb = cross(np.array([1.55, 0.10, 0]))
        over = txt("too big", 20, GREY, bold=False)
        over.move_to(np.array([0, -0.42, 0]))
        self.play(ShowCreation(xb), FadeIn(over), run_time=self.T(1))
        self.wait(self.T(1))

        st = self.strip("2")
        self.play(FadeIn(st, shift=0.1 * DOWN), run_time=self.T(1))
        self.wait(self.T(1))

        sub = txt("475 − 468 = 7", 29, GOLD)
        sub.move_to(np.array([0, -1.20, 0]))
        self.play(FadeIn(sub, shift=0.1 * UP), run_time=self.T(2),
                  rate_func=rush_from)
        rem = txt("carry the 7", 21, GREY, bold=False)
        rem.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(rem), run_time=self.T(1))
        self.wait(self.T(2))
        self.finish(3, head, a, ta, b, xb, over, st, sub, rem)

    # ==================================================================
    # 4 — THE TWO ZEROS.  702 shows up again, and this time it matters.
    # ==================================================================
    def ch4_zeros(self):
        self.chapter(4, "bring down the zeros")
        head = txt("bring the zeros down", 23, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        r1 = txt("7 → 70", 30)
        r1.move_to(np.array([0, 0.95, 0]))
        self.play(FadeIn(r1, shift=0.12 * RIGHT), run_time=self.T(1),
                  rate_func=rush_from)
        n1 = txt("234 doesn't fit — write 0", 22, GREY, bold=False, w=4.3)
        n1.move_to(np.array([0, 0.42, 0]))
        self.play(FadeIn(n1), run_time=self.T(1))
        st = self.strip("20")
        self.play(FadeIn(st, shift=0.1 * DOWN), run_time=self.T(1))
        self.wait(self.T(1))

        r2 = txt("70 → 700", 30)
        r2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(r2, shift=0.12 * RIGHT), run_time=self.T(1),
                  rate_func=rush_from)

        # 702 again. Remember this — chapter 5 is built on it.
        c = txt("234 × 3 = 702", 29, GOLD)
        c.move_to(np.array([0, -0.85, 0]))
        self.play(FadeIn(c), run_time=self.T(1), rate_func=rush_from)
        miss = txt("over by just 2", 22, GOLD, bold=False)
        miss.move_to(np.array([0, -1.32, 0]))
        xc = cross(np.array([1.62, -0.85, 0]))
        self.play(FadeIn(miss), ShowCreation(xc), run_time=self.T(1))
        self.wait(self.T(1))

        d = txt("so 2:  700 − 468 = 232", 26, WHITE_, w=4.3)
        d.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(d), run_time=self.T(2), rate_func=rush_from)
        st2 = self.strip("202")
        self.play(FadeOut(st), FadeIn(st2), run_time=self.T(1))
        self.wait(self.T(2))
        self.finish(4, head, r1, n1, st, st2, r2, c, miss, xc, d)

    # ==================================================================
    # 5 — THE PAYOFF.  The near-miss from chapter 4 was the answer.
    # ==================================================================
    def ch5_payoff(self):
        self.chapter(5, "the payoff")
        head = txt("202, remainder 232", 24, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        self.wait(self.T(1))
        a = txt("232 out of 234", 28)
        a.move_to(np.array([0, 1.15, 0]))
        self.play(FadeIn(a), run_time=self.T(1))
        self.wait(self.T(1))
        b = txt("that's 0.99", 30, GOLD)
        b.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(b, scale=1.1), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))

        # Beat 88 = 35.2s, and the stopwatch started at 16.0s — so it reads 19
        # exactly as the answer lands. The waits above are load-bearing.
        c = txt("so: a hair under 203", 27, WHITE_, w=4.3)
        c.move_to(np.array([0, -0.15, 0]))
        self.play(FadeIn(c, shift=0.1 * UP), run_time=self.T(1))
        self.wait(self.T(2))

        chk = txt("check:  234 × 203 = 47502", 24, GREY, w=4.3)
        chk.move_to(np.array([0, -0.95, 0]))
        self.play(FadeIn(chk), run_time=self.T(2), rate_func=rush_from)
        # Held to here so "19s" is on screen for 1.8s, not the 0.2s it gets if
        # the timer stops the instant it hits 19.
        self.stop_timer()
        self.wait(self.T(1))

        pun = self.dance(txt("the same 2 you saw earlier", 24, GOLD, w=4.3)
                         .move_to(np.array([0, LINE_Y, 0])), 0.05)
        self.play(FadeIn(pun), run_time=self.T(1))
        self.wait(self.T(1))
        self.finish(5, head, a, b, c, chk, pun)

    # ==================================================================
    # 6 — THE ANSWER, then the signature.
    # ==================================================================
    def ch6_answer(self):
        self.chapter(6, "no calculator")
        ans = VGroup(txt("47500 ÷ 234", 34, GREY),
                     txt("≈ 202.99", 52, GOLD)).arrange(DOWN, buff=0.22)
        ans.move_to(np.array([0, 1.15, 0]))
        self.play(FadeIn(ans[0]), run_time=self.T(1))
        self.play(FadeIn(ans[1], scale=1.15), run_time=self.T(1),
                  rate_func=rush_from)
        self.wait(self.T(2))

        no = txt("no calculator", 26, WHITE_)
        no.move_to(np.array([0, -0.35, 0]))
        self.play(FadeIn(no, shift=0.1 * UP), run_time=self.T(1))
        self.wait(self.T(2))
        self.play(FadeOut(ans), FadeOut(no), run_time=self.T(1))

        self.clock.clear_updaters()
        if self.hud is not None:
            self.remove(self.hud)

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
