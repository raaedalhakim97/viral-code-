"""
cosine_similarity — how AI decides two things mean the same. 40.0s.

    BPM=150 manimgl cosine_similarity.py CosineSimilarity -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 2 OF "WHY DID WE LEARN THIS?" — same shell as sales_line.py: the
equation is the spine, it sits at the top from the first second to the last,
it starts EMPTY, and every number is dragged into its slot off the picture.

                a · b
    cos θ  =  ─────────
               |a| · |b|

Two things become two arrows. The angle between them is how alike they are,
and cos of that angle is the score. That is cosine similarity, and it is the
number underneath every search box, every recommendation and every RAG lookup
in production — computed with the cos everybody met in a triangle.

    a · b      ←  15      multiply the matching numbers and add
    |a|·|b|    ←  25      five long times five long
    cos θ      →  0.6     dropped back onto the angle nobody measured

SAME NUMBER DISCIPLINE AS EPISODE 1. Small integers, one new number per stage,
each stage's numbers cleared before the next arrives, and the payoff exact
rather than rounded:

    a = (5, 0)   |a| = 5          a lies along the axis, so its length is free
    b = (3, 4)   |b| = 5          the 3-4-5, the one length everybody knows
    a · b = 5×3 + 0×4 = 15
    |a||b| = 25
    cos θ = 15/25 = 0.6           exact, and the angle is 53°, big enough to see

The (5, 0) choice is doing real work: it makes |a| = 5 readable straight off the
grid with no side quest, and it leaves one honest multiplication by zero in the
dot product, which is the clearest possible demonstration of "multiply the
matching numbers".

WHY c GOES DOWN, LIKE EPISODE 1's PREDICTION. You can count both arrows off the
grid. Nobody can measure the angle between them. So a·b and |a||b| are dragged
UP into the equation and the score is dropped back DOWN onto the arc.

VERIFIED AT IMPORT
    |a| and |b| are whole numbers          nothing on screen needs a square root
    a·b == 15 and |a||b| == 25             in integers
    cos == Fraction(3, 5) == 0.6           exact, checked as a fraction
    the angle is between 30° and 75°       so the arc is actually visible

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import math
import os
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_ARROWS, END_DOT, END_LEN, END_SCORE = 26, 46, 64, 82
END_TAKE = 90

SERIES = "WHY DID WE LEARN THIS?"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
LINE_Y  = -2.05
EQ_Y    = 2.40
ANS_Y   = 1.68
NOTE_Y  = -2.34

# the two arrows
AX, AY = 5, 0
BX, BY = 3, 4

LA = math.hypot(AX, AY)
LB = math.hypot(BX, BY)
DOT = AX * BX + AY * BY
DEN = int(round(LA * LB))
COS = Fraction(DOT, DEN)
THETA = math.degrees(math.acos(DOT / (LA * LB)))

assert LA == int(LA) and LB == int(LB), (LA, LB)      # no square roots on screen
assert (DOT, DEN) == (15, 25), (DOT, DEN)
assert COS == Fraction(3, 5) and float(COS) == 0.6, COS
assert 30 < THETA < 75, THETA                         # the arc has to be visible

LAS, LBS = f"{LA:.0f}", f"{LB:.0f}"
DOTS, DENS = str(DOT), str(DEN)
COSS = f"{float(COS):.1f}"

# the grid
GMAX = 5
OX, OY, GS = -1.60, -1.78, 0.58

# the equation: cos θ = (a·b) / (|a|·|b|)
NUM0, DEN0 = "a · b", "|a| · |b|"


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


def P(x, y):
    return np.array([OX + GS * x, OY + GS * y, 0.0])


def arrow(tip, color, wid=5.0):
    """A shaft plus a hand-built head — Arrow's tip scaling is fiddly at this
    size and this only ever needs two of them."""
    o = P(0, 0)
    d = tip - o
    n = d / (np.linalg.norm(d) + 1e-9)
    perp = np.array([-n[1], n[0], 0.0])
    g = VGroup(seg(o, tip - n * 0.10, color, wid))
    head = VMobject(stroke_width=0)
    head.set_points_as_corners([tip, tip - n * 0.26 + perp * 0.11,
                                tip - n * 0.26 - perp * 0.11, tip])
    head.set_fill(color, opacity=1.0)
    g.add(head)
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


class CosineSimilarity(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.num = None                 # what is in the numerator slot
        self.den = None                 # and the denominator

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
        self.stage_arrows()
        self.stage_dot()
        self.stage_lengths()
        self.stage_score()
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
    def make_eq(self, active=None, num=None, den=None, size=38):
        """cos θ = (a·b)/(|a|·|b|), as three pieces, the third a fraction.

        `active` is "cos", "num" or "den" — that piece goes gold and a size
        bigger. A slot holds its letters until a number is dragged into it."""
        n = num if num is not None else (self.num or NUM0)
        d = den if den is not None else (self.den or DEN0)
        n_done = (num is not None) or (self.num is not None)
        d_done = (den is not None) or (self.den is not None)

        def piece(s, done, is_active, base):
            if is_active:
                return txt(s, int(base * 1.14), GOLD, w=2.0)
            return txt(s, base, GOLD if done else DIM, w=2.0)

        nt = piece(n, n_done, active == "num", size)
        dt = piece(d, d_done, active == "den", size)
        bar = Line(LEFT * 0.5, RIGHT * 0.5, stroke_color=WHITE_, stroke_width=2.6)
        bar.set_width(max(nt.get_width(), dt.get_width()) + 0.22)
        frac = VGroup(nt, bar, dt).arrange(DOWN, buff=0.11)

        head = txt("cos θ", int(size * (1.14 if active == "cos" else 1.0)),
                   GOLD if active == "cos" else WHITE_, w=2.0)
        g = VGroup(head, txt("=", size, WHITE_, w=0.6), frac) \
            .arrange(RIGHT, buff=0.20)
        if g.get_width() > 4.5:
            g.set_width(4.5)
        return g.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats, extra=()):
        self.play(Transform(self.eq, self.make_eq(active)), *extra,
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, size, fly=3.0, settle=2.0):
        """Lift a number off the picture and drop it into its slot. The target
        is read off a freshly built equation, because the fraction re-widths
        every time either half changes."""
        kw = {"num": value} if slot == "num" else {"den": value}
        nxt = self.make_eq(active=slot, **kw)
        target = nxt[2][0 if slot == "num" else 2]
        flier = txt(value, size, GOLD, w=2.0).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        if slot == "num":
            self.num = value
        else:
            self.den = value
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    def show_ans(self, s, beats, color=WHITE_, size=32):
        new = txt(s, size, color, w=4.0).move_to(np.array([0, ANS_Y, 0]))
        if getattr(self, "ans", None) is None:
            self.ans = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(Transform(self.ans, new), run_time=self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("cos", 74, GOLD, w=4.6),
                     txt("is how AI compares", 30, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.26)
        big.move_to(np.array([0, 0.75, 0]))
        sub = txt("you learned it for triangles", 23, GREY, bold=False)
        sub.move_to(np.array([0, -0.35, 0]))
        self.add(big, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.ans = None
        self.pad_to(END_OPEN)

    # ==================================================================
    # two things become two arrows, and the angle between them is the answer
    # ==================================================================
    def stage_arrows(self):
        grid = VGroup()
        for i in range(GMAX + 1):
            grid.add(seg(P(i, 0), P(i, GMAX), FAINT, 1.6, 0.7))
            grid.add(seg(P(0, i), P(GMAX, i), FAINT, 1.6, 0.7))
        ax = VGroup(seg(P(0, 0), P(GMAX + 0.4, 0), GREY, 2.4, 0.8),
                    seg(P(0, 0), P(0, GMAX + 0.4), GREY, 2.4, 0.8))
        self.grid = VGroup(grid, ax)
        self.play(ShowCreation(grid), ShowCreation(ax), run_time=self.T(2))

        self.a = arrow(P(AX, AY), GOLD)
        self.la_ = txt("a", 30, GOLD, w=0.5).move_to(P(AX, AY)
                                                     + np.array([0.06, -0.30, 0]))
        self.play(ShowCreation(self.a), FadeIn(self.la_), run_time=self.T(2))
        self.say("AI turns everything it knows into arrows.", 2.5)

        self.b = arrow(P(BX, BY), SKY)
        self.lb_ = txt("b", 30, SKY, w=0.5).move_to(P(BX, BY)
                                                    + np.array([-0.26, 0.16, 0]))
        self.play(ShowCreation(self.b), FadeIn(self.lb_), run_time=self.T(2))
        self.say("two things. two arrows.", 2)

        r = GS * 1.35
        pts = [P(0, 0) + r * np.array([math.cos(t), math.sin(t), 0])
               for t in np.linspace(0, math.radians(THETA), 40)]
        self.arc = VMobject(stroke_color=WHITE_, stroke_width=3.4)
        self.arc.set_points_as_corners(pts)
        half = math.radians(THETA / 2)
        self.th = txt("θ", 28, WHITE_, w=0.5).move_to(
            P(0, 0) + (r + 0.30) * np.array([math.cos(half), math.sin(half), 0]))
        self.play(ShowCreation(self.arc), FadeIn(self.th),
                  Transform(self.eq, self.make_eq("cos")), run_time=self.T(2))
        self.say("how alike they are IS the angle between them.", 2.5)
        self.say("and nobody can measure that angle.", 2.5)
        self.pad_to(END_ARROWS)

    # ==================================================================
    # a · b — multiply the matching numbers and add. Drag it up.
    # ==================================================================
    def stage_dot(self):
        self.relight("num", 2, extra=[self.zoom.animate.set_value(0.95)])

        self.na = txt(f"({AX}, {AY})", 26, GOLD, w=1.4).move_to(
            P(AX, AY) + np.array([-0.10, 0.34, 0]))
        self.nb = txt(f"({BX}, {BY})", 26, SKY, w=1.4).move_to(
            P(BX, BY) + np.array([0.52, 0.06, 0]))
        self.play(FadeIn(self.na, scale=1.3), run_time=self.T(2))
        self.play(FadeIn(self.nb, scale=1.3), run_time=self.T(2))
        self.say("count them off the grid. that is all an arrow is.", 2.5)

        self.show_ans(f"{AX}×{BX} + {AY}×{BY}", 2.5, WHITE_)
        self.say("multiply the matching numbers, then add.", 2)
        self.show_ans(f"{AX*BX} + {AY*BY} = {DOTS}", 2, GOLD)
        self.drag_into(self.ans.get_center(), "num", DOTS, 30, fly=3, settle=2)
        self.pad_to(END_DOT)

    # ==================================================================
    # |a| · |b| — how long each arrow is. Drag that up too.
    # ==================================================================
    def stage_lengths(self):
        self.relight("den", 2, extra=[FadeOut(self.na), FadeOut(self.nb)])

        la = txt(LAS, 26, GOLD, w=0.6).move_to((P(0, 0) + P(AX, AY)) / 2
                                               + np.array([0, -0.32, 0]))
        lb = txt(LBS, 26, SKY, w=0.6).move_to((P(0, 0) + P(BX, BY)) / 2
                                              + np.array([-0.34, 0.06, 0]))
        self.play(FadeIn(la, scale=1.3), FadeIn(lb, scale=1.3),
                  run_time=self.T(2.5))
        self.say("each arrow is 5 long.", 2)

        self.show_ans(f"{LAS} × {LBS} = {DENS}", 2.5, GOLD)
        self.say("so the bottom is 25.", 2)
        self.lens = VGroup(la, lb)
        self.drag_into(self.ans.get_center(), "den", DENS, 30, fly=3, settle=2)
        self.pad_to(END_LEN)

    # ==================================================================
    # the score — and it goes back DOWN onto the angle nobody measured
    # ==================================================================
    def stage_score(self):
        self.relight("cos", 2, extra=[self.zoom.animate.set_value(0.93)])
        self.show_ans(f"{DOTS} ÷ {DENS} = {COSS}", 2.5, GOLD, size=36)

        half = math.radians(THETA / 2)
        # far enough out along the bisector to clear the θ label, which sits
        # at ~1.1 units — at 2.35 the score landed straight on top of it
        drop = P(0, 0) + (GS * 3.40) * np.array([math.cos(half),
                                                 math.sin(half), 0])
        flier = txt(COSS, 26, GOLD, w=1.0).move_to(self.ans.get_center())
        self.add(flier)
        self.play(flier.animate.move_to(drop).set_height(
            txt(COSS, 34).get_height()), run_time=self.T(3), rate_func=smooth)
        self.play(self.arc.animate.set_stroke(GOLD, 5.0), run_time=self.T(1.5))
        self.say("that is the score for this angle.", 2)

        # give the number a scale, or 0.6 means nothing
        self.play(FadeOut(self.grid), FadeOut(self.a), FadeOut(self.b),
                  FadeOut(self.la_), FadeOut(self.lb_), FadeOut(self.arc),
                  FadeOut(self.th), FadeOut(self.lens), FadeOut(flier),
                  run_time=self.T(2))
        bar = seg(np.array([-1.55, -0.55, 0]), np.array([1.55, -0.55, 0]),
                  GREY, 3.0, 0.8)
        z = txt("0", 24, GREY, w=0.4).move_to(np.array([-1.55, -0.95, 0]))
        o = txt("1", 24, GREY, w=0.4).move_to(np.array([1.55, -0.95, 0]))
        zl = txt("nothing in common", 20, GREY, bold=False, w=1.7)
        zl.move_to(np.array([-1.20, -1.35, 0]))
        ol = txt("the same", 20, GREY, bold=False, w=1.3)
        ol.move_to(np.array([1.30, -1.35, 0]))
        mark = Dot(np.array([-1.55 + 3.10 * float(COS), -0.55, 0]),
                   radius=0.11, fill_color=GOLD)
        val = txt(COSS, 30, GOLD, w=1.0).move_to(
            mark.get_center() + np.array([0, 0.36, 0]))
        self.scale_bar = VGroup(bar, z, o, zl, ol, mark, val)
        self.play(ShowCreation(bar), FadeIn(z), FadeIn(o), FadeIn(zl),
                  FadeIn(ol), FadeIn(mark, scale=2.0), FadeIn(val),
                  run_time=self.T(2.5))
        # the bar's own labels say what 0 and 1 mean, so the note does not
        # have to — it gets the one line that names the thing instead
        self.say("AI calls this cosine similarity.", 2.5, GOLD)
        self.pad_to(END_SCORE)

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
        l1.move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.5)
        l2.move_to(np.array([0, -0.65, 0]))
        self.play(FadeIn(l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)
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
