"""
net_vs_gross — every manager gets this wrong. 40.0s.

    BPM=150 manimgl net_vs_gross.py NetVsGross -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

BUILT TO THE SHORT-FORM HOOK RULES, not to a lecture plan:

    frame 1 shows the MISTAKE, already made, already crossed out —
    no title card, no build-up, no fade-in. The stake is on screen
    at t=0: "this costs you 95.24. every single invoice."

    the ANSWER lands by 0:05, not at the end. 38,095.24 hits the
    screen before any explanation, then pins to the top as
    "38,095.24  not  38,000" and holds the loop open all the way down.

    identity callout in the banner: EVERY MANAGER GETS THIS WRONG.

    second person, present tense, 4-7 words a line.

THE STORY. 40,000 comes in, tax already inside. You take 5% off — 2,000
— and book 38,000. But 5% of WHAT? Nobody ever charged 5% of 40,000.
The 5% came off YOUR price and was added on top.

THE SHAPE. Cut your price into 20 equal parts. The tax is one more part
exactly like them, on the end. So what came in is 21 parts, not 20.

        [][][][][][][][][][][][][][][][][][][][]  []   =  40,000
         \___________ 20 = yours ____________/    1 = tax

        one part  =  40,000 ÷ 21  =  1,904.76      <- the whole tax
        yours     =  20 parts     =  38,095.24
                     38,095.24 + 1,904.76 = 40,000.00

THE STAKE. Subtracting hands over 2,000 where 1,904.76 was owed: 95.24
gone per invoice, 9,523.81 across a hundred of them.

THE RULE: 5% -> 21 parts. 10% -> 11. 20% -> 6. Always one more.

VERIFIED AT IMPORT
    every figure is exact Fraction arithmetic — nothing typed in by hand
    one part really is 5% OF THE NET, so the slices agree with ÷ 1.05
    38,095.24 + 1,904.76 == 40,000.00, at cent precision, exactly as shown
    95.24 per invoice, 9,523.81 per hundred, 2,380.95 on a million
    the 5/10/20% -> 21/11/6 rule is checked against 1/s == r/(1+r)

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_HOOK, END_ANSWER = 5, 14
END_SETUP, END_QUESTION = 26, 34
END_BAR, END_NUMBERS = 62, 80
END_TAKE, END_SHARE = 88, 92

SERIES = "EVERY MANAGER GETS THIS WRONG"

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
EQ_Y   = 3.08
WORK_Y = 2.30
NOTE_Y = -3.30
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
PAID = Fraction(40000)
RATE = Fraction(5, 100)

PARTS_NET = int(1 / RATE)                 # 20 parts make the price
SLICES = PARTS_NET + 1                    # 21 parts make what came in
assert PARTS_NET == 20 and SLICES == 21

ONE = PAID / SLICES                       # one part — and that IS the tax
NET = ONE * PARTS_NET
assert ONE == Fraction(40000, 21)
assert NET == Fraction(800000, 21)
assert NET + ONE == PAID
assert ONE / NET == RATE                  # one part really is 5% OF THE NET
assert NET * (1 + RATE) == PAID           # so the slices agree with ÷ 1.05

ONE_2DP, NET_2DP = round(float(ONE), 2), round(float(NET), 2)
assert ONE_2DP == 1904.76 and NET_2DP == 38095.24
assert NET_2DP + ONE_2DP == 40000.00      # the two on-screen numbers add up

WRONG_TAX = PAID * RATE
OVERPAID = WRONG_TAX - ONE
assert WRONG_TAX == 2000 and PAID - WRONG_TAX == 38000
assert OVERPAID == Fraction(2000, 21)
assert round(float(OVERPAID), 2) == 95.24
assert round(float(OVERPAID * 100), 2) == 9523.81      # across 100 invoices

_M = Fraction(1000000)
assert round(float(_M * RATE - _M / SLICES), 2) == 2380.95

for _pct, _want in ((5, 21), (10, 11), (20, 6)):
    _r = Fraction(_pct, 100)
    _s = int(1 / _r) + 1
    assert _s == _want
    assert Fraction(1, _s) == _r / (1 + _r)

# ------------------------------------------------------------------ layout
PITCH, CELL_W, CELL_H = 0.20, 0.185, 0.58
BAR_Y = 0.00
HALF = CELL_W / 2


def slot(k):
    return (k - 10) * PITCH


GOLD_X0, GOLD_X1 = slot(0) - HALF, slot(PARTS_NET - 1) + HALF
FULL_X0, FULL_X1 = slot(0) - HALF, slot(SLICES - 1) + HALF
GOLD_MID = (GOLD_X0 + GOLD_X1) / 2
ROSE_X = slot(SLICES - 1)
TOP_Y, BOT_Y = BAR_Y + CELL_H / 2 + 0.17, BAR_Y - CELL_H / 2 - 0.17
LAB_TOP = BAR_Y + CELL_H / 2 + 0.52
LAB_BOT = BAR_Y - CELL_H / 2 - 0.52
FVAL_Y = BAR_Y - CELL_H / 2 - 1.10
ROSE_LAB_X, ROSE_LAB_W = 1.80, 1.28        # keeps 1,904.76 off the right edge
LIFT = 0.22                                # rose cell steps out of the bar
assert FULL_X1 < 2.45
assert ROSE_LAB_X + ROSE_LAB_W / 2 < 2.48
assert BAR_Y + CELL_H / 2 + LIFT < LAB_TOP - 0.16


# ------------------------------------------------------------------ drawing
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


def bracket(x0, x1, y, color, down=True):
    d = -0.13 if down else 0.13
    return VGroup(
        seg(np.array([x0, y, 0]), np.array([x1, y, 0]), color, 2.0),
        seg(np.array([x0, y, 0]), np.array([x0, y + d, 0]), color, 2.0),
        seg(np.array([x1, y, 0]), np.array([x1, y + d, 0]), color, 2.0))


def cell(k, color, fill=0.20):
    return Rectangle(width=CELL_W, height=CELL_H, stroke_color=color,
                     stroke_width=1.6, fill_color=color,
                     fill_opacity=fill).move_to(np.array([slot(k), BAR_Y, 0]))


def cross_at(x, y, color, d=0.19, wid=5.0):
    return VGroup(
        seg(np.array([x - d, y - d, 0]), np.array([x + d, y + d, 0]), color, wid),
        seg(np.array([x - d, y + d, 0]), np.array([x + d, y - d, 0]), color, wid))


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


class NetVsGross(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.work = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.hook()
        self.stage_answer()
        self.stage_setup()
        self.stage_question()
        self.stage_bar()
        self.stage_numbers()
        self.takeaway("5% tax means 21 parts.",
                      "10% means 11.  20% means 6.")
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

    def say(self, s, beats=2, color=WHITE_, size=26):
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def set_work(self, s, color, beats=2.5, size=23):
        new = txt(s, size, color, bold=False, w=4.6)
        new.move_to(np.array([0, WORK_Y, 0]))
        if self.work is None:
            self.work = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            old, self.work = self.work, new
            self.play(FadeOut(old), FadeIn(new), run_time=self.T(beats))
            self.work = new

    # ------------------------------------------------------------------
    def hook(self):
        """Frame 1 is the mistake, already made and already crossed out."""
        self.title = txt(SERIES, 20, ROSE, w=4.4)
        self.title.move_to(np.array([0, 3.62, 0]))

        sum_ = txt("40,000  −  5%", 32, GREY, w=3.6)
        sum_.move_to(np.array([0, 1.52, 0]))

        bad = txt("38,000", 58, ROSE, w=2.9)
        bad.move_to(np.array([-0.30, 0.66, 0]))
        strike = seg(bad.get_left() + np.array([-0.12, 0, 0]),
                     bad.get_right() + np.array([0.12, 0, 0]), ROSE, 4.5)
        x = cross_at(1.62, 0.66, ROSE, 0.24, 6.0)

        l1 = txt("this costs you 95.24", 30, WHITE_, w=4.4)
        l1.move_to(np.array([0, -0.55, 0]))
        l2 = txt("every single invoice", 27, ROSE, w=4.0)
        l2.move_to(np.array([0, -1.30, 0]))

        self.hookgrp = VGroup(sum_, bad, strike, x, l1, l2)
        self.add(self.title, self.hookgrp)
        self.wait(self.T(END_HOOK))

    # ==================================================================
    def stage_answer(self):
        big = txt("38,095.24", 54, GOLD, w=4.3)
        big.move_to(np.array([0, 0.55, 0]))
        self.play(FadeOut(self.hookgrp), FadeIn(big, scale=1.15),
                  run_time=self.T(2.5))
        self.say("that's what you actually keep.", 2.5, GOLD)

        self.eq = txt("38,095.24   not   38,000", 25, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(Transform(big, self.eq), run_time=self.T(2.5))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_ANSWER)

    # ==================================================================
    def stage_setup(self):
        # the sum runs in the CENTRE of the frame, not in the work line —
        # otherwise the stage sits empty from the answer pin until the bar
        # arrives, which is the stretch where people scroll.
        c1 = txt("40,000", 40, WHITE_, w=2.0)
        c2 = txt("−   2,000", 40, ROSE, w=2.6)
        c3 = txt("38,000", 46, ROSE, w=2.3)
        for m, y in ((c1, 1.15), (c2, 0.42), (c3, -0.48)):
            m.move_to(np.array([0, y, 0]))
            m.align_to(np.array([1.05, 0, 0]), RIGHT)
        rule = seg(np.array([-1.25, -0.02, 0]), np.array([1.15, -0.02, 0]),
                   GREY, 2.4)
        x = cross_at(1.72, -0.48, ROSE, 0.21, 5.5)
        self.sum_blk = VGroup(c1, c2, c3, rule, x)

        self.play(FadeIn(c1), run_time=self.T(1.5))
        self.say("40,000 comes in. tax already inside.", 2)
        self.play(FadeIn(c2), run_time=self.T(1.5))
        self.say("so you take 5% off. everyone does.", 2, GREY)
        self.play(FadeIn(rule), FadeIn(c3), ShowCreation(x), run_time=self.T(2))
        self.say("and you book 38,000.", 2, ROSE)
        self.pad_to(END_SETUP)

    # ==================================================================
    def stage_question(self):
        self.say("5% of WHAT?", 3, SKY)
        self.set_work("nobody charged 5% of 40,000", SKY, 2.5)
        self.pad_to(END_QUESTION)

    # ==================================================================
    def stage_bar(self):
        self.play(FadeOut(self.sum_blk), run_time=self.T(1.5))
        self.say("the 5% came off YOUR price.", 2, GOLD)

        self.gold = VGroup(*[cell(k, GOLD) for k in range(PARTS_NET)])
        self.play(FadeIn(self.gold, lag_ratio=0.05), run_time=self.T(3))

        self.gbr = bracket(GOLD_X0, GOLD_X1, TOP_Y, GOLD, down=True)
        self.glab = txt("YOUR PRICE", 24, GOLD, w=2.4)
        self.glab.move_to(np.array([GOLD_MID, LAB_TOP, 0]))
        self.play(ShowCreation(self.gbr), FadeIn(self.glab), run_time=self.T(1.5))
        self.set_work("cut it into 20 equal parts", GOLD, 2.5)

        self.say("the tax is one more part.", 2.5, ROSE)
        self.rose = cell(PARTS_NET, ROSE, 0.80)
        self.rose.set_stroke(ROSE, 2.6)
        self.rlab = txt("+ 5%", 22, ROSE, w=1.05)
        self.rlab.move_to(np.array([ROSE_LAB_X, LAB_TOP, 0]))
        self.play(FadeIn(self.rose, shift=0.30 * LEFT), run_time=self.T(2))
        self.play(FadeIn(self.rlab), run_time=self.T(1.5))

        self.fbr = bracket(FULL_X0, FULL_X1, BOT_Y, WHITE_, down=False)
        self.flab = txt("what came in", 22, WHITE_, bold=False, w=2.6)
        self.flab.move_to(np.array([0, LAB_BOT, 0]))
        self.fval = txt("40,000", 34, WHITE_, w=2.2)
        self.fval.move_to(np.array([0, FVAL_Y, 0]))
        self.play(ShowCreation(self.fbr), FadeIn(self.flab), run_time=self.T(2))
        self.play(FadeIn(self.fval), run_time=self.T(1.5))

        self.play(self.rose.animate.shift(LIFT * UP), run_time=self.T(1.5))
        self.set_work("20 yours  +  1 tax  =  21 parts", SKY, 2.5)
        self.say("twenty-one. not twenty.", 2.5, GOLD)
        self.pad_to(END_BAR)

    # ==================================================================
    def stage_numbers(self):
        self.set_work("40,000 ÷ 21  =  1,904.76", ROSE, 2.5)
        newr = txt("1,904.76", 22, ROSE, w=ROSE_LAB_W)
        newr.move_to(np.array([ROSE_LAB_X, LAB_TOP, 0]))
        self.play(Transform(self.rlab, newr), run_time=self.T(1.5))

        self.set_work("the other 20 are yours", GOLD, 2.5)
        newg = txt("38,095.24", 28, GOLD, w=2.4)
        newg.move_to(np.array([GOLD_MID, LAB_TOP, 0]))
        self.play(Transform(self.glab, newg), run_time=self.T(1.5))
        self.say("38,095.24 + 1,904.76 = 40,000.00", 2.5, GREEN)

        self.set_work("you handed over 2,000. he was owed 1,904.76.", ROSE, 2.5)
        self.say("95.24 gone. × 100 invoices = 9,523.81.", 2.5, ROSE)
        self.pad_to(END_NUMBERS)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.5).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to whoever", 27, WHITE_, w=4.5)
        s2 = txt("signs off your invoices", 27, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.eq), FadeOut(self.title),
                  run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
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
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(1.5))
