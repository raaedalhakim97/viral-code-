"""
trick_sub_1000 — subtract any 3-digit number from 1000, instantly. 60.0s.

    BPM=150 manimgl trick_sub_1000.py TrickSub1000 -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE 5 OF "MENTAL MATH TRICKS". Same shell: the rule is pinned at the
TOP for the whole video. Plain language — built so someone who "isn't a
math person" can follow every step.

THE TRICK. 1000 minus a 3-digit number, with zero borrowing: subtract the
first two digits from 9, and the last digit from 10.

    1000 - 457:  9-4=5,  9-5=4,  10-7=3  ->  543
    1000 - 457 = 543. Matches.

A second example, to show it isn't a one-off:

    1000 - 138:  9-1=8,  9-3=6,  10-8=2  ->  862
    1000 - 138 = 862. Matches.

VERIFIED AT IMPORT
    1000 - 457 == 543 exactly     1000 - 138 == 862 exactly
    both trick results match real subtraction exactly

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
def digits3(n):
    h, r = divmod(n, 100)
    t, u = divmod(r, 10)
    return h, t, u


def sub1000_trick(n):
    h, t, u = digits3(n)
    return (9 - h) * 100 + (9 - t) * 10 + (10 - u)


N1, N2 = 457, 138
D1 = digits3(N1)
D2 = digits3(N2)
assert D1[2] != 0 and D2[2] != 0
assert sub1000_trick(N1) == 1000 - N1 == 543
assert sub1000_trick(N2) == 1000 - N2 == 862


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


class TrickSub1000(Scene):
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
        self.stage_harder()
        self.stage_why()
        self.takeaway("No borrowing. No carrying.",
                      "Instant subtraction from a thousand.")
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

    def set_work(self, s, color, beats=2.5, size=25):
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
        big = txt("9, 9, 10 — minus each digit", 24, GOLD, w=4.6)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("subtract from 1000 instantly", 26, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("zero borrowing. zero carrying.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("9, 9, 10 — minus each digit", 22, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_easy(self):
        h, t, u = D1
        self.set_work(f"1000 − {N1}", WHITE_, 2.5)
        self.say("first two digits: subtract from 9.", 3)
        self.set_work(f"9−{h}={9-h}     9−{t}={9-t}", SKY, 2.5)
        self.say("last digit: subtract from 10 instead.", 3.5)
        self.set_work(f"10−{u}={10-u}", ROSE, 2)
        self.say("put them together. that's the answer.", 3)
        self.set_work(f"{9-h}  {9-t}  {10-u}  ->  {1000-N1}", GOLD, 3)
        self.say(f"check it: 1000 − {N1} = {1000-N1}. matches.", 3.5)
        self.pad_to(END_A)

    def stage_harder(self):
        h, t, u = D2
        self.say("try another. 1000 minus 138.", 3)
        self.set_work(f"1000 − {N2}", WHITE_, 2.5)
        self.set_work(f"9−{h}={9-h}     9−{t}={9-t}     10−{u}={10-u}", SKY, 3)
        self.set_work(f"{9-h}  {9-t}  {10-u}  ->  {1000-N2}", GOLD, 3)
        self.say(f"check it: 1000 − {N2} = {1000-N2}. still matches.", 3.5)
        self.set_work("no regrouping, ever — just read it off", GREEN, 3)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("why? 999 minus anything never needs to borrow.", 3.5)
        self.set_work("1000 = 999 + 1 — that +1 lands on the last digit", GOLD, 3.5)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 27, WHITE_, w=4.5).move_to(np.array([0, 0.10, 0]))
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
