"""
best_line — what if the dots DON'T line up? 40.0s.

    BPM=150 manimgl best_line.py BestLine -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 6 OF "WHY DID WE LEARN THIS?" — and the direct sequel to episode 1.
Same shell: the equation is the spine, it sits at the top for the whole video,
it starts EMPTY, and every number is dragged into its slot off the picture.

        miss  =  real  −  guess

EPISODE 1 CHEATED, ON PURPOSE. Its four dots sat exactly on the line, so the
line could just be drawn through them. Real sales never do that — and the
moment they don't, "draw the line" stops being a thing you can do by eye and
becomes a thing you have to MEASURE. That measurement is the whole of this
video, and it is the same measurement every AI on earth is trained by.

        day     1    2    3    4
        sales  30   45   50   65        the dots do not line up

    line A   y = 10x + 20  ->  30  40  50  60     nails two, misses two by 5
    line B   y = 11x + 20  ->  31  42  53  64     misses all four, a little

    total    A:  0² + 5² + 0² + 5²  =  50
             B:  1² + 3² + 3² + 1²  =  20

THE LESSON IS IN THAT COMPARISON. The line that nails two points is the WORSE
line. The good line misses everything slightly rather than some things badly —
which is not obvious, is genuinely useful, and is a sentence about maths that
also happens to be a sentence about life.

WHY SQUARE. A dot 3 below is exactly as wrong as a dot 3 above, so the signs
have to stop cancelling. Squaring is the cheapest way to do that, and it is
where "least squares" gets its name.

AND IT CLOSES THE LOOP ON EPISODE 4. That total IS the height of the valley the
ball rolls down. Episode 4 said "the height is how wrong the model is" and never
said where the height came from. This is where it comes from.

VERIFIED AT IMPORT
    line B is the real least-squares fit    computed, not asserted — (11, 20)
    every prediction is a whole number      both lines, all four days
    the two totals are 50 and 20            in integers
    line A really does nail days 1 and 3    the claim the picture makes
    B beats A                               so the payoff is a fact, not a hope

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
END_DOTS, END_MISS, END_TOTAL, END_BETTER = 26, 50, 68, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "WHY DID WE LEARN THIS?"

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
ANS_Y  = 1.80
TOT_Y  = 1.06
NOTE_Y = -3.16
LINE_Y = -2.05

MINUS = "−"

# ------------------------------------------------------------------ numbers
DAYS  = [1, 2, 3, 4]
SALES = [30, 45, 50, 65]

MA, BA = 10, 20          # line A — the line episode 1 ended on
MB, BB = 11, 20          # line B — the real best fit for this data

GA = [MA * d + BA for d in DAYS]
GB = [MB * d + BB for d in DAYS]
EA = [s - g for s, g in zip(SALES, GA)]
EB = [s - g for s, g in zip(SALES, GB)]
TA = sum(e * e for e in EA)
TB = sum(e * e for e in EB)


def least_squares(xs, ys):
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    mx, my = x.mean(), y.mean()
    m = ((x - mx) * (y - my)).sum() / ((x - mx) ** 2).sum()
    return m, my - m * mx


_m, _b = least_squares(DAYS, SALES)
assert (_m, _b) == (float(MB), float(BB)), (_m, _b)   # B is computed, not claimed
assert all(isinstance(g, int) for g in GA + GB)
assert EA == [0, 5, 0, 5] and EB == [-1, 3, -3, 1], (EA, EB)
assert (TA, TB) == (50, 20), (TA, TB)
assert TB < TA, "the whole video depends on B winning"
assert not all(SALES[i] == MA * DAYS[i] + BA for i in range(len(DAYS))), \
    "the dots must NOT line up — that was episode 1"
assert sum(1 for e in EA if e == 0) == 2, "line A nails exactly two of them"

# day 2 is the one the spine gets built from
D2 = 1
REAL_S, GUESS_S, MISS_S = str(SALES[D2]), str(GA[D2]), str(EA[D2])

Y_LO, Y_HI = 25.0, 72.0
PX0, PX1 = -1.66, 1.70
PY0, PY1 = -2.36, 0.46

BASE = ["miss", "=", "real", MINUS, "guess"]
S_MISS, S_REAL, S_GUESS = 0, 2, 4
SLOTS = (S_MISS, S_REAL, S_GUESS)


def sx(d):
    return PX0 + (PX1 - PX0) * (d - 0.4) / 4.4


def sy(v):
    return PY0 + (PY1 - PY0) * (v - Y_LO) / (Y_HI - Y_LO)


def P(d, v):
    return np.array([sx(d), sy(v), 0.0])


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


class BestLine(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.ans = None
        self.tot = None
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
        self.stage_miss()
        self.stage_total()
        self.stage_better()
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
        g.arrange(RIGHT, buff=0.14)
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

    def drop_onto(self, slot, value, target_point, size, fly=2.5, settle=1.5):
        """The other direction: the number the formula gives you, handed back
        down onto the picture it came from."""
        nxt = self.make_eq(active=slot, also={slot: value})
        self.filled[slot] = value
        self.play(Transform(self.eq, nxt), run_time=self.T(settle))
        src = nxt[slot]
        flier = txt(value, size, GOLD, w=1.7).move_to(src.get_center())
        flier.set_height(src.get_height())
        self.add(flier)
        self.play(flier.animate.move_to(target_point).set_height(0.30),
                  run_time=self.T(fly), rate_func=smooth)
        return flier

    def show_tot(self, s, beats, color=GOLD, size=34):
        new = txt(s, size, color, w=4.3).move_to(np.array([0, TOT_Y, 0]))
        if self.tot is None:
            self.tot = new
            self.play(FadeIn(new, scale=1.12), run_time=self.T(beats),
                      rate_func=rush_from)
        else:
            self.play(Transform(self.tot, new), run_time=self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("miss = real − guess", 40, GOLD, w=4.5)
        big.move_to(np.array([0, 1.05, 0]))
        q = VGroup(txt("but what if the dots", 31, WHITE_, w=4.6),
                   txt("DON'T line up?", 31, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.10, 0]))
        sub = txt("real sales never do", 22, GREY, bold=False)
        sub.move_to(np.array([0, -1.00, 0]))
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
    # Four dots that do not line up.
    # ==================================================================
    def stage_dots(self):
        xa = seg(P(0.4, Y_LO), P(4.4, Y_LO), GREY, 2.4, 0.85)
        ya = seg(P(0.55, Y_LO), P(0.55, Y_HI), GREY, 2.4, 0.85)
        self.axes = VGroup(xa, ya)
        self.day_lab = {}
        for d in DAYS:
            self.axes.add(seg(P(d, Y_LO), P(d, Y_LO + 1.6), FAINT, 2.2))
            lab = txt(str(d), 18, GREY, bold=False, w=0.4)
            lab.move_to(P(d, Y_LO) + np.array([0, -0.26, 0]))
            self.day_lab[d] = lab
            self.axes.add(lab)
        for v in (30, 50, 70):
            self.axes.add(txt(str(v), 17, GREY, bold=False, w=0.6)
                          .move_to(P(0.55, v) + np.array([-0.34, 0, 0])))
        self.axes.add(txt("day", 20, GREY, bold=False, w=0.8)
                      .move_to(P(4.4, Y_LO) + np.array([-0.04, -0.28, 0])))
        self.axes.add(txt("sales", 20, GREY, bold=False, w=1.0)
                      .move_to(P(0.55, Y_HI) + np.array([0.52, 0.02, 0])))
        self.play(ShowCreation(xa), ShowCreation(ya), run_time=self.T(2))
        self.play(FadeIn(self.axes), run_time=self.T(1.5))

        self.dots = VGroup(*[Dot(P(d, s), radius=0.085, fill_color=WHITE_)
                             for d, s in zip(DAYS, SALES)])
        self.vals = VGroup(*[txt(str(s), 22, WHITE_, w=0.8)
                             .move_to(P(d, s) + np.array([-0.04, 0.32, 0]))
                             for d, s in zip(DAYS, SALES)])
        self.play(LaggedStart(*[AnimationGroup(FadeIn(dd, scale=1.6), FadeIn(vv))
                                for dd, vv in zip(self.dots, self.vals)],
                              lag_ratio=0.55), run_time=self.T(4))
        self.say("last time the dots sat perfectly on a line.", 3)
        self.say("these don't. so which line is right?", 3.5)
        self.pad_to(END_DOTS)

    # ==================================================================
    # One line, one dot: what "miss" means.
    # ==================================================================
    def stage_miss(self):
        self.lineA = seg(P(0.55, MA * 0.55 + BA), P(4.4, MA * 4.4 + BA),
                         SKY, 3.6)
        self.play(ShowCreation(self.lineA), self.zoom.animate.set_value(0.96),
                  run_time=self.T(2.5))
        self.say("try one. the line from last time.", 2, SKY)

        # day 2 — the biggest gap, and the one the spine gets built from
        d = DAYS[D2]
        self.bar2 = seg(P(d, GA[D2]), P(d, SALES[D2]), GOLD, 5.0)
        self.gdot = Dot(P(d, GA[D2]), radius=0.075, fill_color=SKY)
        self.glab = txt(GUESS_S, 21, SKY, w=0.7).move_to(
            P(d, GA[D2]) + np.array([0.34, -0.04, 0]))
        self.play(FadeIn(self.gdot, scale=1.8), FadeIn(self.glab),
                  run_time=self.T(2))
        self.say("day 2. the line says 40. the shop sold 45.", 2.5)

        self.relight(S_REAL, 1)
        self.drag_into(self.vals[D2].get_center(), S_REAL, REAL_S, 22,
                       fly=2.5, settle=1)
        self.drag_into(self.glab.get_center(), S_GUESS, GUESS_S, 22,
                       fly=2.5, settle=1)

        self.play(ShowCreation(self.bar2), run_time=self.T(1.5))
        flier = self.drop_onto(S_MISS, MISS_S,
                               P(d, (SALES[D2] + GA[D2]) / 2)
                               + np.array([0.30, 0, 0]), 22,
                               fly=2, settle=1)
        self.miss2 = flier
        self.say("that gap is the miss. 5.", 2, GOLD)
        self.pad_to(END_MISS)

    # ==================================================================
    # All four misses, squared, added: one number for the whole line.
    # ==================================================================
    def stage_total(self):
        self.play(FadeOut(self.miss2), FadeOut(self.gdot), FadeOut(self.glab),
                  FadeOut(self.vals), self.zoom.animate.set_value(1.0),
                  run_time=self.T(2))
        self.barsA = VGroup(self.bar2)
        for i, d in enumerate(DAYS):
            if i == D2:
                continue
            self.barsA.add(seg(P(d, GA[i]), P(d, SALES[i]), GOLD, 5.0))
        self.play(*[ShowCreation(b) for b in self.barsA if b is not self.bar2],
                  run_time=self.T(2))
        self.say("now every day. the misses are 0, 5, 0, 5.", 2.5)

        self.say("a dot below counts the same as above — so square them.", 3.5)
        sumline = txt("0² + 5² + 0² + 5²", 27, GOLD, w=4.0)
        sumline.move_to(np.array([0, ANS_Y, 0]))
        self.ans = sumline
        self.play(FadeIn(sumline), run_time=self.T(2))
        self.show_tot(f"total miss  =  {TA}", 2.5)
        self.say("one number for how wrong the WHOLE line is.", 3)
        self.pad_to(END_TOTAL)

    # ==================================================================
    # Tilt it. The total falls. That is training.
    # ==================================================================
    def stage_better(self):
        self.say("tilt it, and watch that number.", 2, SKY)
        lineB = seg(P(0.55, MB * 0.55 + BB), P(4.4, MB * 4.4 + BB), GREEN, 3.6)
        barsB = VGroup(*[seg(P(d, GB[i]), P(d, SALES[i]), GREEN, 5.0)
                         for i, d in enumerate(DAYS)])
        sumB = txt("1² + 3² + 3² + 1²", 27, GREEN, w=4.0)
        sumB.move_to(np.array([0, ANS_Y, 0]))
        self.play(Transform(self.lineA, lineB),
                  Transform(self.barsA, barsB),
                  Transform(self.ans, sumB),
                  run_time=self.T(2.5), rate_func=smooth)
        self.show_tot(f"total miss  =  {TB}", 2.5, GREEN)
        self.say(f"{TA} down to {TB}. a better line.", 2, GREEN)
        self.say("it misses all four a little, instead of two badly.", 3)
        self.say("shrink that number — that IS training.", 1.5)
        self.pad_to(END_BETTER)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.tot, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        self.ans = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, -0.20, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.92, 0]))
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
        self.play(FadeOut(grp), FadeOut(self.eq), FadeOut(self.tot),
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
