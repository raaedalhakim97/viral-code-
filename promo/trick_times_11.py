"""
trick_times_11 — multiply any 2-digit number by 11, in your head. 60.0s.

    BPM=150 manimgl trick_times_11.py TrickTimes11 -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE 1 OF "MENTAL MATH TRICKS". A new sub-series: no proof-heavy setup,
just the trick, a live example, a harder example that proves it isn't a
fluke, and the one-line reason it works. Same shell: the rule is pinned at
the TOP for the whole video. Plain language throughout — built so someone
who "isn't a math person" can follow every step.

THE TRICK. For any 2-digit number with digits a and b: split it, add the
two digits, and drop that sum in the middle.

    52 -> 5 | 2 -> 5+2=7 -> 572
    52 x 11 = 572. Matches.

THE CATCH EVERYONE FORGETS: if the digits add to 10 or more, that middle
digit doesn't fit — carry the 1 into the left digit.

    87 -> 8 | 7 -> 8+7=15 -> carry: (8+1) 5 7 -> 957
    87 x 11 = 957. Matches.

VERIFIED AT IMPORT
    52 * 11 == 572 (no-carry case)     87 * 11 == 957 (carry case)
    both trick results match real multiplication exactly

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 12
END_A, END_B = 44, 96
END_WHY, END_TAKE, END_SHARE = 117, 132, 138

SERIES = "MENTAL MATH TRICKS"

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
def split(n):
    return divmod(n, 10)


def x11_trick(n):
    a, b = split(n)
    s = a + b
    if s < 10:
        return a * 100 + s * 10 + b
    return (a + 1) * 100 + (s - 10) * 10 + b


N1, N2 = 52, 87
assert x11_trick(N1) == N1 * 11 == 572
assert x11_trick(N2) == N2 * 11 == 957
A1, B1 = split(N1)
A2, B2 = split(N2)
assert A1 + B1 < 10
assert A2 + B2 >= 10


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


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


class TrickTimes11(Scene):
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
        self.stage_easy()
        self.stage_carry()
        self.stage_why()
        self.takeaway("Try it on any two-digit number.",
                      "It works every single time.")
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

    def set_work(self, s, color, beats=2.5, size=26):
        new = txt(s, size, color, bold=True, w=4.6)
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
        big = txt("split. add. insert.", 30, GOLD, w=4.5)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("multiply by 11 in your head", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("no calculator. three seconds.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("split. add. insert.", 28, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_easy(self):
        self.set_work(f"{N1}", WHITE_, 2)
        self.say(f"split it: {A1} and {B1}.", 3)
        self.set_work(f"{A1}   |   {B1}", SKY, 2.5)
        self.say("add the two digits.", 2.5)
        self.set_work(f"{A1} + {B1} = {A1+B1}", GOLD, 2.5)
        self.say("drop that sum right in the middle.", 3.5)
        self.set_work(f"{A1}  {A1+B1}  {B1}  ->  {N1*11}", GREEN, 3)
        self.say(f"check it: {N1} × 11 = {N1*11}. matches.", 3.5)
        self.pad_to(END_A)

    def stage_carry(self):
        self.say("try a harder one. 87.", 3)
        self.set_work(f"{N2}", WHITE_, 2)
        self.set_work(f"{A2}   |   {B2}", SKY, 2.5)
        self.say(f"{A2} + {B2} = {A2+B2}. that's two digits — too big to fit.", 3.5)
        self.set_work(f"{A2} + {B2} = {A2+B2}  (carry the 1)", ROSE, 3)
        self.say("carry the 1 into the left digit instead.", 3.5)
        self.set_work(f"({A2}+1)  {A2+B2-10}  {B2}  ->  {N2*11}", GOLD, 3)
        self.say(f"check it: {N2} × 11 = {N2*11}. still matches.", 3.5)
        self.set_work("works every time — with or without the carry", GREEN, 3)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("why? 11 × n is just 10n + n.", 3)
        self.set_work("shift it over, then add — that IS the trick", GOLD, 3.5)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 28, WHITE_, w=4.5).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 25, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to someone who says", 27, WHITE_, w=4.5)
        s2 = txt("they're \"bad at math\"", 27, GOLD, w=4.6)
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
