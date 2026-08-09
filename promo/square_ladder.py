"""
square_ladder — the formula you memorised, drawn as one square. 28.8s.

    BPM=150 manimgl square_ladder.py SquareLadder -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

ONE PICTURE CARRIES FIVE RUNGS.  Sister video to circle_ladder.py, and built
the same way: nothing is ever added to the picture, only relabelled.

A square of side a + b, cut once across and once down. Four pieces:

    a·a        a·b
    a·b        b·b

    1   one square, side a + b                    its area is (a+b)²
    2   cut it — four pieces, nothing else        a² + ab + ab + b²
    3   the two rectangles are congruent          (a+b)² = a² + 2ab + b²
    4   drop them and the square has a hole       (a+b)² ≠ a² + b²
    5   let b shrink, call it h                   (x+h)² = x² + 2xh + h²
                                                  d(x²)/dx = 2x

Rung 3 is the whole point: the 2ab nobody could explain is TWO IDENTICAL
RECTANGLES, and rung 3 proves they are identical by rotating one onto the
other. Rung 5 is the same square with b shrunk to a sliver — the corner h²
becomes a speck, the growth is the two strips, and the derivative of x² falls
out of a picture a fourteen-year-old already knows.

VERIFIED AT IMPORT
    the four regions tile the square exactly, across 200 split fractions
    (a+b)² == a² + 2ab + b² across 2000 random pairs
    (x+h)² − x² == 2xh + h² exactly
    ((x+h)² − x²)/h → 2x as h → 0

manimgl traps, all silent:
    Text -> fill_color=   Rectangle -> set_fill()   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    an updater that hard-codes opacity fights FadeIn and every
    .animate.set_opacity() — drive opacity from a ValueTracker it reads
    a position updater must NOT be attached during ShowCreation: it overwrites
    the partial draw every frame
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 72

END_OPEN = 4
END_R1, END_R2, END_R3, END_R4, END_R5 = 14, 26, 36, 46, 60
END_TAKE = 64

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"
LEAF   = "#A3BE8C"

FRAME_H = 9.0
LINE_Y  = -2.05
EQ_Y    = 2.55
NOTE_Y  = -2.30

SIDE = 3.0                  # the square, in scene units
OX, OY = 0.0, -0.15         # its centre
F0 = 0.62                   # a / (a + b) to start
F1 = 0.90                   # after b shrinks to h

FILL_COLOR = [GOLD, COOL, COOL, LEAF]
FILL_OP    = [0.30, 0.42, 0.42, 0.38]


def geom(f):
    """Bottom-left corner, then the lengths of a and b on screen."""
    bl = np.array([OX - SIDE / 2, OY - SIDE / 2, 0.0])
    return bl, f * SIDE, (1.0 - f) * SIDE


def region(f, i):
    """Centre, width, height of piece i.  0: a²  1,2: ab  3: b²"""
    bl, ax, bx = geom(f)
    if i == 0:
        return bl + np.array([ax / 2, ax / 2, 0]), ax, ax
    if i == 1:
        return bl + np.array([ax + bx / 2, ax / 2, 0]), bx, ax
    if i == 2:
        return bl + np.array([ax / 2, ax + bx / 2, 0]), ax, bx
    return bl + np.array([ax + bx / 2, ax + bx / 2, 0]), bx, bx


# ---------------------------------------------------------------- verified
for _f in np.linspace(0.05, 0.95, 200):            # the pieces tile the square
    _area = sum(region(_f, _i)[1] * region(_f, _i)[2] for _i in range(4))
    assert abs(_area - SIDE ** 2) < 1e-9, _f
    assert abs(region(_f, 1)[1] * region(_f, 1)[2]
               - region(_f, 2)[1] * region(_f, 2)[2]) < 1e-12   # the two ab's

_rng = np.random.default_rng(7)
_a, _b = _rng.uniform(0.1, 40, 2000), _rng.uniform(0.1, 40, 2000)
assert np.allclose((_a + _b) ** 2, _a ** 2 + 2 * _a * _b + _b ** 2, rtol=1e-12)
assert not np.allclose((_a + _b) ** 2, _a ** 2 + _b ** 2)       # the mistake

# the growth identity, in exact integer arithmetic — in float64 the subtraction
# (x+h)² − x² loses ~1e-14 to cancellation and would only prove the rounding
for _x in range(1, 40):                                         # the two strips
    for _h in range(1, 40):                                     # plus the corner
        assert (_x + _h) ** 2 - _x ** 2 == 2 * _x * _h + _h ** 2
_x, _h = 7.0, 1e-6                                              # the derivative
assert abs(((_x + _h) ** 2 - _x ** 2) / _h - 2 * _x) < 1e-4


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def frac(num, den, size=28, color=WHITE_):
    """A horizontal fraction, typeset by hand — there is no LaTeX here."""
    n = txt(num, size, color, w=1.9)
    d = txt(den, size, color, w=1.9)
    bar = Line(LEFT * 0.5, RIGHT * 0.5, stroke_color=color, stroke_width=2.4)
    bar.set_width(max(n.get_width(), d.get_width()) + 0.16)
    return VGroup(n, bar, d).arrange(DOWN, buff=0.09)


def eqn(*parts, size=30, color=WHITE_, w=4.5):
    g = VGroup(*[p if isinstance(p, VMobject) else txt(p, size, color, w=3.4)
                 for p in parts]).arrange(RIGHT, buff=0.16)
    if g.get_width() > w:
        g.set_width(w)
    return g


def seg(a, b, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners([a, b])
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


class SquareLadder(Scene):
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

        self.frac_t = ValueTracker(F0)
        self.op = [ValueTracker(0.0) for _ in range(4)]
        self.cut_op = ValueTracker(0.0)
        self.lab_op = ValueTracker(0.0)

        self.open_card()
        self.rung1()
        self.rung2()
        self.rung3()
        self.rung4()
        self.rung5()
        self.takeaway("You memorised this in school.",
                      "Nobody showed you it was a square.")
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
        """`extra` rides along on the same play, so a line and the thing it is
        pointing at land on the same beat instead of one beat apart."""
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

    def show_eq(self, s, beats=2, color=WHITE_, size=30):
        """The dancing equation — it pulses on every beat for the whole video."""
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
        big = txt("(a + b)² = a² + 2ab + b²", 36, WHITE_, w=4.7)
        big.move_to(np.array([0, 0.85, 0]))
        sub = txt("where does the 2ab come from?", 24, GOLD, bold=False)
        sub.move_to(np.array([0, 0.12, 0]))
        self.add(big, sub)
        self.wait(self.T(3))
        self.title = txt("ONE SQUARE, FIVE EQUATIONS", 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.play(FadeOut(big), FadeOut(sub), FadeIn(self.title),
                  run_time=self.T(1))
        self.pad_to(END_OPEN)

    # ==================================================================
    # 1 — one square.
    # ==================================================================
    def rung1(self):
        self.show_eq("(a + b)²", 2)

        self.outer = Square(side_length=SIDE, stroke_color=WHITE_, stroke_width=3.2)
        self.outer.set_fill(BLACK, opacity=0).move_to(np.array([OX, OY, 0]))
        self.play(ShowCreation(self.outer), run_time=self.T(2))
        self.say("one square. its side is a + b.", 2)

        self.lab_a = txt("a", 26, GOLD, w=0.4)
        self.lab_b = txt("b", 26, LEAF, w=0.4)
        for m, i in ((self.lab_a, 0), (self.lab_b, 1)):
            m.add_updater(lambda x, i=i: self.place_edge(x, i))
            m.set_opacity(0)
        self.add(self.lab_a, self.lab_b)
        self.play(self.lab_op.animate.set_value(1.0), run_time=self.T(2))
        self.say("the whole area is (a + b)²", 2)
        self.pad_to(END_R1)

    def place_edge(self, m, which):
        bl, ax, bx = geom(self.frac_t.get_value())
        x = ax / 2 if which == 0 else ax + bx / 2
        m.move_to(bl + np.array([x, -0.34, 0]))
        m.set_opacity(self.lab_op.get_value())

    # ==================================================================
    # 2 — cut it.  Four pieces, and there is nothing else in the square.
    # ==================================================================
    def rung2(self):
        self.show_eq("a² + ab + ab + b²", 2)

        self.fills = VGroup()
        for i in range(4):
            c, w, h = region(F0, i)
            r = Rectangle(width=w, height=h, stroke_width=0).move_to(c)
            r.add_updater(lambda m, i=i: self.place_fill(m, i))
            self.fills.add(r)
        self.cuts = VGroup(seg(ORIGIN, RIGHT, WHITE_, 2.4), seg(ORIGIN, RIGHT, WHITE_, 2.4))
        for j in range(2):
            self.cuts[j].add_updater(lambda m, j=j: self.place_cut(m, j))
        self.add(self.fills, self.cuts)
        self.bring_to_back(self.fills)

        self.play(self.cut_op.animate.set_value(0.85), run_time=self.T(2))
        self.say("cut it once across, once down", 2)

        names = ["a²", "ab", "ab", "b²"]
        self.plabs = VGroup()
        for i, n in enumerate(names):
            lab = txt(n, 26, WHITE_, w=0.9)
            lab.add_updater(lambda m, i=i: m.move_to(region(self.frac_t.get_value(), i)[0]))
            self.plabs.add(lab)
            self.play(self.op[i].animate.set_value(FILL_OP[i]),
                      FadeIn(lab), run_time=self.T(1))
        self.say("four pieces. that is the whole formula.", 2)
        self.pad_to(END_R2)

    def place_fill(self, m, i):
        c, w, h = region(self.frac_t.get_value(), i)
        m.set_width(max(w, 1e-3), stretch=True)
        m.set_height(max(h, 1e-3), stretch=True)
        m.move_to(c)
        m.set_fill(FILL_COLOR[i], opacity=self.op[i].get_value())

    def place_cut(self, m, j):
        bl, ax, bx = geom(self.frac_t.get_value())
        if j == 0:      # the vertical cut
            m.set_points_as_corners([bl + np.array([ax, 0, 0]),
                                     bl + np.array([ax, SIDE, 0])])
        else:           # the horizontal cut
            m.set_points_as_corners([bl + np.array([0, ax, 0]),
                                     bl + np.array([SIDE, ax, 0])])
        m.set_stroke(WHITE_, 2.4, opacity=self.cut_op.get_value())

    # ==================================================================
    # 3 — the two rectangles are the SAME rectangle.  Proved, not asserted.
    # ==================================================================
    def rung3(self):
        self.show_eq("(a + b)² = a² + 2ab + b²", 2)
        self.say("those two rectangles are identical", 2)

        # rotate a copy of the top-left one onto the bottom-right one
        c2, w2, h2 = region(F0, 2)
        c1, _, _ = region(F0, 1)
        ghost = Rectangle(width=w2, height=h2, stroke_color=GOLD, stroke_width=4.0)
        ghost.set_fill(GOLD, opacity=0.16).move_to(c2)
        self.add(ghost)
        self.play(ghost.animate.rotate(PI / 2).move_to(c1),
                  run_time=self.T(2), rate_func=smooth)
        self.say("same rectangle, twice — there is your 2ab", 2, GOLD)
        self.play(FadeOut(ghost), run_time=self.T(2))
        self.pad_to(END_R3)

    # ==================================================================
    # 4 — the mistake, shown as a hole.
    # ==================================================================
    def rung4(self):
        self.show_eq("(a + b)² ≠ a² + b²", 2, GOLD)
        self.say("this is the mistake everyone makes", 2)
        self.play(self.op[1].animate.set_value(0.0),
                  self.op[2].animate.set_value(0.0),
                  FadeOut(self.plabs[1]), FadeOut(self.plabs[2]),
                  run_time=self.T(2))
        self.say("leave out the 2ab and the square has a hole", 2, GOLD)
        self.play(self.op[1].animate.set_value(FILL_OP[1]),
                  self.op[2].animate.set_value(FILL_OP[2]),
                  FadeIn(self.plabs[1]), FadeIn(self.plabs[2]),
                  run_time=self.T(2))
        self.pad_to(END_R4)

    # ==================================================================
    # 5 — same square, b shrunk to a sliver.  That is the derivative.
    # ==================================================================
    def rung5(self):
        # rename, and drop the piece labels: at F1 the thin pieces have no room
        for m in self.plabs:
            m.clear_updaters()
        new_a = txt("x", 26, GOLD, w=0.4).move_to(self.lab_a.get_center())
        new_b = txt("h", 26, LEAF, w=0.4).move_to(self.lab_b.get_center())
        self.play(*[FadeOut(m) for m in self.plabs],
                  Transform(self.lab_a, new_a), Transform(self.lab_b, new_b),
                  run_time=self.T(2))
        self.say("same square. call them x and h.", 1.5)

        self.show_eq("(x + h)² = x² + 2xh + h²", 2)
        self.play(self.frac_t.animate.set_value(F1),
                  run_time=self.T(2.5), rate_func=smooth)
        self.say("now let h get small", 1.5)

        c3, w3, _ = region(F1, 3)
        call = txt("h²", 24, LEAF, w=0.6).move_to(c3 + np.array([-0.75, 0.62, 0]))
        lead = seg(call.get_center() + np.array([0.22, -0.14, 0]),
                   c3 + np.array([-0.06, 0.02, 0]), LEAF, 1.8, 0.8)
        # light the speck up as it is named — at F1 it is 0.3 units across and
        # at its normal fill it is invisible, which defeats the whole callout
        self.play(FadeIn(call), ShowCreation(lead),
                  self.op[3].animate.set_value(0.85), run_time=self.T(1.5))
        self.say("the corner is a speck. the growth is 2xh.", 1, GOLD,
                 extra=[self.op[1].animate.set_value(0.78),
                        self.op[2].animate.set_value(0.78)])

        self.show_eq(eqn(frac("d(x²)", "dx", 26, GOLD), txt("= 2x", 30, GOLD, w=1.4)),
                     2, GOLD)
        self.pad_to(END_R5)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        # the derivative STAYS. It arrives on the last beat of rung 5, and if
        # the takeaway cleared it too the payoff would hold for a third of a
        # second — it now sits over the closing lines for seven beats.
        keep = (self.clock, self.title, self.eq)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None
        l1 = txt(a, 28, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 26, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(END_TAKE)
        self.eq.clear_updaters()
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq),
                  FadeOut(self.title), run_time=self.T(1))
        self.eq = None

    def signature(self):
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
