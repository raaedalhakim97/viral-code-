"""
sales_line — where m, x and b actually come from. 40.0s.

    BPM=150 manimgl sales_line.py SalesLine -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 1 OF "WHY DID WE LEARN THIS?" — the page series about the maths
everybody was made to memorise and nobody was told the use of.

THE EQUATION IS THE SPINE, NOT A CAPTION. It sits at the top from the first
second to the last, and it starts EMPTY:

        y  =  m  ·  x  +  b

Each letter is a hole. The graph below fills them, one at a time, and every
number is physically DRAGGED off the picture and into its slot:

    x  ←  the day            it was always just the day number
    m  ←  the step           +10 from one day to the next, every time
    b  ←  the start          run the line back past day one: 20
    x  ←  5                  now put tomorrow in and read the answer

        y = m·x + b   →   y = 10·x + b   →   y = 10·x + 20
                      →   y = 10·5 + 20  →   = 70

That is the whole design. A viewer who has only ever seen the letters gets to
watch each one get replaced by a thing they can point at on a graph.

WHY THE MULTIPLICATION DOT. School writes "mx". Written that way the final
substitution reads "105 + 20", which is unreadable. The explicit "·" costs one
glyph and makes "10 · 5 + 20" say exactly what it means.

    day     1    2    3    4         (and 5, which is the point)
    sales  30   40   50   60

VERIFIED AT IMPORT
    every point is exactly on the line          s == M*d + B, integers
    every step is exactly +10                   the claim the staircase makes
    STEP == M                                   the visible step IS the slope
    least squares on this data returns (10, 20) the fit is computed, not stated
    the prediction at day 5 is 70               exactly

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
END_X, END_M, END_B, END_USE = 24, 44, 64, 82
END_TAKE = 90

SERIES = "WHY DID WE LEARN THIS?"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"

FRAME_H = 9.0
BREATH_BEATS = 32.0     # one slow push-in and pull-out
BREATH_AMT   = 0.05
LINE_Y  = -2.05
EQ_Y    = 2.42          # the equation lives here for the whole video
ANS_Y   = 1.86          # and its answer appears just under it
NOTE_Y  = -2.34

DAYS  = [1, 2, 3, 4]
SALES = [30, 40, 50, 60]
AHEAD = 5

X_MAX, Y_MAX = 6.0, 75.0
PX0, PX1 = -1.72, 1.80
PY0, PY1 = -1.70, 1.35     # lifted: the day-5 ring sits under the
                           # axis and was landing on the note line

# the equation, as seven separate pieces so any one of them can be replaced
BASE = ["y", "=", "m", "·", "x", "+", "b"]
IDX_M, IDX_X, IDX_B = 2, 4, 6


# ---------------------------------------------------------------- the fit
def least_squares(xs, ys):
    x, y = np.asarray(xs, float), np.asarray(ys, float)
    mx, my = x.mean(), y.mean()
    m = ((x - mx) * (y - my)).sum() / ((x - mx) ** 2).sum()
    return m, my - m * mx


M, B = least_squares(DAYS, SALES)
PRED = M * AHEAD + B
STEP = SALES[1] - SALES[0]

assert (M, B) == (10.0, 20.0), (M, B)
assert all(s == M * d + B for d, s in zip(DAYS, SALES))
assert all(b - a == STEP for a, b in zip(SALES, SALES[1:]))
assert STEP == M, (STEP, M)
assert PRED == 70.0, PRED

MS, BS, PS, AS_ = f"{M:.0f}", f"{B:.0f}", f"{PRED:.0f}", f"{AHEAD:.0f}"


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
        self.note = None
        self.filled = {}                 # slot index -> the number now in it

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        # A slow breath for the whole video, plus deliberate pushes on the
        # stages with small detail in them. camera.frame already lives in
        # scene.mobjects, which is why this updater runs — and why takeaway()
        # has to keep it out of the mobjects it clears and fades.
        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_x()
        self.stage_m()
        self.stage_b()
        self.stage_use()
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
    def make_eq(self, active=None, also=None, size=40):
        """The equation as seven pieces. A slot holds its letter until a number
        has been dragged into it; the slot being talked about is gold and a
        size bigger, everything settled is gold, everything waiting is dim."""
        fill = dict(self.filled)
        if also:
            fill.update(also)
        g = VGroup()
        for i, base in enumerate(BASE):
            s = fill.get(i, base)
            done = i in fill
            if i == active:
                col, sz = GOLD, int(size * 1.14)
            elif done:
                col, sz = GOLD, size
            elif i in (IDX_M, IDX_X, IDX_B):
                col, sz = DIM, size
            else:
                col, sz = WHITE_, size
            g.add(txt(s, sz, col, w=1.6))
        g.arrange(RIGHT, buff=0.13)
        if g.get_width() > 4.6:
            g.set_width(4.6)
        return g.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats):
        """Move the spotlight to another slot without changing anything in it."""
        self.play(Transform(self.eq, self.make_eq(active)),
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, size, fly=3.0, settle=2.0):
        """Lift the number off the graph and drop it into its slot.

        The target is read off a freshly built equation rather than off the
        live one, because the slots re-space every time one of them changes
        width — the flier has to land where the piece is ABOUT to be."""
        nxt = self.make_eq(active=slot, also={slot: value})
        target = nxt[slot]
        flier = txt(value, size, GOLD, w=1.6).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled[slot] = value
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("y = m · x + b", 52, GOLD, w=4.6)
        big.move_to(np.array([0, 0.95, 0]))
        q = VGroup(txt("where do m, x and b", 30, WHITE_, w=4.6),
                   txt("come from?", 30, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, 0.02, 0]))
        sub = txt("nobody ever showed you", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.85, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.eq = self.make_eq()
        # the hook itself becomes the tool: it shrinks into place at the top
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # x — it was always just the day.
    # ==================================================================
    def stage_x(self):
        xa = seg(P(0, 0), P(X_MAX, 0), GREY, 2.6, 0.8)
        ya = seg(P(0, 0), P(0, Y_MAX), GREY, 2.6, 0.8)
        self.marks = VGroup()
        self.day_lab = {}
        for d in range(1, 6):
            self.marks.add(seg(P(d, 0), P(d, 0) + np.array([0, 0.08, 0]),
                               FAINT, 2.2))
            lab = txt(str(d), 18, GREY, bold=False, w=0.4)
            lab.move_to(P(d, 0) + np.array([0, -0.28, 0]))
            self.day_lab[d] = lab
            self.marks.add(lab)
        xlab = txt("day", 21, GREY, bold=False, w=0.8)
        xlab.move_to(P(X_MAX, 0) + np.array([-0.02, -0.30, 0]))
        ylab = txt("sales", 21, GREY, bold=False, w=1.0)
        ylab.move_to(P(0, Y_MAX) + np.array([0.50, 0.04, 0]))
        self.play(ShowCreation(xa), ShowCreation(ya), run_time=self.T(2))
        self.play(FadeIn(self.marks), FadeIn(xlab), FadeIn(ylab),
                  run_time=self.T(1))

        self.relight(IDX_X, 2)
        self.say("x is the day. that is all x ever was.", 3)

        self.dots = VGroup(*[Dot(P(d, s), radius=0.085, fill_color=WHITE_)
                             for d, s in zip(DAYS, SALES)])
        self.vals = VGroup(*[txt(str(s), 23, WHITE_, w=0.8)
                             .move_to(P(d, s) + np.array([-0.02, 0.36, 0]))
                             for d, s in zip(DAYS, SALES)])
        self.play(LaggedStart(*[AnimationGroup(FadeIn(dd, scale=1.6), FadeIn(vv))
                                for dd, vv in zip(self.dots, self.vals)],
                              lag_ratio=0.55), run_time=self.T(4))
        self.say("a small shop. four days of sales.", 3)
        self.pad_to(END_X)

    # ==================================================================
    # m — the step, dragged into its slot.
    # ==================================================================
    def stage_m(self):
        self.play(Transform(self.eq, self.make_eq(IDX_M)),
                  FadeOut(self.vals),
                  self.zoom.animate.set_value(0.95), run_time=self.T(2))
        self.say("m? look at the step from day to day.", 3)

        self.stairs = VGroup()
        last = None
        for i in range(len(DAYS) - 1):
            d0, s0, d1, s1 = DAYS[i], SALES[i], DAYS[i + 1], SALES[i + 1]
            across = seg(P(d0, s0), P(d1, s0), SKY, 3.4)
            up = seg(P(d1, s0), P(d1, s1), SKY, 3.4)
            lab = txt(f"+{STEP}", 22, SKY, bold=False, w=0.9)
            lab.move_to(P(d1, (s0 + s1) / 2) + np.array([0.46, 0, 0]))
            self.stairs.add(VGroup(across, up, lab))
            last = lab
            self.play(ShowCreation(across), ShowCreation(up), FadeIn(lab),
                      run_time=self.T(2))

        self.say(f"same jump every time: {MS}", 2, GOLD)
        self.drag_into(last.get_center(), IDX_M, MS, 22, fly=3, settle=2)
        self.say("that is m. m is the step.", 2)
        self.pad_to(END_M)

    # ==================================================================
    # b — where the line came from, dragged into its slot.
    # ==================================================================
    def stage_b(self):
        self.play(Transform(self.eq, self.make_eq(IDX_B)),
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.play(FadeOut(self.stairs), run_time=self.T(2))

        self.line = seg(P(DAYS[0], SALES[0]), P(DAYS[-1], SALES[-1]), GOLD, 3.8)
        self.play(ShowCreation(self.line), run_time=self.T(2.5))
        self.say("join the dots — one straight line", 2.5)

        back = dashed(P(DAYS[0], SALES[0]), P(0, B), GOLD, 3.0, 8)
        b_dot = Dot(P(0, B), radius=0.10, fill_color=GOLD)
        b_lab = txt(BS, 24, GOLD, w=0.8).move_to(P(0, B) + np.array([-0.34, 0.16, 0]))
        self.bmark = VGroup(back, b_dot, b_lab)
        self.play(ShowCreation(back), FadeIn(b_dot, scale=1.8), FadeIn(b_lab),
                  run_time=self.T(3))
        self.say(f"run it back past day one. it started at {BS}.", 2)

        self.drag_into(b_lab.get_center(), IDX_B, BS, 24, fly=3, settle=2)
        self.say("that is b. b is the start.", 1)
        self.pad_to(END_B)

    # ==================================================================
    # x again — put tomorrow in, and read the answer out.
    # ==================================================================
    def stage_use(self):
        self.play(Transform(self.eq, self.make_eq(IDX_X)),
                  FadeOut(self.bmark),
                  self.zoom.animate.set_value(0.93), run_time=self.T(2))
        self.say("the equation is full. now put tomorrow in.", 2)

        # ring the day-5 tick that is ALREADY on the axis, rather than adding
        # a second 5 next to it — the number being dragged has to be a thing
        # the viewer can already see
        five = self.day_lab[AHEAD]
        ring = Circle(radius=0.22, stroke_color=GOLD, stroke_width=2.8)
        ring.move_to(five.get_center())
        glow = txt(AS_, 20, GOLD, bold=False, w=0.4).move_to(five.get_center())
        self.play(ShowCreation(ring), FadeIn(glow), run_time=self.T(1.5))

        self.drag_into(five.get_center(), IDX_X, AS_, 26, fly=3, settle=1.5)
        self.say("x becomes 5.", 1.5)

        self.ans = txt(f"= {PS}", 40, GOLD, w=2.0)
        self.ans.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.ans, scale=1.15), FadeOut(ring), FadeOut(glow),
                  run_time=self.T(2), rate_func=rush_from)
        self.say(f"ten times five, plus twenty. {PS}.", 2)

        ext = dashed(P(DAYS[-1], SALES[-1]), P(AHEAD, PRED), GOLD, 3.4, 7)
        hit = Dot(P(AHEAD, PRED), radius=0.12, fill_color=GOLD)
        self.play(ShowCreation(ext), FadeIn(hit, scale=2.0), run_time=self.T(2))
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
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.30, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.5)
        l2.move_to(np.array([0, -0.45, 0]))
        self.play(FadeIn(l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)          # the closing line keeps two clear beats
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq), FadeOut(self.ans),
                  FadeOut(self.title), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3.5))
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
