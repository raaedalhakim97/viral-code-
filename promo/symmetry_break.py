"""
symmetry_break — why AI never starts with equal numbers. 40.0s.

    BPM=150 manimgl symmetry_break.py SymmetryBreak -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

THREE NEURONS, ONE TINY JOB: see +1, output +3. See -1, output -3. Each neuron
is one ReLU with an input weight w_i and an output weight v_i:

        y_hat(x) = sum_i  v_i * relu(w_i * x)

trained by real gradient descent on exactly those two examples — no shortcuts,
the gradients below are the actual calculus, computed by hand once and then
re-run at import to prove the numbers on screen are real.

STARTED IDENTICAL, THEY MOVE IDENTICALLY, FOREVER. If w_1=w_2=w_3 and
v_1=v_2=v_3 at step zero, every gradient every neuron ever receives is
identical too — the three neurons are mathematically indistinguishable to the
optimiser, and gradient descent has no way to tell them apart. The three bars
in that half of the video are not a good visual; they are ONE trajectory drawn
three times, and the loss gets stuck at exactly 4.500 forever, because two
opposite-signed examples cannot both be solved by three neurons that are only
ever allowed to move together.

BREAK THE TIE, AND THE LOSS GOES TO ZERO. The same two examples, the same
learning rate, the same number of steps — the only change is the starting
numbers are three DIFFERENT small values. One neuron ends up strongly
positive, one strongly negative, one near zero: they specialise, and between
them they hit both examples. Final loss lands at 32-bit float noise.

THIS IS WHY REAL NETWORKS INITIALISE RANDOMLY, not from superstition: equal
starting weights are a mathematical trap, not a bad-luck starting point.

VERIFIED AT IMPORT
    identical init keeps every weight identical, every step   0.0 spread, always
    the symmetric run's loss floor is exactly 4.500            not "roughly"
    the broken-symmetry run reaches float-noise loss           < 1e-9
    both runs train on the same two examples, same rate, same steps

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats), always a multiple of 0.25 beats
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN, END_SETUP, END_SYM, END_RAND, END_WHY, END_FOLLOW = 8, 20, 46, 72, 84, 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"
NCOLOR = (GOLD, SKY, ROSE)

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.035
TITLE_Y = 3.15
NOTE_Y  = -3.60
LINE_Y  = -2.05

# ------------------------------------------------------------------ the maths
XS, TS = np.array([1.0, -1.0]), np.array([3.0, -3.0])
LR, STEPS = 0.05, 200


def relu(x):
    return np.maximum(x, 0.0)


def drelu(x):
    return (x > 0).astype(float)


def train(w0, v0):
    w, v = w0.copy(), v0.copy()
    hw, hv, losses = [w.copy()], [v.copy()], []
    for _ in range(STEPS):
        outs = np.array([(v * relu(w * x)).sum() for x in XS])
        losses.append(float(np.mean((outs - TS) ** 2)))
        gw, gv = np.zeros_like(w), np.zeros_like(v)
        for x, t, out in zip(XS, TS, outs):
            dout = (2.0 / len(XS)) * (out - t)
            gv += dout * relu(w * x)
            gw += dout * v * drelu(w * x) * x
        w, v = w - LR * gw, v - LR * gv
        hw.append(w.copy())
        hv.append(v.copy())
    outs = np.array([(v * relu(w * x)).sum() for x in XS])
    losses.append(float(np.mean((outs - TS) ** 2)))
    return np.array(hw), np.array(hv), np.array(losses)


W_SYM0, V_SYM0 = np.array([0.5, 0.5, 0.5]), np.array([1.0, 1.0, 1.0])
HW_SYM, HV_SYM, LOSS_SYM = train(W_SYM0, V_SYM0)

_rng = np.random.default_rng(153)
W_RAND0 = _rng.uniform(-1.0, 1.0, size=3)
V_RAND0 = _rng.uniform(-1.0, 1.0, size=3)
HW_RAND, HV_RAND, LOSS_RAND = train(W_RAND0, V_RAND0)

CKPT = [0, 4, 10, 24, 60, 140, 199]

assert (HW_SYM.max(axis=1) - HW_SYM.min(axis=1)).max() == 0.0, \
    "identically-initialised neurons must stay identical, exactly, forever"
assert (HV_SYM.max(axis=1) - HV_SYM.min(axis=1)).max() == 0.0
assert LOSS_SYM[-1] == 4.5, "the symmetric loss floor must be exactly 4.5"
assert LOSS_RAND[-1] < 1e-9, "broken symmetry must reach float-noise loss"
assert (HW_RAND[-1].max() - HW_RAND[-1].min()) > 1.0, \
    "the three neurons must visibly specialise"
assert max(CKPT) <= STEPS

BAR_X = (-0.62, 0.0, 0.62)
BASE_Y = -0.30
BAR_W = 0.30
BAR_SCALE = 0.52   # screen units per unit of weight — keeps the tallest bar
                    # (|w| up to ~1.8) clear of the loss readout below it


def bar_height(w):
    return w * BAR_SCALE


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


def make_bar(x, w, color):
    h = bar_height(w)
    r = Rectangle(width=BAR_W, height=abs(h) + 1e-4, fill_color=color,
                 fill_opacity=0.85, stroke_width=0)
    r.move_to(np.array([x, BASE_Y + h / 2, 0.0]))
    return r


class SymmetryBreak(Scene):
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
        self.stage_setup()
        self.stage_run(HW_SYM, LOSS_SYM, symmetric=True)
        self.stage_run(HW_RAND, LOSS_RAND, symmetric=False)
        self.stage_why()
        self.stage_follow()
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

    def say(self, s, beats=2, color=WHITE_, size=26):
        new = txt(s, size, color, bold=False, w=4.6)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    # ==================================================================
    def open_card(self):
        self.hook = VGroup(txt("WHY DOESN'T AI START", 28, WHITE_, w=4.4),
                           txt("WITH EQUAL NUMBERS?", 34, GOLD, w=4.4)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, 0.4, 0]))
        self.play(FadeIn(self.hook), run_time=self.T(2))
        self.say("it's not superstition. it's provable.", 3)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_setup(self):
        self.play(FadeOut(self.hook), run_time=self.T(1))
        self.title = txt("three neurons. one tiny job.", 25, GREY, bold=False, w=4.3)
        self.title.move_to(np.array([0, TITLE_Y, 0]))
        task = VGroup(txt("see +1  ->  output +3", 22, WHITE_, bold=False, w=3.6),
                     txt("see −1  ->  output −3", 22, WHITE_, bold=False, w=3.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, 1.55, 0]))
        self.task = task

        self.baseline = Line(np.array([-1.1, BASE_Y, 0]), np.array([1.1, BASE_Y, 0]),
                             stroke_color=GREY, stroke_width=1.6)
        self.bars = VGroup(*[make_bar(x, 0.5, NCOLOR[i])
                             for i, x in enumerate(BAR_X)])
        self.play(FadeIn(self.title), FadeIn(task), run_time=self.T(1.5))
        self.play(ShowCreation(self.baseline), FadeIn(self.bars), run_time=self.T(2))
        self.say("started identical. watch what that costs.", 3.5)
        self.pad_to(END_SETUP)

    # ==================================================================
    def stage_run(self, hist_w, loss_hist, symmetric):
        end = END_SYM if symmetric else END_RAND
        assert BASE_Y - 1.8 * BAR_SCALE > -1.5, \
            "the tallest possible bar must stay clear of the loss readout"
        first = txt(f"loss {loss_hist[0]:.3f}", 26, WHITE_, w=2.8)
        first.move_to(np.array([0, -1.85, 0]))
        if symmetric:
            self.loss_txt = first
            self.play(FadeIn(self.loss_txt), run_time=self.T(1.5))
        else:
            self.say("same problem. tiny random nudges at the start.", 3.5)
            reset = [Transform(self.bars[i], make_bar(x, hist_w[0][i], NCOLOR[i]))
                    for i, x in enumerate(BAR_X)]
            # self.loss_txt here is still the SYMMETRIC stage's on-screen text
            # — fade that actual mobject out, not a freshly-built stand-in, or
            # it is left behind forever underneath every later number.
            self.play(*reset, FadeOut(self.loss_txt), FadeIn(first),
                     run_time=self.T(1.5))
            self.loss_txt = first

        # The checkpoints run back-to-back with no hold in between, so a
        # crossfade on the number is ALWAYS mid-fade at every sampled frame —
        # it never once reads clean. A readout is a measurement, not a
        # caption: snap it instantly (no animation) right as each bar
        # transform lands, instead of fading it alongside the bars.
        for step in CKPT[1:]:
            anims = [Transform(self.bars[i], make_bar(x, hist_w[step][i], NCOLOR[i]))
                     for i, x in enumerate(BAR_X)]
            self.play(*anims, run_time=self.T(2.75))
            newl = txt(f"loss {loss_hist[step]:.3f}", 26, WHITE_, w=2.8)
            newl.move_to(np.array([0, -1.85, 0]))
            self.remove(self.loss_txt)
            self.add(newl)
            self.loss_txt = newl

        if symmetric:
            self.say("stuck. exactly 4.500. no matter how long you train.", 3.5, ROSE)
        else:
            self.say("loss zero. the three neurons split up.", 3.5, GOLD)
        self.pad_to(end)

    # ==================================================================
    def stage_why(self):
        self.say("three identical numbers can only move together.", 3.5)
        self.say("break the tie, and they specialise.", 3.5, GOLD)
        self.pad_to(END_WHY)

    # ==================================================================
    def stage_follow(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None

        f1 = txt("SYMMETRY BREAKING", 30, GOLD, w=4.5)
        f1.move_to(np.array([0, 0.92, 0]))
        f2 = txt("that's why weights start random", 23, WHITE_, w=4.3)
        f2.move_to(np.array([0, 0.24, 0]))
        f3 = txt("follow — the math behind AI", 21, GREY, bold=False, w=4.2)
        f3.move_to(np.array([0, -0.50, 0]))
        self.card = VGroup(f1, f2, f3)
        self.play(FadeIn(f1, scale=1.10), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.play(FadeIn(f2), run_time=self.T(1))
        self.play(FadeIn(f3), run_time=self.T(1))
        self.pad_to(END_FOLLOW - 1.5)
        self.play(FadeOut(self.card), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.10, 0])).scale(0.74)
        self.play(ShowCreation(eye), run_time=self.T(2.5))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.42, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.5))
        cta = txt("@observer.collapse", 25, GREY, bold=False)
        cta.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cta, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cta),
                  run_time=self.T(1.5))
