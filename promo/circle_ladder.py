"""
circle_ladder — dancing equations, drawn as one circle. 28.8s.

    BPM=150 manimgl circle_ladder.py CircleLadder -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

ONE PICTURE CARRIES SIX RUNGS.

A point P goes round the unit circle at angle t. Drop it to the x-axis and you
have a right triangle whose hypotenuse is the radius:

    horizontal leg  =  cos t
    vertical leg    =  sin t
    hypotenuse      =  1

Every rung is that same triangle, relabelled:

    1   a point going round a circle
    2   its height IS sin t
    3   its width  IS cos t
    4   sin^2 t + cos^2 t = 1      — Pythagoras, on a hypotenuse of 1
    5   e^(it) = cos t + i sin t   — the point IS the exponential
    6   t = pi  ->  e^(i pi) + 1 = 0

Rung 4 is not a fact to memorise, it is the triangle. Rung 6 is not a mystery,
it is P standing at (-1, 0). The viewer watches the most famous equation in
mathematics arrive as a position on a circle they have been looking at for
twenty seconds.

VERIFIED AT IMPORT
    sin^2 + cos^2 == 1 across 2000 angles
    e^(it) == cos t + i sin t across 2000 angles, to 1e-12
    e^(i pi) + 1 == 0 to floating point (1.2e-16)

THE GEOMETRY DANCES. P advances with the beat, so the two legs breathe in and
out for the whole video — the equation at the top pulses on the beat and the
triangle under it is what the equation is doing.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import cmath
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 72
RUNGS = 6
RUNG_BEATS = 8
END_OPEN = 4
END_RUNGS = END_OPEN + RUNGS * RUNG_BEATS        # 52
END_TAKE = 60

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
EQ_Y    = 2.55
NOTE_Y  = -2.30

OX, OY = -0.25, -0.35        # circle centre on screen
R = 1.45                     # radius in scene units
SPIN = 0.55                  # radians of P per beat

# ---------------------------------------------------------------- verified
_ts = np.linspace(0, 2 * np.pi, 2000)
assert np.allclose(np.sin(_ts) ** 2 + np.cos(_ts) ** 2, 1.0, atol=1e-12)
assert all(abs(cmath.exp(1j * t) - (np.cos(t) + 1j * np.sin(t))) < 1e-12
           for t in _ts)
assert abs(cmath.exp(1j * np.pi) + 1) < 1e-15

# rung, equation, note
LADDER = [
    ("a point on a circle",        "one point, going round"),
    ("sin t",                      "its HEIGHT is sin"),
    ("cos t",                      "its WIDTH is cos"),
    ("sin²t + cos²t = 1",          "Pythagoras — the slope is the radius"),
    (("POW", "it", "= cos t + i sin t"), "the point IS the exponential"),
    (("POW", "iπ", "+ 1 = 0"),            "put the point at half a turn"),
]
assert len(LADDER) == RUNGS


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def power(base, exp, size=32, color=WHITE_):
    """e to the something, typeset by hand.

    There is no LaTeX in this environment and Unicode has no superscript pi, so
    "e^(it)" would have to be written with a literal caret — which reads as code
    rather than mathematics. This raises a smaller Text instead.
    """
    b = txt(base, size, color, w=1.2)
    e = txt(exp, int(size * 0.58), color, w=1.2)
    e.next_to(b, RIGHT, buff=0.05)
    e.shift(np.array([0, b.get_height() * 0.34, 0]))
    return VGroup(b, e)


def eqn(*parts, size=32, color=WHITE_, w=4.5):
    """A row of Text and power() pieces, sized to fit."""
    g = VGroup(*[p if isinstance(p, VMobject) else txt(p, size, color, w=3.2)
                 for p in parts]).arrange(RIGHT, buff=0.14)
    if g.get_width() > w:
        g.set_width(w)
    return g


def seg(a, b, color=WHITE_, w=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    return m


def P(x, y):
    return np.array([OX + x * R, OY + y * R, 0.0])


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


class CircleLadder(Scene):
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

        self.theta = ValueTracker(0.35)
        self.spinning = False
        self.theta.add_updater(
            lambda m, dt: m.increment_value(dt * SPIN / self.B) if self.spinning else None)
        self.add(self.theta)

        self.show_sin = False
        self.show_cos = False

        self.open_card()
        self.build_circle()
        for i, (eq, note) in enumerate(LADDER):
            self.rung(i, eq, note)
        self.takeaway("Every wave you have ever seen", "is a point going round a circle.")
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

    def say(self, s, beats=2, color=WHITE_, size=24):
        new = txt(s, size, color, bold=False, w=4.4)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def show_eq(self, s, beats=2, color=WHITE_, size=32):
        """The dancing equation. It pulses on every beat for the whole video."""
        if isinstance(s, tuple):
            _, exp, rest = s
            body = eqn(power("e", exp, size, color), rest, size=size, color=color)
        else:
            body = txt(s, size, color, w=4.5)
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
        self.title = txt("EVERY WAVE IS A CIRCLE", 42, WHITE_, w=4.6)
        self.title.move_to(np.array([0, 0.85, 0]))
        sub = txt("six equations, one picture", 23, GOLD, bold=False)
        sub.move_to(np.array([0, 0.15, 0]))
        self.add(self.title, sub)
        self.wait(self.T(2))
        self.play(self.title.animate.set_height(
                      self.title.get_height() * 0.46).move_to(np.array([0, 3.35, 0])),
                  FadeOut(sub), run_time=self.T(1))
        self.pad_to(END_OPEN)

    def build_circle(self):
        """The one object. Everything after this is a relabelling of it."""
        circ = Circle(radius=R, stroke_color=GREY, stroke_width=2.6)
        circ.move_to(np.array([OX, OY, 0])).set_stroke(opacity=0.75)
        ax = VGroup(seg(P(-1.35, 0), P(1.35, 0), FAINT, 2.0),
                    seg(P(0, -1.35), P(0, 1.35), FAINT, 2.0))
        self.add(ax, circ)

        radius = seg(P(0, 0), P(1, 0), WHITE_, 3.4)
        dot = Dot(P(1, 0), radius=0.10, fill_color=WHITE_)
        sinl = seg(P(1, 0), P(1, 0), GOLD, 5.0)
        cosl = seg(P(0, 0), P(1, 0), COOL, 5.0)
        slab = txt("sin t", 22, GOLD, bold=False, w=1.0)
        clab = txt("cos t", 22, COOL, bold=False, w=1.0)

        def upd(_):
            t = self.theta.get_value()
            c, s = np.cos(t), np.sin(t)
            radius.set_points_as_corners([P(0, 0), P(c, s)])
            dot.move_to(P(c, s))
            if self.show_sin:
                sinl.set_points_as_corners([P(c, 0), P(c, s)])
                sinl.set_stroke(opacity=0.95)
                slab.move_to(P(c, s / 2) + np.array([0.42 * np.sign(c or 1), 0, 0]))
                # at t = pi the leg has no length, and its label would sit on
                # top of the "-1" that is the whole point of the last rung
                slab.set_opacity(0.95 if abs(s) > 0.10 else 0.0)
            else:
                sinl.set_stroke(opacity=0.0); slab.set_opacity(0.0)
            if self.show_cos:
                cosl.set_points_as_corners([P(0, 0), P(c, 0)])
                cosl.set_stroke(opacity=0.95)
                clab.move_to(P(c / 2, 0) + np.array([0, -0.36, 0]))
                clab.set_opacity(0.95)
            else:
                cosl.set_stroke(opacity=0.0); clab.set_opacity(0.0)

        self.geo = VGroup(cosl, sinl, radius, dot, slab, clab)
        self.geo.add_updater(upd)
        self.add(self.geo)
        self.spinning = True

    # ------------------------------------------------------------------
    def rung(self, i, eq, note):
        end = END_OPEN + (i + 1) * RUNG_BEATS
        if i == 1:
            self.show_sin = True
        if i == 2:
            self.show_cos = True
        if i == 3:
            self.show_sin = self.show_cos = True

        self.show_eq(eq, 2, GOLD if i >= 4 else WHITE_)
        self.say(note, 2)

        if i == 3:
            hyp = txt("1", 24, WHITE_, w=0.4)
            t = self.theta.get_value()
            n = np.array([-np.sin(t), np.cos(t), 0.0])      # outward normal
            hyp.move_to(P(np.cos(t) / 2, np.sin(t) / 2) + n * 0.32)
            self.play(FadeIn(hyp), run_time=self.T(1))
            self.play(FadeOut(hyp), run_time=self.T(1))

        if i == 5:
            # stop the spin on the next half turn, so P lands exactly at (-1, 0)
            cur = self.theta.get_value()
            target = np.ceil((cur - np.pi) / (2 * np.pi)) * 2 * np.pi + np.pi
            self.spinning = False
            self.play(self.theta.animate.set_value(target),
                      run_time=self.T(3), rate_func=smooth)
            mark = txt("−1", 26, GOLD, w=0.7)
            mark.move_to(P(-1, 0) + np.array([-0.10, -0.42, 0]))
            self.play(FadeIn(mark, scale=1.3), run_time=self.T(1))

        self.pad_to(end)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        self.spinning = False
        self.geo.clear_updaters()
        if self.eq:
            self.eq.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects
                    if m not in (self.clock, self.theta, self.title)],
                  run_time=self.T(1))
        self.note = self.eq = None
        l1 = txt(a, 28, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 26, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(END_TAKE)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.title), run_time=self.T(1))

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
