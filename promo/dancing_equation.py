"""
dancing_equation — four numbers, and everything they do. 40.0s.

    BPM=150 manimgl dancing_equation.py DancingEquation -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

A DANCE VIDEO THAT HAPPENS TO BE THE MOST IMPORTANT EQUATION IN AI. A circle of
dots and two arrows get multiplied by a 2x2 matrix. The matrix changes pose on
every bar, and the shape does whatever the four numbers say. Rotate. Stretch.
Shear. Flip. Swap.

    x  ->  W x

EVERY POSE IS AN INTEGER MATRIX. That is the whole reason this works as a house
video: on every downbeat all four numbers on screen are exact whole numbers, and
so is the determinant. The dance is a walk between integer poses, not a smear of
decimals — the display shows a plain integer whenever the live value is one to
within 1e-9, and one decimal place while it is travelling.

THE COLUMNS ARE THE ARROWS, AND THAT IS THE WHOLE OF MATRIX MULTIPLICATION.
Column one is where the gold arrow lands. Column two is where the blue one
lands. Everything else follows, and the video says so out loud at the end.

THE DETERMINANT IS ON SCREEN THROUGHOUT because it is the one number you can
watch mean something: it is how much bigger the area got, and it goes negative
at exactly the moment the shape turns inside out.

    this is one layer of a neural network. that is all a layer is.

SEAMLESS LOOP. The choreography starts at the identity and its last pose is the
identity, so the final frame and the first frame are the same picture. Rewatch
is the metric Shorts actually rewards.

VERIFIED AT IMPORT
    every pose is integer                      or the downbeats show decimals
    the choreography returns to the identity   or the loop has a seam
    no pose leaves the frame                   largest singular value * UNIT
    the determinants are what is claimed       computed, never typed

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

END_OPEN, END_DANCE, END_WHY = 8, 72, 86
END_FOLLOW = 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.04
MAT_Y   = 3.02
DET_Y   = 2.12
NOTE_Y  = -3.58
LINE_Y  = -2.05
SHAPE_C = np.array([0.0, -0.45, 0.0])

# ------------------------------------------------------------------ the dance
I      = (1, 0, 0, 1)
R90    = (0, -1, 1, 0)
WIDE   = (2, 0, 0, 1)
TALL   = (1, 0, 0, 2)
SHEAR  = (1, 1, 0, 1)
SHEARB = (1, -1, 0, 1)
FLIP   = (1, 0, 0, -1)
SWAP   = (0, 1, 1, 0)

# Sixteen bars. Starts from the identity, ends on the identity, so it loops.
POSES = [R90, I, WIDE, TALL, SHEAR, I, SWAP, FLIP,
         I, R90, SHEARB, WIDE, TALL, SHEAR, R90, I]

UNIT = 1.02                        # screen units for one unit of space
NDOTS = 72


def det(M):
    return M[0] * M[3] - M[1] * M[2]


def extent(M):
    """Largest distance the unit circle reaches under M, in screen units."""
    a, b, c, d = M
    return float(np.linalg.svd(np.array([[a, b], [c, d]], float),
                               compute_uv=False)[0]) * UNIT


assert all(isinstance(v, int) for M in POSES + [I] for v in M), \
    "a non-integer pose would put decimals on a downbeat"
assert POSES[-1] == I, "the last pose must be the identity or the loop seams"
assert len(POSES) == 16, "sixteen bars"
assert 4 * len(POSES) == END_DANCE - END_OPEN
assert max(extent(M) for M in POSES + [I]) < 2.35, "a pose leaves the frame"
assert [det(M) for M in (I, R90, WIDE, TALL, SHEAR, SHEARB, FLIP, SWAP)] == \
    [1, 1, 2, 2, 1, 1, -1, -1], "the determinants are computed, not claimed"
assert any(det(M) < 0 for M in POSES), "nothing ever turns inside out"


# Captions, keyed by bar. A line that names a move has to sit on the bar that
# actually performs it — NAMED pins that, so the two can never drift apart.
LINES = {0: ("watch the numbers.", WHITE_),
         2: ("the shape only does what they say.", WHITE_),
         6: ("swap.", GOLD),
         7: ("inside out — look at det.", ROSE),
         9: ("rotate.", GOLD),
         10: ("shear.", GOLD),
         11: ("stretch.", GOLD),
         14: ("same four numbers. every time.", WHITE_)}
NAMED = {6: SWAP, 7: FLIP, 9: R90, 10: SHEARB, 11: WIDE}

assert all(POSES[i] == M for i, M in NAMED.items()), \
    "a caption names a move the matrix is not making"
assert set(LINES) <= set(range(len(POSES)))
assert det(POSES[7]) < 0, "'inside out' has to land on a negative determinant"


def hit(t):
    """A dance move lands before the beat is over and then holds."""
    return smooth(min(t / 0.62, 1.0))


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


class Cell(VMobject):
    """One entry of the matrix. Shows a plain integer when the value is one,
    and one decimal place while it is travelling between poses."""

    def __init__(self, labeller, home, color=WHITE_, size=32, **kw):
        super().__init__(**kw)
        self.label = labeller
        self.home = np.array(home, float)
        self.col = color
        self.size = size
        self.shown = None
        self.refresh()

    @staticmethod
    def show(v):
        r = round(v)
        return str(int(r)) if abs(v - r) < 1e-9 else f"{v:.1f}"

    def refresh(self):
        s = self.label()
        if s == self.shown:
            return
        self.shown = s
        self.set_submobjects([txt(s, self.size, self.col, w=1.0)])
        self.move_to(self.home)


class DancingEquation(Scene):
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

        self.W = [ValueTracker(float(v)) for v in I]

        self.build()
        self.open_card()
        self.stage_dance()
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

    def note_anims(self, s, color=WHITE_):
        """The cross-fade for a caption, as animations rather than a play(), so
        a line can ride along with a dance move instead of stopping it."""
        new = txt(s, 26, color, bold=False, w=4.6)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            return [FadeIn(new)]
        old, self.note = self.note, new
        return [FadeOut(old, shift=0.10 * UP), FadeIn(new, shift=0.10 * UP)]

    def say(self, s, beats=2, color=WHITE_):
        self.play(*self.note_anims(s, color), run_time=self.T(beats))

    # ---------------------------------------------------------------- pieces
    def mat(self):
        a, b, c, d = (t.get_value() for t in self.W)
        return np.array([[a, b], [c, d]], float)

    def build(self):
        M0 = np.array([[1.0, 0.0], [0.0, 1.0]])

        self.dots = VGroup()
        for k in range(NDOTS):
            th = 2 * np.pi * k / NDOTS
            p = np.array([np.cos(th), np.sin(th)])
            col = interpolate_color(GOLD, SKY, 0.5 + 0.5 * np.sin(th))
            d = Dot(SHAPE_C, radius=0.052, fill_color=col)

            def up(mo, p=p):
                q = self.mat() @ p
                mo.move_to(SHAPE_C + UNIT * np.array([q[0], q[1], 0.0]))

            d.add_updater(up)
            self.dots.add(d)

        self.arrows = VGroup()
        for j, col in ((0, GOLD), (1, SKY)):
            ln = Line(SHAPE_C, SHAPE_C + RIGHT, stroke_color=col,
                      stroke_width=5.0)
            tip = Dot(SHAPE_C, radius=0.085, fill_color=col)

            def lu(mo, j=j):
                q = self.mat()[:, j]
                mo.put_start_and_end_on(
                    SHAPE_C, SHAPE_C + UNIT * np.array([q[0], q[1], 0.0]))

            def tu(mo, j=j):
                q = self.mat()[:, j]
                mo.move_to(SHAPE_C + UNIT * np.array([q[0], q[1], 0.0]))

            ln.add_updater(lu)
            tip.add_updater(tu)
            self.arrows.add(ln, tip)

        # the matrix, live
        self.cells = VGroup()
        for i, (dx, dy, col) in enumerate(((-0.44, 0.34, GOLD), (0.44, 0.34, SKY),
                                           (-0.44, -0.34, GOLD), (0.44, -0.34, SKY))):
            c = Cell(lambda t=self.W[i]: Cell.show(t.get_value()),
                     [dx, MAT_Y + dy, 0.0], col)
            c.add_updater(lambda mo: mo.refresh())
            self.cells.add(c)

        br = VGroup()
        for sx in (-1, 1):
            x = sx * 0.92
            br.add(Line(np.array([x, MAT_Y + 0.66, 0]),
                        np.array([x, MAT_Y - 0.66, 0]),
                        stroke_color=GREY, stroke_width=2.4))
            for sy in (1, -1):
                br.add(Line(np.array([x, MAT_Y + sy * 0.66, 0]),
                            np.array([x - sx * 0.20, MAT_Y + sy * 0.66, 0]),
                            stroke_color=GREY, stroke_width=2.4))
        self.brackets = br

        self.dlabel = txt("det", 22, GREY, bold=False, w=1.0)
        self.dlabel.move_to(np.array([-0.52, DET_Y, 0]))
        self.dcell = Cell(self._detstr, [0.28, DET_Y, 0.0], WHITE_, 27)
        self.dcell.add_updater(lambda mo: mo.refresh())

    def _detstr(self):
        return Cell.show(float(np.linalg.det(self.mat())))

    def pose(self, M, beats=4, note=None, color=WHITE_):
        anims = [t.animate.set_value(float(v)) for t, v in zip(self.W, M)]
        if note is not None:
            anims += self.note_anims(note, color)
        self.play(*anims, run_time=self.T(beats), rate_func=hit)

    # ==================================================================
    def open_card(self):
        self.title = txt("x  →  W x", 34, WHITE_, w=3.0)
        self.title.move_to(np.array([0, MAT_Y + 1.15, 0]))
        self.add(self.dots, self.arrows, self.cells, self.brackets,
                 self.dlabel, self.dcell)
        self.play(FadeIn(self.title), FadeIn(self.brackets),
                  FadeIn(self.cells), FadeIn(self.dots), FadeIn(self.arrows),
                  FadeIn(self.dlabel), FadeIn(self.dcell), run_time=self.T(2.5))
        self.say("four numbers.", 2.5, GOLD)
        self.pad_to(END_OPEN)

    # ==================================================================
    # Sixteen bars. The shape does exactly what the numbers say.
    # ==================================================================
    def stage_dance(self):
        for i, M in enumerate(POSES):
            n, c = LINES.get(i, (None, WHITE_))
            self.pose(M, 4, n, c)
        self.pad_to(END_DANCE)

    # ==================================================================
    # What it was.
    # ==================================================================
    def stage_why(self):
        self.say("column one is where the gold arrow lands.", 3.5, GOLD)
        self.say("column two is where the blue one lands.", 3.5, SKY)
        self.say("that is all matrix multiplication is.", 3.5)
        self.say("and one layer of an AI is exactly this.", 3.5, GOLD)
        self.pad_to(END_WHY)

    # ==================================================================
    def stage_follow(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None

        f1 = txt("y = W x + b", 40, GOLD, w=4.2)
        f1.move_to(np.array([0, 0.95, 0]))
        f2 = txt("that is the whole machine", 26, WHITE_, w=4.4)
        f2.move_to(np.array([0, 0.24, 0]))
        f3 = txt("follow — the math behind AI", 21, GREY, bold=False, w=4.2)
        f3.move_to(np.array([0, -0.52, 0]))
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
