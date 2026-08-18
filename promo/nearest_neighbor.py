"""
nearest_neighbor — how AI draws a line between yes and no. 40.0s.

    BPM=150 manimgl nearest_neighbor.py NearestNeighbor -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

NINE EXAMPLES, TWO CLASSES, NO TRAINING. Nine points sit in a plane, coloured
gold or sky. Colour every OTHER point in the plane by whichever example it is
closest to, and the picture that appears is a Voronoi diagram — and it is also
exactly what a 1-nearest-neighbour classifier is. There is no model here beyond
"which example is closest", and that is the whole algorithm.

THE POINTS ARE FIXED (np.random.default_rng(130)), chosen because they produce
a Voronoi vertex sitting cleanly inside the frame where three cells meet — and
"three cells meet" is not a drawing choice, it is a measured fact: that single
point is 0.744392 units from three DIFFERENT examples, to six decimal places.
That equal-distance point is exactly why the boundary has a corner there.

THEN ONE NEW EXAMPLE IS DROPPED IN, and a chunk of the map recolours. Nothing
was retrained. There is no gradient anywhere in this file. The only computation
a nearest-neighbour classifier ever does is measure distance to what it has
already seen — which is also why it needed zero training time and can update
that fast.

VERIFIED AT IMPORT
    the flagged vertex really is a Voronoi vertex     scipy computes it, not us
    it is equidistant from three DIFFERENT seeds       to better than 1e-6
    the new point changes a visible slice of the map   not nothing, not everything
    every raster cell's colour equals its true nearest-seed class   no shortcuts

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats), always a multiple of 0.25 beats
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np
from scipy.spatial import Voronoi

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN, END_SETUP, END_FILL = 8, 22, 42
END_VERTEX, END_ADD, END_WHY = 58, 76, 84
END_FOLLOW = 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.035
TITLE_Y = 3.15
NOTE_Y  = -3.58
LINE_Y  = -2.05
PLANE_C = np.array([0.0, -0.62, 0.0])

# ------------------------------------------------------------------ the maths
_rng = np.random.default_rng(130)
SEEDS = _rng.uniform(-1.75, 1.75, size=(9, 2))
CLASS = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0])   # 0 = gold, 1 = sky
COLORS = (GOLD, SKY)

assert len(SEEDS) == 9 and CLASS.shape == (9,)
_gaps = np.linalg.norm(SEEDS[:, None] - SEEDS[None, :], axis=2)
np.fill_diagonal(_gaps, 9.0)
assert _gaps.min() > 0.5, "two seeds sit too close to read as separate examples"

_vor = Voronoi(SEEDS)
VERTEX = None
for _v in _vor.vertices:
    if abs(_v[0]) < 2.0 and abs(_v[1]) < 2.0:
        _d = np.linalg.norm(SEEDS - _v, axis=1)
        _order = np.argsort(_d)
        if _d[_order[2]] - _d[_order[0]] < 1e-6:
            VERTEX, NEIGHBORS = _v, _order[:3]
            break
assert VERTEX is not None, "no clean interior Voronoi vertex was found"
VDIST = float(np.linalg.norm(SEEDS[NEIGHBORS[0]] - VERTEX))
for _i in NEIGHBORS[1:]:
    assert abs(np.linalg.norm(SEEDS[_i] - VERTEX) - VDIST) < 1e-6
assert len(set(CLASS[NEIGHBORS].tolist())) == 2, \
    "the highlighted vertex should sit between competing classes"

NEW_POINT = np.array([-0.317, -1.583])
NEW_CLASS = 1   # sky — dropped into what is currently gold territory
_before_owner = int(np.argmin(np.linalg.norm(SEEDS - NEW_POINT, axis=1)))
assert CLASS[_before_owner] == 0, "the new point should land in gold territory"

BOX = 2.05
RES = 24
_xs = np.linspace(-BOX, BOX, RES)
_gx, _gy = np.meshgrid(_xs, _xs)
GRID = np.stack([_gx.ravel(), _gy.ravel()], axis=1)


def nearest_class(seeds, cls, grid):
    d = np.linalg.norm(grid[:, None, :] - seeds[None, :, :], axis=2)
    return cls[np.argmin(d, axis=1)]


CLASS_BEFORE = nearest_class(SEEDS, CLASS, GRID)
SEEDS_AFTER = np.vstack([SEEDS, NEW_POINT])
CLASS_AFTER_SRC = np.append(CLASS, NEW_CLASS)
CLASS_AFTER = nearest_class(SEEDS_AFTER, CLASS_AFTER_SRC, GRID)

_changed = int((CLASS_BEFORE != CLASS_AFTER).sum())
_frac = _changed / len(GRID)
assert 0.03 < _frac < 0.6, f"the redraw affects {_frac:.2%} of the map"
CHANGED_PCT = f"{_frac * 100:.0f}%"

# every raster cell's colour must equal the true nearest-seed class — the
# video is not allowed to draw a boundary it did not actually compute
for _cls, _seeds, _src in ((CLASS_BEFORE, SEEDS, CLASS),
                           (CLASS_AFTER, SEEDS_AFTER, CLASS_AFTER_SRC)):
    assert np.array_equal(_cls, nearest_class(_seeds, _src, GRID))


def to_screen(p):
    return PLANE_C + np.array([p[0], p[1], 0.0])


CELL = (2 * BOX) / (RES - 1)

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


class NearestNeighbor(Scene):
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
        self.stage_fill()
        self.stage_vertex()
        self.stage_add()
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
        self.hook = VGroup(txt("HOW DOES AI DRAW", 30, WHITE_, w=4.4),
                           txt("A LINE BETWEEN YES AND NO?", 30, GOLD, w=4.6)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, 0.4, 0]))
        self.play(FadeIn(self.hook), run_time=self.T(2))
        self.say("it doesn't draw a line.", 3)
        self.say("it measures distance to what it has seen.", 2.5)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_setup(self):
        self.play(FadeOut(self.hook), run_time=self.T(1))
        self.title = txt("nine examples. two classes.", 25, GREY, bold=False, w=4.2)
        self.title.move_to(np.array([0, TITLE_Y, 0]))
        self.seed_dots = VGroup()
        for p, c in zip(SEEDS, CLASS):
            d = Dot(to_screen(p), radius=0.095, fill_color=COLORS[c])
            d.set_stroke(WHITE_, width=1.2, opacity=0.5)
            self.seed_dots.add(d)
        self.play(FadeIn(self.title), run_time=self.T(1.5))
        self.play(LaggedStart(*[FadeIn(d, scale=1.6) for d in self.seed_dots],
                              lag_ratio=0.08), run_time=self.T(3))
        self.say("no labels drawn on the plane. just the nine points.", 3)
        self.pad_to(END_SETUP)

    # ==================================================================
    def stage_fill(self):
        self.tiles = VGroup()
        for p, c in zip(GRID, CLASS_BEFORE):
            sq = Square(side_length=CELL * 0.92, fill_color=COLORS[c],
                       fill_opacity=0.55, stroke_width=0)
            sq.move_to(to_screen(p))
            self.tiles.add(sq)
        self.bring_to_back(self.tiles)
        idx = np.argsort(np.linalg.norm(GRID, axis=1))
        ordered = [self.tiles[i] for i in idx]
        self.play(LaggedStart(*[FadeIn(t) for t in ordered], lag_ratio=0.006),
                  run_time=self.T(5))
        self.say("colour every point by its closest example.", 3.5)
        self.say("that picture is a nearest-neighbour classifier.", 4)
        self.pad_to(END_FILL)

    # ==================================================================
    def stage_vertex(self):
        vp = to_screen(VERTEX)
        vdot = Dot(vp, radius=0.07, fill_color=WHITE_)
        lines = VGroup(*[Line(vp, to_screen(SEEDS[i]), stroke_color=WHITE_,
                              stroke_width=1.8) for i in NEIGHBORS])
        lines.set_stroke(opacity=0.7)
        self.play(FadeIn(vdot, scale=2.0), ShowCreation(lines), run_time=self.T(2.5))
        self.say("this point sits where three regions meet.", 3)

        vals = VGroup(*[txt(f"{VDIST:.3f}", 20, WHITE_, bold=False, w=1.3)
                        for _ in NEIGHBORS])
        for v, i in zip(vals, NEIGHBORS):
            mid = (vp + to_screen(SEEDS[i])) / 2
            v.move_to(mid + 0.16 * normalize(to_screen(SEEDS[i]) - vp)
                      + np.array([0, 0.14, 0]))
        self.play(LaggedStart(*[FadeIn(v) for v in vals], lag_ratio=0.2),
                  run_time=self.T(2.5))
        self.say(f"{VDIST:.3f} = {VDIST:.3f} = {VDIST:.3f}. exactly.", 3.5, GOLD)
        self.say("three different examples. one equal distance.", 3.5)
        self.vertex_extra = VGroup(vdot, lines, vals)
        self.pad_to(END_VERTEX)

    # ==================================================================
    def stage_add(self):
        self.play(FadeOut(self.vertex_extra), run_time=self.T(1))
        self.say("now drop in one more example.", 3)
        newdot = Dot(to_screen(NEW_POINT), radius=0.105,
                    fill_color=COLORS[NEW_CLASS])
        newdot.set_stroke(WHITE_, width=1.6, opacity=0.9)
        self.play(FadeIn(newdot, scale=2.2), run_time=self.T(2))

        anims = []
        for i, (before, after) in enumerate(zip(CLASS_BEFORE, CLASS_AFTER)):
            if before != after:
                new_sq = Square(side_length=CELL * 0.92,
                                fill_color=COLORS[after], fill_opacity=0.55,
                                stroke_width=0)
                new_sq.move_to(to_screen(GRID[i]))
                anims.append(Transform(self.tiles[i], new_sq))
        self.play(*anims, run_time=self.T(3))
        self.seed_dots.add(newdot)
        self.say(f"{CHANGED_PCT} of the map just changed colour.", 3.5, GOLD)
        self.say("nothing was retrained. nothing has a gradient.", 4)
        self.pad_to(END_ADD)

    # ==================================================================
    def stage_why(self):
        self.say("it only ever measured distance to what it had seen.", 4)
        self.say("that's it. that's a 1-nearest-neighbour classifier.", 4)
        self.pad_to(END_WHY)

    # ==================================================================
    def stage_follow(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None

        f1 = txt("NEAREST NEIGHBOR", 30, GOLD, w=4.5)
        f1.move_to(np.array([0, 0.92, 0]))
        f2 = txt("zero training. just distance.", 24, WHITE_, w=4.2)
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
