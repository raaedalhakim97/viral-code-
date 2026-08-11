"""
sales_line — y = mx + b, and what it was always for. 28.8s.

    BPM=150 manimgl sales_line.py SalesLine -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

ONE PICTURE CARRIES SIX RUNGS. Fourth in the ladder family, after
circle_ladder.py, square_ladder.py and sine_unroll.py. Same shell: one set of
axes, seven dots, and nothing is ever added — only named.

    x = the day        y = the sales

    day     1   2   3   4   5   6   7
    sales  12  15  14  19  21  20  25

    1   the axes                          y = mx + b
    2   seven dots, one per day           x = day, y = sales
    3   b is where it starts              b = 10
    4   m is how fast it climbs           m = rise ÷ run = 2
    5   the line that misses by least     y = 2x + 10
    6   run the line one day further      day 8 → 26

THE FIT IS REAL AND IT IS EXACT. These seven points are not decoration: the
least-squares line through them is y = 2x + 10 with no rounding anywhere, so
every number the video says out loud is the true answer rather than a
convenient one. Mean day 4, mean sales 18, Sxy 56, Sxx 28, m = 56/28 = 2,
b = 18 − 2·4 = 10. The residuals are 0, +1, −2, +1, +1, −2, +1 — they sum to
exactly zero, which is what "best fit" means.

WHY IT MATTERS, WHICH IS THE POINT OF THE VIDEO. This is linear regression, the
first model in every machine-learning course, and the affine part of every
neural network layer is the same expression with matrices in it: y = Wx + b.
The video ends there, and that claim is the only thing in it not derived on
screen.

VERIFIED AT IMPORT
    m == 2 and b == 10                      exactly, and against np.polyfit
    residuals sum to 0                      exactly
    no nearby (m, b) has a smaller SSE      40401-point grid
    the prediction at day 8 is 26           exactly

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 72

END_OPEN = 4
END_R1, END_R2, END_R3, END_R4, END_R5, END_R6 = 12, 22, 30, 40, 50, 58
END_TAKE = 64

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"
SKY    = "#88C0D0"
LEAF   = "#A3BE8C"

FRAME_H = 9.0
LINE_Y  = -2.05
EQ_Y    = 2.55
NOTE_Y  = -2.30

DAYS  = [1, 2, 3, 4, 5, 6, 7]
SALES = [12, 15, 14, 19, 21, 20, 25]
AHEAD = 8                       # the day being predicted

X_MAX, Y_MAX = 9.0, 30.0        # what the axes span, in data units
PX0, PX1 = -1.90, 1.95          # and where that lands on screen
PY0, PY1 = -1.74, 1.70


# ---------------------------------------------------------------- the fit
def least_squares(xs, ys):
    """The line that minimises the total squared miss. Written out rather than
    called from numpy, because the video says these steps on screen."""
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    mx, my = x.mean(), y.mean()
    m = ((x - mx) * (y - my)).sum() / ((x - mx) ** 2).sum()
    return m, my - m * mx


M, B = least_squares(DAYS, SALES)
PRED = M * AHEAD + B
RESID = [s - (M * d + B) for d, s in zip(DAYS, SALES)]

assert (M, B) == (2.0, 10.0), (M, B)
assert np.allclose(np.polyfit(DAYS, SALES, 1), [M, B])
assert abs(sum(RESID)) < 1e-12, RESID          # what "best fit" means
assert PRED == 26.0, PRED

_sse = sum(r * r for r in RESID)
for _dm in np.linspace(-1, 1, 201):            # nothing nearby fits better
    for _db in np.linspace(-4, 4, 201):
        _e = sum((s - ((M + _dm) * d + (B + _db))) ** 2
                 for d, s in zip(DAYS, SALES))
        assert _e >= _sse - 1e-9, (_dm, _db)

MS = f"{M:.0f}"
BS = f"{B:.0f}"
PS = f"{PRED:.0f}"


def sx(d):
    return PX0 + (PX1 - PX0) * d / X_MAX


def sy(v):
    return PY0 + (PY1 - PY0) * v / Y_MAX


def P(d, v):
    return np.array([sx(d), sy(v), 0.0])


# ---------------------------------------------------------------- drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    return m


def dashed(a, b, color=GOLD, wid=2.4, n=14):
    """A dashed segment, built by hand so it needs no DashedLine behaviour."""
    g = VGroup()
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


class SalesLine(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.eq = None
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open_card()
        self.rung1_axes()
        self.rung2_dots()
        self.rung3_b()
        self.rung4_m()
        self.rung5_line()
        self.rung6_predict()
        self.takeaway("You learned this at 14.",
                      "A neural net layer is still y = Wx + b.")
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

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.06):
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def say(self, s, beats=2, color=WHITE_, size=24, extra=()):
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

    def show_eq(self, s, beats=2, color=WHITE_, size=32):
        body = s if isinstance(s, VMobject) else txt(s, size, color, w=4.6)
        new = self.dance(body.move_to(np.array([0, EQ_Y, 0])))
        if self.eq is None:
            self.eq = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.eq.clear_updaters()
            self.play(FadeOut(self.eq, shift=0.12 * UP),
                      FadeIn(new, shift=0.12 * UP), run_time=self.T(beats))
            self.eq = new

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("y = mx + b", 56, GOLD, w=4.6),
                     txt("predicts tomorrow", 30, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.26)
        big.move_to(np.array([0, 0.85, 0]))
        sub = txt("the one they never explained", 23, GREY, bold=False)
        sub.move_to(np.array([0, -0.20, 0]))
        self.add(big, sub)
        self.wait(self.T(3))
        self.title = txt("y = mx + b", 20, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.play(FadeOut(big), FadeOut(sub), FadeIn(self.title),
                  run_time=self.T(1))
        self.pad_to(END_OPEN)

    # ==================================================================
    # 1 — the axes.  x is the day, y is the sales.  Nothing else.
    # ==================================================================
    def rung1_axes(self):
        self.show_eq("y = mx + b", 2)

        xa = seg(P(0, 0), P(X_MAX, 0), GREY, 2.6, 0.8)
        ya = seg(P(0, 0), P(0, Y_MAX), GREY, 2.6, 0.8)
        ticks = VGroup()
        for d in range(1, 9):
            ticks.add(seg(P(d, 0), P(d, 0) + np.array([0, 0.07, 0]), FAINT, 2.0))
        for v in (10, 20, 30):
            ticks.add(seg(P(0, v), P(0, v) + np.array([0.07, 0, 0]), FAINT, 2.0))
            lab = txt(str(v), 17, GREY, bold=False, w=0.5)
            lab.move_to(P(0, v) + np.array([-0.26, 0, 0]))
            ticks.add(lab)
        xlab = txt("day", 20, GREY, bold=False, w=0.8)
        xlab.move_to(P(X_MAX, 0) + np.array([-0.10, -0.30, 0]))
        ylab = txt("sales", 20, GREY, bold=False, w=1.0)
        ylab.move_to(P(0, Y_MAX) + np.array([0.46, 0.06, 0]))
        self.axes = VGroup(xa, ya, ticks, xlab, ylab)
        self.play(ShowCreation(xa), ShowCreation(ya), run_time=self.T(1))
        self.play(FadeIn(ticks), FadeIn(xlab), FadeIn(ylab), run_time=self.T(1))

        self.say("you did this at school and never used it", 2)
        self.say("x is the day.   y is the sales.", 2)
        self.pad_to(END_R1)

    # ==================================================================
    # 2 — the data.  Seven days of a small shop.
    # ==================================================================
    def rung2_dots(self):
        self.show_eq("x = day     y = sales", 2)

        self.dots = VGroup(*[Dot(P(d, s), radius=0.075, fill_color=WHITE_)
                             for d, s in zip(DAYS, SALES)])
        self.play(LaggedStart(*[FadeIn(dd, scale=1.6) for dd in self.dots],
                              lag_ratio=0.45), run_time=self.T(3))
        self.say("one dot per day. that is all the data.", 2)
        self.say(", ".join(str(s) for s in SALES), 2, GOLD)
        self.pad_to(END_R2)

    # ==================================================================
    # 3 — b.  Where you were before day one.
    # ==================================================================
    def rung3_b(self):
        self.show_eq(f"b = {BS}", 2, GOLD)
        b_dot = Dot(P(0, B), radius=0.085, fill_color=GOLD)
        b_lab = txt(BS, 24, GOLD, w=0.6).move_to(P(0, B) + np.array([0.30, 0.30, 0]))
        self.play(FadeIn(b_dot, scale=1.8), FadeIn(b_lab), run_time=self.T(2))
        self.bmark = VGroup(b_dot, b_lab)
        self.say("b is where the line starts — day zero", 2)
        self.say(f"you were already selling {BS}", 2)
        self.pad_to(END_R3)

    # ==================================================================
    # 4 — m.  Along one, up two.  That is the whole of slope.
    # ==================================================================
    def rung4_m(self):
        self.show_eq("m = rise ÷ run", 2)

        d0 = 4
        run = seg(P(d0, M * d0 + B), P(d0 + 1, M * d0 + B), COOL, 3.4)
        rise = seg(P(d0 + 1, M * d0 + B), P(d0 + 1, M * (d0 + 1) + B), GOLD, 3.4)
        rl = txt("+1 day", 18, COOL, bold=False, w=1.0)
        rl.move_to((P(d0, M * d0 + B) + P(d0 + 1, M * d0 + B)) / 2
                   + np.array([0, -0.22, 0]))
        ul = txt(f"+{MS} sales", 18, GOLD, bold=False, w=1.2)
        ul.move_to((P(d0 + 1, M * d0 + B) + P(d0 + 1, M * (d0 + 1) + B)) / 2
                   + np.array([0.62, 0, 0]))
        self.step = VGroup(run, rise, rl, ul)
        self.play(ShowCreation(run), FadeIn(rl), run_time=self.T(1.5))
        self.play(ShowCreation(rise), FadeIn(ul), run_time=self.T(1.5))

        self.say(f"one day along, {MS} sales up", 1.5)
        self.show_eq(f"m = {MS}", 1.5, GOLD)
        self.say(f"m is the climb: +{MS} every single day", 2)
        self.pad_to(END_R4)

    # ==================================================================
    # 5 — the line.  Best fit is not a mystery: it is smallest total miss.
    # ==================================================================
    def rung5_line(self):
        self.show_eq(f"y = {MS}x + {BS}", 2, GOLD)
        line = seg(P(0, B), P(7, M * 7 + B), GOLD, 3.6)
        self.play(ShowCreation(line), run_time=self.T(2))
        self.line = line

        misses = VGroup(*[seg(P(d, s), P(d, M * d + B), SKY, 4.4, 1.0)
                          for d, s in zip(DAYS, SALES) if abs(s - (M * d + B)) > 1e-9])
        self.play(ShowCreation(misses), run_time=self.T(1.5))
        self.say("no line hits them all", 1.5)
        self.play(FadeOut(misses), run_time=self.T(1))
        self.say("this is the one that misses by the least", 2, GOLD)
        self.pad_to(END_R5)

    # ==================================================================
    # 6 — the prediction.  Run the same line one day further.
    # ==================================================================
    def rung6_predict(self):
        self.play(FadeOut(self.step), FadeOut(self.bmark), run_time=self.T(1))
        self.show_eq(f"day {AHEAD}  →  {MS}({AHEAD}) + {BS}", 1.5)

        ext = dashed(P(7, M * 7 + B), P(AHEAD, PRED), GOLD, 3.0, 9)
        self.play(ShowCreation(ext), run_time=self.T(1.5))
        hit = Dot(P(AHEAD, PRED), radius=0.11, fill_color=GOLD)
        drop = dashed(P(AHEAD, PRED), P(AHEAD, 0), GREY, 1.8, 12)
        self.play(FadeIn(hit, scale=2.0), ShowCreation(drop), run_time=self.T(1.5))

        self.show_eq(f"= {PS} sales", 1.5, GOLD)
        self.say(f"tomorrow: {PS}. that is a prediction.", 1)
        self.pad_to(END_R6)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None
        l1 = txt(a, 28, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 25, GOLD, w=4.5)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(END_TAKE)          # two clear beats on the closing line
        self.eq.clear_updaters()
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq),
                  FadeOut(self.title), run_time=self.T(1))
        self.eq = None

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
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
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))
