"""
times_table_dance — 400 dots, one multiplication, thirty seconds. 40.0s.

    BPM=150 manimgl times_table_dance.py TimesTableDance -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

ALMOST NO WORDS. One line at the top of the video, one at the end, and
in between thirty seconds of uninterrupted movement. The figure is the
content; anything written over it is a distraction.

THE INSTRUCTION, never stated on screen:

    400 dots round a circle, numbered 0 to 399
    join every dot n to dot k*n

k = 2 gives a cardioid. Push k upward and the figure never stops moving,
because the k times table draws k - 1 lobes and k is always climbing.

WHY IT LOOKS LIKE DANCING RATHER THAN SLIDING. k is not swept at a
constant rate. It runs on

        k(s) = 2 + s - (A / 2pi) * sin(2 pi s)

so dk/ds = 1 - A*cos(2 pi s): near an integer the speed drops to 0.1 and
the shape HOLDS, between integers it rises to 1.9 and the whole thing
whips through. One clean figure per bar, nineteen bars, and every hold
lands on a downbeat. The motion is continuous the whole way through --
nothing cuts, nothing restarts.

A quarter-turn of drift is layered on top so the figure travels instead
of pulsing in place.

VERIFIED AT IMPORT
    the envelope of the chord family is solved numerically and its cusps
    counted for every k the sweep passes through: always exactly k - 1
    the envelope's inner radius matches (k-1)/(k+1)
    k(s) is checked to be strictly increasing and to land on an integer
    at every integer s, so the holds cannot drift off the beat
    the ring is asserted to fit the platform safe box

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    AnimationGroup rebuilds a VGroup of its children, so a group carrying
    an updater must be self.add()ed, never introduced by LaggedStartMap
"""
import os

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
N = 400
K0 = 2                                    # first multiplier
UNITS = 12                                # ...and it climbs this many
BEATS_PER_UNIT = 6                        # 2.4s a shape: hold, whip, hold
# past about k=14 four hundred chords stop being a figure and become grey
# mush, so the sweep stops there rather than running on into noise
assert K0 + UNITS <= 14
EASE_A = 0.9                              # 0 = constant speed, ->1 = big holds
ROT_TURNS = 0.25                          # gentle drift over the whole dance

assert UNITS * BEATS_PER_UNIT == END_DANCE - END_HOOK


def k_of(s):
    """Climbs by 1 per unit of s, but crawls near integers and whips between."""
    return K0 + s - (EASE_A / (2 * np.pi)) * np.sin(2 * np.pi * s)


_s = np.linspace(0, UNITS, 20001)
assert np.all(np.diff(k_of(_s)) > 0)                       # never goes backwards
for _i in range(UNITS + 1):
    assert abs(k_of(_i) - (K0 + _i)) < 1e-12               # holds land on integers
assert 0 < 1 - EASE_A < 1                                  # the hold is a hold


def _envelope(k, M=60000):
    """Envelope of the chord family, solved as F = dF/dtheta = 0."""
    th = np.linspace(0, 2 * np.pi, M, endpoint=False)
    ax, ay = np.cos(th), np.sin(th)
    bx, by = np.cos(k * th), np.sin(k * th)
    a, b = -(by - ay), (bx - ax)
    c = (by - ay) * ax - (bx - ax) * ay
    da = -(k * np.cos(k * th) - np.cos(th))
    db = -k * np.sin(k * th) + np.sin(th)
    dc = ((k * np.cos(k * th) - np.cos(th)) * ax + (by - ay) * (-np.sin(th))
          - (-k * np.sin(k * th) + np.sin(th)) * ay - (bx - ax) * np.cos(th))
    det = a * db - b * da
    ok = np.abs(det) > 1e-9
    d = np.where(ok, det, 1.0)
    return np.stack([((-c * db + b * dc) / d)[ok],
                     ((-a * dc + c * da) / d)[ok]], 1)


