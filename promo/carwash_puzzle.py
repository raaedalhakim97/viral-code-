"""
carwash_puzzle — a question that looks like one problem and is another. 48.0s.

Second video in the puzzle format: pose it, make the viewer commit, show why the
wrong answer is tempting, pay it off at the end.

    BPM=150 manimgl carwash_puzzle.py CarWashPuzzle -w -r 1080x1920
    python3 carwash_puzzle.py --click 150 click.wav

5 chapters x 24 beats = 120 beats = 30 bars = 48.000s at 150 BPM.

THE PUZZLE
    "I need to wash my car. The car wash is five minutes away.
     Should I walk or drive?"
Walking is the wrong answer, and the reason is not distance. The car is not how
you get there — it is what you are taking. Walk and the car is still at home,
so the goal is not met at any distance.

WHAT THIS VIDEO DOES AND DOES NOT CLAIM. It does NOT claim that AI models get
this wrong. That was not verifiable at build time and frontier models most
likely answer it correctly, so asserting the failure would be the same error as
building a video on "AI says 1+1=3" — a claim whose top comment is a correction.

What it does claim is true of any pattern matcher, human included: a question
whose SURFACE matches a familiar template invites the template's answer. "X is
five minutes away, walk or drive" is a travel-optimisation shape, and that shape
answers "walk". The goal — the car has to BE there — sits outside the template.

That is the channel's existing thesis restated: answering the form of a question
rather than the question.

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


def node(label, color=WHITE_, rw=1.35, rh=0.66, size=21):
    box = Rectangle(width=rw, height=rh, stroke_width=2.4)
    box.set_stroke(color, opacity=0.9)
    t = txt(label, size, color, bold=False, w=rw - 0.16)
    t.move_to(box.get_center())
    return VGroup(box, t)


def car_glyph(color=WHITE_, s=1.0):
    """The object the whole puzzle turns on. Shown parked in ch1, driving in ch4."""
    p = [(-0.34, -0.07), (0.34, -0.07), (0.34, 0.07), (0.20, 0.07),
         (0.09, 0.21), (-0.13, 0.21), (-0.22, 0.07), (-0.34, 0.07)]
    body = poly([np.array([x, y, 0]) for x, y in p], color, 2.2)
    g = VGroup(body)
    for x in (-0.18, 0.18):
        g.add(Circle(radius=0.075, stroke_color=color, stroke_width=2.0)
              .move_to(np.array([x, -0.105, 0])))
    return g.scale(s)


def tick(o, color=GOLD, s=0.3):
    return poly([o + np.array([-s, 0.05, 0]), o + np.array([-s * 0.25, -s * 0.6, 0]),
                 o + np.array([s, s * 0.75, 0])], color, 4.0, close=False)


def cross(o, color=GREY, s=0.26):
    return VGroup(seg(o + np.array([-s, -s, 0]), o + np.array([s, s, 0]), color, 3.6),
                  seg(o + np.array([-s, s, 0]), o + np.array([s, -s, 0]), color, 3.6))


class CarWashPuzzle(Scene):
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
        self.ch2_pick()
        self.ch3_trap()
        self.ch4_answer()
        self.ch5_why()

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
        self.chapter(1, "the question")
        lines = VGroup(txt("I need to wash my car.", 29),
                       txt("The car wash is", 27, GREY),
                       txt("5 minutes away.", 30)) \
            .arrange(DOWN, buff=0.24).move_to(np.array([0, 1.25, 0]))
        for m in lines:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=self.T(1),
                      rate_func=rush_from)
        self.wait(self.T(2))

        home = node("HOME").move_to(np.array([-1.25, -0.65, 0]))
        wash = node("CAR WASH").move_to(np.array([1.25, -0.65, 0]))
        road = seg(np.array([-0.55, -0.65, 0]), np.array([0.55, -0.65, 0]),
                   FAINT, 2.6)
        five = txt("5 min", 19, GREY, bold=False)
        five.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(home), FadeIn(wash), run_time=self.T(1),
                  rate_func=rush_from)
        self.play(ShowCreation(road), FadeIn(five), run_time=self.T(1))
        self.wait(self.T(1))

        # The car itself, parked. Nothing later makes sense without it on screen.
        car = car_glyph(GREY).move_to(np.array([-1.25, -1.42, 0]))
        self.play(ShowCreation(car), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(1))

        q = self.dance(txt("walk or drive?", 32, GOLD)
                       .move_to(np.array([0, LINE_Y, 0])), 0.06)
        self.play(FadeIn(q, scale=1.15), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))
        self.finish(1, lines, home, wash, road, five, car, q)

    # ==================================================================
    # 2 — COMMIT
    # ==================================================================
    def ch2_pick(self):
        self.chapter(2, "pick one")
        head = txt("it is only five minutes", 24, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        rows = []
        for i, (k, label) in enumerate([("A", "walk"), ("B", "drive")]):
            y = 0.9 - i * 1.3
            box = Rectangle(width=0.66, height=0.66, stroke_width=2.4)
            box.set_stroke(GREY, opacity=0.9)
            key = txt(k, 29).move_to(box.get_center())
            g = VGroup(box, key).move_to(np.array([-1.3, y, 0]))
            l = txt(label, 30)
            l.move_to(np.array([0, y, 0]))
            l.align_to(np.array([-0.7, 0, 0]), LEFT)
            row = VGroup(g, l)
            self.play(FadeIn(row, shift=0.16 * RIGHT), run_time=self.T(2),
                      rate_func=rush_from)
            rows.append(row)

        self.wait(self.T(1))
        pick = txt("pick before you scroll", 24, GOLD)
        pick.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(pick), run_time=self.T(1))
        self.dance(pick, 0.05)

        # A draining bar, not a frozen frame. This is the commit window — the
        # viewer has to actually choose, and 8 beats of still image loses them.
        track = Rectangle(width=3.2, height=0.06, stroke_width=0)
        track.set_fill(FAINT, opacity=1.0).move_to(np.array([0, -1.35, 0]))
        bar = Rectangle(width=3.2, height=0.06, stroke_width=0)
        bar.set_fill(GOLD, opacity=0.9).move_to(np.array([0, -1.35, 0]))
        self.play(FadeIn(track), FadeIn(bar), run_time=self.T(1))
        self.play(bar.animate.set_width(0.001, about_edge=LEFT),
                  run_time=self.T(8), rate_func=linear)
        self.finish(2, head, pick, track, bar, *rows)

    # ==================================================================
    # 3 — WHY "WALK" IS TEMPTING.  The sentence has a familiar shape.
    # ==================================================================
    def ch3_trap(self):
        self.chapter(3, "the shape of it")
        head = txt("the sentence looks like this", 24, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        slots = [("somewhere to go", 1.35), ("a short distance", 0.55),
                 ("walk or drive?", -0.25)]
        boxes = VGroup()
        for label, y in slots:
            b = node(label, GREY, rw=3.0, rh=0.6, size=21)
            b.move_to(np.array([0, y, 0]))
            boxes.add(b)
            self.play(FadeIn(b, shift=0.12 * RIGHT), run_time=self.T(1),
                      rate_func=rush_from)

        arrow = seg(np.array([0, -0.62, 0]), np.array([0, -1.08, 0]), FAINT, 2.4)
        ans = txt("walk. it's close.", 28, GREY)
        ans.move_to(np.array([0, -1.45, 0]))
        self.play(ShowCreation(arrow), FadeIn(ans), run_time=self.T(1),
                  rate_func=rush_from)
        self.wait(self.T(2))

        t = txt("that shape has a stock answer", 23, WHITE_, bold=False, w=4.3)
        t.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(t), run_time=self.T(1))
        self.wait(self.T(2))

        # The slots light up together: this is the template being matched.
        self.play(*[Indicate(b, color=GOLD, scale_factor=1.05) for b in boxes],
                  run_time=self.T(1))

        t2 = txt("but the car isn't the transport", 24, GOLD, w=4.3)
        t2.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(t), FadeIn(t2), run_time=self.T(1))
        self.dance(t2, 0.05)
        self.wait(self.T(2))
        self.finish(3, head, boxes, arrow, ans, t2)

    # ==================================================================
    # 4 — THE ANSWER.  Two end states, drawn.
    # ==================================================================
    def ch4_answer(self):
        self.chapter(4, "the answer")
        head = txt("what has to be true at the end", 23, GREY, w=4.3)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        # walking
        wlab = txt("A · walk", 24, GREY).move_to(np.array([0, 1.55, 0]))
        h1 = node("HOME + car", GREY).move_to(np.array([-1.2, 0.85, 0]))
        w1 = node("WASH + you", GREY).move_to(np.array([1.2, 0.85, 0]))
        x1 = cross(np.array([0, 0.85, 0]))
        self.play(FadeIn(wlab), FadeIn(h1), FadeIn(w1), run_time=self.T(1),
                  rate_func=rush_from)
        self.play(ShowCreation(x1), run_time=self.T(1), rate_func=rush_into)
        n1 = txt("the car never arrived", 22, GREY, bold=False)
        n1.move_to(np.array([0, 0.25, 0]))
        self.play(FadeIn(n1), run_time=self.T(1))
        self.wait(self.T(2))

        # driving
        dlab = txt("B · drive", 24, GOLD).move_to(np.array([0, -0.6, 0]))
        h2 = node("HOME", GREY).move_to(np.array([-1.2, -1.3, 0]))
        w2 = node("WASH + car", GOLD).move_to(np.array([1.2, -1.3, 0]))
        t2 = tick(np.array([0, -1.3, 0]))
        # The car crosses the corridor between the nodes. Half-width 0.21 at this
        # scale, corridor is +/-0.525, so -0.30 -> +0.30 travels without clipping
        # either box. It fades out as the tick lands; they never coexist.
        car = car_glyph(GOLD, 0.62).move_to(np.array([-0.30, -1.3, 0]))
        self.play(FadeIn(dlab), FadeIn(h2), FadeIn(w2), FadeIn(car),
                  run_time=self.T(1), rate_func=rush_from)
        self.play(car.animate.move_to(np.array([0.30, -1.3, 0])),
                  run_time=self.T(2), rate_func=smooth)
        self.play(FadeOut(car), ShowCreation(t2), run_time=self.T(1),
                  rate_func=rush_from)
        self.wait(self.T(1))

        ans = self.dance(txt("answer: B", 32, GOLD)
                         .move_to(np.array([0, LINE_Y, 0])), 0.06)
        self.play(FadeIn(ans, scale=1.18), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))
        self.finish(4, head, wlab, h1, w1, x1, n1, dlab, h2, w2, car, t2, ans)

    # ==================================================================
    # 5 — THE POINT, then the signature.
    # ==================================================================
    def ch5_why(self):
        self.chapter(5, "why it works")
        g = VGroup(txt("distance was never the question", 24, GREY, w=4.3),
                   txt("the car had to be there", 27),
                   txt("that was outside the pattern", 24, GOLD, w=4.3)) \
            .arrange(DOWN, buff=0.24).move_to(np.array([0, 1.05, 0]))
        for m in g:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=self.T(1),
                      rate_func=rush_from)
        self.wait(self.T(2))

        end = txt("match the form, answer the form", 24, WHITE_, bold=False, w=4.3)
        end.move_to(np.array([0, -0.85, 0]))
        self.play(FadeIn(end), run_time=self.T(1))
        self.wait(self.T(2))
        self.play(FadeOut(g), FadeOut(end), run_time=self.T(1))

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
