"""
odds_vs_chance — "4 to 1" is not 1 in 4. 40.0s.

    BPM=150 manimgl odds_vs_chance.py OddsVsChance -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — probability lane. The ANSWER is
pinned at the TOP for the whole video.

        4 to 1  =  1 in 5  =  20%

ODDS AND CHANCES ARE NOT THE SAME NUMBER. "Four to one against" counts
the ways to LOSE against the ways to WIN — four to one, so five outcomes
in total, and the winning one is one of five. Almost everyone reads it as
one in four, which is 25%. It is 20%.

        a to b against   ->   b / (a + b)

THE PAYOFF: run that conversion across a whole bookmaker's board and the
chances don't add to 100%.

        1 to 1  -> 50%      4 to 1 -> 20%
        3 to 1  -> 25%      9 to 1 -> 10%
                            ---------------
                            105%

Exactly one runner can win, so the true chances must sum to 100. The
extra five points is the margin — the bookmaker's edge, 1/21 of every
pound staked, sitting in plain sight on the board.

VERIFIED AT IMPORT
    4 to 1 converts to Fraction(1, 5), exactly — not rounded for effect
    the four board prices sum to Fraction(21, 20), i.e. exactly 105%
    the edge is exactly Fraction(1, 21)
    a genuinely fair book (1/1, 2/1, 5/1) is checked to sum to exactly 1

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

END_OPEN = 8
END_FIVE, END_MISTAKE = 30, 42
END_BOOK, END_EDGE = 63, 80
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
EQ_Y   = 3.08
WORK_Y = 2.30
NOTE_Y = -3.30
LINE_Y = -2.05


# ------------------------------------------------------------------ numbers
def chance(a, b=1):
    """'a to b against' -> the chance of the b side. Exact."""
    return Fraction(b, a + b)


assert chance(4) == Fraction(1, 5)
assert float(chance(4)) * 100 == 20.0
assert chance(3) == Fraction(1, 4)        # the number people *think* 4/1 is

BOOK = [("1 to 1", 1, GOLD), ("3 to 1", 3, SKY),
        ("4 to 1", 4, ROSE), ("9 to 1", 9, GREEN)]
SHARES = [chance(a) for _, a, _ in BOOK]
assert [str(s) for s in SHARES] == ["1/2", "1/4", "1/5", "1/10"]
PCTS = [int(s * 100) for s in SHARES]
assert PCTS == [50, 25, 20, 10]

TOTAL_P = sum(SHARES, Fraction(0))
assert TOTAL_P == Fraction(21, 20)        # exactly 105%
assert sum(PCTS) == 105

EDGE = (TOTAL_P - 1) / TOTAL_P
assert EDGE == Fraction(1, 21)
assert abs(float(EDGE) * 100 - 4.761904761904) < 1e-9

FAIR = sum((chance(a) for a in (1, 2, 5)), Fraction(0))
assert FAIR == 1                          # a book with no margin at all


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


class OddsVsChance(Scene):
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
        self.stage_five()
        self.stage_mistake()
        self.stage_book()
        self.stage_edge()
        self.takeaway("Odds count the ways to lose.",
                      "Chances count everything.")
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
        big = txt("4 to 1", 46, GOLD, w=2.6)
        big.move_to(np.array([0, 1.25, 0]))
        q = txt("so that's a 1 in 4 shot,", 27, WHITE_, w=4.5)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("right?", 27, GREY, bold=False, w=2.0)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("4 to 1  =  1 in 5  =  20%", 23, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_five(self):
        self.say("odds count ways to LOSE against ways to WIN.", 3, GOLD)

        side, buff = 0.70, 0.13
        pitch = side + buff
        boxes = VGroup()
        marks = VGroup()
        for k in range(5):
            win = (k == 4)
            col = GOLD if win else DIM
            x = (k - 2) * pitch
            c = np.array([x, 0.55, 0])
            boxes.add(Square(side_length=side, stroke_color=col,
                             stroke_width=2.4, fill_color=col,
                             fill_opacity=0.18 if win else 0.0).move_to(c))
            marks.add(txt("WIN" if win else "LOSE", 14,
                          col, bold=win, w=side * 0.82).move_to(c))
        self.boxes, self.marks = boxes, marks

        self.play(FadeIn(boxes[:4], lag_ratio=0.15),
                  FadeIn(marks[:4], lag_ratio=0.15), run_time=self.T(3))
        self.set_work("four ways to lose . . .", DIM, 2.5)
        self.play(FadeIn(boxes[4], scale=1.2), FadeIn(marks[4]),
                  run_time=self.T(2))
        self.set_work(". . . for one way to win", GOLD, 2.5)

        brace = VGroup(
            seg(np.array([-2.06, 0.02, 0]), np.array([-2.06, -0.12, 0]), SKY, 2.2),
            seg(np.array([-2.06, -0.12, 0]), np.array([2.06, -0.12, 0]), SKY, 2.2),
            seg(np.array([2.06, -0.12, 0]), np.array([2.06, 0.02, 0]), SKY, 2.2))
        five = txt("5 outcomes, not 4", 24, SKY, w=3.2)
        five.move_to(np.array([0, -0.55, 0]))
        self.five = VGroup(brace, five)
        self.play(ShowCreation(brace), FadeIn(five), run_time=self.T(2.5))
        self.say("four plus one. five outcomes.", 3, SKY)
        self.pad_to(END_FIVE)

    # ==================================================================
    def stage_mistake(self):
        self.set_work("1 in 5  =  20%        (not 1 in 4 = 25%)", GOLD, 3)
        self.say("a to b against  →  b / (a + b). that's the whole rule.", 3.5)
        self.say("everyone overrates their own bet by a quarter.", 3.5, ROSE)
        self.pad_to(END_MISTAKE)

    # ==================================================================
    def stage_book(self):
        self.play(FadeOut(self.boxes), FadeOut(self.marks), FadeOut(self.five),
                  run_time=self.T(1.5))
        self.say("now read a whole betting board that way.", 3, GOLD)

        rows = VGroup()
        for k, ((name, a, col), pct) in enumerate(zip(BOOK, PCTS)):
            y = 1.05 - k * 0.72
            left = txt(name, 26, col, w=1.5)
            left.move_to(np.array([-1.25, y, 0]))
            arrow = txt("→", 24, DIM, bold=False, w=0.4)
            arrow.move_to(np.array([-0.18, y, 0]))
            right = txt(f"{pct}%", 26, col, w=1.1)
            right.move_to(np.array([0.95, y, 0]))
            rows.add(VGroup(left, arrow, right))
        self.rows = rows

        for r in rows:
            self.play(FadeIn(r, shift=0.10 * RIGHT), run_time=self.T(1.75))
        self.say("four runners. exactly one of them wins.", 3.5, SKY)
        self.set_work("so the four chances must add up to 100%", SKY, 3)
        self.pad_to(END_BOOK)

    # ==================================================================
    def stage_edge(self):
        self.play(FadeOut(self.rows), run_time=self.T(1.5))

        unit = 3.0 / 100.0              # 3.0 world units per 100%
        x0, ybar, hbar = -1.62, -0.10, 0.44
        bar = VGroup()
        x = x0
        for (name, a, col), pct in zip(BOOK, PCTS):
            w = pct * unit
            r = Rectangle(width=w, height=hbar, stroke_color=col,
                          stroke_width=1.8, fill_color=col, fill_opacity=0.40)
            r.move_to(np.array([x + w / 2, ybar, 0]))
            bar.add(r)
            x += w
        assert abs(x - (x0 + 105 * unit)) < 1e-9

        hundred = x0 + 100 * unit
        tick = seg(np.array([hundred, ybar - 0.46, 0]),
                   np.array([hundred, ybar + 0.46, 0]), WHITE_, 2.2)
        tlab = txt("100%", 18, WHITE_, bold=False, w=0.8)
        tlab.move_to(np.array([hundred, ybar + 0.68, 0]))

        self.play(FadeIn(bar, lag_ratio=0.2), run_time=self.T(2.5))
        self.play(ShowCreation(tick), FadeIn(tlab), run_time=self.T(2))
        self.set_work("50 + 25 + 20 + 10  =  105%", GOLD, 2.5)
        self.say("105%. a chance that doesn't exist.", 2.5, ROSE)

        xo = hundred + 2.5 * unit
        over = Rectangle(width=5 * unit, height=hbar + 0.26, stroke_color=ROSE,
                         stroke_width=2.4, fill_color=ROSE, fill_opacity=0.90)
        over.move_to(np.array([xo, ybar, 0]))
        olab = txt("the 5% they keep", 21, ROSE, w=2.4)
        olab.move_to(np.array([0.80, ybar - 0.94, 0]))
        oarr = seg(np.array([xo, ybar - 0.28, 0]),
                   np.array([xo, ybar - 0.70, 0]), ROSE, 2.0)
        self.play(ShowCreation(over), ShowCreation(oarr), FadeIn(olab),
                  run_time=self.T(2.5))
        self.say("those 5 points are the bookmaker's margin.", 3, ROSE)
        self.pad_to(END_EDGE)

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
        s1 = txt("Send this to the friend who says", 26, WHITE_, w=4.5)
        s2 = txt("\"it's basically a 1 in 4\"", 25, GOLD, w=4.6)
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
