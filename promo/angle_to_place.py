"""
angle_to_place — sin and cos turn an angle into a place. 40.0s.

    BPM=150 manimgl angle_to_place.py AngleToPlace -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 5 OF "WHY DID WE LEARN THIS?" — same shell as sales_line.py: the
equation is the spine, it sits at the top for the whole video, it starts EMPTY,
and every number is dragged into its slot off the picture.

        x  =  r · cos θ
        y  =  r · sin θ

WHAT COS AND SIN ACTUALLY ARE. Draw a circle of radius ONE. Put a point on it.
Its width is cos θ. Its height is sin θ. That is not a fact about them — that
IS them, the whole definition, and it is the thing school never says out loud.
So both numbers are read straight off the grid:

    cos θ  ←  0.8      how far across the point is
    sin θ  ←  0.6      how far up it is

Then the only other idea in the video: a circle of radius 5 is the same circle,
five times bigger, so the point is in the same direction and five times further:

    x = 5 · 0.8 = 4
    y = 5 · 0.6 = 3

THE TWO-WAY PATTERN, same as every episode. What the viewer can measure gets
dragged UP into the equation — the width, the height, the length. What only the
formula can give them gets dropped back DOWN onto the picture: the place.

WHY THE ANGLE NEVER GETS A NUMBER. θ here is 36.87°, which is ugly, and its
value is irrelevant — the video is about turning an angle into a place, not
about which angle. Leaving it as θ keeps the one rounded number in the whole
series off the screen.

VERIFIED AT IMPORT
    cos² + sin² == 1                exactly, as fractions
    5·cos == 4 and 5·sin == 3       whole numbers, no square roots on screen
    the fractions match real trig    against np.cos/np.sin at the true angle

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_UNIT, END_DRAG, END_REAL = 34, 54, 80
END_TAKE, END_SHARE = 88, 92

SERIES = "WHY DID WE LEARN THIS?"

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
EQ_Y   = 2.66           # two rows, so the spine sits a little higher
ANS_Y  = 1.44
NOTE_Y = -3.10
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
COS = Fraction(4, 5)          # 0.8
SIN = Fraction(3, 5)          # 0.6
R   = 5

PX, PY = R * COS, R * SIN     # 4 and 3, exactly

assert COS * COS + SIN * SIN == 1, "the point has to be ON the unit circle"
assert PX == 4 and PY == 3, (PX, PY)
assert float(COS) == 0.8 and float(SIN) == 0.6

_th = float(np.arccos(float(COS)))
assert abs(np.cos(_th) - float(COS)) < 1e-12
assert abs(np.sin(_th) - float(SIN)) < 1e-12
assert 25 < np.degrees(_th) < 65, "the arc has to be big enough to see"

CS, SS = "0.8", "0.6"
RS      = str(R)
XS, YS  = str(PX), str(PY)

# the spine, two rows of five pieces — flat slots 0..9
ROWS = [["x", "=", "r", "·", "cos θ"],
        ["y", "=", "r", "·", "sin θ"]]
FLAT = [p for row in ROWS for p in row]
S_R1, S_COS, S_R2, S_SIN = 2, 4, 7, 9
SLOTS = (S_R1, S_COS, S_R2, S_SIN)


def rc(slot):
    """flat slot index -> (row, column)"""
    return divmod(slot, len(ROWS[0]))


# ------------------------------------------------------------------ drawing
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


def dashed(a, b, color=GOLD, wid=2.4, n=12):
    g = VGroup()
    a, b = np.asarray(a, float), np.asarray(b, float)
    for i in range(n):
        t0, t1 = i / n, (i + 0.55) / n
        g.add(seg(a + (b - a) * t0, a + (b - a) * t1, color, wid, 0.9))
    return g


def arrow(a, b, color=GOLD, wid=4.0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0], 0.0])
    h = min(0.20, 0.32 * L)
    g = VGroup(seg(a, b - u * h * 0.55, color, wid))
    head = VMobject(stroke_width=0)
    head.set_points_as_corners([b, b - u * h + n * h * 0.46,
                                b - u * h - n * h * 0.46, b])
    head.set_fill(color, 1.0)
    g.add(head)
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


class AngleToPlace(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.ans = None
        self.filled = {}

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
        self.stage_unit()
        self.stage_drag()
        self.stage_real()
        self.takeaway("We learned this at school.",
                      "Nobody ever said what for.")
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
        rows = VGroup()
        for r, row in enumerate(ROWS):
            g = VGroup()
            for c, base in enumerate(row):
                i = r * len(row) + c
                s = fill.get(i, base)
                if i == active:
                    col, sz = GOLD, int(size * 1.14)
                elif i in fill:
                    col, sz = GOLD, size
                elif i in SLOTS:
                    col, sz = DIM, size
                else:
                    col, sz = WHITE_, size
                g.add(txt(s, sz, col, w=1.5))
            g.arrange(RIGHT, buff=0.12)
            rows.add(g)
        rows.arrange(DOWN, buff=0.20)
        # line the two "=" signs up on each other, or the spine reads crooked
        rows[1].shift(RIGHT * (rows[0][1].get_center()[0]
                               - rows[1][1].get_center()[0]))
        if rows.get_width() > 4.5:
            rows.set_width(4.5)
        return rows.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats):
        self.play(Transform(self.eq, self.make_eq(active)),
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, size, fly=3.0, settle=2.0,
                  also=None):
        """Lift the number off the picture and drop it into its slot.

        The target is read off a freshly built equation, not the live one —
        the slots re-space every time one of them changes width, so the flier
        has to land where the piece is ABOUT to be. `also` fills sibling slots
        in the same move, which is how one r lands in both rows."""
        fill = {slot: value}
        if also:
            fill.update(also)
        nxt = self.make_eq(active=slot, also=fill)
        r, c = rc(slot)
        target = nxt[r][c]
        flier = txt(value, size, GOLD, w=1.6).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("x = r · cos θ", 42, GOLD, w=4.2),
                     txt("y = r · sin θ", 42, GOLD, w=4.2)) \
            .arrange(DOWN, buff=0.20).move_to(np.array([0, 1.15, 0]))
        q = VGroup(txt("sin and cos", 32, WHITE_, w=4.6),
                   txt("what are they FOR?", 32, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.20, 0]))
        sub = txt("they turn an angle into a place", 22, GREY, bold=False)
        sub.move_to(np.array([0, -1.10, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # What cos and sin ARE: a circle of radius one, and one point on it.
    # ==================================================================
    def stage_unit(self):
        self.U = 1.72                       # screen units per 1 on the grid
        self.O = np.array([0.0, -1.16, 0])  # where (0,0) sits

        def Q(x, y):
            return self.O + np.array([float(x) * self.U, float(y) * self.U, 0])

        self.Q = Q
        grid = VGroup()
        for k in range(-12, 13):
            v = k / 10.0
            if abs(v) > 1.21:
                continue
            wid = 1.6 if k % 5 else 2.1
            grid.add(seg(Q(v, -1.2), Q(v, 1.2), FAINT, wid, 0.75))
            grid.add(seg(Q(-1.2, v), Q(1.2, v), FAINT, wid, 0.75))
        axes = VGroup(seg(Q(-1.25, 0), Q(1.25, 0), GREY, 2.4, 0.85),
                      seg(Q(0, -1.25), Q(0, 1.25), GREY, 2.4, 0.85))
        ticks = VGroup()
        for v in (0.5, 1.0):
            ticks.add(txt(f"{v:g}", 16, GREY, bold=False, w=0.5)
                      .move_to(Q(v, 0) + np.array([0, -0.24, 0])))
            ticks.add(txt(f"{v:g}", 16, GREY, bold=False, w=0.5)
                      .move_to(Q(0, v) + np.array([-0.26, 0, 0])))
        self.picA = VGroup(grid, axes, ticks)
        self.play(FadeIn(grid), ShowCreation(axes), FadeIn(ticks),
                  run_time=self.T(2.5))

        circ = Circle(radius=self.U, stroke_color=SKY, stroke_width=3.0) \
            .move_to(Q(0, 0))
        rlab = txt("radius 1", 20, SKY, bold=False, w=1.3)
        rlab.move_to(Q(-0.62, 0.92))
        self.picA.add(circ, rlab)
        self.play(ShowCreation(circ), FadeIn(rlab), run_time=self.T(2.5))
        self.say("a circle. radius one. that is the whole set-up.", 3)

        P1 = Q(COS, SIN)
        ray = arrow(Q(0, 0), P1, GOLD, 4.0)
        dot = Dot(P1, radius=0.10, fill_color=GOLD)
        arc = Arc(start_angle=0, angle=_th, radius=self.U * 0.34,
                  stroke_color=GOLD, stroke_width=3.0).move_to(
                      Q(0, 0) + np.array([np.cos(_th / 2), np.sin(_th / 2), 0])
                      * self.U * 0.34)
        tl = txt("θ", 24, GOLD, w=0.4).move_to(
            Q(0, 0) + np.array([np.cos(_th / 2), np.sin(_th / 2), 0])
            * self.U * 0.60)
        self.picA.add(ray, dot, arc, tl)
        self.play(ShowCreation(ray), FadeIn(dot, scale=1.8), run_time=self.T(2.5))
        self.play(ShowCreation(arc), FadeIn(tl), run_time=self.T(2))
        self.say("turn by any angle θ. where does the point land?", 2.5)

        # the two measurements, straight off the grid
        wl = dashed(P1, Q(COS, 0), GOLD, 2.6, 7)
        self.cnum = txt(CS, 24, GOLD, w=0.8).move_to(
            Q(COS, 0) + np.array([0.02, -0.30, 0]))
        self.picA.add(wl, self.cnum)
        self.play(ShowCreation(wl), FadeIn(self.cnum, shift=0.1 * DOWN),
                  run_time=self.T(2.5))
        self.say("how far ACROSS it went — 0.8. that is cos θ.", 3, GOLD)

        hl = dashed(P1, Q(0, SIN), SKY, 2.6, 7)
        self.snum = txt(SS, 24, SKY, w=0.8).move_to(
            Q(0, SIN) + np.array([-0.34, 0.02, 0]))
        self.picA.add(hl, self.snum)
        self.play(ShowCreation(hl), FadeIn(self.snum, shift=0.1 * LEFT),
                  run_time=self.T(2.5))
        self.say("how far UP it went — 0.6. that is sin θ.", 3, SKY)
        self.pad_to(END_UNIT)

    # ==================================================================
    # Both numbers are measurements. Drag them up into the spine.
    # ==================================================================
    def stage_drag(self):
        self.say("that is not a fact about cos and sin. it IS them.", 3)
        self.drag_into(self.cnum.get_center(), S_COS, CS, 24, fly=3, settle=2)
        self.drag_into(self.snum.get_center(), S_SIN, SS, 24, fly=3, settle=2)
        self.say("width and height of one turn. nothing else.", 3)
        self.pad_to(END_DRAG)

    # ==================================================================
    # r — the only other idea: same direction, five times further.
    # ==================================================================
    def stage_real(self):
        self.play(FadeOut(self.picA), self.zoom.animate.set_value(0.96),
                  run_time=self.T(2))

        # the same picture, drawn on a grid five times coarser
        U = self.U / 3.30
        O = np.array([0.0, -1.28, 0])

        def Q(x, y):
            return O + np.array([float(x) * U, float(y) * U, 0])

        grid = VGroup()
        for k in range(-1, 7):
            grid.add(seg(Q(k, -1), Q(k, 5.4), FAINT, 1.8, 0.75))
            grid.add(seg(Q(-1, k), Q(6.0, k), FAINT, 1.8, 0.75))
        axes = VGroup(seg(Q(-1.1, 0), Q(6.1, 0), GREY, 2.4, 0.85),
                      seg(Q(0, -1.1), Q(0, 5.5), GREY, 2.4, 0.85))
        ticks = VGroup()
        for k in (2, 4):
            ticks.add(txt(str(k), 16, GREY, bold=False, w=0.4)
                      .move_to(Q(k, 0) + np.array([0, -0.24, 0])))
            ticks.add(txt(str(k), 16, GREY, bold=False, w=0.4)
                      .move_to(Q(0, k) + np.array([-0.26, 0, 0])))
        self.picB = VGroup(grid, axes, ticks)

        ray = arrow(Q(0, 0), Q(PX, PY), GOLD, 4.0)
        arc = Arc(start_angle=0, angle=_th, radius=U * 1.5,
                  stroke_color=GOLD, stroke_width=3.0).move_to(
                      Q(0, 0) + np.array([np.cos(_th / 2), np.sin(_th / 2), 0])
                      * U * 1.5)
        tl = txt("θ", 22, GOLD, w=0.4).move_to(
            Q(0, 0) + np.array([np.cos(_th / 2), np.sin(_th / 2), 0]) * U * 2.5)
        self.picB.add(ray, arc, tl)
        self.play(FadeIn(grid), ShowCreation(axes), FadeIn(ticks),
                  run_time=self.T(2))
        self.play(ShowCreation(ray), ShowCreation(arc), FadeIn(tl),
                  run_time=self.T(2.5))
        self.say("same angle. but the arrow is 5 long, not 1.", 2.5)

        rlab = txt(RS, 24, ROSE, w=0.6).move_to(
            Q(PX, PY) * 0.5 + Q(0, 0) * 0.5 + np.array([-0.30, 0.24, 0]))
        self.picB.add(rlab)
        self.play(FadeIn(rlab, scale=1.4), run_time=self.T(1))
        self.say("that length is r.", 2, ROSE)
        self.drag_into(rlab.get_center(), S_R1, RS, 24, fly=2.5, settle=1.5,
                       also={S_R2: RS})
        self.say("five times bigger circle. five times further out.", 2.5)

        # and the place drops back DOWN onto the picture
        self.ans = txt(f"= {XS}          = {YS}", 30, GOLD, w=4.2)
        self.ans.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.ans, scale=1.12), run_time=self.T(2),
                  rate_func=rush_from)

        dx = dashed(Q(PX, PY), Q(PX, 0), GOLD, 2.4, 6)
        dy = dashed(Q(PX, PY), Q(0, PY), GOLD, 2.4, 6)
        hit = Dot(Q(PX, PY), radius=0.11, fill_color=GOLD)
        place = txt(f"( {XS} , {YS} )", 26, GOLD, w=1.8).move_to(
            Q(PX, PY) + np.array([0.16, 0.34, 0]))
        self.picB.add(dx, dy, hit, place)
        self.play(ShowCreation(dx), ShowCreation(dy), FadeIn(hit, scale=2.0),
                  run_time=self.T(2))
        self.play(FadeIn(place, shift=0.10 * UP), run_time=self.T(1.5))
        self.say("an angle went in. a place came out.", 2)
        self.pad_to(END_REAL)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.ans, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is how it's solved", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.eq), FadeOut(self.ans),
                  FadeOut(self.title), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
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
