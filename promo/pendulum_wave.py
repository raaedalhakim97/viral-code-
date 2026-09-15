"""
pendulum_wave — ten pendulums, one release, and they come back. 60.0s.

    BPM=150 manimgl pendulum_wave.py PendulumWave -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

ENTERTAINMENT EPISODE. No lesson, no formula on screen until the payoff —
this one is built to be watched, not studied. Same house grade, same
signature, far less talking.

THE SETUP. Ten pendulums, released at the same instant, all pushed the
same distance sideways. Their lengths are chosen so that in one 22-second
cycle, pendulum k completes exactly 16+k full swings — 16, 17, 18, ... 25.

Because a pendulum's frequency depends only on its length (f ∝ 1/√L, so
L ∝ 1/f²), picking those swing counts fixes the lengths exactly. Nothing
is driving them, nothing is connecting them, and no two are ever nudged
back into place. They drift apart into what looks like total noise — and
then, 22 seconds later, every one of them is back in line at the same
instant, because every one has completed a whole number of swings.

The video shows the cycle twice: chaos, snap, chaos, snap.

VERIFIED AT IMPORT
    L * f² is the same constant for all ten     real pendulum physics
    every pendulum's swing count per cycle is a whole number
    the smallest vertical gap between bobs exceeds a bob diameter
    max swing angle 5.93° — small-angle regime, so period really is
        amplitude-independent and the realignment is exact
    the motion window is exactly 2 cycles long (44.000s = 2 x 22.0s)

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
import math

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 8
MOTION_START, MOTION_END = 10, 120
END_TAKE, END_SHARE = 132, 138

SERIES = "SATISFYING MATH"

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
NOTE_Y = -3.30
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
N = 10
N0 = 16
CYCLE = 22.0

L0 = 5.2
AMP = 0.22
BOB_R = 0.075
PIVOT_Y = 2.6
X_SPAN = 4.2

SWINGS = [N0 + k for k in range(N)]
LENGTHS = [L0 * (N0 / (N0 + k)) ** 2 for k in range(N)]
FREQS = [s / CYCLE for s in SWINGS]
PIVOT_X = [-X_SPAN / 2 + X_SPAN * k / (N - 1) for k in range(N)]

# a real pendulum's length scales as 1 / frequency^2
for _k in range(N):
    assert abs(LENGTHS[_k] * FREQS[_k] ** 2 - LENGTHS[0] * FREQS[0] ** 2) < 1e-9

# whole number of swings per cycle — this is what makes them realign
for _k in range(N):
    assert abs(FREQS[_k] * CYCLE - round(FREQS[_k] * CYCLE)) < 1e-12

# bobs must never collide
assert min(LENGTHS[_k] - LENGTHS[_k + 1] for _k in range(N - 1)) > 2 * BOB_R

# small-angle regime, so the period really is amplitude-independent
MAX_THETA = math.asin(AMP / LENGTHS[-1])
assert MAX_THETA < 0.2

# the motion window is exactly two full cycles
assert abs((MOTION_END - MOTION_START) * (60.0 / BPM) - 2 * CYCLE) < 1e-9


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


def bob_xy(k, t):
    """Horizontal offset is AMP*cos(2*pi*f*t); the bob rides the arc of
    its own arm, so the height follows from the arm length."""
    x = AMP * math.cos(2 * math.pi * FREQS[k] * t)
    return (PIVOT_X[k] + x,
            PIVOT_Y - math.sqrt(LENGTHS[k] ** 2 - x ** 2))


class PendulumWave(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_wave()
        self.takeaway("Nothing is coordinating them.",
                      "Ten lengths. That's the whole trick.")
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

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("they come back.", 32, GOLD, w=4.5)
        big.move_to(np.array([0, 0.85, 0]))
        q = txt("ten pendulums, one release", 26, WHITE_, w=4.6)
        q.move_to(np.array([0, -0.10, 0]))
        sub = txt("nothing is connecting them.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.80, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.play(FadeOut(big), FadeOut(q), FadeOut(sub),
                  FadeIn(self.title), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def build_wave(self):
        bar = seg(np.array([PIVOT_X[0] - 0.25, PIVOT_Y, 0]),
                  np.array([PIVOT_X[-1] + 0.25, PIVOT_Y, 0]), FAINT, 2.0, 0.8)
        grp = VGroup()
        for k in range(N):
            bx, by = bob_xy(k, 0.0)
            arm = seg(np.array([PIVOT_X[k], PIVOT_Y, 0]),
                      np.array([bx, by, 0]), DIM, 1.3, 0.8)
            bob = Dot(np.array([bx, by, 0]), radius=BOB_R, fill_color=GOLD)
            grp.add(VGroup(arm, bob))
        return bar, grp

    def stage_wave(self):
        bar, wave = self.build_wave()
        self.wave = wave
        # FadeIn on the group itself, not LaggedStartMap: AnimationGroup builds
        # a fresh VGroup of the children, so the scene would track that copy and
        # never call this group's updater. lag_ratio still staggers the reveal.
        self.play(FadeIn(bar), FadeIn(wave, lag_ratio=0.06), run_time=self.T(2))
        self.add(wave)

        t0 = self.clock.get_value()

        def swing(m):
            t = self.clock.get_value() - t0
            for k, pend in enumerate(m):
                bx, by = bob_xy(k, t)
                pend[0].set_points_as_corners([
                    np.array([PIVOT_X[k], PIVOT_Y, 0]),
                    np.array([bx, by, 0])])
                pend[1].move_to(np.array([bx, by, 0]))

        wave.add_updater(swing)

        self.say("ten pendulums. released together.", 3)
        self.pad_to(22)
        self.say("watch them come apart.", 3)
        self.pad_to(45)
        self.say("no pattern. nothing in step.", 3.5)
        self.pad_to(61)
        self.say("wait.", 2.5, GOLD)
        self.pad_to(65)

        # first realignment lands exactly here
        self.say("...and they're back. all ten.", 3, GOLD)
        self.eq = txt("every 22 seconds.", 26, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeIn(self.eq), run_time=self.T(2))

        self.pad_to(85)
        self.say("nothing is connecting them.", 3)
        self.pad_to(100)
        self.say("the only difference is length.", 3.5)
        self.pad_to(114)
        self.say("here it comes again.", 3, GOLD)
        self.pad_to(MOTION_END)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 28, WHITE_, w=4.4).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 25, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to someone who needs", 26, WHITE_, w=4.5)
        s2 = txt("sixty seconds of calm", 26, GOLD, w=4.6)
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
