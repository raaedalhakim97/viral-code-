"""
linear_geometry — dancing linear equations, drawn as geometry. 28.8s.

    BPM=150 manimgl linear_geometry.py LinearGeometry -w -r 1080x1920

88 beats = 22 bars = 35.200s at 150 BPM.

ONE MATRIX CARRIES THE WHOLE VIDEO.

        A = [ 2  1 ]        det A = 3
            [ 1  2 ]

Its ROWS are the two equations:      2x +  y = 0
                                      x + 2y = 3      solution (-1, 2)
Its COLUMNS are where the basis lands: (1,0) -> (2,1),  (0,1) -> (1,2)
Its unit square becomes (0,0) (2,1) (3,3) (1,2), area exactly 3 = det A
Its EIGENVECTORS are (1,1) stretched x3, and (-1,1) left alone x1

Every one of those is the same nine numbers seen from a different side, which is
the entire argument of the video: the equation, the picture and the matrix are
one object. Nothing here is an analogy.

The singular case reuses it:  B = [ 2  1 ]   det B = 0
                                  [ 4  2 ]
B's columns (2,4) and (1,2) both lie on y = 2x, so the plane collapses onto a
line — and B's rows are 2x + y = 0 and 4x + 2y = 3, which are parallel and never
meet. Space collapsing and the system having no solution are the same fact.

All values verified with numpy before the scene was written.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 88            # 22 bars = 35.200s
BODY_END = 68
TAKE_END = 75

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
TOP_Y   = 3.30
CAP_Y   = 1.78
NOTE_Y  = -1.62

R = 3                      # plot spans -3..3 in both directions
S = 0.46                   # scene units per math unit
OX, OY = 0.0, 0.05         # where the maths origin sits on screen
# A stretches by x3, so the transformed plane CANNOT stay inside a fixed box —
# (3,3) is as far out as the honest picture goes. The plot is therefore a
# viewport: opaque bands mask everything above and below it, and the grid runs
# off the sides, which is what looking at part of an infinite plane looks like.
VIEW_TOP, VIEW_BOT = 1.46, -1.36

A = np.array([[2.0, 1.0], [1.0, 2.0]])
B = np.array([[2.0, 1.0], [4.0, 2.0]])

# Checked at import, so a bad edit fails the render instead of shipping.
assert round(float(np.linalg.det(A)), 9) == 3.0
assert round(float(np.linalg.det(B)), 9) == 0.0
assert list(np.linalg.solve(A, [0.0, 3.0])) == [-1.0, 2.0]
assert list(A @ np.array([1.0, 1.0])) == [3.0, 3.0]


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, w=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    return m


def P(x, y):
    """maths coordinates -> scene coordinates."""
    return np.array([OX + x * S, OY + y * S, 0])


def clip(m, b):
    """Where y = mx + b leaves the plot box. Both lines here have finite slope."""
    pts = []
    for x in (-R, R):
        y = m * x + b
        if -R - 1e-9 <= y <= R + 1e-9:
            pts.append((x, y))
    if abs(m) > 1e-9:
        for y in (-R, R):
            x = (y - b) / m
            if -R - 1e-9 <= x <= R + 1e-9:
                pts.append((x, y))
    uniq = []
    for p in pts:
        if not any(abs(p[0] - q[0]) < 1e-6 and abs(p[1] - q[1]) < 1e-6
                   for q in uniq):
            uniq.append(p)
    return uniq[0], uniq[1]


def line_mob(m, b, color=WHITE_, w=3.2):
    a, c = clip(m, b)
    return seg(P(*a), P(*c), color, w)


def grid_mob(M=None, color=FAINT, w=1.3, op=0.9):
    """The plane. A linear map sends lines to lines, so two points per line is
    exact — and it makes Transform interpolate the deformation correctly."""
    g = VGroup()
    for i in range(-R, R + 1):
        for p, q in (((i, -R), (i, R)), ((-R, i), (R, i))):
            if M is not None:
                p = tuple(M @ np.array(p))
                q = tuple(M @ np.array(q))
            g.add(seg(P(*p), P(*q), color, w, op))
    return g


def arrow(x, y, color=GOLD, w=4.0, head=0.16):
    o, t = P(0, 0), P(x, y)
    d = t - o
    n = np.linalg.norm(d)
    if n < 1e-9:
        return VGroup()
    u = d / n
    perp = np.array([-u[1], u[0], 0])
    g = VGroup(seg(o, t, color, w))
    g.add(seg(t, t - u * head * 2 + perp * head, color, w),
          seg(t, t - u * head * 2 - perp * head, color, w))
    return g


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


class LinearGeometry(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.eq = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open_card()
        self.ch1_line()
        self.ch2_cross()
        self.ch3_matrix()
        self.ch4_collapse()
        self.ch5_eigen()
        self.close("Every equation here is a shape you can watch move.",
                   "That is all linear algebra is.")

    # ------------------------------------------------------------------
    def T(self, beats):
        self.used += beats
        return round(beats * self.B * FPS) / FPS

    def pad_to(self, target):
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(f"overruns by {-rem:.2f} beats — trim it")
        if rem > 0.01:
            self.wait(self.T(rem))

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.055):
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def say(self, s, beats=2, color=WHITE_, size=23):
        new = txt(s, size, color, bold=False, w=4.4)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def show_eq(self, s, beats=1, color=WHITE_, size=30):
        """The dancing equation. It pulses on every beat for the whole video —
        that is the only thing on screen that never stops moving."""
        new = self.dance(txt(s, size, color, w=4.4)
                         .move_to(np.array([0, CAP_Y, 0])), 0.06)
        if self.eq is None:
            self.eq = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.eq.clear_updaters()
            self.play(FadeOut(self.eq), FadeIn(new), run_time=self.T(beats))
            self.eq = new

    # ------------------------------------------------------------------
    def open_card(self):
        self.title = txt("WHAT IS A MATRIX?", 50, WHITE_, w=4.6)
        self.title.move_to(np.array([0, 1.05, 0]))
        self.sub = txt("linear equations, drawn", 24, GOLD, bold=False)
        self.sub.move_to(np.array([0, 0.35, 0]))
        self.add(self.title, self.sub)
        self.wait(self.T(2))
        self.mark = txt("OBSERVER COLLAPSE", 18, GREY, bold=False, w=3.0)
        self.mark.move_to(np.array([0, TOP_Y, 0]))
        self.play(FadeIn(self.mark), run_time=self.T(1))
        self.play(self.title.animate.set_height(
                      self.title.get_height() * 0.50).move_to(np.array([0, 2.62, 0])),
                  self.sub.animate.set_height(
                      self.sub.get_height() * 0.86).move_to(np.array([0, 2.18, 0])),
                  run_time=self.T(1))

    def close(self, a, b):
        self.pad_to(BODY_END)
        keep = self.stage + [m for m in (self.note, self.eq) if m is not None]
        for m in keep:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in keep], run_time=self.T(1))

        l1 = txt(a, 28, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 25, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(TAKE_END)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.title),
                  FadeOut(self.sub), FadeOut(self.mark), run_time=self.T(1))
        self.signature()

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

    # ==================================================================
    # 1 — a linear equation IS a line, and the two numbers move it
    # ==================================================================
    def ch1_line(self):
        self.grid = grid_mob()
        axes = VGroup(seg(P(-R, 0), P(R, 0), GREY, 2.0, 0.7),
                      seg(P(0, -R), P(0, R), GREY, 2.0, 0.7))
        self.play(FadeIn(self.grid), ShowCreation(axes), run_time=self.T(2))
        self.stage = [self.grid, axes]

        # Masks, then the header re-added so it sits on top of them. manimgl's
        # Scene.add removes before appending, so re-adding raises z-order.
        for lo, hi in ((VIEW_TOP, 4.7), (-4.7, VIEW_BOT)):
            band = Rectangle(width=6.0, height=hi - lo, stroke_width=0)
            band.set_fill(BLACK, opacity=1.0)
            band.move_to(np.array([0, (lo + hi) / 2, 0]))
            self.add(band)
        self.add(self.title, self.sub, self.mark)

        self.show_eq("y = mx + b", 1)
        self.line = line_mob(1.0, 0.0, WHITE_)
        self.play(ShowCreation(self.line), run_time=self.T(2))
        self.stage.append(self.line)
        self.say("two numbers, and you have every line there is", 2)

        for m, note in ((0.35, "m tilts it"), (2.2, None), (1.0, None)):
            new = line_mob(m, 0.0, WHITE_)
            self.play(Transform(self.line, new), run_time=self.T(1))
            if note:
                self.say(note, 1, GOLD)
        self.say("b lifts it", 1, GOLD)
        for b in (1.6, -1.6, 0.0):
            new = line_mob(1.0, b, WHITE_)
            self.play(Transform(self.line, new), run_time=self.T(1))

    # ==================================================================
    # 2 — two equations, and solving is where the pictures meet
    # ==================================================================
    def ch2_cross(self):
        self.show_eq("2x + y = 0", 1)
        l1 = line_mob(-2.0, 0.0, COOL)
        self.play(Transform(self.line, l1), run_time=self.T(1.5))
        self.say("one equation, one line", 1)

        self.show_eq("x + 2y = 3", 1)
        l2 = line_mob(-0.5, 1.5, WHITE_)
        self.play(ShowCreation(l2), run_time=self.T(1.5))
        self.stage.append(l2)
        self.say("a second one, a second line", 2)

        hit = Dot(P(-1, 2), radius=0.11, fill_color=GOLD)
        self.play(FadeIn(hit, scale=2.0), run_time=self.T(1))
        self.stage.append(hit)
        lab = txt("(−1, 2)", 24, GOLD, w=1.5)
        lab.move_to(P(-1, 2) + np.array([0.75, 0.30, 0]))
        self.play(FadeIn(lab), run_time=self.T(1))
        self.stage.append(lab)
        self.say("solving them is finding where they cross", 3, GOLD)

    # ==================================================================
    # 3 — the same four numbers, as a transformation of the plane
    # ==================================================================
    def ch3_matrix(self):
        self.play(FadeOut(self.line), FadeOut(self.stage[-1]),
                  FadeOut(self.stage[-2]), FadeOut(self.stage[-3]),
                  run_time=self.T(1))
        for m in self.stage[-3:]:
            self.stage.remove(m)
        self.stage.remove(self.line)

        self.show_eq("[ 2  1 ;  1  2 ]", 1, WHITE_, 28)
        self.say("stack the four numbers and you get a matrix", 2)

        sq = VMobject(stroke_color=GOLD, stroke_width=3.0)
        sq.set_points_as_corners([P(0, 0), P(1, 0), P(1, 1), P(0, 1), P(0, 0)])
        sq.set_fill(GOLD, opacity=0.20)
        self.play(ShowCreation(sq), run_time=self.T(1))
        self.stage.append(sq)
        self.say("watch one square while the plane moves", 2)

        newgrid = grid_mob(A)
        corners = [tuple(A @ np.array(p)) for p in ((0, 0), (1, 0), (1, 1), (0, 1))]
        newsq = VMobject(stroke_color=GOLD, stroke_width=3.0)
        newsq.set_points_as_corners([P(*c) for c in corners] + [P(*corners[0])])
        newsq.set_fill(GOLD, opacity=0.20)
        self.play(Transform(self.grid, newgrid), Transform(sq, newsq),
                  run_time=self.T(3))
        self.say("that is the whole meaning of the matrix", 2)

        det = txt("area  1  →  3", 26, GOLD, w=3.0)
        det.move_to(np.array([0, -0.98, 0]))
        self.play(FadeIn(det), run_time=self.T(1))
        self.stage.append(det)
        self.say("the determinant is that number: 3", 3, GOLD)

    # ==================================================================
    # 4 — determinant zero, from both sides at once
    # ==================================================================
    def ch4_collapse(self):
        self.show_eq("[ 2  1 ;  4  2 ]", 1, WHITE_, 28)
        flat = grid_mob(B)
        # B sends the unit square to the degenerate quad (0,0) (2,4) (3,6) (1,2)
        # — every corner on y = 2x, area 0. Two of those corners are outside the
        # plot box, so what is drawn is that segment clipped to it: (0,0)-(1.5,3).
        # Drawing the full image would punch straight through the header mask.
        newsq = VMobject(stroke_color=GOLD, stroke_width=3.0)
        newsq.set_points_as_corners([P(0, 0), P(1.5, 3), P(1.5, 3), P(0, 0), P(0, 0)])
        newsq.set_fill(GOLD, opacity=0.0)
        newdet = txt("area  1  →  0", 26, GOLD, w=3.0)
        newdet.move_to(np.array([0, -0.98, 0]))
        self.play(Transform(self.grid, flat), Transform(self.stage[-2], newsq),
                  Transform(self.stage[-1], newdet), run_time=self.T(3))
        self.say("change one number and the plane falls onto a line", 3)
        self.say("no crossing. no solution. same fact.", 3, GOLD)

    # ==================================================================
    # 5 — the direction that refuses to turn
    # ==================================================================
    def ch5_eigen(self):
        self.play(Transform(self.grid, grid_mob(A)),
                  FadeOut(self.stage[-1]), FadeOut(self.stage[-2]),
                  run_time=self.T(2))
        for m in self.stage[-2:]:
            self.stage.remove(m)
        self.show_eq("Av = 3v", 1, GOLD, 30)

        v = arrow(1, 1, WHITE_)
        self.play(ShowCreation(v), run_time=self.T(1))
        self.stage.append(v)
        self.play(Transform(v, arrow(3, 3, GOLD)), run_time=self.T(2))
        self.say("almost every arrow turns. this one only grew.", 3, GOLD)


