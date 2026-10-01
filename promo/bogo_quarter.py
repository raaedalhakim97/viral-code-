"""
bogo_quarter — "buy one get one 50% off" is 25% off. 40.0s.

    BPM=150 manimgl bogo_quarter.py BogoQuarter -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

Same build as net_vs_gross.py and percent_back.py: frame 1 is the mistake
already made and already crossed out, the answer lands by 0:05 and pins to
the top, and the shape does the explaining. Different shape though — two
separate items rather than one pile being cut.

THE TRICK. The sign says fifty. Two items at 20 each:

        pay 20 + 10  =  30        full price 40
        saved 10 of 40            = a quarter, not a half

THE DOUBT. Half off WHAT? Half of one item, not half of your basket.

THE SHAPE. Cut each item into four. Two items is eight quarters. The deal
removes two of them — the right half of the second item. Two out of eight
is countable on screen, and it is 25%.

THE PAYOFF, and the reason this one is worth posting: rank the offers and
the sign with the biggest number on it comes LAST.

        buy one get one FREE   ->  50%
        3 for 2                ->  33.3%
        buy one get one 50%    ->  25%      <- the one shouting "50"

VERIFIED AT IMPORT
    every figure is exact Fraction arithmetic — nothing typed in by hand
    BOGO-half-price is exactly 1/4 off, 3-for-2 exactly 1/3, BOGOF exactly 1/2
    the ranking is asserted, so the payoff cannot silently invert
    the saving is checked to be price-independent, at 3, 7, 19 and 250
    two cells of eight is checked to equal the headline fraction
    the cells are asserted to fit the platform safe box

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
END_BAR, END_TABLE = 62, 80
END_TAKE, END_SHARE = 88, 92

SERIES = "EVERY SHOPPER FALLS FOR THIS"

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
NOTE_Y = -2.36
LINE_Y = -2.05

SAFE_X, SAFE_BOT = 1.68, -2.58
assert NOTE_Y - 0.20 >= SAFE_BOT

# ------------------------------------------------------------------ numbers
PRICE = Fraction(20)
ITEMS = 2
FULL = PRICE * ITEMS                       # 40
PAID = PRICE + PRICE / 2                   # 30 — one full, one half
SAVED = FULL - PAID                        # 10
assert (FULL, PAID, SAVED) == (40, 30, 10)

BOGO_HALF = SAVED / FULL                   # the headline
THREE_FOR_TWO = 1 - Fraction(2, 3)
BOGO_FREE = 1 - Fraction(PRICE, PRICE * 2)
assert BOGO_HALF == Fraction(1, 4)         # exactly 25%
assert THREE_FOR_TWO == Fraction(1, 3)     # exactly 33.3%
assert BOGO_FREE == Fraction(1, 2)         # exactly 50%

# the payoff: the loudest sign is the worst deal
assert BOGO_HALF < THREE_FOR_TWO < BOGO_FREE

# and none of it depends on the price
for _p in (3, 7, 19, 250):
    _q = Fraction(_p)
    assert (_q / 2) / (2 * _q) == Fraction(1, 4)

CELLS_PER_ITEM = 4
CELLS = ITEMS * CELLS_PER_ITEM             # 8 quarters on screen
GONE = CELLS // 4                          # the deal removes 2 of them
assert CELLS == 8 and GONE == 2
assert Fraction(GONE, CELLS) == BOGO_HALF  # the picture equals the claim

# short labels: at the width the two columns need, the long wording
# collided with the percentage
TABLE = [("buy 1 get 1 FREE", "50%", GREEN),
         ("3 for 2", "33%", SKY),
         ("buy 1 get 1 half", "25%", ROSE)]
LAB_W, PCT_W, COL_L, COL_R = 1.80, 0.86, -1.52, 1.52
assert COL_L + LAB_W < COL_R - PCT_W        # the columns cannot touch

# ------------------------------------------------------------------ layout
PITCH, CW, CH = 0.36, 0.32, 1.40
GROUP_GAP = 0.22
BAR_Y = 0.45
X0 = -1.55                                  # left edge of cell 0


def cell_left(k):
    return X0 + k * PITCH + (GROUP_GAP if k >= CELLS_PER_ITEM else 0.0)


assert cell_left(CELLS - 1) + CW <= SAFE_X
assert X0 >= -SAFE_X
VAL_Y = BAR_Y - CH / 2 - 0.62
GRP_Y = BAR_Y + CH / 2 + 0.34
assert BAR_Y + CH / 2 + 0.60 < WORK_Y - 0.16
assert VAL_Y - 0.28 > NOTE_Y + 0.20


def cell(k, color, fill=0.30):
    r = Rectangle(width=CW, height=CH, stroke_color=color, stroke_width=2.0,
                  fill_color=color, fill_opacity=fill)
    r.move_to(np.array([cell_left(k) + CW / 2, BAR_Y, 0]))
    return r


def hole(k):
    r = Rectangle(width=CW, height=CH, stroke_color=ROSE, stroke_width=3.0,
                  fill_color=ROSE, fill_opacity=0.22)
    r.move_to(np.array([cell_left(k) + CW / 2, BAR_Y, 0]))
    return r


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=2 * SAFE_X - 0.15):
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


class BogoQuarter(Scene):
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
        self.stage_cells()
        self.stage_table()
        self.takeaway("Half off one isn't half off two.",
                      "The 3-for-2 beats it.")
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

    def say(self, s, beats=2, color=WHITE_, size=25):
        new = txt(s, size, color, bold=False)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def set_work(self, s, color, beats=2.5, size=23):
        new = txt(s, size, color, bold=False, w=4.3)
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

        sign = txt("BUY ONE GET ONE 50% OFF", 27, GREY, w=3.9)
        sign.move_to(np.array([0, 1.58, 0]))

        bad = txt("50% off", 52, ROSE, w=2.7)
        bad.move_to(np.array([-0.38, 0.72, 0]))
        strike = seg(bad.get_left() + np.array([-0.12, 0, 0]),
                     bad.get_right() + np.array([0.12, 0, 0]), ROSE, 4.5)
        x = cross_at(1.42, 0.72, ROSE, 0.24, 6.0)

        l1 = txt("it's twenty-five", 32, WHITE_)
        l1.move_to(np.array([0, -0.50, 0]))
        l2 = txt("and 3-for-2 beats it", 27, ROSE, w=2 * SAFE_X - 0.30)
        l2.move_to(np.array([0, -1.25, 0]))

        self.hookgrp = VGroup(sign, bad, strike, x, l1, l2)
        self.add(self.title, self.hookgrp)
        self.wait(self.T(END_HOOK))

    # ==================================================================
    def stage_answer(self):
        big = txt("25%", 62, GOLD, w=2.4)
        big.move_to(np.array([0, 0.55, 0]))
        self.play(FadeOut(self.hookgrp), FadeIn(big, scale=1.15),
                  run_time=self.T(2.5))
        self.say("that's what you actually save.", 2.5, GOLD)

        self.eq = txt("25%   not   50%", 26, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(Transform(big, self.eq), run_time=self.T(2.5))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_ANSWER)

    # ==================================================================
    def stage_setup(self):
        # the sum runs in the CENTRE, not the work line, so the stage is
        # never empty between the answer pinning and the cells arriving
        c1 = txt("two items          40", 32, WHITE_, w=3.1)
        c2 = txt("pay 20 + 10        30", 32, ROSE, w=3.1)
        c3 = txt("saved              10", 32, GOLD, w=3.1)
        for m, y in ((c1, 1.15), (c2, 0.40), (c3, -0.35)):
            m.move_to(np.array([0, y, 0]))
        self.sum_blk = VGroup(c1, c2, c3)

        self.play(FadeIn(c1), run_time=self.T(1.5))
        self.say("two things, twenty each.", 2)
        self.play(FadeIn(c2), run_time=self.T(1.5))
        self.say("one full price, one half price.", 2, GREY)
        self.play(FadeIn(c3), run_time=self.T(2))
        self.say("ten saved. out of forty.", 2, GOLD)
        self.pad_to(END_SETUP)

    # ==================================================================
    def stage_question(self):
        self.say("half off WHAT?", 3, SKY)
        self.set_work("half of one item. not half of your basket.", SKY, 2.5)
        self.pad_to(END_QUESTION)

    # ==================================================================
    def stage_cells(self):
        self.play(FadeOut(self.sum_blk), run_time=self.T(1.5))
        self.say("cut each item into four.", 2, GOLD)

        self.row = VGroup(*[cell(k, GOLD) for k in range(CELLS)])
        self.play(FadeIn(self.row, lag_ratio=0.08), run_time=self.T(3))

        g1 = txt("item 1", 20, DIM, bold=False, w=0.9)
        g1.move_to(np.array([(cell_left(0) + cell_left(3) + CW) / 2, GRP_Y, 0]))
        g2 = txt("item 2", 20, DIM, bold=False, w=0.9)
        g2.move_to(np.array([(cell_left(4) + cell_left(7) + CW) / 2, GRP_Y, 0]))
        self.tags = VGroup(g1, g2)
        self.val = txt("40", 40, WHITE_, w=1.2)
        self.val.move_to(np.array([0, VAL_Y, 0]))
        self.play(FadeIn(self.tags), FadeIn(self.val), run_time=self.T(1.5))
        self.say("eight quarters on the table.", 2.5, GOLD)

        gone = VGroup(self.row[6], self.row[7])
        self.play(gone.animate.set_stroke(ROSE).set_fill(ROSE, 0.30),
                  run_time=self.T(1))
        self.holes = VGroup(hole(6), hole(7))
        new_val = txt("30", 40, WHITE_, w=1.2).move_to(np.array([0, VAL_Y, 0]))
        self.play(FadeOut(gone, shift=0.35 * UP),
                  FadeIn(self.holes), Transform(self.val, new_val),
                  run_time=self.T(2))
        self.say("the deal takes two of them.", 2.5, ROSE)
        self.set_work("2 gone  out of  8", GOLD, 2.5)
        self.say("two out of eight is a quarter.", 2.5, GOLD)
        self.pad_to(END_BAR)

    # ==================================================================
    def stage_table(self):
        self.play(FadeOut(self.row), FadeOut(self.tags), FadeOut(self.val),
                  FadeOut(self.holes), run_time=self.T(1.5))
        self.set_work("so how do the signs rank?", WHITE_, 2)

        rows = VGroup()
        for i, (name, pct, col) in enumerate(TABLE):
            y = 1.05 - i * 0.80
            left = txt(name, 24, col, w=LAB_W)
            left.move_to(np.array([0, y, 0]))
            left.align_to(np.array([COL_L, 0, 0]), LEFT)
            right = txt(pct, 30, col, w=PCT_W)
            right.move_to(np.array([0, y, 0]))
            right.align_to(np.array([COL_R, 0, 0]), RIGHT)
            rows.add(VGroup(left, right))
        self.rows = rows

        for r in rows:
            self.play(FadeIn(r, shift=0.10 * RIGHT), run_time=self.T(2))
        box = Rectangle(width=3.20, height=0.64, stroke_color=ROSE,
                        stroke_width=2.6, fill_opacity=0)
        box.move_to(np.array([0, 1.05 - 2 * 0.80, 0]))
        self.box = box
        self.play(ShowCreation(box), run_time=self.T(1.5))
        self.say("the biggest number on the sign. the worst deal.", 3, ROSE)
        self.pad_to(END_TABLE)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 28, WHITE_).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 28, GOLD).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to whoever", 27, WHITE_)
        s2 = txt("does the big shop", 27, GOLD)
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
        if cg.get_width() > 2 * SAFE_X - 0.15:
            cg.set_width(2 * SAFE_X - 0.15)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1))
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(1.5))
