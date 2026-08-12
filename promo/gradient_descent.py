"""
gradient_descent — how AI actually learns: roll downhill. 40.0s.

    BPM=150 manimgl gradient_descent.py GradientDescent -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 4 OF "WHY DID WE LEARN THIS?" — same shell as the rest: the equation
is the spine, it sits at the top for the whole video, it starts EMPTY, and
every number is dragged into its slot off the picture.

    new  =  old  −  step · slope

One curve: how wrong the model is, for every setting it could have. The bottom
of the valley is the right answer, and the whole of training is one rule
applied over and over — look at the slope where you are, and step the other
way.

    old    ←  4        where the ball is now
    step   ←  1        the one number that is a CHOICE, not a measurement
    slope  ←  2        read off the tangent: along 1, up 2

    new = 4 − 1·2 = 2      and the ball moves to 2
    then 2 − 1·1 = 1       and it moves again
    then it settles at the bottom

THE CURVE IS y = x²/4, CHOSEN SO EVERY NUMBER ON SCREEN IS WHOLE. Its slope at
x is x/2, so at x = 4 the slope is 2 and at x = 2 it is 1 — both drawable as
"along 1, up 2" on a grid where the x and y scales are equal, which is why they
are equal. With step = 1 the update halves the position every time: 4 → 2 → 1,
so the arithmetic stays in integers and the convergence is visible rather than
asserted.

THE STEP IS THE ONE NUMBER THAT IS NOT MEASURED. old and slope are dragged off
the picture; step fades in with the line that says it is yours to pick. Being
straight about that is the honest version — it is the learning rate, and
choosing it is most of the job.

VERIFIED AT IMPORT
    slope(x) == x/2 for the curve used         checked numerically, not assumed
    the update sequence is 4 -> 2 -> 1         in integers
    every slope shown is a whole number        so nothing on screen is rounded
    each step lowers the height                which is what "downhill" means

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
TOTAL = 100

END_OPEN = 8
END_HILL, END_FILL, END_STEP1, END_MORE = 26, 46, 64, 82
END_TAKE = 90

SERIES = "WHY DID WE LEARN THIS?"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
LEAF   = "#A3BE8C"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
LINE_Y  = -2.05
EQ_Y    = 2.42
ANS_Y   = 1.72
NOTE_Y  = -2.34
MINUS   = "−"


def height(x):
    """How wrong the model is. A valley, with the answer at the bottom."""
    return x * x / 4.0


def slope(x):
    return x / 2.0


START, STEP = 4, 1
SEQ = [START]
while len(SEQ) < 3:
    SEQ.append(SEQ[-1] - STEP * slope(SEQ[-1]))

# checked, not assumed: a numerical derivative agrees with x/2
_h = 1e-6
for _x in np.linspace(-4, 4, 200):
    assert abs(((height(_x + _h) - height(_x - _h)) / (2 * _h)) - slope(_x)) < 1e-6

assert SEQ == [4, 2, 1], SEQ
assert all(float(slope(v)).is_integer() for v in SEQ[:2]), SEQ
assert all(height(b) < height(a) for a, b in zip(SEQ, SEQ[1:]))   # downhill

S0, S1, S2 = (f"{v:.0f}" for v in SEQ)
G0, G1 = (f"{slope(v):.0f}" for v in SEQ[:2])
STEPS = str(STEP)

# the curve on stage — equal x and y scales, so a slope of 2 draws as a slope
# of 2 and "along 1, up 2" is literally true
XLO, XHI = -4.6, 4.6
SC = 0.38
CX, CY = 0.0, -1.62

BASE = ["new", "=", "old", MINUS, "step", "·", "slope"]
IDX_OLD, IDX_STEP, IDX_SLOPE = 2, 4, 6


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


def P(x, y):
    return np.array([CX + SC * x, CY + SC * y, 0.0])


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


class GradientDescent(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.filled = {}
        self.ans = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_hill()
        self.stage_fill()
        self.stage_step1()
        self.stage_more()
        self.takeaway("We learned this at school.",
                      "Nobody ever said what for.")
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

    def say(self, s, beats=2, color=WHITE_, size=25, extra=()):
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

    # ---------------------------------------------------- the equation
    def make_eq(self, active=None, also=None, size=36):
        fill = dict(self.filled)
        if also:
            fill.update(also)
        g = VGroup()
        for i, base in enumerate(BASE):
            s = fill.get(i, base)
            done = i in fill
            if i == active:
                col, sz = GOLD, int(size * 1.14)
            elif done:
                col, sz = GOLD, size
            elif i in (IDX_OLD, IDX_STEP, IDX_SLOPE):
                col, sz = DIM, size
            else:
                col, sz = WHITE_, size
            g.add(txt(s, sz, col, w=1.8))
        g.arrange(RIGHT, buff=0.13)
        if g.get_width() > 4.6:
            g.set_width(4.6)
        return g.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats, extra=()):
        self.play(Transform(self.eq, self.make_eq(active)), *extra,
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, size, fly=2.5, settle=1.5):
        nxt = self.make_eq(active=slot, also={slot: value})
        target = nxt[slot]
        flier = txt(value, size, GOLD, w=1.8).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled[slot] = value
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    def show_ans(self, s, beats, color=WHITE_, size=32):
        new = txt(s, size, color, w=4.2).move_to(np.array([0, ANS_Y, 0]))
        if self.ans is None:
            self.ans = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(Transform(self.ans, new), run_time=self.T(beats))

    # ---------------------------------------------------- the picture
    def tangent(self, x, half=0.90, color=SKY, wid=3.6):
        m = slope(x)
        return seg(P(x - half, height(x) - m * half),
                   P(x + half, height(x) + m * half), color, wid)

    def ball_at(self, x):
        return P(x, height(x))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("how does AI learn?", 40, WHITE_, w=4.6),
                     txt("it rolls downhill", 44, GOLD, w=4.6)) \
            .arrange(DOWN, buff=0.26)
        big.move_to(np.array([0, 0.80, 0]))
        sub = txt("one line of maths, a few billion times", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.30, 0]))
        self.add(big, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # the valley: how wrong the model is, for every setting it could have
    # ==================================================================
    def stage_hill(self):
        xs = np.linspace(XLO, XHI, 220)
        self.curve = VMobject(stroke_color=GREY, stroke_width=3.4)
        self.curve.set_points_as_corners([P(x, height(x)) for x in xs])
        self.axis = seg(P(XLO, 0), P(XHI, 0), FAINT, 2.2)
        self.play(ShowCreation(self.axis), ShowCreation(self.curve),
                  run_time=self.T(2.5))
        self.say("this curve is how WRONG the model is.", 2.5)

        self.low = Dot(P(0, 0), radius=0.09, fill_color=LEAF)
        self.lowl = txt("the answer", 21, LEAF, bold=False, w=1.5)
        self.lowl.move_to(P(0, 0) + np.array([0, -0.36, 0]))
        self.play(FadeIn(self.low, scale=1.8), FadeIn(self.lowl),
                  run_time=self.T(2))
        self.say("the bottom of the valley is the right answer.", 2.5)

        self.ball = Dot(self.ball_at(SEQ[0]), radius=0.13, fill_color=GOLD)
        self.play(FadeIn(self.ball, scale=1.8), run_time=self.T(2))
        self.say("the model starts up here.", 2)
        self.say("and it cannot see where the bottom is.", 2.5)
        self.pad_to(END_HILL)

    # ==================================================================
    # fill the rule: where you are, how big a step, and which way is down
    # ==================================================================
    def stage_fill(self):
        self.relight(IDX_OLD, 1.0, extra=[self.zoom.animate.set_value(0.95)])
        self.n0 = txt(S0, 26, GOLD, w=0.6).move_to(self.ball.get_center()
                                                   + np.array([0.34, 0.16, 0]))
        self.play(FadeIn(self.n0, scale=1.3), run_time=self.T(1))
        self.drag_into(self.n0.get_center(), IDX_OLD, S0, 26)

        self.relight(IDX_SLOPE, 1.0)
        self.tan = self.tangent(SEQ[0])
        rise = txt(f"along 1, up {G0}", 21, SKY, bold=False, w=1.9)
        rise.move_to(self.ball_at(SEQ[0]) + np.array([-0.95, 0.34, 0]))
        self.play(ShowCreation(self.tan), FadeIn(rise), run_time=self.T(2.5))
        self.say("the slope where you stand. here it is 2.", 2)
        self.drag_into(rise.get_center(), IDX_SLOPE, G0, 26)
        self.rise = rise

        self.relight(IDX_STEP, 1.0)
        self.play(Transform(self.eq,
                            self.make_eq(IDX_STEP, also={IDX_STEP: STEPS})),
                  run_time=self.T(1.5))
        self.filled[IDX_STEP] = STEPS
        self.say("the step is the one number you CHOOSE. call it 1.", 2)
        self.pad_to(END_FILL)

    # ==================================================================
    # one step downhill
    # ==================================================================
    def stage_step1(self):
        self.show_ans(f"{S0} {MINUS} {STEPS} · {G0}", 2.5)
        self.say("four, minus one times two.", 2)
        self.show_ans(f"= {S1}", 2.5, GOLD)

        self.play(FadeOut(self.tan), FadeOut(self.rise), FadeOut(self.n0),
                  run_time=self.T(1.5))
        self.play(self.ball.animate.move_to(self.ball_at(SEQ[1])),
                  run_time=self.T(2.5), rate_func=smooth)
        self.say("the ball moved downhill.", 2)

        self.play(Transform(self.eq, self.make_eq(IDX_OLD,
                                                  also={IDX_OLD: S1})),
                  run_time=self.T(2.5))
        self.filled[IDX_OLD] = S1
        self.say("the new one becomes the old one.", 2)
        self.pad_to(END_STEP1)

    # ==================================================================
    # again, and again, until it stops
    # ==================================================================
    def stage_more(self):
        self.say("now do it again.", 2,
                 extra=[self.zoom.animate.set_value(0.93)])

        tan2 = self.tangent(SEQ[1])
        self.play(ShowCreation(tan2),
                  Transform(self.eq, self.make_eq(IDX_SLOPE,
                                                  also={IDX_SLOPE: G1})),
                  run_time=self.T(2.5))
        self.filled[IDX_SLOPE] = G1
        self.show_ans(f"{S1} {MINUS} {STEPS} · {G1}  =  {S2}", 2.5, GOLD)

        self.play(FadeOut(tan2),
                  self.ball.animate.move_to(self.ball_at(SEQ[2])),
                  run_time=self.T(2.5), rate_func=smooth)
        self.say("smaller slope, smaller step.", 2)

        # let it run home — the slope shrinks to nothing at the bottom
        rest = [SEQ[2] * (0.5 ** k) for k in range(1, 5)]
        for x in rest:
            self.play(self.ball.animate.move_to(self.ball_at(x)),
                      run_time=self.T(0.5), rate_func=linear)
        self.say("flat ground. nothing left to change.", 2)
        self.say("that is training. a few billion times.", 2.5, GOLD)
        self.pad_to(END_MORE)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.ans, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.5)
        l2.move_to(np.array([0, -0.65, 0]))
        self.play(FadeIn(l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq), FadeOut(self.ans),
                  FadeOut(self.title), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3.5))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.5))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))
