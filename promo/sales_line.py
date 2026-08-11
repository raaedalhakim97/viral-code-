"""
sales_line — y = mx + b, and what it was always for. 28.8s.

    BPM=150 manimgl sales_line.py SalesLine -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

EPISODE 1 OF "WHY DID WE LEARN THIS?" — the page series about the maths
everybody was made to memorise and nobody was told the use of. The series name
sits in the header for the whole video.

ONE PICTURE CARRIES FIVE RUNGS. Fourth in the ladder family, after
circle_ladder.py, square_ladder.py and sine_unroll.py. Same shell: one set of
axes, four dots, and nothing is ever added — only named.

    day     1    2    3    4         (and 5, which is the point)
    sales  30   40   50   60

    1   four dots, one per day        a shop. that is all the data.
    2   the step between them         m = 10
    3   the line, run back to day 0   b = 20
    4   put the two together          y = 10x + 20
    5   run it one day further        day 5 → 70

WHY THE DOTS SIT EXACTLY ON THE LINE. The first cut used seven days of realistic
wobbly sales and spent a whole rung on least squares — residuals, "the line that
misses by the least", the lot. Every word of it was true and it made the video
hard, and worse, seven data values plus axis ticks plus m plus b plus the
prediction put a dozen numbers on screen at once. This cut shows FOUR values,
introduces exactly ONE new number per rung, and clears each rung's numbers
before the next arrives. The shop's sales go up by ten a day because that is the
setup, not a claim about shops.

VERIFIED AT IMPORT
    every point is exactly on the line          s == M*d + B, integers
    every step is exactly +10                   the claim rung 2 makes
    least squares on this data returns (10, 20) the fit is real, not asserted
    every residual is exactly zero
    the prediction at day 5 is 70               exactly

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
END_R1, END_R2, END_R3, END_R4, END_R5 = 16, 28, 40, 48, 58
END_TAKE = 64

SERIES = "WHY DID WE LEARN THIS?"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"

FRAME_H = 9.0
LINE_Y  = -2.05
EQ_Y    = 2.50
NOTE_Y  = -2.30

DAYS  = [1, 2, 3, 4]
SALES = [30, 40, 50, 60]
AHEAD = 5                       # the day being predicted

X_MAX, Y_MAX = 6.0, 75.0        # what the axes span, in data units
PX0, PX1 = -1.72, 1.86          # and where that lands on screen
PY0, PY1 = -1.80, 1.72


# ---------------------------------------------------------------- the fit
def least_squares(xs, ys):
    """The real thing, not a hard-coded answer — on this data it happens to
    come out whole because the data is clean."""
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    mx, my = x.mean(), y.mean()
    m = ((x - mx) * (y - my)).sum() / ((x - mx) ** 2).sum()
    return m, my - m * mx


M, B = least_squares(DAYS, SALES)
PRED = M * AHEAD + B
STEP = SALES[1] - SALES[0]

assert (M, B) == (10.0, 20.0), (M, B)
assert all(s == M * d + B for d, s in zip(DAYS, SALES))        # exactly on it
assert all(b - a == STEP for a, b in zip(SALES, SALES[1:]))    # rung 2's claim
assert STEP == M, (STEP, M)                                    # the step IS m
assert PRED == 70.0, PRED

MS, BS, PS = f"{M:.0f}", f"{B:.0f}", f"{PRED:.0f}"


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


def dashed(a, b, color=GOLD, wid=2.4, n=12):
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
        self.rung1_dots()
        self.rung2_step()
        self.rung3_start()
        self.rung4_together()
        self.rung5_predict()
        self.takeaway("We learned this at school.",
                      "Nobody ever said what for.")
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

    def show_eq(self, s, beats=2, color=WHITE_, size=34):
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
        big = VGroup(txt("y = mx + b", 54, GOLD, w=4.6),
                     txt("WHAT IS IT FOR?", 34, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.28)
        big.move_to(np.array([0, 0.85, 0]))
        sub = txt("you wondered at 14. nobody answered.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.25, 0]))
        self.add(big, sub)
        self.wait(self.T(3))
        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.play(FadeOut(big), FadeOut(sub), FadeIn(self.title),
                  run_time=self.T(1))
        self.pad_to(END_OPEN)

    # ==================================================================
    # 1 — four dots.  Four numbers, and that is the whole of the data.
    # ==================================================================
    def rung1_dots(self):
        self.show_eq("y = mx + b", 2)

        xa = seg(P(0, 0), P(X_MAX, 0), GREY, 2.6, 0.8)
        ya = seg(P(0, 0), P(0, Y_MAX), GREY, 2.6, 0.8)
        marks = VGroup()
        for d in range(1, 6):
            marks.add(seg(P(d, 0), P(d, 0) + np.array([0, 0.08, 0]), FAINT, 2.2))
            marks.add(txt(str(d), 17, GREY, bold=False, w=0.4)
                      .move_to(P(d, 0) + np.array([0, -0.26, 0])))
        xlab = txt("day", 20, GREY, bold=False, w=0.8)
        xlab.move_to(P(X_MAX, 0) + np.array([-0.02, -0.28, 0]))
        ylab = txt("sales", 20, GREY, bold=False, w=1.0)
        ylab.move_to(P(0, Y_MAX) + np.array([0.48, 0.04, 0]))
        self.play(ShowCreation(xa), ShowCreation(ya), run_time=self.T(1))
        self.play(FadeIn(marks), FadeIn(xlab), FadeIn(ylab), run_time=self.T(0.5))
        self.say("a small shop. four days of sales.", 2)

        self.dots = VGroup(*[Dot(P(d, s), radius=0.085, fill_color=WHITE_)
                             for d, s in zip(DAYS, SALES)])
        self.vals = VGroup(*[txt(str(s), 23, GOLD, w=0.8)
                             .move_to(P(d, s) + np.array([-0.02, 0.34, 0]))
                             for d, s in zip(DAYS, SALES)])
        self.play(LaggedStart(*[AnimationGroup(FadeIn(dd, scale=1.6), FadeIn(vv))
                                for dd, vv in zip(self.dots, self.vals)],
                              lag_ratio=0.5), run_time=self.T(3))
        self.say("four dots. that is all the data.", 2)
        self.pad_to(END_R1)

    # ==================================================================
    # 2 — m.  The step from one dot to the next, and it never changes.
    # ==================================================================
    def rung2_step(self):
        self.show_eq("m = the step", 2)
        # the four values have done their job; clear them before the next
        # number arrives, or the screen ends up a wall of digits
        self.play(FadeOut(self.vals), run_time=self.T(1))

        self.stairs = VGroup()
        for a, b in zip(range(len(DAYS) - 1), range(1, len(DAYS))):
            d0, s0, d1, s1 = DAYS[a], SALES[a], DAYS[b], SALES[b]
            across = seg(P(d0, s0), P(d1, s0), SKY, 3.4)
            up = seg(P(d1, s0), P(d1, s1), SKY, 3.4)
            lab = txt(f"+{STEP}", 21, SKY, bold=False, w=0.9)
            lab.move_to(P(d1, (s0 + s1) / 2) + np.array([0.44, 0, 0]))
            step = VGroup(across, up, lab)
            self.stairs.add(step)
            self.play(ShowCreation(across), ShowCreation(up), FadeIn(lab),
                      run_time=self.T(1))

        self.say(f"every day: {STEP} more. always {STEP}.", 2)
        self.show_eq(f"m = {MS}", 2, GOLD)
        self.say("m is the step. that is the whole of m.", 2)
        self.pad_to(END_R2)

    # ==================================================================
    # 3 — b.  Run the line backwards and see where it came from.
    # ==================================================================
    def rung3_start(self):
        self.show_eq("b = the start", 2)
        self.play(FadeOut(self.stairs), run_time=self.T(1))

        self.line = seg(P(DAYS[0], SALES[0]), P(DAYS[-1], SALES[-1]), GOLD, 3.8)
        self.play(ShowCreation(self.line), run_time=self.T(2))
        self.say("join the dots — one straight line", 2)

        back = dashed(P(DAYS[0], SALES[0]), P(0, B), GOLD, 3.0, 8)
        b_dot = Dot(P(0, B), radius=0.10, fill_color=GOLD)
        b_lab = txt(BS, 26, GOLD, w=0.8).move_to(P(0, B) + np.array([-0.32, 0.16, 0]))
        self.bmark = VGroup(back, b_dot, b_lab)
        self.play(ShowCreation(back), FadeIn(b_dot, scale=1.8), FadeIn(b_lab),
                  run_time=self.T(2))
        self.show_eq(f"b = {BS}", 2, GOLD)
        self.say("b is where it started. before day one.", 1)
        self.pad_to(END_R3)

    # ==================================================================
    # 4 — the two numbers, together.  That is the whole formula.
    # ==================================================================
    def rung4_together(self):
        self.show_eq(f"y = {MS}x + {BS}", 2, GOLD)
        self.say(f"the step is {MS}. the start is {BS}.", 2)
        self.say("that is the entire line.", 2)
        self.pad_to(END_R4)

    # ==================================================================
    # 5 — the prediction.  One more day of the same line.
    # ==================================================================
    def rung5_predict(self):
        self.play(FadeOut(self.bmark), run_time=self.T(1))
        self.show_eq(f"day {AHEAD}  →  {MS}×{AHEAD} + {BS}", 1.5)

        ext = dashed(P(DAYS[-1], SALES[-1]), P(AHEAD, PRED), GOLD, 3.4, 7)
        hit = Dot(P(AHEAD, PRED), radius=0.12, fill_color=GOLD)
        lab = txt(PS, 28, GOLD, w=0.9).move_to(P(AHEAD, PRED)
                                               + np.array([-0.06, 0.38, 0]))
        self.play(ShowCreation(ext), run_time=self.T(1))
        self.play(FadeIn(hit, scale=2.0), FadeIn(lab), run_time=self.T(1.5))

        self.show_eq(f"= {PS}", 1.5, GOLD)
        self.say(f"tomorrow you sell {PS}.", 1.5)
        self.say("you just predicted the future.", 2)
        self.pad_to(END_R5)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.5)
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
