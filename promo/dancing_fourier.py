"""
dancing_fourier — spinning arrows that draw the eye. 60.0s.

    BPM=150 manimgl dancing_fourier.py DancingFourier -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

"SATISFYING MATH" episode. The sequel to dancing_equation.py: that one
danced a 2x2 matrix, this one dances a Fourier series.

THE IDEA, and it is the whole idea: take a chain of arrows, joined tip to
tail. Spin each one at its own constant speed. Follow the tip of the last
arrow. That path can be *any* closed shape you like — you only have to
choose the right lengths and speeds.

    x(t)  =  sum of  c · e^(i k t)

Each arrow is one term. Its length is |c|, its speed is k.

WHAT IT DRAWS. The channel's own eye mark, taken as a closed outline: out
along the top curve, back along the bottom. The coefficients are not hand
tuned — they are the discrete Fourier transform of that outline, sorted by
size, largest arrow first.

    1 arrow   -> a circle      max error 0.50  = 16% of the shape width
    4 arrows  -> the shape     max error 0.16  =  5%
    24 arrows -> sharp corners max error 0.027 =  0.8%

AND THE PAYOFF IS THE LOPSIDEDNESS. The arrows are nothing like equal. The
first is 5.5x the second and 137x the tenth, and the first four carry
91.6% of the total arrow length between them. The remaining twenty are
8.4% — they do nothing but sharpen the two corners.

Which is the whole trick behind image compression: keep the few large
coefficients, throw the many small ones away, and the picture survives.
That is what a JPEG does, in two dimensions and with cosines.

Only odd frequencies survive — a consequence of the outline's symmetry,
not a choice.

VERIFIED AT IMPORT
    the outline is closed                      first point meets last
    reconstruction error falls as terms are added, 1 -> 4 -> 24
    24 terms land within 0.03 of the true outline
    the first four arrows really are >90% of the total arrow length
    the first arrow really is >5x the second
    the arrow chain can never leave the frame   sum of all |c| is checked
    every frequency used is odd                 the symmetry claim is real

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    a group carrying an updater must be self.add()ed itself: LaggedStartMap
    and AnimationGroup hand the scene a rebuilt copy, and the original —
    the one holding the updater — never gets ticked
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 10
END_A, END_B, END_C = 32, 58, 106
END_PUNCH = 120
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
SCALE = 1.25
DRAW_C = np.array([0.0, -0.35, 0])
N_SAMPLES = 512
TRACE_RES = 420
STAGE_TERMS = (1, 4, 24)


def eye_outline(n=N_SAMPLES):
    """The observer eye as one closed curve: out along the top, back along
    the bottom. Same formula the signature mark uses."""
    half = n // 2
    xs = np.linspace(-1.6, 1.6, half, endpoint=False)
    top = 0.9 * np.sin(np.pi * ((xs + 1.6) / 3.2))
    xs2 = np.linspace(1.6, -1.6, half, endpoint=False)
    bot = -0.9 * np.sin(np.pi * ((xs2 + 1.6) / 3.2))
    return np.concatenate([xs + 1j * top, xs2 + 1j * bot])


OUTLINE = eye_outline()
FREQS_ALL = np.fft.fftfreq(N_SAMPLES, d=1.0 / N_SAMPLES).astype(int)
COEFFS_ALL = np.fft.fft(OUTLINE) / N_SAMPLES

# the closed-curve check: the outline's two ends meet
assert abs(OUTLINE[0] - OUTLINE[-1]) < 0.05

_order = [i for i in np.argsort(-np.abs(COEFFS_ALL)) if FREQS_ALL[i] != 0]
MAX_TERMS = max(STAGE_TERMS)
IDX = _order[:MAX_TERMS]
FREQS = [int(FREQS_ALL[i]) for i in IDX]
COEFFS = [complex(COEFFS_ALL[i]) for i in IDX]
CENTRE = complex(COEFFS_ALL[FREQS_ALL == 0][0])


def reconstruct(n_terms, n_pts=TRACE_RES):
    t = np.arange(n_pts + 1) / n_pts
    out = np.full(n_pts + 1, CENTRE, dtype=complex)
    for c, k in zip(COEFFS[:n_terms], FREQS[:n_terms]):
        out = out + c * np.exp(2j * np.pi * k * t)
    return out


# more arrows must mean less error, and 24 must be close
_errs = []
for _m in STAGE_TERMS:
    _r = reconstruct(_m, N_SAMPLES)[:N_SAMPLES]
    _errs.append(float(np.abs(_r - OUTLINE).max()))
assert _errs[0] > _errs[1] > _errs[2]
assert _errs[2] < 0.03

# the chain can never swing out of frame (half-width 2.40 at deepest breath)
REACH = float(sum(abs(c) for c in COEFFS)) * SCALE
assert REACH < 2.30
assert float(np.abs(OUTLINE).max()) * SCALE < 2.30

# the symmetry claim: only odd harmonics survive
assert all(k % 2 != 0 for k in FREQS)

# the lopsidedness, which is the point of the whole video
_mag = [abs(c) for c in COEFFS]
_total = sum(_mag)
SHARE_4 = sum(_mag[:4]) / _total
SHARE_REST = 1.0 - SHARE_4
RATIO_1_2 = _mag[0] / _mag[1]
assert SHARE_4 > 0.90 and SHARE_REST < 0.10
assert RATIO_1_2 > 5.0
assert round(SHARE_4 * 100) == 92 and round(SHARE_REST * 100) == 8


def to_screen(zv):
    return DRAW_C + np.array([zv.real * SCALE, zv.imag * SCALE, 0])


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


class DancingFourier(Scene):
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
        self.build_rig()
        self.stage_one()
        self.stage_four()
        self.stage_all()
        self.stage_punch()
        self.takeaway("That is what a JPEG does.",
                      "Keep the big ones. Bin the rest.")
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
        big = txt("every arrow is a number.", 28, GOLD, w=4.6)
        big.move_to(np.array([0, 0.85, 0]))
        q = txt("spin them all at once", 26, WHITE_, w=4.6)
        q.move_to(np.array([0, -0.10, 0]))
        sub = txt("and watch what they draw.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.80, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("x(t)  =  Σ  c · e^(i k t)", 24, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(big), FadeOut(q), FadeOut(sub),
                  FadeIn(self.title), FadeIn(self.eq), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def build_rig(self):
        """One rig, reused by every stage. Arrows past n_terms are parked
        invisible rather than rebuilt."""
        self.arms = VGroup()
        self.rings = VGroup()
        for _ in range(MAX_TERMS):
            arm = VMobject(stroke_color=GREY, stroke_width=1.8)
            arm.set_points_as_corners([DRAW_C, DRAW_C + RIGHT * 0.01])
            self.arms.add(arm)
            ring = Circle(radius=0.01, stroke_color=FAINT, stroke_width=1.2)
            ring.move_to(DRAW_C)
            self.rings.add(ring)
        self.trace = VMobject(stroke_color=GOLD, stroke_width=3.4)
        self.trace.set_points_as_corners([DRAW_C, DRAW_C + RIGHT * 0.01])
        self.tip = Dot(DRAW_C, radius=0.055, fill_color=GOLD)

        self.rig = VGroup(self.rings, self.arms, self.trace, self.tip)
        self.n_terms = 0
        self.t0 = 0.0
        self.period = 1.0
        self.curve = reconstruct(1)

        def tick(m):
            if self.n_terms == 0:
                return
            prog = (self.clock.get_value() - self.t0) / self.period
            pos = CENTRE
            for i in range(MAX_TERMS):
                arm, ring = self.arms[i], self.rings[i]
                if i >= self.n_terms:
                    arm.set_stroke(opacity=0)
                    ring.set_stroke(opacity=0)
                    continue
                prev = pos
                pos = pos + COEFFS[i] * np.exp(2j * np.pi * FREQS[i] * prog)
                arm.set_points_as_corners([to_screen(prev), to_screen(pos)])
                arm.set_stroke(opacity=0.85)
                ring.set_width(2 * abs(COEFFS[i]) * SCALE)
                ring.move_to(to_screen(prev))
                ring.set_stroke(opacity=0.5)
            self.tip.move_to(to_screen(pos))
            drawn = int(np.clip(prog, 0.0, 1.0) * TRACE_RES)
            if drawn >= 1:
                self.trace.set_points_as_corners(
                    [to_screen(v) for v in self.curve[:drawn + 1]])

        self.rig.add_updater(tick)
        self.add(self.rig)          # the group itself, so its updater ticks

    def run_stage(self, n_terms, period_beats):
        self.n_terms = n_terms
        self.curve = reconstruct(n_terms)
        self.period = period_beats * self.B
        self.t0 = self.clock.get_value()
        self.trace.set_points_as_corners([DRAW_C, DRAW_C + RIGHT * 0.01])

    # ==================================================================
    def stage_one(self):
        self.play(FadeIn(self.rig), run_time=self.T(2))
        self.run_stage(1, 16)
        self.say("one arrow, spinning.", 3)
        self.pad_to(28)
        self.say("one arrow only ever draws a circle.", 3, GOLD)
        self.pad_to(END_A)

    def stage_four(self):
        self.run_stage(4, 16)
        self.say("now four.", 2.5)
        self.pad_to(48)
        self.say("four arrows and it's already the shape.", 3.5)
        self.pad_to(END_B)

    def stage_all(self):
        self.run_stage(MAX_TERMS, 40)
        self.say("twenty-four.", 2.5, GOLD)
        self.pad_to(75)
        self.say("nothing is steering the tip.", 3.5)
        self.pad_to(98)
        self.say("the last twenty only sharpen the corners.", 3.5, GOLD)
        self.pad_to(END_C)

    def stage_punch(self):
        self.say("look at the sizes. they're nothing like equal.", 4)
        self.say("the first four are %d%% of the total length."
                 % round(SHARE_4 * 100), 4, GOLD)
        self.say("the other twenty are %d%%." % round(SHARE_REST * 100), 3)
        self.say("bin them and you'd barely see it.", 3)
        self.pad_to(END_PUNCH)

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
        self.l2 = txt(b, 27, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to someone", 27, WHITE_, w=4.5)
        s2 = txt("who likes watching things line up", 25, GOLD, w=4.6)
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
