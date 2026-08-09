"""
sine_unroll — why it is called a sine WAVE. 28.8s.

    BPM=150 manimgl sine_unroll.py SineUnroll -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

ONE PICTURE CARRIES SIX RUNGS. Third in the ladder family, after
circle_ladder.py and square_ladder.py, and built on the same shell: nothing is
ever added to the picture, only relabelled.

A point P goes round a circle on the left. To its right is a window on the last
1.2 wavelengths of its HEIGHT — the newest sample sits against the circle and
older ones slide right, so the wave never runs off the frame:

    wave(x, t) = A·R·sin( t − k·f·(x − X0) )      wave(X0, t) = the dot's height

    1   one point, going round                     the circle
    2   its HEIGHT, drawn over time                y = sin t
    3   a SECOND point, a quarter turn ahead       y = cos t
    4   slide the gold wave a quarter wavelength   cos t = sin(t + 90°)
    5   spin faster / draw it bigger               y = A·sin(f t)
    6   look at the circle edge-on                 y = sin t

RUNG 3 IS WHY THERE IS A SECOND DOT. cos t is plotted as a height, but on the
circle it is a WIDTH — so a horizontal connector from P to the cosine pen would
be a lie. sin(t + 90°) == cos t exactly, so a second dot a quarter turn ahead of
P has cos t as its HEIGHT, and the same honest horizontal connector works. It
also makes rung 4 something the viewer has already watched happen.

RUNG 4 PROVES THE SHIFT rather than asserting it: a ghost of the gold wave
slides right by exactly a quarter wavelength, pi/(2k) screen units, and lands on
the blue one.

RUNG 6 IS THE PAYOFF AND IT IS LITERALLY TRUE. Squash the circle to a vertical
line — that is what circular motion looks like from the side — and the dot is
left going up and down, still driving the same wave.

VERIFIED AT IMPORT
    cos t == sin(t + pi/2)                    2000 angles, 1e-12
    sin has period 2 pi                       2000 angles, 1e-12
    the pen at X0 equals the dot's height     2000 angles, exactly
    the quarter-wavelength slide lands on cos 2000 angles x the whole window

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    an updater that hard-codes opacity fights FadeIn and .animate.set_opacity()
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 72

END_OPEN = 4
END_R1, END_R2, END_R3, END_R4, END_R5, END_R6 = 12, 22, 32, 42, 52, 60
END_TAKE = 64

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
EQ_Y    = 2.55
NOTE_Y  = -2.30

CX, CY = -1.38, 0.35         # the circle
R0 = 0.95
X0, X1 = -0.12, 1.92         # the window on the wave
K = np.pi                    # radians of phase per screen unit at f = 1
NS = 150                     # samples across the window
SPIN = 0.62                  # radians of theta per beat at f = 1
QUARTER = np.pi / (2 * K)    # a quarter wavelength, in screen units

LADDER = [
    ("one point, going round",  "watch one point travel round a circle"),
    ("y = sin t",               "now draw its HEIGHT, over time"),
    ("y = cos t",               "a second point, a quarter turn ahead"),
    ("cos t = sin(t + 90°)",    "same wave. it just started earlier."),
    ("y = A · sin(f t)",        "spin faster and the wave tightens"),
    ("y = sin t",               "now look at the circle edge-on"),
]
assert len(LADDER) == 6


# ---------------------------------------------------------------- verified
_ts = np.linspace(0, 4 * np.pi, 2000)
assert np.allclose(np.cos(_ts), np.sin(_ts + np.pi / 2), atol=1e-12)
assert np.allclose(np.sin(_ts), np.sin(_ts + 2 * np.pi), atol=1e-12)

_xs = np.linspace(X0, X1, NS)


def _wave(th, xs, f=1.0, phase=0.0):
    return np.sin(th - K * f * (xs - X0) + phase)


# the newest sample, hard against the circle, IS the dot's height
assert np.allclose(_wave(_ts, np.array([X0]).reshape(-1, 1), 1.0).ravel(),
                   np.sin(_ts), atol=1e-15)
# sliding the sine right by a quarter wavelength gives the cosine, everywhere
for _t in _ts[::7]:
    assert np.allclose(_wave(_t, _xs - QUARTER), np.cos(_t - K * (_xs - X0)),
                       atol=1e-12)


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def poly(pts, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners(pts)
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


class SineUnroll(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.eq = None
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.theta = ValueTracker(0.0)
        self.amp = ValueTracker(1.0)
        self.freq = ValueTracker(1.0)
        self.squash = ValueTracker(1.0)          # 1 = round, 0 = edge-on
        self.op_sin = ValueTracker(0.0)
        self.op_cos = ValueTracker(0.0)
        self.op_q = ValueTracker(0.0)
        self.gshift = ValueTracker(0.0)
        self.gop = ValueTracker(0.9)
        self.add(self.amp, self.freq, self.squash)

        self.spinning = False
        self.theta.add_updater(
            lambda m, dt: m.increment_value(
                dt * SPIN * self.freq.get_value() / self.B) if self.spinning else None)
        self.add(self.theta)

        self.open_card()
        self.build_picture()
        self.rung1()
        self.rung2()
        self.rung3()
        self.rung4()
        self.rung5()
        self.rung6()
        self.takeaway("A sine wave is a circle,", "seen from the side.")
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

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.06):
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def say(self, s, beats=2, color=WHITE_, size=24, extra=()):
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), *extra, run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), *extra,
                      run_time=self.T(beats))
            self.note = new

    def show_eq(self, s, beats=2, color=WHITE_, size=30):
        body = s if isinstance(s, VMobject) else txt(s, size, color, w=4.6)
        new = self.dance(body.move_to(np.array([0, EQ_Y, 0])))
        if self.eq is None:
            self.eq = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.eq.clear_updaters()
            self.play(FadeOut(self.eq, shift=0.12 * UP),
                      FadeIn(new, shift=0.12 * UP), run_time=self.T(beats))
            self.eq = new

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("WHY IS IT CALLED", 34, WHITE_, w=4.6),
                     txt("A SINE WAVE?", 44, GOLD, w=4.6)).arrange(DOWN, buff=0.22)
        big.move_to(np.array([0, 0.85, 0]))
        sub = txt("watch the circle unroll", 24, GREY, bold=False)
        sub.move_to(np.array([0, -0.10, 0]))
        self.add(big, sub)
        self.wait(self.T(3))
        self.title = txt("ONE CIRCLE, SIX EQUATIONS", 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.play(FadeOut(big), FadeOut(sub), FadeIn(self.title),
                  run_time=self.T(1))
        self.pad_to(END_OPEN)

    # ------------------------------------------------------------------
    def pt(self, th):
        """A point on the circle, honouring amplitude and the edge-on squash."""
        a, s = self.amp.get_value(), self.squash.get_value()
        return np.array([CX + s * a * R0 * np.cos(th),
                         CY + a * R0 * np.sin(th), 0.0])

    def wave_pts(self, phase=0.0, shift=0.0):
        th, a, f = (self.theta.get_value(), self.amp.get_value(),
                    self.freq.get_value())
        xs = np.linspace(X0, X1, NS)
        ys = CY + a * R0 * np.sin(th - K * f * (xs - shift - X0) + phase)
        return np.stack([xs, ys, np.zeros_like(xs)], axis=1)

    def build_picture(self):
        ring = VMobject(stroke_color=GREY, stroke_width=2.6)
        ring.add_updater(lambda m: m.set_points_as_corners(
            [self.pt(u) for u in np.linspace(0, 2 * np.pi, 121)]))
        axis = poly([np.array([X0, CY, 0]), np.array([X1, CY, 0])], FAINT, 2.0)
        vaxis = VMobject(stroke_color=FAINT, stroke_width=2.0)
        vaxis.add_updater(lambda m: m.set_points_as_corners(
            [np.array([CX, CY - 1.30, 0]), np.array([CX, CY + 1.30, 0])]))

        dotP = Dot(ORIGIN, radius=0.095, fill_color=GOLD)
        dotP.add_updater(lambda m: m.move_to(self.pt(self.theta.get_value())))
        dotQ = Dot(ORIGIN, radius=0.085, fill_color=COOL)
        dotQ.add_updater(lambda m: (
            m.move_to(self.pt(self.theta.get_value() + np.pi / 2)),
            m.set_opacity(self.op_q.get_value())))

        sinw = VMobject(stroke_color=GOLD, stroke_width=3.4)
        sinw.add_updater(lambda m: (m.set_points_as_corners(self.wave_pts()),
                                    m.set_stroke(GOLD, 3.4,
                                                 opacity=self.op_sin.get_value())))
        cosw = VMobject(stroke_color=COOL, stroke_width=3.4)
        cosw.add_updater(
            lambda m: (m.set_points_as_corners(self.wave_pts(np.pi / 2)),
                       m.set_stroke(COOL, 3.4, opacity=self.op_cos.get_value())))

        linkP = VMobject(stroke_color=GOLD, stroke_width=1.8)
        linkP.add_updater(lambda m: self.link(m, 0.0, GOLD, self.op_sin))
        linkQ = VMobject(stroke_color=COOL, stroke_width=1.8)
        linkQ.add_updater(lambda m: self.link(m, np.pi / 2, COOL, self.op_cos))

        self.pic = VGroup(vaxis, axis, ring, sinw, cosw, linkP, linkQ, dotQ, dotP)
        self.add(self.pic)
        self.spinning = True

    def link(self, m, phase, color, op):
        """The horizontal connector: the dot's HEIGHT is the pen's height."""
        th, a = self.theta.get_value(), self.amp.get_value()
        y = CY + a * R0 * np.sin(th + phase)
        p = self.pt(th + phase)
        m.set_points_as_corners([p, np.array([X0, y, 0])])
        m.set_stroke(color, 1.8, opacity=0.55 * op.get_value())

    # ==================================================================
    def rung1(self):
        self.show_eq(LADDER[0][0], 2)
        self.say(LADDER[0][1], 2)
        self.say("that is the whole ingredient list", 2)
        self.pad_to(END_R1)

    def rung2(self):
        self.show_eq(LADDER[1][0], 2)
        self.play(self.op_sin.animate.set_value(1.0), run_time=self.T(2))
        self.say(LADDER[1][1], 2)
        self.say("the height IS the wave — nothing else happened", 2)
        self.pad_to(END_R2)

    def rung3(self):
        self.show_eq(LADDER[2][0], 2)
        self.play(self.op_q.animate.set_value(1.0), run_time=self.T(2))
        self.say(LADDER[2][1], 2)
        self.play(self.op_cos.animate.set_value(1.0), run_time=self.T(2))
        self.say("its height is cos t", 2, COOL)
        self.pad_to(END_R3)

    def rung4(self):
        self.show_eq(LADDER[3][0], 2, GOLD)
        self.say("the blue wave is the gold one, moved", 2)

        # A ghost of the sine slides a quarter wavelength right, onto the cosine.
        # It is driven by a shift TRACKER rather than being a frozen copy that
        # gets .shift()ed — a snapshot would fall behind the live wave over the
        # three beats of the slide and land on nothing.
        ghost = VMobject(stroke_color=GOLD, stroke_width=5.0)
        ghost.add_updater(lambda m: (
            m.set_points_as_corners(self.wave_pts(shift=self.gshift.get_value())),
            m.set_stroke(GOLD, 5.0, opacity=self.gop.get_value())))
        self.add(ghost)
        self.play(self.gshift.animate.set_value(QUARTER),
                  run_time=self.T(3), rate_func=smooth)
        # once it has landed, thin the ghost out so the blue wave shows through
        # underneath it — otherwise the thick gold simply hides what it matched
        self.say(LADDER[3][1], 2, GOLD,
                 extra=[self.gop.animate.set_value(0.30)])
        self.play(FadeOut(ghost), run_time=self.T(1))
        self.pad_to(END_R4)

    def rung5(self):
        self.show_eq(LADDER[4][0], 2)
        self.play(self.freq.animate.set_value(2.2), run_time=self.T(2))
        self.say(LADDER[4][1], 1.5, GOLD)
        self.play(self.freq.animate.set_value(1.0), run_time=self.T(1))
        self.play(self.amp.animate.set_value(1.20), run_time=self.T(1.5))
        self.say("a bigger circle makes a taller wave", 1)
        self.play(self.amp.animate.set_value(1.0), run_time=self.T(1))
        self.pad_to(END_R5)

    def rung6(self):
        self.show_eq(LADDER[5][0], 2, GOLD)
        self.play(self.squash.animate.set_value(0.04),
                  run_time=self.T(3), rate_func=smooth)
        self.say(LADDER[5][1], 2, GOLD)
        self.pad_to(END_R6)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        # the equation stays: it arrives on the last beat of rung 6 and would
        # otherwise be cleared before anyone read it
        self.spinning = False
        keep = (self.clock, self.theta, self.amp, self.freq, self.squash,
                self.title, self.eq)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None
        l1 = txt(a, 28, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 26, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(END_TAKE)
        self.eq.clear_updaters()
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq),
                  FadeOut(self.title), run_time=self.T(1))
        self.eq = None

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
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
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))