def _lobes(k):
    e = np.diff(_envelope(k), axis=0)
    sp = np.hypot(e[:, 0], e[:, 1])
    low = sp < sp.mean() * 0.05
    return int(np.sum((low.astype(int) - np.roll(low, 1).astype(int)) == 1))


for _k in range(K0, K0 + UNITS + 1):
    assert _lobes(_k) == _k - 1, (_k, _lobes(_k))
    _r = np.hypot(*_envelope(_k).T)
    assert abs(_r.min() - (_k - 1) / (_k + 1)) < 5e-3
    assert abs(_r.max() - 1.0) < 5e-3

# ------------------------------------------------------------------ layout
RING_C = np.array([0.0, 0.15, 0])
R = 1.62
assert R <= SAFE_X - 0.05
assert RING_C[1] - R - 0.10 > NOTE_Y + 0.20
assert RING_C[1] + R + 0.10 < READ_Y - 0.22

IDX = np.arange(N)
BASE = 2 * np.pi * IDX / N + np.pi / 2


def ring_points(mult, phase):
    """Both ends of all N chords at once."""
    a = BASE + phase
    b = 2 * np.pi * (IDX * mult) / N + np.pi / 2 + phase
    A = RING_C + R * np.stack([np.cos(a), np.sin(a), np.zeros(N)], 1)
    B = RING_C + R * np.stack([np.cos(b), np.sin(b), np.zeros(N)], 1)
    return A, B


def wheel(n):
    """Gold -> rose -> sky -> gold, once round the ring."""
    stops = [GOLD, ROSE, SKY, GOLD]
    t = (n / N) * 3.0
    i = min(int(t), 2)
    return interpolate_color(stops[i], stops[i + 1], t - i)


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


class TimesTableDance(Scene):
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

        self.st = ValueTracker(0.0)
        self.build_ring()
        self.hook()
        self.dance()
        self.close()
        self.signature()

    # ------------------------------------------------------------------
    def build_ring(self):
        self.chords = VGroup(*[
            VMobject(stroke_color=wheel(n), stroke_width=0.95)
            for n in range(N)])

        def upd(grp):
            s = self.st.get_value()
            k = k_of(s)
            phase = 2 * np.pi * ROT_TURNS * (s / UNITS)
            A, B = ring_points(k, phase)
            mid = 0.5 * (A + B)
            for n, m in enumerate(grp):
                # a straight chord as one quadratic bezier: start, mid, end
                m.set_points(np.array([A[n], mid[n], B[n]]))
            # crossings pile up as k climbs; fade the strokes to match or the
            # figure saturates into a flat grey disc
            grp.set_stroke(opacity=float(np.clip(0.52 * 6.0 / (k + 4.0),
                                                 0.13, 0.52)))

        self.chords.add_updater(upd)
        upd(self.chords)
        # the group carries the updater, so it is added directly — an
        # AnimationGroup would rebuild it and the updater would never fire
        self.add(self.chords)

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
        """One line. It leaves before the dance starts and does not come back."""
        self.read = Integer(K0, font_size=34).set_fill(DIM)
        self.read.add_updater(lambda m: (
            m.set_value(int(round(k_of(self.st.get_value())))),
            m.move_to(np.array([0, READ_Y, 0]))))
        self.line = txt("the 2 times table drew this.", 27, WHITE_, bold=False)
        self.line.move_to(np.array([0, NOTE_Y, 0]))
        self.add(self.read, self.line)
        self.wait(self.T(6))
        self.play(FadeOut(self.line), run_time=self.T(2))

    # ==================================================================
    def dance(self):
        """One continuous move. No cuts, no captions, nothing to read."""
        self.play(self.st.animate.set_value(float(UNITS)),
                  run_time=self.T(END_DANCE - self.used), rate_func=linear)

    # ------------------------------------------------------------------
    def close(self):
        self.chords.clear_updaters()
        self.read.clear_updaters()
        s1 = txt("Comment a times table", 27, WHITE_)
        s2 = txt("and I'll run it", 27, GOLD)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.chords), FadeOut(self.read),
                  run_time=self.T(2))
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
