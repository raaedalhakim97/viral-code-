"""
rope_puzzle — a puzzle, the method, then the answer. 48.0s, silent.

FORMAT: hook with a question the viewer can answer wrong, make them commit,
show the working, pay it off at the end. The commitment step is the whole
point — someone who has picked an answer in their head watches to find out if
they were right, and a chunk of them say it in the comments.

    BPM=150 manimgl rope_puzzle.py RopePuzzle -w -r 1080x1920
    python3 rope_puzzle.py --click 150 click.wav

5 chapters x 24 beats = 120 beats = 30 bars = 48.000s at 150 BPM.

THE MATHS, verified:
    lift = ((C + 1) / 2pi) - r  =  1 / 2pi  =  0.159155 m  =  15.92 cm
    Earth (r = 6,371 km):  15.92 cm
    tennis ball:           15.92 cm
    a pea:                 15.92 cm
The radius cancels. Same gap for every sphere there is.

DRAWING HONESTLY. A 15.9 cm gap on a 6,371 km radius cannot be drawn to scale —
it is one part in forty million. So the Earth diagrams are schematic and say
"not to scale" on screen, and the answer is shown twice at scales where it CAN
be truthful: a ground line with a hand under it, and a tennis ball where the
same absolute gap is now enormous. That second drawing is both honest and the
punchline.

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
CHAPTERS = 5
CH_BEATS = 24

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


class RopePuzzle(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.hud = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.ch1_puzzle()
        self.ch2_guess()
        self.ch3_solve()
        self.ch4_answer()
        self.ch5_close()

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
        w, gap = 0.58, 0.12
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
    # 1 — THE PUZZLE
    # ==================================================================
    def ch1_puzzle(self):
        self.chapter(1, "the puzzle")
        O = np.array([0, 0.55, 0])
        earth = Circle(radius=1.45, stroke_color=GREY, stroke_width=2.6).move_to(O)
        earth.set_fill(WHITE_, opacity=0.05)
        rope = Circle(radius=1.45, stroke_color=WHITE_, stroke_width=4.0).move_to(O)
        el = txt("Earth", 22, GREY, bold=False).move_to(O)

        self.play(ShowCreation(earth), FadeIn(el), run_time=self.T(1),
                  rate_func=rush_from)
        self.play(ShowCreation(rope), run_time=self.T(1), rate_func=rush_from)
        t1 = txt("a rope, tight around the equator", 24, GREY, w=4.3)
        t1.move_to(np.array([0, -1.45, 0]))
        self.play(FadeIn(t1), run_time=self.T(1))
        self.wait(self.T(2))

        add = self.dance(txt("+ 1 metre", 40, GOLD)
                         .move_to(np.array([0, -1.45, 0])), 0.07)
        self.play(FadeOut(t1), run_time=self.T(1))
        self.play(FadeIn(add, scale=1.2), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))

        # the rope lifts. NOT to scale, and the frame says so.
        rope2 = Circle(radius=1.72, stroke_color=GOLD, stroke_width=4.0).move_to(O)
        self.play(ShowCreation(rope2), run_time=self.T(1), rate_func=rush_from)
        ns = txt("(not to scale)", 18, FAINT, bold=False)
        ns.move_to(np.array([0, -2.62, 0]))
        self.play(FadeIn(ns), run_time=self.T(1))

        q = txt("how high does it lift?", 29)
        q.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(add), FadeIn(q), run_time=self.T(1))
        self.finish(1, earth, el, rope, rope2, ns, q)

    # ==================================================================
    # 2 — COMMIT.  Three options, all of them plausible-sounding.
    # ==================================================================
    def ch2_guess(self):
        self.chapter(2, "pick one")
        head = txt("all the way around the planet", 24, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        opts = [("A", "a hair's width"), ("B", "a coin"), ("C", "your hand fits under")]
        rows = []
        for i, (k, label) in enumerate(opts):
            y = 1.15 - i * 1.0
            box = Rectangle(width=0.62, height=0.62, stroke_width=2.4)
            box.set_stroke(GREY, opacity=0.9)
            key = txt(k, 28).move_to(box.get_center())
            g = VGroup(box, key).move_to(np.array([-1.55, y, 0]))
            # left-align rather than centre: "your hand fits under" is wide
            # enough that centring pushes it back over the letter box.
            l = txt(label, 24, w=3.1)
            l.move_to(np.array([0, y, 0]))
            l.align_to(np.array([-1.05, 0, 0]), LEFT)
            row = VGroup(g, l)
            self.play(FadeIn(row, shift=0.16 * RIGHT), run_time=self.T(1),
                      rate_func=rush_from)
            rows.append(row)

        pick = txt("pick before you scroll", 24, GOLD)
        pick.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(pick), run_time=self.T(1))
        self.dance(pick, 0.05)
        self.finish(2, head, pick, *rows)

    # ==================================================================
    # 3 — THE METHOD.  Two lines of algebra, and the radius vanishes.
    # ==================================================================
    def ch3_solve(self):
        self.chapter(3, "the method")
        head = txt("one circle, then a slightly bigger one", 22, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        l1 = txt("C = 2πr", 40).move_to(np.array([0, 1.5, 0]))
        self.play(FadeIn(l1, scale=1.12), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(1))

        l2 = txt("C + 1 = 2π(r + d)", 36).move_to(np.array([0, 0.5, 0]))
        self.play(FadeIn(l2, scale=1.1), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))

        l3 = txt("2πr + 1 = 2πr + 2πd", 32, GREY).move_to(np.array([0, -0.4, 0]))
        self.play(FadeIn(l3), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))

        gone = txt("the r cancels", 26, GOLD).move_to(np.array([0, -1.2, 0]))
        self.play(FadeIn(gone), run_time=self.T(1))
        self.dance(gone, 0.06)
        self.wait(self.T(2))

        l4 = self.dance(txt("d = 1 / 2π", 42, GOLD)
                        .move_to(np.array([0, -2.0, 0])), 0.06)
        self.play(FadeIn(l4, scale=1.18), run_time=self.T(1), rate_func=rush_from)
        self.finish(3, head, l1, l2, l3, gone, l4)

    # ==================================================================
    # 4 — THE ANSWER, drawn where it can be drawn truthfully.
    # ==================================================================
    def ch4_answer(self):
        self.chapter(4, "the answer")
        ans = self.dance(txt("15.9 cm", 62, GOLD)
                         .move_to(np.array([0, 1.85, 0])), 0.07)
        self.play(FadeIn(ans, scale=1.2), run_time=self.T(1), rate_func=rush_from)
        c = txt("answer: C", 26).move_to(np.array([0, 1.0, 0]))
        self.play(FadeIn(c), run_time=self.T(1))
        self.wait(self.T(1))

        # at human scale the gap is truthful: ground, rope, a hand under it
        gy = -1.05
        ground = seg(np.array([-1.9, gy, 0]), np.array([1.9, gy, 0]), GREY, 2.6)
        ropel = seg(np.array([-1.9, gy + 0.62, 0]),
                    np.array([1.9, gy + 0.62, 0]), GOLD, 3.4)
        hand = poly([np.array([-0.45, gy + 0.06, 0]),
                     np.array([0.45, gy + 0.06, 0]),
                     np.array([0.45, gy + 0.5, 0]),
                     np.array([-0.45, gy + 0.5, 0])], WHITE_, 2.4, 0.9)
        hl = txt("your hand slides under", 22, WHITE_, bold=False)
        hl.move_to(np.array([0, gy - 0.5, 0]))
        self.play(ShowCreation(ground), ShowCreation(ropel),
                  run_time=self.T(1), rate_func=rush_from)
        self.play(ShowCreation(hand), FadeIn(hl), run_time=self.T(1),
                  rate_func=rush_from)
        self.wait(self.T(2))

        self.play(FadeOut(ans), FadeOut(c), FadeOut(ground), FadeOut(ropel),
                  FadeOut(hand), FadeOut(hl), run_time=self.T(1))
        ans.clear_updaters()

        # the twist — at tennis-ball scale the SAME gap is drawable to scale
        O = np.array([0, 0.75, 0])
        ball = Circle(radius=0.32, stroke_color=GREY, stroke_width=2.6).move_to(O)
        ball.set_fill(WHITE_, opacity=0.08)
        ring = Circle(radius=1.86, stroke_color=GOLD, stroke_width=3.4).move_to(O)
        bl = txt("a tennis ball", 22, GREY, bold=False)
        bl.move_to(np.array([0, -1.55, 0]))
        self.play(ShowCreation(ball), FadeIn(bl), run_time=self.T(1),
                  rate_func=rush_from)
        self.play(ShowCreation(ring), run_time=self.T(1), rate_func=rush_from)
        same = txt("same rope. same 15.9 cm.", 26, GOLD, w=4.3)
        same.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(same), run_time=self.T(1))
        self.dance(same, 0.05)
        self.finish(4, ball, ring, bl, same)

    # ==================================================================
    # 5 — WHY, then the signature.
    # ==================================================================
    def ch5_close(self):
        self.chapter(5, "why")
        g = VGroup(txt("the size of the sphere", 25, GREY),
                   txt("never entered the answer", 27),
                   txt("it is 1 / 2π for all of them", 25, GOLD)) \
            .arrange(DOWN, buff=0.22).move_to(np.array([0, 1.0, 0]))
        for m in g:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=self.T(1),
                      rate_func=rush_from)
        self.wait(self.T(3))
        self.play(FadeOut(g), run_time=self.T(1))

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
