"""
dice_seven — why 7 is the number to bet on. 40.0s.

    BPM=150 manimgl dice_seven.py DiceSeven -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — probability lane. The ANSWER is
pinned at the TOP for the whole video, same as the equation is in the
trig episodes.

        P(7) = 6/36 = 1/6

TWO DICE DON'T GIVE ELEVEN EQUAL ANSWERS. The sums run 2 to 12, so it
feels like eleven options — but the dice don't roll sums, they roll
PAIRS, and there are 36 pairs. Six of them make 7. Exactly one makes 12.

        7  ->  1+6  2+5  3+4  4+3  5+2  6+1     6 of 36  =  1/6  = 16.7%
        12 ->  6+6                              1 of 36         =  2.8%

Seven comes up SIX TIMES as often as twelve. That is the whole of why
the board game hands you 7 and why the casino prices it the way it does.

VERIFIED AT IMPORT
    all 36 ordered pairs enumerated, not hard-coded
    the 11 sum counts are 1,2,3,4,5,6,5,4,3,2,1 and total 36
    P(7) == Fraction(1, 6) exactly, and 7 beats every other sum
    the 7:12 ratio is exactly 6

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from collections import Counter
from fractions import Fraction
from itertools import product

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_GRID, END_SEVEN, END_TWELVE = 28, 52, 63
END_HIST, END_TAKE, END_SHARE = 78, 88, 92

SERIES = "WHY DID WE LEARN THIS?"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
EQ_Y   = 3.08
WORK_Y = 2.30
NOTE_Y = -3.30
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
ROLLS = list(product(range(1, 7), repeat=2))
assert len(ROLLS) == 36

WAYS = Counter(a + b for a, b in ROLLS)
assert [WAYS[s] for s in range(2, 13)] == [1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1]
assert sum(WAYS.values()) == 36

P7 = Fraction(WAYS[7], 36)
assert P7 == Fraction(1, 6)
assert WAYS[7] == 6 and WAYS[12] == 1
assert all(WAYS[s] < WAYS[7] for s in range(2, 13) if s != 7)
assert WAYS[7] // WAYS[12] == 6

SEVENS = [r for r in ROLLS if sum(r) == 7]
assert len(SEVENS) == 6

# ------------------------------------------------------------------ layout
U  = 0.58
GC = np.array([0.29, -1.04, 0])          # grid+labels centred on (0, -0.75)


def cell(i, j):
    """i = row 0..6 (0 is the die-A label strip), j = col 0..6 likewise."""
    return GC + np.array([(j - 3.5) * U, (3.5 - i) * U, 0])


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


PIPS = {
    1: [(0, 0)],
    2: [(-1, 1), (1, -1)],
    3: [(-1, 1), (0, 0), (1, -1)],
    4: [(-1, 1), (1, 1), (-1, -1), (1, -1)],
    5: [(-1, 1), (1, 1), (0, 0), (-1, -1), (1, -1)],
    6: [(-1, 1), (1, 1), (-1, 0), (1, 0), (-1, -1), (1, -1)],
}


def die_face(n, side, color=WHITE_):
    """A square die showing n pips. Returns a VGroup centred on ORIGIN."""
    g = VGroup()
    g.add(Square(side_length=side, stroke_color=color, stroke_width=2.0,
                 fill_opacity=0))
    off = side * 0.27
    for px, py in PIPS[n]:
        g.add(Dot(np.array([px * off, py * off, 0]),
                  radius=side * 0.085, fill_color=color))
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


class DiceSeven(Scene):
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

        self.open_card()
        self.stage_grid()
        self.stage_seven()
        self.stage_twelve()
        self.stage_hist()
        self.takeaway("Eleven sums. Thirty-six rolls.",
                      "That's the whole trick.")
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
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def set_work(self, s, color, beats=2.5, size=22):
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
    def open_card(self):
        d1 = die_face(3, 0.62, GOLD)
        d2 = die_face(4, 0.62, GOLD)
        pair = VGroup(d1, d2).arrange(RIGHT, buff=0.30)
        pair.move_to(np.array([0, 1.30, 0]))
        q = txt("roll two dice.", 29, WHITE_, w=4.4)
        q.move_to(np.array([0, 0.20, 0]))
        sub = txt("which total should you bet on?", 24, GREY, bold=False)
        sub.move_to(np.array([0, -0.50, 0]))
        self.add(pair, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("P(7) = 6/36 = 1/6", 24, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), FadeOut(pair),
                  FadeIn(self.eq), FadeIn(self.title), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_grid(self):
        self.say("the sums go 2 to 12. eleven of them.", 2.5, GREY)

        labels = VGroup()
        for k in range(1, 7):
            labels.add(die_face(k, U * 0.66, SKY).move_to(cell(0, k)))
            labels.add(die_face(k, U * 0.66, ROSE).move_to(cell(k, 0)))

        self.cells = {}
        boxes = VGroup()
        nums = VGroup()
        for i in range(1, 7):
            for j in range(1, 7):
                bx = Square(side_length=U * 0.86, stroke_color=FAINT,
                            stroke_width=1.6, fill_opacity=0).move_to(cell(i, j))
                nm = txt(str(i + j), 19, DIM, bold=False, w=0.5).move_to(cell(i, j))
                self.cells[(i, j)] = (bx, nm)
                boxes.add(bx)
                nums.add(nm)

        self.grid = VGroup(labels, boxes, nums)
        self.play(FadeIn(labels, lag_ratio=0.05), run_time=self.T(2.5))
        self.play(ShowCreation(boxes, lag_ratio=0.02), run_time=self.T(4))
        self.play(FadeIn(nums, lag_ratio=0.02), run_time=self.T(3))
        self.say("but the dice don't roll sums. they roll pairs.", 3, SKY)
        self.set_work("6 × 6 = 36 pairs, all equally likely", SKY, 3)
        self.pad_to(END_GRID)

    # ==================================================================
    def stage_seven(self):
        self.say("so how many of the 36 pairs make 7?", 3, GOLD)

        anims = []
        for (i, j) in SEVENS:
            bx, nm = self.cells[(i, j)]
            anims.append(bx.animate.set_stroke(GOLD, 3.0))
            anims.append(nm.animate.set_fill(GOLD).scale(1.15))
        self.play(*anims, run_time=self.T(3))

        self.set_work("1+6   2+5   3+4   4+3   5+2   6+1", GOLD, 3)
        self.say("six. a whole diagonal of them.", 3, GOLD)
        self.set_work("6 out of 36  =  1/6  =  16.7%", GOLD, 3)
        self.say("no other total has six ways.", 3)
        self.pad_to(END_SEVEN)

    # ==================================================================
    def stage_twelve(self):
        bx, nm = self.cells[(6, 6)]
        self.play(bx.animate.set_stroke(ROSE, 3.0),
                  nm.animate.set_fill(ROSE).scale(1.15), run_time=self.T(2))
        self.set_work("12 needs 6+6.  one pair out of 36  =  2.8%", ROSE, 3)
        self.say("seven turns up SIX TIMES as often as twelve.", 3.5, ROSE)
        self.pad_to(END_TWELVE)

    # ==================================================================
    def stage_hist(self):
        self.play(FadeOut(self.grid), run_time=self.T(1.5))

        pitch, bw, hu = 0.38, 0.27, 0.285
        base = -1.95
        bars = VGroup()
        caps = VGroup()
        for k, s in enumerate(range(2, 13)):
            n = WAYS[s]
            col = GOLD if s == 7 else (ROSE if s == 12 else DIM)
            x = (k - 5) * pitch
            h = n * hu
            r = Rectangle(width=bw, height=h, stroke_color=col,
                          stroke_width=1.8, fill_color=col, fill_opacity=0.30)
            r.move_to(np.array([x, base + h / 2, 0]))
            bars.add(r)
            caps.add(txt(str(s), 15, col, bold=False, w=0.34).move_to(
                np.array([x, base - 0.22, 0])))

        self.play(FadeIn(bars, lag_ratio=0.08), FadeIn(caps, lag_ratio=0.08),
                  run_time=self.T(3.5))
        self.hist = VGroup(bars, caps)
        self.set_work("1  2  3  4  5  6  5  4  3  2  1", GOLD, 3)
        self.say("stack the 36 pairs by total and you get a hill.", 3.5, GOLD)
        self.say("7 is the top of it. every board game knows.", 3)
        self.pad_to(END_HIST)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to whoever always", 27, WHITE_, w=4.5)
        s2 = txt("bets on double six", 25, GOLD, w=4.6)
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
