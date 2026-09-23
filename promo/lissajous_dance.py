"""
lissajous_dance — two sine waves, 1800 dots, thirty seconds. 40.0s.

    BPM=150 manimgl lissajous_dance.py LissajousDance -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

Companion to times_table_dance.py: same recipe, different machine. One
line at the start, one at the end, and thirty seconds of uninterrupted
movement in between.

THE INSTRUCTION, never stated on screen:

    x = sin(3t + pi/2)          side to side
    y = sin(b t)                up and down

One dot per value of t. Eighteen hundred of them. Both coordinates are
plain sine waves — the only thing that ever changes is how fast the
vertical one runs.

WHAT YOU SEE WHEN b LANDS ON A WHOLE NUMBER. The ribbon closes, and the
figure touches the frame a exact number of times:

        b touches on the top and bottom      3 on the left and right

...divided through by any factor b shares with 3. Which is why b = 3
collapses the whole thing to a perfect circle, b = 6 to a figure of
eight, b = 9 to a trefoil — the shared factor folds the curve onto
itself.

WHY IT LOOKS LIKE DANCING RATHER THAN SLIDING. b is moved between whole
numbers on smooth(smooth(t)) — flat at both ends, steep in the middle.
The ribbon HOLDS closed on the whole number, then the loop breaks open
and the whole thing whips through to the next one. One shape every 8
beats — two bars — so every hold lands on a downbeat.

The path is 2 3 4 5 6 7 6 5 4 3: it climbs, turns round and comes back,
resting on b = 3, where the entire figure is a perfect circle. Every
step is one unit, so the ribbon always travels at the same speed.

Nothing here can blur: a dot at parameter t only ever shifts by t*db,
and t never exceeds 2*pi, so no part of the figure runs away from the
rest the way a spinning rim would.

VERIFIED AT IMPORT
    tangencies counted from the exact contact parameters, not sampled:
    for every b in the sweep the figure touches top and bottom b/g times
    and the sides 3/g times, with g = gcd(3, b)
    b = 3 is checked to be a circle to 1e-12
    every integer b is checked to close the loop exactly at t = 2 pi
    the easing is measured, not assumed: near-zero slope over the first
    and last 3% of each move, peak slope above 1.9x the average
    every step of the path is checked to be exactly one unit
    the figure is asserted to fit the platform safe box

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    AnimationGroup rebuilds a VGroup of its children, so a mobject
    carrying an updater must be self.add()ed, never handed to a
    LaggedStartMap
"""
import os
from math import gcd

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_HOOK, END_DANCE, END_SHARE = 8, 80, 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
NOTE_Y = -2.36
LINE_Y = -2.05
READ_Y = 2.62

SAFE_X, SAFE_BOT = 1.68, -2.58
assert NOTE_Y - 0.20 >= SAFE_BOT

# ------------------------------------------------------------------ numbers
# 1800 dots keeps the ribbon solid at the busiest shape: the curve gets
# two and a half times longer between b=2 and b=7, and at 900 the dots
# pulled apart into loose scatter
N = 1800                                  # dots along the ribbon
A_FREQ = 3                                # the horizontal wave, fixed
DELTA = np.pi / 2
BEATS_PER_UNIT = 8                        # two bars a shape: hold, whip, hold

# up to seven and back down, resting on the circle. Every step is one
# unit, so the ribbon always travels at the same speed.
BPATH = [2, 3, 4, 5, 6, 7, 6, 5, 4, 3]
B0 = BPATH[0]
UNITS = len(BPATH) - 1
assert all(abs(b - a) == 1 for a, b in zip(BPATH, BPATH[1:]))
assert UNITS * BEATS_PER_UNIT == END_DANCE - END_HOOK


def held(t):
    """Flat at both ends, steep in the middle: the hold and the whip."""
    return smooth(smooth(t))


_d = np.diff([held(t) for t in np.linspace(0, 1, 2001)]) * 2000
assert _d[:60].max() < 0.10 and _d[-60:].max() < 0.10     # it really holds
assert _d.max() > 1.9                                     # and really whips
assert abs(held(0.0)) < 1e-12 and abs(held(1.0) - 1) < 1e-12


