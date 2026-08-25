"""
delivery_shortcut — Pythagoras cuts 2 of every 7 delivery blocks. 60.0s.

    BPM=150 manimgl delivery_shortcut.py DeliveryShortcut -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE 3 OF "WHERE MATH ACTUALLY GETS USED". Same shell: the number is
the spine, pinned at the TOP for the whole video.

A courier on a city grid can only legally drive along streets: 3 blocks
over, 4 blocks up, 7 blocks total. But a straight path — a bike lane, an
alley, a park crossing — cuts the corner: the diagonal is exactly 5 blocks,
by the smallest whole-number right triangle there is.

    streets:   3 + 4 = 7 blocks
    diagonal:  sqrt(3^2 + 4^2) = 5 blocks

7 down to 5 is a 28.6% shorter trip. Multiply that by thousands of
deliveries a day and this is the actual reason routing apps score a path
with a shortcut higher than one without.

VERIFIED AT IMPORT
    3^2 + 4^2 == 5^2                genuine Pythagorean triple
    saved == 2 blocks exactly       28.6% shorter, not rounded up
"""
import os
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 12
END_A, END_B = 44, 96
END_WHY, END_TAKE, END_SHARE = 117, 132, 138

SERIES = "WHERE MATH ACTUALLY GETS USED"

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
A, B, C = 3, 4, 5
assert A * A + B * B == C * C

STREETS = A + B
DIAG = C
SAVED = STREETS - DIAG
assert SAVED == 2
PCT = Fraction(SAVED, STREETS)
assert abs(float(PCT) - 0.2857142857142857) < 1e-9


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


def grid_group(O, U):
    def Q(x, y):
        return O + np.array([float(x) * U, float(y) * U, 0])
    grid = VGroup()
    for k in range(0, A + 2):
        grid.add(seg(Q(k, 0), Q(k, B + 1), FAINT, 1.4, 0.55))
    for k in range(0, B + 2):
        grid.add(seg(Q(0, k), Q(A + 1, k), FAINT, 1.4, 0.55))
    return grid, Q


class DeliveryShortcut(Scene):
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
        self.stage_streets()
        self.stage_diagonal()
        self.stage_why()
        self.takeaway("This is why we learned Pythagoras.",
                      "Every routing app scores around it.")
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
        big = txt("3² + 4² = 5²", 30, GOLD, w=4.5)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("a delivery courier's route", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("one shortcut. 2 fewer blocks.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("3² + 4² = 5²", 28, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_streets(self):
        O = np.array([-1.35, -1.85, 0])
        U = 0.46
        self.grid, Q = grid_group(O, U)
        self.Aoff, self.Boff = Q(0, 0), Q(A, B)
        self.play(FadeIn(self.grid), run_time=self.T(2))

        path = VGroup(
            seg(Q(0, 0), Q(A, 0), WHITE_, 4.0),
            seg(Q(A, 0), Q(A, B), WHITE_, 4.0),
        )
        self.pathgrp = path
        self.play(ShowCreation(path[0]), run_time=self.T(1.5))
        self.play(ShowCreation(path[1]), run_time=self.T(1.5))
        start = Dot(Q(0, 0), radius=0.13, fill_color=SKY)
        end = Dot(Q(A, B), radius=0.13, fill_color=ROSE)
        self.play(FadeIn(start), FadeIn(end), run_time=self.T(1))

        self.say("along streets: 3 blocks over, 4 blocks up.", 4)
        self.set_work("3 + 4 = 7 blocks", WHITE_, 2.5)
        self.say("that's the only legal route. seven blocks.", 3.5)
        self.pad_to(END_A)

    def stage_diagonal(self):
        diag = seg(self.Aoff, self.Boff, GOLD, 4.4)
        self.say("but a bike lane cuts straight across.", 4)
        self.play(ShowCreation(diag), run_time=self.T(2.5))
        self.set_work("√(3² + 4²) = 5 blocks", GOLD, 3)
        self.say("the diagonal isn't a guess. it's exact.", 3.5)
        self.set_work("7 blocks -> 5 blocks", GOLD, 2.5)
        self.say("two fewer blocks. every single trip.", 3.5)
        self.set_work("28.6% shorter", GREEN, 3)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("the smallest whole-number right triangle there is.", 3)
        self.set_work("3-4-5, on a million deliveries a day", GOLD, 3.5)
        self.say("that's not a rounding error. that's real fuel and time.", 4)
        self.pad_to(END_WHY)

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
        self.l2 = txt(b, 25, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is where it's used", 25, GOLD, w=4.6)
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
