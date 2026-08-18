"""
the_series — connective tissue for the OBSERVER COLLAPSE long cut.

    BPM=150 manimgl the_series.py SeriesOpen   -w -r 1080x1920
    BPM=150 manimgl the_series.py SeriesBridge1 -w -r 1080x1920
    BPM=150 manimgl the_series.py SeriesBridge2 -w -r 1080x1920
    BPM=150 manimgl the_series.py SeriesOutro  -w -r 1080x1920

NOT A VIDEO. These are the four short pieces that get stitched between the three
episodes to make the single YouTube cut. `build_series.sh` does the stitching.

WHY THE EPISODES TRIM AT 34.400s. Every episode in this shell runs its content
to beat 86 and then spends beats 86-100 on the follow card and the signature.
34.400s IS beat 86 at 150 BPM, and 34.4 * 60 = 2064 frames exactly, so the cut
lands on a frame boundary rather than between two. Three sign-offs in a row
would be the only thing wrong with a naive concatenation, so the long cut takes
0-34.400s of each episode and ends on ONE signature.

    open      10 beats     4.0 s
    bridge     8 beats     3.2 s   (x2)
    outro     20 beats     8.0 s
    total             121.6 s  =  304 beats

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats), always a multiple of 0.25 beats
    Scene.run() is manimlib's OWN entry point — never name a method run()
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"

FRAME_H = 9.0
LINE_Y  = -2.05

EPISODE_TRIM = 34.4                        # seconds. beat 86.
assert abs(EPISODE_TRIM * FPS - round(EPISODE_TRIM * FPS)) < 1e-9, \
    "the trim has to land on a whole frame"
assert round(EPISODE_TRIM * FPS) == 2064


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


class Beat(Scene):
    """Shared clock. Subclasses set TOTAL and fill in body()."""
    TOTAL = 8

    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.body()
        self.pad_to(self.TOTAL)

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

    def body(self):
        raise NotImplementedError


class SeriesOpen(Beat):
    TOTAL = 10

    def body(self):
        a = txt("OBSERVER COLLAPSE", 42, GOLD, w=4.6)
        a.move_to(np.array([0, 0.95, 0]))
        b = txt("what an observer can have", 27, WHITE_, w=4.4)
        b.move_to(np.array([0, 0.18, 0]))
        c = txt("and what it never will", 27, SKY, w=4.4)
        c.move_to(np.array([0, -0.42, 0]))
        d = txt("three parts", 21, GREY, bold=False, w=2.4)
        d.move_to(np.array([0, -1.25, 0]))
        self.play(FadeIn(a, scale=1.10), run_time=self.T(2), rate_func=rush_from)
        self.play(FadeIn(b), run_time=self.T(1.5))
        self.play(FadeIn(c), run_time=self.T(1.5))
        self.play(FadeIn(d), run_time=self.T(1.5))
        self.pad_to(8.5)
        self.play(FadeOut(VGroup(a, b, c, d)), run_time=self.T(1.5))


class Bridge(Beat):
    TOTAL = 8
    TOP, BOT = "", ""

    def body(self):
        a = txt(self.TOP, 30, GREY, bold=False, w=4.4)
        a.move_to(np.array([0, 0.42, 0]))
        b = txt(self.BOT, 32, GOLD, w=4.5)
        b.move_to(np.array([0, -0.38, 0]))
        self.play(FadeIn(a, shift=0.12 * UP), run_time=self.T(1.75))
        self.play(FadeIn(b, shift=0.12 * UP), run_time=self.T(1.75))
        self.pad_to(6.5)
        self.play(FadeOut(VGroup(a, b)), run_time=self.T(1.5))


class SeriesBridge1(Bridge):
    TOP = "that was one box,"
    BOT = "and one line of sight."


class SeriesBridge2(Bridge):
    TOP = "you have seen the room."
    BOT = "now stand up in it."


class SeriesOutro(Beat):
    TOTAL = 20

    def body(self):
        a = txt("it can measure where you are.", 29, WHITE_, w=4.6)
        a.move_to(np.array([0, 1.30, 0]))
        b = txt("it cannot measure that you know.", 29, GOLD, w=4.6)
        b.move_to(np.array([0, 0.62, 0]))
        self.play(FadeIn(a, shift=0.10 * UP), run_time=self.T(2))
        self.play(FadeIn(b, shift=0.10 * UP), run_time=self.T(2))
        self.pad_to(6)
        self.play(FadeOut(VGroup(a, b)), run_time=self.T(1.5))

        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.10, 0])).scale(0.74)
        self.play(ShowCreation(eye), run_time=self.T(2.5))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.42, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.5))
        cta = txt("@observer.collapse", 25, GREY, bold=False)
        cta.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cta, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(18.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cta),
                  run_time=self.T(1.5))
