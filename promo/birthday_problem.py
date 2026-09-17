"""
birthday_problem — 23 people is already a coin flip. 40.0s.

    BPM=150 manimgl birthday_problem.py BirthdayProblem -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — probability lane. The ANSWER is
pinned at the TOP for the whole video.

        23 people  →  50.7%

THE MISTAKE IS PUTTING YOURSELF IN THE MIDDLE. Asked how many people it
takes before two share a birthday, everyone silently solves a different
problem: how many before someone matches ME. That one really is slow —
22 other people gives you a 5.9% chance.

But nobody said it had to be you. ANY two of them will do, and a room of
23 holds 253 different pairs:

        23 × 22 / 2  =  253 pairs

Each pair is a fresh chance to collide, and 253 of them is plenty:

        22 people  ->  47.6%
        23 people  ->  50.7%     <- past the coin flip
        50 people  ->  97.0%
        70 people  ->  99.9%

VERIFIED AT IMPORT
    p(n) computed exactly with Fractions, not from a remembered table
    22 is genuinely below 50% and 23 genuinely above — the claim is the crossing
    50.7 / 47.6 / 97.0 / 99.9 all reproduced to one decimal place
    253 pairs from comb(23, 2), and the 5.9% "someone matches me" figure

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from fractions import Fraction
from itertools import combinations
from math import comb

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_ROOM, END_YOU = 28, 42
END_PAIRS, END_CURVE = 59, 78
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
DAYS = 365
N = 23
N_MAX = 70


def p_share(n, days=DAYS):
    """Exact chance that at least two of n people share a birthday."""
    q = Fraction(1)
    for k in range(n):
        q *= Fraction(days - k, days)
    return 1 - q


P23, P22 = p_share(23), p_share(22)
assert float(P22) < 0.5 < float(P23)                 # 23 is where it crosses
assert round(float(P23) * 100, 1) == 50.7
assert round(float(P22) * 100, 1) == 47.6
assert round(float(p_share(50)) * 100, 1) == 97.0
assert round(float(p_share(70)) * 100, 1) == 99.9

PAIRS = comb(N, 2)
assert PAIRS == 253 == N * (N - 1) // 2
assert len(list(combinations(range(N), 2))) == PAIRS

P_ME = 1 - Fraction(364, 365) ** (N - 1)             # someone matches *me*
assert round(float(P_ME) * 100, 1) == 5.9

CURVE = [(n, float(p_share(n))) for n in range(1, N_MAX + 1)]

# ------------------------------------------------------------------ layout
RING_C = np.array([0.0, -0.45, 0])
RING_R = 1.46
DOTS = [RING_C + RING_R * np.array([np.sin(2 * np.pi * k / N),
                                    np.cos(2 * np.pi * k / N), 0])
        for k in range(N)]

PX0, PX1 = -1.85, 1.85
PY0, PY1 = -1.90, 0.55


def plot(n, p):
    return np.array([PX0 + (n / N_MAX) * (PX1 - PX0),
                     PY0 + p * (PY1 - PY0), 0])


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


class BirthdayProblem(Scene):
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
        self.stage_room()
        self.stage_you()
        self.stage_pairs()
        self.stage_curve()
        self.takeaway("You counted yourself.",
                      "The room was counting pairs.")
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
        q = txt("how many people in a room", 27, WHITE_, w=4.5)
        q.move_to(np.array([0, 1.25, 0]))
        q2 = txt("before two share a birthday?", 27, WHITE_, w=4.5)
        q2.move_to(np.array([0, 0.62, 0]))
        sub = txt("it's a coin flip sooner than you think.", 23, GREY, bold=False)
        sub.move_to(np.array([0, -0.35, 0]))
        self.add(q, q2, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("23 people  →  50.7%", 24, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(q2), FadeOut(sub),
                  FadeIn(self.eq), FadeIn(self.title), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_room(self):
        self.say("most people guess a hundred and eighty.", 3, GREY)
        self.dots = VGroup(*[Dot(p, radius=0.072, fill_color=SKY) for p in DOTS])
        self.play(FadeIn(self.dots, lag_ratio=0.06), run_time=self.T(3.5))
        self.set_work("23 people. that's a school class.", SKY, 3)
        self.say("twenty-three is already better than even.", 3.5, GOLD)
        self.say("so why does that feel impossible?", 3, WHITE_)
        self.pad_to(END_ROOM)

    # ==================================================================
    def stage_you(self):
        me = self.dots[0]
        spokes = VGroup(*[seg(DOTS[0], DOTS[k], ROSE, 1.4, 0.55)
                          for k in range(1, N)])
        self.spokes = spokes
        self.play(me.animate.set_fill(ROSE).scale(1.5),
                  ShowCreation(spokes, lag_ratio=0.04), run_time=self.T(3))
        self.set_work("you against the other 22:  5.9%", ROSE, 3)
        self.say("that's the sum you did in your head. it's tiny.", 3.5, ROSE)
        self.say("but nobody said it had to be YOU.", 3.5, GOLD)
        self.pad_to(END_YOU)

    # ==================================================================
    def stage_pairs(self):
        self.play(FadeOut(self.spokes),
                  self.dots[0].animate.set_fill(SKY).scale(1 / 1.5),
                  run_time=self.T(1.5))

        web = VGroup(*[seg(DOTS[a], DOTS[b], GOLD, 1.0, 0.22)
                       for a, b in combinations(range(N), 2)])
        assert len(web) == PAIRS
        self.web = web
        self.play(ShowCreation(web, lag_ratio=0.004), run_time=self.T(5))
        self.set_work("23 × 22 / 2  =  253 pairs", GOLD, 3)
        self.say("every one of those lines is its own chance.", 3.5, GOLD)
        self.say("253 chances. that's why 23 is enough.", 3.5)
        self.pad_to(END_PAIRS)

    # ==================================================================
    def stage_curve(self):
        self.play(FadeOut(self.web), FadeOut(self.dots), run_time=self.T(1.5))

        ax = VGroup(
            seg(plot(0, 0.0), plot(N_MAX, 0.0), DIM, 2.0),
            seg(plot(0, 0.0), plot(0, 1.0), DIM, 2.0))
        half = seg(plot(0, 0.5), plot(N_MAX, 0.5), FAINT, 1.8, 0.9)
        hlab = txt("50%", 16, DIM, bold=False, w=0.7)
        hlab.move_to(plot(N_MAX, 0.5) + np.array([0.28, 0, 0]))

        curve = VMobject(stroke_color=GOLD, stroke_width=3.2)
        curve.set_points_smoothly([plot(n, p) for n, p in CURVE])

        self.play(ShowCreation(ax), FadeIn(half), FadeIn(hlab),
                  run_time=self.T(2))
        self.play(ShowCreation(curve), run_time=self.T(3.5))

        mk = Dot(plot(23, float(P23)), radius=0.085, fill_color=WHITE_)
        drop = seg(plot(23, 0.0), plot(23, float(P23)), WHITE_, 1.6, 0.7)
        nlab = txt("23", 18, WHITE_, w=0.5)
        nlab.move_to(plot(23, 0.0) + np.array([0, -0.26, 0]))
        plab = txt("50.7%", 21, WHITE_, w=1.0)
        plab.move_to(plot(23, float(P23)) + np.array([0.62, 0.22, 0]))
        self.curve = VGroup(ax, half, hlab, curve, mk, drop, nlab, plab)

        self.play(FadeIn(drop), FadeIn(mk), FadeIn(nlab), FadeIn(plab),
                  run_time=self.T(2))
        self.set_work("22 → 47.6%        23 → 50.7%", GOLD, 3)
        self.say("and it keeps climbing. 50 people: 97%.", 3.5, SKY)
        self.say("70 people: 99.9%. a near certainty.", 3, SKY)
        self.pad_to(END_CURVE)

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
        s1 = txt("Send this to your group chat", 27, WHITE_, w=4.5)
        s2 = txt("and count how many of you there are", 24, GOLD, w=4.6)
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
