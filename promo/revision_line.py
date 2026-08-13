"""
revision_line — the best line, run on your own revision. 40.0s.

    BPM=150 manimgl revision_line.py RevisionLine -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 9, AND THE SECOND "WHERE YOU ACTUALLY USE IT" COMPANION — episode 6's
measurement, run on a problem the audience for this page literally has.

        mark  =  m · hours  +  b

EPISODE 6 FOUND THE BEST LINE. It never used one. This does: four students,
hours revised against the mark they got, dots that do not line up, the line that
misses least, and then the only question anybody actually asks — *what do I get
if I do five?*

        hours   1    2    3    4
        mark   48   52   60   72        the dots do NOT line up

        best line   mark = 8 · hours + 38
        it gives    46   54   62   70    total miss 2² + 2² + 2² + 2² = 16
        at 5 hours  8 · 5 + 38  =  78

THE LAST BEAT IS THE HONEST ONE, AND IT IS THE POINT. The line describes those
four students. It is not a promise about the viewer. Every model in the world
has exactly this limitation and almost nobody says it out loud — a model finds
the pattern in the data it was shown, and then gets asked about somebody who
was not in it. Saying that on a maths page is worth more than the prediction.

        "the line knows four people. it does not know you."

WHY THIS DATA. Every residual is ±2, so the total is a clean 16 and no single
point looks like the odd one out — the line is visibly a compromise rather than
a near-miss on one outlier. And 8 marks per hour of revision is optimistic
enough to be motivating and small enough not to be a silly claim.

VERIFIED AT IMPORT
    the line is the real least-squares fit    computed, not asserted — (8, 38)
    every predicted mark is a whole number
    every miss is exactly ±2, total 16        in integers
    the dots do NOT lie on the line           or there is nothing to fit
    the answer at 5 hours is exactly 78
    every mark stays inside 0..100            it is a percentage

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_DOTS, END_FIT, END_USE = 26, 52, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "WHERE YOU ACTUALLY USE IT"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"
GREEN  = "#A3BE8C"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
EQ_Y   = 2.42
ANS_Y  = 1.72
NOTE_Y = -3.16
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
HOURS = [1, 2, 3, 4]
MARKS = [48, 52, 60, 72]
M, B = 8, 38
AHEAD = 5

FIT = [M * h + B for h in HOURS]
MISS = [a - f for a, f in zip(MARKS, FIT)]
TOTAL_MISS = sum(e * e for e in MISS)
PRED = M * AHEAD + B


def least_squares(xs, ys):
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    mx, my = x.mean(), y.mean()
    m = ((x - mx) * (y - my)).sum() / ((x - mx) ** 2).sum()
    return m, my - m * mx


_m, _b = least_squares(HOURS, MARKS)
assert (_m, _b) == (float(M), float(B)), (_m, _b)   # computed, not claimed
assert all(isinstance(f, int) for f in FIT)
assert all(abs(e) == 2 for e in MISS), MISS
assert TOTAL_MISS == 16, TOTAL_MISS
assert MARKS != FIT, "the dots must not lie on the line"
assert PRED == 78, PRED
assert all(0 <= v <= 100 for v in MARKS + FIT + [PRED]), "marks are percentages"

MS, BS, PS, AS_ = str(M), str(B), str(PRED), str(AHEAD)

Y_LO, Y_HI = 40.0, 82.0
PX0, PX1 = -1.62, 1.66
PY0, PY1 = -2.30, 0.52

BASE = ["mark", "=", "m", "·", "hours", "+", "b"]
S_M, S_H, S_B = 2, 4, 6
SLOTS = (S_M, S_H, S_B)


def sx(h):
    return PX0 + (PX1 - PX0) * (h - 0.3) / 5.4


def sy(v):
    return PY0 + (PY1 - PY0) * (v - Y_LO) / (Y_HI - Y_LO)


def P(h, v):
    return np.array([sx(h), sy(v), 0.0])


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners([np.asarray(a, float), np.asarray(b, float)])
    m.set_stroke(opacity=op)
    return m


def dashed(a, b, color=GOLD, wid=2.4, n=12):
    g = VGroup()
    a, b = np.asarray(a, float), np.asarray(b, float)
    for i in range(n):
        t0, t1 = i / n, (i + 0.55) / n
        g.add(seg(a + (b - a) * t0, a + (b - a) * t1, color, wid, 0.9))
    return g


def observer_eye(color):
    grp = VGroup()
    for sign in (1, -1):
        m = VMobject(color=color, stroke_width=2.2)
        m.set_points_smoothly(
            [np.array([x, sign * 0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
             for x in np.linspace(-1.6, 1.6, 20)])
        grp.add(m)
    grp.add(Circle(radius=0.42, stroke_color=color, stroke_width=2.2).move_to(ORIGIN))
    grp.add(Dot(ORIGIN, radius=0.12, fill_color=color))
    rng = np.random.default_rng(2)
    for _ in range(5):
        s = rng.uniform(0.05, 0.12)
        sq = Square(side_length=s, color=color, stroke_width=1.5)
        sq.move_to([rng.uniform(1.7, 2.4), rng.uniform(-0.6, 0.6), 0])
        sq.set_fill(color, opacity=0.5)
        grp.add(sq)
    return grp


class RevisionLine(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.ans = None
        self.filled = {}

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_dots()
        self.stage_fit()
        self.stage_use()
        self.takeaway("We learned this at school.",
                      "Nobody ever said what for.")
        self.share()
        self.signature()

    # ------------------------------------------------------------------
    def T(self, beats):
        f0 = round(self.used * self.B * FPS)
        self.used += beats
        f1 = round(self.used * self.B * FPS)
        return (f1 - f0) / FPS

    def pad_to(self, target):
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(f"overruns by {-rem:.2f} beats — trim it")
        if rem > 0.01:
            self.wait(self.T(rem))

    def say(self, s, beats=2, color=WHITE_, size=25, extra=()):
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), *extra, run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), *extra,
                      run_time=self.T(beats))
            self.note = new

    # ---------------------------------------------------- the equation
    def make_eq(self, active=None, also=None, size=36):
        fill = dict(self.filled)
        if also:
            fill.update(also)
        g = VGroup()
        for i, base in enumerate(BASE):
            s = fill.get(i, base)
            if i == active:
                col, sz = GOLD, int(size * 1.14)
            elif i in fill:
                col, sz = GOLD, size
            elif i in SLOTS:
                col, sz = DIM, size
            else:
                col, sz = WHITE_, size
            g.add(txt(s, sz, col, w=1.7))
        g.arrange(RIGHT, buff=0.13)
        if g.get_width() > 4.6:
            g.set_width(4.6)
        return g.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats):
        self.play(Transform(self.eq, self.make_eq(active)),
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, size, fly=2.5, settle=1.5):
        nxt = self.make_eq(active=slot, also={slot: value})
        target = nxt[slot]
        flier = txt(value, size, GOLD, w=1.7).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled[slot] = value
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("mark = m · hours + b", 38, GOLD, w=4.5)
        big.move_to(np.array([0, 1.05, 0]))
        q = VGroup(txt("how many hours", 32, WHITE_, w=4.6),
                   txt("is enough?", 32, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.14, 0]))
        sub = txt("the line will tell you", 22, GREY, bold=False)
        sub.move_to(np.array([0, -1.02, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # Four students. Hours revised, and what they got.
    # ==================================================================
    def stage_dots(self):
        xa = seg(P(0.3, Y_LO), P(5.7, Y_LO), GREY, 2.4, 0.85)
        ya = seg(P(0.45, Y_LO), P(0.45, Y_HI), GREY, 2.4, 0.85)
        self.axes = VGroup(xa, ya)
        self.h_lab = {}
        for h in HOURS + [AHEAD]:
            self.axes.add(seg(P(h, Y_LO), P(h, Y_LO + 1.3), FAINT, 2.2))
            lab = txt(str(h), 18, GREY, bold=False, w=0.4)
            lab.move_to(P(h, Y_LO) + np.array([0, -0.26, 0]))
            self.h_lab[h] = lab
            self.axes.add(lab)
        for v in (50, 60, 70, 80):
            self.axes.add(txt(str(v), 16, GREY, bold=False, w=0.6)
                          .move_to(P(0.45, v) + np.array([-0.34, 0, 0])))
        self.axes.add(txt("hours revised", 19, GREY, bold=False, w=1.9)
                      .move_to(P(3.6, Y_LO) + np.array([0, -0.60, 0])))
        self.axes.add(txt("mark", 19, GREY, bold=False, w=0.9)
                      .move_to(P(0.45, Y_HI) + np.array([0.42, 0.04, 0])))
        self.play(ShowCreation(xa), ShowCreation(ya), run_time=self.T(2))
        self.play(FadeIn(self.axes), run_time=self.T(1.5))

        self.dots = VGroup(*[Dot(P(h, v), radius=0.085, fill_color=WHITE_)
                             for h, v in zip(HOURS, MARKS)])
        self.vals = VGroup(*[txt(str(v), 21, WHITE_, w=0.8)
                             .move_to(P(h, v) + np.array([-0.06, 0.30, 0]))
                             for h, v in zip(HOURS, MARKS)])
        self.play(LaggedStart(*[AnimationGroup(FadeIn(dd, scale=1.6), FadeIn(vv))
                                for dd, vv in zip(self.dots, self.vals)],
                              lag_ratio=0.55), run_time=self.T(4))
        self.say("four students. hours revised, and what they got.", 3)
        self.say("no straight line goes through all four.", 3)
        self.pad_to(END_DOTS)

    # ==================================================================
    # The line that misses least — episode 6's measurement, used.
    # ==================================================================
    def stage_fit(self):
        self.line = seg(P(0.45, M * 0.45 + B), P(AHEAD, M * AHEAD + B),
                        SKY, 3.6)
        self.play(ShowCreation(self.line), self.zoom.animate.set_value(0.96),
                  run_time=self.T(2.5))
        self.bars = VGroup(*[seg(P(h, f), P(h, v), GOLD, 4.4)
                             for h, v, f in zip(HOURS, MARKS, FIT)])
        self.play(*[ShowCreation(b) for b in self.bars], run_time=self.T(2))
        self.say(f"the line that misses least. every miss is 2.", 2.5, GOLD)
        self.say(f"total {TOTAL_MISS}. nothing beats it.", 2, GOLD)

        self.play(FadeOut(self.bars), FadeOut(self.vals), run_time=self.T(1.5))

        # the step and the start, dragged in — episode 1's two numbers
        st = VGroup(seg(P(2, FIT[1]), P(3, FIT[1]), ROSE, 3.2),
                    seg(P(3, FIT[1]), P(3, FIT[2]), ROSE, 3.2))
        self.step_lab = txt(f"+{MS}", 21, ROSE, w=0.8).move_to(
            P(3, (FIT[1] + FIT[2]) / 2) + np.array([0.42, 0, 0]))
        self.steps = VGroup(st, self.step_lab)
        self.play(ShowCreation(st), FadeIn(self.step_lab), run_time=self.T(2.5))
        self.say("one more hour is worth 8 marks. that is m.", 2.5, ROSE)
        self.drag_into(self.step_lab.get_center(), S_M, MS, 21,
                       fly=2.5, settle=1)

        self.b_lab = txt(BS, 21, ROSE, w=0.8).move_to(
            P(0.45, B) + np.array([0.30, -0.26, 0]))
        self.bmark = VGroup(self.b_lab)
        self.play(FadeIn(self.b_lab), FadeOut(self.steps), run_time=self.T(1.5))
        self.say("with zero hours it starts at 38. that is b.", 2, ROSE)
        self.drag_into(self.b_lab.get_center(), S_B, BS, 21,
                       fly=2.5, settle=1)
        self.pad_to(END_FIT)

    # ==================================================================
    # Five hours. And then the honest bit.
    # ==================================================================
    def stage_use(self):
        self.relight(S_H, 1.5)
        self.say("so — what if you do five?", 2.5)
        five = self.h_lab[AHEAD]
        ring = Circle(radius=0.20, stroke_color=GOLD, stroke_width=2.8)
        ring.move_to(five.get_center())
        self.play(ShowCreation(ring), run_time=self.T(1.5))
        self.drag_into(five.get_center(), S_H, AS_, 22, fly=2.5, settle=1.5)

        self.ans = txt(f"= {PS}", 38, GOLD, w=2.0)
        self.ans.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.ans, scale=1.15), FadeOut(ring),
                  run_time=self.T(2), rate_func=rush_from)
        self.say("eight times five, plus thirty-eight. 78.", 2.5)

        ext = dashed(P(HOURS[-1], FIT[-1]), P(AHEAD, PRED), GOLD, 3.2, 6)
        hit = Dot(P(AHEAD, PRED), radius=0.11, fill_color=GOLD)
        plab = txt(PS, 22, GOLD, w=0.8).move_to(
            P(AHEAD, PRED) + np.array([-0.06, 0.30, 0]))
        self.play(ShowCreation(ext), FadeIn(hit, scale=2.0), FadeIn(plab),
                  run_time=self.T(2.5))

        self.say("and now the part nobody says out loud.", 3, ROSE)
        self.say("the line knows four people.", 2.5, ROSE)
        self.say("it does not know you.", 2.5, ROSE)
        self.say("every AI has exactly this problem —", 2.5)
        self.say("it learns a pattern, then gets asked about someone new.", 2.5)
        self.pad_to(END_USE)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.ans, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, -0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.82, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is how it's solved", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.40, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.eq), FadeOut(self.ans),
                  FadeOut(self.title), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.5))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))
