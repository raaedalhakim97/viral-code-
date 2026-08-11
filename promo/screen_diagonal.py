"""
screen_diagonal — a² + b² = c², and the number on the box. 40.0s.

    BPM=150 manimgl screen_diagonal.py ScreenDiagonal -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 2 OF "WHY DID WE LEARN THIS?" — same shell as sales_line.py: the
equation is the spine, it sits at the top from the first second to the last,
it starts empty, and every number is dragged into its slot off a picture.

        a²  +  b²  =  c²

WHAT MAKES THIS ONE WORK IS THAT c GOES THE OTHER WAY. a and b are measured
off the screen and dragged UP into the equation. c is worked out INSIDE the
equation and then dropped back DOWN onto the picture — because the diagonal
is the one length nobody ever measures. That is what an equation is for: you
put in what you can measure and it hands you what you cannot.

    a  ←  8      across the screen
    b  ←  6      up the screen
    c  →  10     dropped onto the diagonal

        8² + 6² = 64 + 36 = 100 = 10²

AND THE PAYOFF IS A THING EVERYONE HAS BOUGHT. Screens are sold by their
DIAGONAL — a "10-inch tablet" is 8 inches across and 6 inches up, and the 10
on the box is c. The convention dates to round CRT tubes, where the diagonal
was the only single number that described a circular screen, and it survived
because it is the one measurement that compares across aspect ratios:

    https://www.slashgear.com/1333864/tvs-measured-diagonally/
    https://www.bgr.com/2202051/why-is-screen-size-measured-diagonally/

THE NUMBERS ARE EXACT, NOT ROUNDED. 8 × 6 is 4:3, a real screen ratio — the
classic one — and 8² + 6² = 100 = 10² exactly, so nothing on screen is an
approximation. A 16:9 screen would have given 48 × 27 → 55.07, and a video
that has to say "approximately" in its payoff has lost.

VERIFIED AT IMPORT
    A² + B² == C²                exactly, in integers
    the ratio A:B is 4:3         a real aspect ratio, not one invented to fit
    C is a whole number          so the payoff needs no rounding

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from math import gcd

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_NAME, END_MEASURE, END_SOLVE, END_REVEAL = 24, 46, 64, 82
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
EQ_Y    = 2.44
ANS_Y   = 1.80
NOTE_Y  = -2.34

# the screen: 8 across, 6 up, so the diagonal is exactly 10
A, B = 8, 6
C = int(round((A * A + B * B) ** 0.5))

assert A * A + B * B == C * C, (A, B, C)
assert (A // gcd(A, B), B // gcd(A, B)) == (4, 3)      # a real aspect ratio
assert C == 10

AS_, BS_, CS_ = str(A), str(B), str(C)

# where the screen sits on stage
SW, SH = 3.00, 2.25                # 4:3, same as the real thing
SCX, SCY = 0.0, -0.30
BL = np.array([SCX - SW / 2, SCY - SH / 2, 0.0])
BR = np.array([SCX + SW / 2, SCY - SH / 2, 0.0])
TR = np.array([SCX + SW / 2, SCY + SH / 2, 0.0])
TL = np.array([SCX - SW / 2, SCY + SH / 2, 0.0])

BASE = ["a²", "+", "b²", "=", "c²"]
IDX_A, IDX_B, IDX_C = 0, 2, 4


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


class ScreenDiagonal(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
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
        self.stage_name()
        self.stage_measure()
        self.stage_solve()
        self.stage_reveal()
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
    def make_eq(self, active=None, also=None, size=44):
        fill = dict(self.filled)
        if also:
            fill.update(also)
        g = VGroup()
        for i, base in enumerate(BASE):
            s = fill.get(i, base)
            done = i in fill
            if i == active:
                col, sz = GOLD, int(size * 1.12)
            elif done:
                col, sz = GOLD, size
            elif i in (IDX_A, IDX_B, IDX_C):
                col, sz = DIM, size
            else:
                col, sz = WHITE_, size
            g.add(txt(s, sz, col, w=1.6))
        g.arrange(RIGHT, buff=0.15)
        if g.get_width() > 4.5:
            g.set_width(4.5)
        return g.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats, extra=()):
        self.play(Transform(self.eq, self.make_eq(active)), *extra,
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, shown, size,
                  fly=3.0, settle=2.0, extra=()):
        """Lift a measurement off the picture and drop it into its slot.

        The target comes off a freshly built equation, not the live one — the
        slots re-space whenever one of them changes width, so the flier has to
        land where the piece is ABOUT to be."""
        nxt = self.make_eq(active=slot, also={slot: shown})
        target = nxt[slot]
        flier = txt(value, size, GOLD, w=1.6).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height() * 0.72),
                  *extra, run_time=self.T(fly), rate_func=smooth)
        self.filled[slot] = shown
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    def drop_onto(self, source_point, target_point, value, size, beats=3.0):
        """The other direction: the equation hands a number back to the picture.
        c is the whole reason the formula exists — nobody measures a diagonal,
        so this is the only number in the video that travels downward."""
        flier = txt(value, int(size * 0.8), GOLD, w=1.6).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target_point)
                  .set_height(txt(value, size).get_height()),
                  run_time=self.T(beats), rate_func=smooth)
        return flier

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("a² + b² = c²", 56, GOLD, w=4.6)
        big.move_to(np.array([0, 0.95, 0]))
        q = VGroup(txt("they teach you this", 29, WHITE_, w=4.6),
                   txt("at school", 29, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, 0.05, 0]))
        sub = txt("you're about to realise what for", 23, GREY, bold=False)
        sub.move_to(np.array([0, -0.80, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # a, b, c — three sides of a thing you own.
    # ==================================================================
    def stage_name(self):
        self.frame_rect = VGroup(seg(BL, BR, GREY, 3.0), seg(BR, TR, GREY, 3.0),
                                 seg(TR, TL, GREY, 3.0), seg(TL, BL, GREY, 3.0))
        self.edge_a = seg(BL, BR, GREY, 3.0)
        self.edge_b = seg(BR, TR, GREY, 3.0)
        self.edge_c = seg(BL, TR, GREY, 3.0, 0.0)
        self.add(self.edge_c)
        self.play(ShowCreation(self.frame_rect), run_time=self.T(2))
        self.add(self.edge_a, self.edge_b)
        self.say("a screen. any screen you own.", 2)

        self.relight(IDX_A, 2,
                     extra=[self.edge_a.animate.set_stroke(GOLD, 6.0)])
        self.say("a is across.", 2)

        self.relight(IDX_B, 2,
                     extra=[self.edge_a.animate.set_stroke(GREY, 3.0),
                            self.edge_b.animate.set_stroke(GOLD, 6.0)])
        self.say("b is up.", 2)

        self.relight(IDX_C, 2,
                     extra=[self.edge_b.animate.set_stroke(GREY, 3.0),
                            self.edge_c.animate.set_stroke(GOLD, 4.0,
                                                           opacity=0.55)])
        self.say("c is corner to corner.", 2)
        self.pad_to(END_NAME)

    # ==================================================================
    # measure what you can, and drag it up into the equation.
    # ==================================================================
    def stage_measure(self):
        self.relight(IDX_A, 2,
                     extra=[self.edge_c.animate.set_stroke(GREY, 3.0,
                                                           opacity=0.35),
                            self.edge_a.animate.set_stroke(GOLD, 6.0),
                            self.zoom.animate.set_value(0.95)])
        lab_a = txt(AS_, 30, GOLD, w=0.8).move_to(
            (BL + BR) / 2 + np.array([0, -0.34, 0]))
        self.play(FadeIn(lab_a, scale=1.4), run_time=self.T(1.5))
        self.say(f"measure across. {AS_}.", 2)
        self.drag_into(lab_a.get_center(), IDX_A, AS_, f"{AS_}²", 30,
                       fly=3, settle=2)

        self.relight(IDX_B, 1.5,
                     extra=[self.edge_a.animate.set_stroke(GREY, 3.0),
                            self.edge_b.animate.set_stroke(GOLD, 6.0)])
        lab_b = txt(BS_, 30, GOLD, w=0.8).move_to(
            (BR + TR) / 2 + np.array([0.36, 0, 0]))
        self.play(FadeIn(lab_b, scale=1.4), run_time=self.T(1.5))
        self.say(f"measure up. {BS_}.", 2)
        self.drag_into(lab_b.get_center(), IDX_B, BS_, f"{BS_}²", 30,
                       fly=3, settle=2)

        self.labs = VGroup(lab_a, lab_b)
        self.say("that is everything you can reach a ruler to.", 1.5)
        self.pad_to(END_MEASURE)

    # ==================================================================
    # solve for c inside the equation.
    # ==================================================================
    def stage_solve(self):
        self.relight(IDX_C, 2,
                     extra=[self.edge_b.animate.set_stroke(GREY, 3.0),
                            self.zoom.animate.set_value(1.0)])

        self.arith = txt(f"{A*A} + {B*B}", 34, WHITE_, w=3.0)
        self.arith.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.arith), run_time=self.T(2.5))
        self.say(f"{AS_} squared is {A*A}. {BS_} squared is {B*B}.", 2.5)

        two = txt(f"{A*A} + {B*B} = {A*A + B*B}", 34, WHITE_, w=3.6)
        two.move_to(np.array([0, ANS_Y, 0]))
        self.play(Transform(self.arith, two), run_time=self.T(2.5))
        self.say(f"so c squared is {A*A + B*B}.", 2.5)

        three = txt(f"c = {CS_}", 38, GOLD, w=2.4)
        three.move_to(np.array([0, ANS_Y, 0]))
        self.play(Transform(self.arith, three), run_time=self.T(3))
        self.say(f"and c is {CS_}.", 3)
        self.pad_to(END_SOLVE)

    # ==================================================================
    # give it back to the picture. THAT is what the formula was for.
    # ==================================================================
    def stage_reveal(self):
        self.say("you never measured the diagonal.", 2.5,
                 extra=[self.zoom.animate.set_value(0.94)])

        mid = (BL + TR) / 2
        d = TR - BL
        n = np.array([-d[1], d[0], 0.0])
        n = n / np.linalg.norm(n)
        drop_at = mid + n * 0.36

        flier = self.drop_onto(self.arith.get_center(), drop_at,
                               CS_, 32, beats=3.5)
        self.play(self.edge_c.animate.set_stroke(GOLD, 6.0, opacity=1.0),
                  run_time=self.T(2))
        self.say("the equation handed it to you.", 2.5)

        box = txt(f'the box says {CS_}"', 30, GOLD, w=4.0)
        box.move_to(np.array([0, -1.98, 0]))
        self.play(FadeIn(box, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.boxlab = box
        self.flier = flier
        self.say("every screen is sold by its diagonal.", 3)
        self.pad_to(END_REVEAL)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
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
        self.pad_to(END_TAKE)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq),
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