def _touches(b):
    """Distinct contact points with the top edge and the left edge, exact."""
    t_top = np.array([(np.pi / 2 + 2 * k * np.pi) / b for k in range(b)])
    xs = np.round(np.sin(A_FREQ * t_top + DELTA), 9)
    t_left = np.array([(-np.pi / 2 - DELTA + 2 * k * np.pi) / A_FREQ
                       for k in range(A_FREQ)])
    ys = np.round(np.sin(b * t_left), 9)
    return len(set(xs.tolist())), len(set(ys.tolist()))


for _b in sorted(set(BPATH)):
    _g = gcd(A_FREQ, _b)
    assert _touches(_b) == (_b // _g, A_FREQ // _g), (_b, _touches(_b))
    # every whole b closes the ribbon exactly at t = 2 pi
    assert abs(np.sin(_b * 0.0) - np.sin(_b * 2 * np.pi)) < 1e-12

_t = np.linspace(0, 2 * np.pi, 20001)
_r = np.hypot(np.sin(A_FREQ * _t + DELTA), np.sin(3 * _t))
assert _r.max() - _r.min() < 1e-12          # b = 3 really is a circle

# ------------------------------------------------------------------ layout
CTR = np.array([0.0, 0.15, 0])
SX, SY = 1.60, 1.75
assert SX <= SAFE_X - 0.05
assert CTR[1] - SY - 0.10 > NOTE_Y + 0.20
assert CTR[1] + SY + 0.10 < READ_Y - 0.22

TT = np.linspace(0, 2 * np.pi, N, endpoint=False)
_ZERO = np.zeros(N)


def ribbon(b):
    """All N dots at once."""
    return CTR + np.stack([SX * np.sin(A_FREQ * TT + DELTA),
                           SY * np.sin(b * TT), _ZERO], 1)


def wheel(u):
    """Gold -> rose -> sky -> gold, once along the ribbon."""
    stops = [GOLD, ROSE, SKY, GOLD]
    t = u * 3.0
    i = min(int(t), 2)
    return interpolate_color(stops[i], stops[i + 1], t - i)


RGBA = np.array([color_to_rgba(wheel(n / N), 0.90) for n in range(N)])


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=2 * SAFE_X - 0.15):
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


class LissajousDance(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.bt = ValueTracker(float(B0))
        self.build_ribbon()
        self.hook()
        self.dance()
        self.close()
        self.signature()

    # ------------------------------------------------------------------
    def build_ribbon(self):
        self.cloud = DotCloud(ribbon(float(B0)), radius=0.016)
        self.cloud.set_rgba_array(RGBA)

        def upd(m):
            m.set_points(ribbon(self.bt.get_value()))
            m.set_rgba_array(RGBA)

        self.cloud.add_updater(upd)
        upd(self.cloud)
        # carries the updater, so it is added directly — an AnimationGroup
        # would rebuild it and the updater would never fire
        self.add(self.cloud)

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

    # ------------------------------------------------------------------
    def hook(self):
        self.read = Integer(B0, font_size=34).set_fill(DIM)
        self.read.add_updater(lambda m: (
            m.set_value(int(round(self.bt.get_value()))),
            m.move_to(np.array([0, READ_Y, 0]))))
        self.line = txt("two sine waves drew this.", 27, WHITE_, bold=False)
        self.line.move_to(np.array([0, NOTE_Y, 0]))
        self.add(self.read, self.line)
        self.wait(self.T(6))
        self.play(FadeOut(self.line), run_time=self.T(2))

    # ==================================================================
    def dance(self):
        """Nine moves, each two bars. Nothing to read the whole way."""
        for target in BPATH[1:]:
            self.play(self.bt.animate.set_value(float(target)),
                      run_time=self.T(BEATS_PER_UNIT), rate_func=held)
        self.pad_to(END_DANCE)

    # ------------------------------------------------------------------
    def close(self):
        self.cloud.clear_updaters()
        self.read.clear_updaters()
        s1 = txt("Comment two numbers", 27, WHITE_)
        s2 = txt("and I'll draw them", 27, GOLD)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.cloud), FadeOut(self.read), run_time=self.T(2))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), run_time=self.T(1.5))

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
