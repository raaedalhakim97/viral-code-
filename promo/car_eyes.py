"""
car_eyes — rotation, run on a self-driving car. 40.0s.

    BPM=150 manimgl car_eyes.py CarEyes -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 10, AND THE THIRD "WHERE YOU ACTUALLY USE IT" COMPANION — episode 7's
formula, run on the job it is genuinely doing right now, in traffic.

        new x  =  x · cos θ  −  y · sin θ
        new y  =  x · sin θ  +  y · cos θ

THE REAL PROBLEM. A car's camera does not see the world. It sees ITS OWN VIEW:
"3 metres to my right, 4 metres in front of me." Front and right are the car's
words, and they move when the car turns. A map does not have a front. It has
north and east, and it never turns.

So every single thing the car sees has to be turned before it means anything —
and turning is the one job sin and cos do.

        camera says   3 right, 4 ahead        the CAR's frame
        car is turned by θ                    cos θ = 0.8, sin θ = 0.6
        on the map    (0, 5)                  5 m due north. Dead ahead of NOTHING.

WHY THIS IS THE RIGHT EXAMPLE. It is the honest one. Self-driving, robot
vacuums, AR filters, drone landing, a phone that knows which way up it is — all
of them do this thousands of times a second, and all of them break in exactly
the same way if it is skipped: the car would brake for a pedestrian who is not
where it thinks. That failure is easy to say in one line and it makes the maths
feel like it matters, because it does.

VERIFIED AT IMPORT
    cos² + sin² == 1                   exactly, as Fractions
    the sighting lands on (0, 5)       in Fractions, not floats
    distance in == distance out == 5   turning cannot move the pedestrian
    it matches a real rotation matrix  against np.cos/np.sin at the true angle
    it lands at exactly 90°            so "due north" is literally true

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
END_SEE, END_PROBLEM, END_TURN, END_WHY = 24, 40, 68, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "WHERE YOU ACTUALLY USE IT"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"
GREEN  = "#A3BE8C"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
EQ_Y   = 2.72
ANS_Y  = 1.62
NOTE_Y = -3.16
LINE_Y = -2.05

MINUS = "−"

# ------------------------------------------------------------------ numbers
COS = Fraction(4, 5)          # 0.8   — episodes 5 and 7, unchanged
SIN = Fraction(3, 5)          # 0.6
X, Y = Fraction(3), Fraction(4)       # 3 right, 4 ahead — the car's own words

NX = X * COS - Y * SIN        # 0
NY = X * SIN + Y * COS        # 5

assert COS * COS + SIN * SIN == 1
assert (NX, NY) == (0, 5), (NX, NY)
assert X * X + Y * Y == NX * NX + NY * NY == 25, \
    "turning cannot move the pedestrian"

_th = float(np.arccos(float(COS)))
_R = np.array([[np.cos(_th), -np.sin(_th)], [np.sin(_th), np.cos(_th)]])
_out = _R @ np.array([float(X), float(Y)])
assert abs(_out[0] - float(NX)) < 1e-12 and abs(_out[1] - float(NY)) < 1e-12
assert abs(np.degrees(np.arctan2(float(NY), float(NX))) - 90.0) < 1e-9, \
    "'due north' has to be literally true"


def dec(f):
    v = float(f)
    assert abs(v * 10 - round(v * 10)) < 1e-12, f
    return f"{v:g}"


CS, SS   = dec(COS), dec(SIN)
XS, YS   = dec(X), dec(Y)
NXS, NYS = dec(NX), dec(NY)

ROWS = [["new x", "=", "x", "·", "cos θ", MINUS, "y", "·", "sin θ"],
        ["new y", "=", "x", "·", "sin θ", "+",   "y", "·", "cos θ"]]
NCOL = len(ROWS[0])
S_X   = (2, 11)
S_Y   = (6, 15)
S_COS = (4, 17)
S_SIN = (8, 13)
SLOTS = S_X + S_Y + S_COS + S_SIN

for _g, _w in ((S_X, "x"), (S_Y, "y"), (S_COS, "cos θ"), (S_SIN, "sin θ")):
    for _i in _g:
        assert ROWS[_i // NCOL][_i % NCOL] == _w, (_i, _w)


def rc(slot):
    return divmod(slot, NCOL)


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners([np.asarray(a, float), np.asarray(b, float)])
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


def car(color, ang):
    """A little wedge, pointing where the car is pointing."""
    g = VGroup()
    body = VMobject(stroke_color=color, stroke_width=3.0)
    body.set_points_as_corners([np.array([0.0, 0.30, 0]),
                                np.array([0.18, -0.22, 0]),
                                np.array([-0.18, -0.22, 0]),
                                np.array([0.0, 0.30, 0])])
    body.set_fill(color, 0.28)
    g.add(body)
    g.rotate(ang - np.pi / 2, about_point=ORIGIN)
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


class CarEyes(Scene):
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
        self.stage_see()
        self.stage_problem()
        self.stage_turn()
        self.stage_why()
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
    def make_eq(self, active=(), also=None, size=30):
        active = active if isinstance(active, (tuple, list)) else (active,)
        fill = dict(self.filled)
        if also:
            fill.update(also)
        rows = VGroup()
        for r, row in enumerate(ROWS):
            g = VGroup()
            for c, base in enumerate(row):
                i = r * NCOL + c
                s = fill.get(i, base)
                if i in active:
                    col, sz = GOLD, int(size * 1.16)
                elif i in fill:
                    col, sz = GOLD, size
                elif i in SLOTS:
                    col, sz = DIM, size
                else:
                    col, sz = WHITE_, size
                g.add(txt(s, sz, col, w=1.4))
            g.arrange(RIGHT, buff=0.09)
            rows.add(g)
        rows.arrange(DOWN, buff=0.22)
        rows[1].shift(RIGHT * (rows[0][1].get_center()[0]
                               - rows[1][1].get_center()[0]))
        if rows.get_width() > 4.62:
            rows.set_width(4.62)
        return rows.move_to(np.array([0, EQ_Y, 0]))

    def drag_into(self, source_point, slots, value, size, fly=2.5, settle=1.5):
        fill = {i: value for i in slots}
        nxt = self.make_eq(active=slots, also=fill)
        r, c = rc(slots[0])
        target = nxt[r][c]
        flier = txt(value, size, GOLD, w=1.4).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("new x = x cos θ − y sin θ", 29, GOLD, w=4.5),
                     txt("new y = x sin θ + y cos θ", 29, GOLD, w=4.5)) \
            .arrange(DOWN, buff=0.20).move_to(np.array([0, 1.22, 0]))
        q = VGroup(txt("a self-driving car", 31, WHITE_, w=4.6),
                   txt("cannot see the world.", 31, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.12, 0]))
        sub = txt("it only sees its own view", 22, GREY, bold=False)
        sub.move_to(np.array([0, -1.02, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.66, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # What the camera says: 3 right, 4 ahead.
    # ==================================================================
    def stage_see(self):
        self.U = 0.40
        self.O = np.array([-0.42, -1.62, 0])

        def Q(x, y):
            return self.O + np.array([float(x) * self.U, float(y) * self.U, 0])

        self.Q = Q
        grid = VGroup()
        for k in range(-2, 7):
            grid.add(seg(Q(k, -1.4), Q(k, 5.6), FAINT, 1.7, 0.75))
            grid.add(seg(Q(-1.4, k), Q(5.6, k), FAINT, 1.7, 0.75))
        axes = VGroup(seg(Q(-1.5, 0), Q(5.7, 0), GREY, 2.4, 0.85),
                      seg(Q(0, -1.5), Q(0, 5.7), GREY, 2.4, 0.85))
        ticks = VGroup()
        for k in (2, 4):
            ticks.add(txt(str(k), 15, GREY, bold=False, w=0.4)
                      .move_to(Q(k, 0) + np.array([0, -0.22, 0])))
            ticks.add(txt(str(k), 15, GREY, bold=False, w=0.4)
                      .move_to(Q(0, k) + np.array([-0.24, 0, 0])))
        self.pic = VGroup(grid, axes, ticks)
        self.play(FadeIn(grid), ShowCreation(axes), FadeIn(ticks),
                  run_time=self.T(2))

        self.carw = car(SKY, _th).move_to(Q(0, 0))
        self.ray = arrow(Q(0, 0), Q(X, Y), GOLD, 4.0)
        ped = Dot(Q(X, Y), radius=0.10, fill_color=ROSE)
        plab = txt("person", 19, ROSE, bold=False, w=1.3)
        plab.move_to(Q(X, Y) + np.array([0.56, 0.18, 0]))
        self.pic.add(self.carw, self.ray, ped, plab)
        self.play(FadeIn(self.carw, scale=1.5), run_time=self.T(1.5))
        self.play(ShowCreation(self.ray), FadeIn(ped, scale=1.8), FadeIn(plab),
                  run_time=self.T(2.5))
        self.say("the camera sees a person.", 2.5)

        wl = dashed(Q(X, Y), Q(X, 0), GOLD, 2.3, 5)
        hl = dashed(Q(X, Y), Q(0, Y), GOLD, 2.3, 5)
        self.xnum = txt(XS, 22, GOLD, w=0.6).move_to(
            Q(X, 0) + np.array([0.02, -0.26, 0]))
        self.ynum = txt(YS, 22, GOLD, w=0.6).move_to(
            Q(0, Y) + np.array([-0.28, 0.02, 0]))
        self.pic.add(wl, hl, self.xnum, self.ynum)
        self.play(ShowCreation(wl), ShowCreation(hl),
                  FadeIn(self.xnum), FadeIn(self.ynum), run_time=self.T(2.5))
        self.say("3 metres right. 4 metres ahead.", 3, GOLD)
        self.pad_to(END_SEE)

    # ==================================================================
    # "Right" and "ahead" are the car's words. A map has neither.
    # ==================================================================
    def stage_problem(self):
        self.say("right and ahead of WHAT? of the car.", 3, ROSE)
        self.say("turn the car, and both words change.", 3, ROSE)
        self.say("a map has no ahead. it has north.", 3, SKY)

        card = VGroup(txt("how far the car is turned:", 21, GREY,
                          bold=False, w=3.5),
                      txt(f"cos θ = {CS}      sin θ = {SS}", 25, SKY, w=4.3)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, 0.42, 0]))
        self.play(FadeIn(card, shift=0.10 * UP), run_time=self.T(2.5))

        fill = {i: CS for i in S_COS}
        fill.update({i: SS for i in S_SIN})
        nxt = self.make_eq(active=S_COS + S_SIN, also=fill)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(card, shift=0.6 * UP),
                  run_time=self.T(3))
        self.pad_to(END_PROBLEM)

    # ==================================================================
    # Turn the sighting. It lands due north.
    # ==================================================================
    def stage_turn(self):
        self.play(self.zoom.animate.set_value(0.96), run_time=self.T(1.5))
        self.drag_into(self.xnum.get_center(), S_X, XS, 22, fly=2.5, settle=1.5)
        self.drag_into(self.ynum.get_center(), S_Y, YS, 22, fly=2.5, settle=1)
        self.say("what the camera said, into the formula.", 2.5)

        self.ans = txt(f"new x = {NXS}     new y = {NYS}", 28, GREEN, w=4.4)
        self.ans.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.ans, scale=1.12), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.say("2.4 minus 2.4 is 0. 1.8 plus 3.2 is 5.", 2.5, GREEN)

        Q = self.Q
        newray = arrow(Q(0, 0), Q(NX, NY), GREEN, 4.2)
        ghost = dashed(Q(X, Y), Q(NX, NY), GREY, 2.0, 9)
        hit = Dot(Q(NX, NY), radius=0.11, fill_color=GREEN)
        self.pic.add(newray, ghost, hit)
        self.play(ShowCreation(ghost), run_time=self.T(1.5))
        self.play(Transform(self.ray, newray),
                  Transform(self.carw, car(GREEN, np.pi / 2).move_to(Q(0, 0))),
                  run_time=self.T(3), rate_func=smooth)
        self.play(FadeIn(hit, scale=2.0), run_time=self.T(1.5))
        self.say("on the map: 5 metres due north.", 3, GREEN)
        self.say("same person. still 5 away. new words.", 2.5)
        self.pad_to(END_TURN)

    # ==================================================================
    # And what happens if you skip it.
    # ==================================================================
    def stage_why(self):
        self.say("skip that step and the car brakes", 2.5, ROSE)
        self.say("for somebody who isn't there.", 2.5, ROSE)
        self.say("robot vacuums, AR filters, drones landing —", 3)
        self.say("all of them, thousands of times a second.", 3)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.ans, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, -0.30, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -1.02, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is how it's solved", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.50, 0]))
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
