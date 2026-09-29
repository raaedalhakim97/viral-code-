"""
percent_back — down 20% then up 20% does not get you back. 40.0s.

    BPM=150 manimgl percent_back.py PercentBack -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

Same build as net_vs_gross.py: frame 1 is the mistake already made and
already crossed out, the answer lands by 0:05 and pins to the top, and
the shape does the explaining.

THE STORY. Your pay is cut 20%, then restored 20%. Everyone expects to
be back at 1,000. You are at 960.

        1,000  − 20%  =   800
          800  + 20%  =   960        <- 40 short, every time

THE DOUBT. 20% of WHAT? It came OFF 1,000 and went back ON to 800. The
second percentage is a percentage of a smaller pile.

THE SHAPE. Cut the 1,000 into ten blocks of a hundred.

        20% off    takes two WHOLE blocks          -> 8 blocks
        20% back   returns 20% of 800 = 160        -> 1.6 blocks

Two blocks out, one point six back. The missing four tenths of a block
is the 40, and it is sitting there on screen to be counted.

THE STAKE. To undo a cut you need a bigger rise than the cut:

        down 10%  ->  up 11.11%        down 20%  ->  up 25%
        down 25%  ->  up 33.33%        down 50%  ->  up 100%

VERIFIED AT IMPORT
    every figure is exact Fraction arithmetic — nothing typed in by hand
    the shortfall is exactly 40, which is exactly 4% of 1,000
    the order does not matter: +20% then -20% lands on 960 too
    the recovery rise is p/(1-p), checked at 10/20/25/50/90%
    the gap is always exactly r squared, checked across rates
    the blocks are asserted to fit the platform safe box

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

SERIES = "EVERY PAY CUT GETS THIS WRONG"

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
PAY = Fraction(1000)
RATE = Fraction(20, 100)

CUT = PAY * RATE                          # 200 off
LOW = PAY - CUT                           # 800
BACK = LOW * RATE                         # 160 back
END = LOW + BACK                          # 960
SHORT = PAY - END                          # 40
assert (CUT, LOW, BACK, END, SHORT) == (200, 800, 160, 960, 40)
assert SHORT / PAY == Fraction(1, 25)      # exactly 4%
assert PAY * (1 + RATE) * (1 - RATE) == END    # the other order lands here too
assert 1 - (1 + RATE) * (1 - RATE) == RATE ** 2   # the gap is always r squared

BLOCKS = 10                                # one block = 100
BLOCK_VALUE = PAY / BLOCKS
OUT_BLOCKS = CUT / BLOCK_VALUE             # 2 whole blocks leave
IN_BLOCKS = BACK / BLOCK_VALUE             # 1.6 come back
assert BLOCK_VALUE == 100
assert OUT_BLOCKS == 2 and IN_BLOCKS == Fraction(8, 5)
assert OUT_BLOCKS - IN_BLOCKS == Fraction(2, 5)    # the missing 0.4 of a block
assert (OUT_BLOCKS - IN_BLOCKS) * BLOCK_VALUE == SHORT


def recover(p):
    """The rise that undoes a cut of p."""
    return p / (1 - p)


assert recover(Fraction(20, 100)) == Fraction(1, 4)     # 25%
assert recover(Fraction(50, 100)) == 1                  # 100%
assert recover(Fraction(10, 100)) == Fraction(1, 9)
assert recover(Fraction(25, 100)) == Fraction(1, 3)
assert recover(Fraction(90, 100)) == 9
assert LOW * (1 + recover(RATE)) == PAY                 # +25% really gets back

# ------------------------------------------------------------------ layout
PITCH, BW, BH = 0.32, 0.29, 1.40    # tall, so the missing 0.4 has area
BAR_Y = 0.45
BAR_X0 = -(BLOCKS * PITCH) / 2             # left edge of block 0
VAL_Y = BAR_Y - BH / 2 - 0.62
assert BAR_Y + BH / 2 < WORK_Y - 0.16
assert BAR_X0 + BLOCKS * PITCH <= SAFE_X
assert BAR_X0 >= -SAFE_X
assert VAL_Y - 0.28 > NOTE_Y + 0.20        # the running total clears the caption


def block_left(k):
    return BAR_X0 + k * PITCH


def block(k, color, frac=1.0, fill=0.30):
    """Block k, optionally only the left `frac` of it."""
    w = BW * frac
    r = Rectangle(width=w, height=BH, stroke_color=color, stroke_width=2.0,
                  fill_color=color, fill_opacity=fill)
    r.move_to(np.array([block_left(k) + w / 2, BAR_Y, 0]))
    return r


def ghost(k, frac_from):
    """The unfilled tail of block k — the bit that never came back."""
    w = BW * (1 - frac_from)
    r = Rectangle(width=w, height=BH, stroke_color=ROSE, stroke_width=3.0,
                  fill_color=ROSE, fill_opacity=0.22)
    r.move_to(np.array([block_left(k) + BW * frac_from + w / 2, BAR_Y, 0]))
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


class PercentBack(Scene):
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
        self.takeaway("Down 20% needs up 25%.",
                      "Down 50% needs up 100%.")
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

        sum_ = txt("1,000   − 20%   + 20%", 30, GREY, w=3.9)
        sum_.move_to(np.array([0, 1.52, 0]))

        bad = txt("1,000", 58, ROSE, w=2.6)
        bad.move_to(np.array([-0.42, 0.66, 0]))
        strike = seg(bad.get_left() + np.array([-0.12, 0, 0]),
                     bad.get_right() + np.array([0.12, 0, 0]), ROSE, 4.5)
        x = cross_at(1.42, 0.66, ROSE, 0.24, 6.0)

        l1 = txt("this costs you 40", 30, WHITE_)
        l1.move_to(np.array([0, -0.55, 0]))
        l2 = txt("every single time", 27, ROSE, w=2 * SAFE_X - 0.40)
        l2.move_to(np.array([0, -1.30, 0]))

        self.hookgrp = VGroup(sum_, bad, strike, x, l1, l2)
        self.add(self.title, self.hookgrp)
        self.wait(self.T(END_HOOK))

    # ==================================================================
    def stage_answer(self):
        big = txt("960", 62, GOLD, w=2.6)
        big.move_to(np.array([0, 0.55, 0]))
        self.play(FadeOut(self.hookgrp), FadeIn(big, scale=1.15),
                  run_time=self.T(2.5))
        self.say("that's what you actually get back.", 2.5, GOLD)

        self.eq = txt("960   not   1,000", 26, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(Transform(big, self.eq), run_time=self.T(2.5))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_ANSWER)

    # ==================================================================
    def stage_setup(self):
        # the sum runs in the CENTRE, not in the work line — otherwise the
        # stage sits empty from the answer pin until the blocks arrive
        c1 = txt("1,000", 40, WHITE_, w=1.7)
        c2 = txt("− 20%   →    800", 34, ROSE, w=2.9)
        c3 = txt("+ 20%   →    960", 34, ROSE, w=2.9)
        for m, y in ((c1, 1.15), (c2, 0.40), (c3, -0.35)):
            m.move_to(np.array([0, y, 0]))
        c1.align_to(c2, LEFT)
        x = cross_at(1.45, -0.35, ROSE, 0.21, 5.5)
        self.sum_blk = VGroup(c1, c2, c3, x)

        self.play(FadeIn(c1), run_time=self.T(1.5))
        self.say("they cut your pay 20%.", 2)
        self.play(FadeIn(c2), run_time=self.T(1.5))
        self.say("a year later they put 20% back.", 2, GREY)
        self.play(FadeIn(c3), ShowCreation(x), run_time=self.T(2))
        self.say("you are not back where you started.", 2, ROSE)
        self.pad_to(END_SETUP)

    # ==================================================================
    def stage_question(self):
        self.say("20% of WHAT?", 3, SKY)
        self.set_work("it came off 1,000. it went back onto 800.", SKY, 2.5)
        self.pad_to(END_QUESTION)

    # ==================================================================
    def stage_bar(self):
        self.play(FadeOut(self.sum_blk), run_time=self.T(1.5))
        self.say("cut the 1,000 into ten blocks.", 2, GOLD)

        self.row = VGroup(*[block(k, GOLD) for k in range(BLOCKS)])
        self.play(FadeIn(self.row, lag_ratio=0.08), run_time=self.T(3))
        self.val = txt("1,000", 40, WHITE_, w=1.8)
        self.val.move_to(np.array([0, VAL_Y, 0]))
        self.play(FadeIn(self.val), run_time=self.T(1.5))

        self.say("20% off takes two WHOLE blocks.", 2.5, ROSE)
        gone = VGroup(self.row[8], self.row[9])
        self.play(gone.animate.set_stroke(ROSE).set_fill(ROSE, 0.30),
                  run_time=self.T(1))
        new_val = txt("800", 40, WHITE_, w=1.4).move_to(np.array([0, VAL_Y, 0]))
        self.play(FadeOut(gone, shift=0.35 * UP),
                  Transform(self.val, new_val), run_time=self.T(1.5))

        self.say("now they put the 20% back.", 2.5, GOLD)
        self.set_work("20% of 800  =  160", GOLD, 2.5)

        self.ret = VGroup(block(8, SKY, 1.0, 0.45),
                          block(9, SKY, 0.6, 0.45))
        self.gh = ghost(9, 0.6)
        self.play(FadeIn(self.ret, lag_ratio=0.3), run_time=self.T(3))
        end_val = txt("960", 40, WHITE_, w=1.4).move_to(np.array([0, VAL_Y, 0]))
        self.play(Transform(self.val, end_val), run_time=self.T(1.5))
        self.say("one point six blocks come back. not two.", 2.5, GOLD)
        self.pad_to(END_BAR)

    # ==================================================================
    def stage_numbers(self):
        self.play(ShowCreation(self.gh), run_time=self.T(2))
        self.set_work("200 out.      160 back.", ROSE, 2.5)
        self.say("that gap is the 40. you can count it.", 2.5, ROSE)
        self.set_work("to get back to 1,000 you need + 25%", GOLD, 3)
        self.say("not twenty. twenty-five.", 2.5, GOLD)
        self.say("because 25% of 800 is 200.", 2.5)
        self.pad_to(END_NUMBERS)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 29, GOLD).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to anyone", 27, WHITE_)
        s2 = txt("who took a pay cut", 27, GOLD)
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
