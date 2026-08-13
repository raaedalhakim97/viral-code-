"""
rotate_it — how you turn anything, with sin and cos. 40.0s.

    BPM=150 manimgl rotate_it.py RotateIt -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 7 OF "WHY DID WE LEARN THIS?" — and the direct sequel to episode 5.
Same shell: the equation is the spine, it sits at the top for the whole video,
it starts EMPTY, and every number is dragged into its slot off the picture.

        new x  =  x · cos θ  −  y · sin θ
        new y  =  x · sin θ  +  y · cos θ

EPISODE 5 BUILT THE INGREDIENTS. It showed that cos θ is how far across one
turn goes and sin θ is how far up — and for this angle those are 0.8 and 0.6.
So this episode does not have to earn them again. They arrive as a recall card
and drop straight into all four slots, and the only things the viewer has to
find on the picture are the two numbers of the point itself.

        point   (3, 4)          counted off the grid
        turn    cos θ = 0.8, sin θ = 0.6

        new x = 3(0.8) − 4(0.6) = 2.4 − 2.4 = 0
        new y = 3(0.6) + 4(0.8) = 1.8 + 3.2 = 5

THE ARROW LANDS ON (0, 5). Dead straight up, exactly 5 tall. That is the whole
reason these numbers were chosen: the payoff is a place the eye can check in
half a second, and the "0" arrives as a visible 2.4 − 2.4 rather than as a
claim. Turning never changes length, and 5 in, 5 out, says so.

WHY THERE IS A MINUS. It is the question every student has about this formula
and nobody answers. Going up-and-left as you turn means the height has to eat
into the width — so the y term comes off the new x. The video says it in one
line, at the moment the 2.4 cancels the 2.4.

VERIFIED AT IMPORT
    cos² + sin² == 1                     exactly, as fractions
    the rotation lands on (0, 5)         in Fractions, not floats
    length in == length out == 5         turning cannot change length
    it matches a real rotation matrix    against np.cos/np.sin at the true angle
    every number shown is exact          0.8 0.6 2.4 1.8 3.2 — one decimal each

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
END_POINT, END_RECALL, END_DRAG, END_TURN = 24, 37, 52, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "WHY DID WE LEARN THIS?"

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
EQ_Y   = 2.70
ANS_Y  = 1.62
WRK_Y  = 1.06
NOTE_Y = -3.16
LINE_Y = -2.05

MINUS = "−"

# ------------------------------------------------------------------ numbers
COS = Fraction(4, 5)          # 0.8   — episode 5's numbers, unchanged
SIN = Fraction(3, 5)          # 0.6
X, Y = Fraction(3), Fraction(4)

NX = X * COS - Y * SIN        # 0
NY = X * SIN + Y * COS        # 5

assert COS * COS + SIN * SIN == 1
assert (NX, NY) == (0, 5), (NX, NY)
assert X * X + Y * Y == NX * NX + NY * NY == 25, "turning cannot change length"

_th = float(np.arccos(float(COS)))
_R = np.array([[np.cos(_th), -np.sin(_th)], [np.sin(_th), np.cos(_th)]])
_out = _R @ np.array([float(X), float(Y)])
assert abs(_out[0] - float(NX)) < 1e-12 and abs(_out[1] - float(NY)) < 1e-12
assert abs(np.degrees(np.arctan2(float(NY), float(NX))) - 90.0) < 1e-9, \
    "the payoff only reads if it lands dead straight up"

# every product on screen, exact to one decimal
P_XC, P_YS = X * COS, Y * SIN      # 2.4 and 2.4 — they cancel
P_XS, P_YC = X * SIN, Y * COS      # 1.8 and 3.2 — they make 5
assert P_XC == P_YS == Fraction(12, 5)
assert P_XS + P_YC == 5


def dec(f):
    """A Fraction with one decimal place, printed without a trailing .0"""
    v = float(f)
    assert abs(v * 10 - round(v * 10)) < 1e-12, f
    return f"{v:g}"


CS, SS   = dec(COS), dec(SIN)          # 0.8  0.6
XS, YS   = dec(X), dec(Y)              # 3    4
NXS, NYS = dec(NX), dec(NY)            # 0    5

# the spine, two rows of nine pieces — flat slots 0..17
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


class RotateIt(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.ans = None
        self.wrk = None
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
        self.stage_point()
        self.stage_recall()
        self.stage_drag()
        self.stage_turn()
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
        """One number, both rows: `slots` is the pair it belongs in. The flier
        aims at the first of them, and the target is read off a FRESHLY built
        equation — the slots re-space every time one changes width, so it has
        to land where the piece is about to be."""
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

    def show_wrk(self, s, beats, color=WHITE_, size=27):
        new = txt(s, size, color, w=4.4).move_to(np.array([0, WRK_Y, 0]))
        if self.wrk is None:
            self.wrk = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(Transform(self.wrk, new), run_time=self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("new x = x cos θ − y sin θ", 30, GOLD, w=4.5),
                     txt("new y = x sin θ + y cos θ", 30, GOLD, w=4.5)) \
            .arrange(DOWN, buff=0.20).move_to(np.array([0, 1.20, 0]))
        q = VGroup(txt("how do you TURN", 32, WHITE_, w=4.6),
                   txt("something?", 32, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.14, 0]))
        sub = txt("sin and cos do the whole job", 22, GREY, bold=False)
        sub.move_to(np.array([0, -1.04, 0]))
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
    # One arrow on a grid, and the two numbers that name it.
    # ==================================================================
    def stage_point(self):
        self.U = 0.40
        self.O = np.array([-0.42, -1.60, 0])

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
                  run_time=self.T(2.5))

        self.ray = arrow(Q(0, 0), Q(X, Y), GOLD, 4.0)
        dot = Dot(Q(X, Y), radius=0.09, fill_color=GOLD)
        self.pic.add(self.ray, dot)
        self.play(ShowCreation(self.ray), FadeIn(dot, scale=1.8),
                  run_time=self.T(2.5))
        self.say("one arrow. now turn it. where does it end up?", 3)

        wl = dashed(Q(X, Y), Q(X, 0), GOLD, 2.3, 5)
        hl = dashed(Q(X, Y), Q(0, Y), GOLD, 2.3, 5)
        self.xnum = txt(XS, 22, GOLD, w=0.6).move_to(
            Q(X, 0) + np.array([0.02, -0.26, 0]))
        self.ynum = txt(YS, 22, GOLD, w=0.6).move_to(
            Q(0, Y) + np.array([-0.28, 0.02, 0]))
        self.pic.add(wl, hl, self.xnum, self.ynum)
        self.play(ShowCreation(wl), ShowCreation(hl),
                  FadeIn(self.xnum), FadeIn(self.ynum), run_time=self.T(2.5))
        self.say("across 3, up 4. that is all the arrow is.", 3)
        self.pad_to(END_POINT)

    # ==================================================================
    # cos θ and sin θ — already earned, last episode.
    # ==================================================================
    def stage_recall(self):
        card = VGroup(txt("from last time:", 22, GREY, bold=False, w=3.0),
                      txt(f"cos θ = {CS}      sin θ = {SS}", 26, SKY, w=4.3)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, 0.30, 0]))
        self.play(FadeIn(card, shift=0.10 * UP), run_time=self.T(2.5))
        self.say("across is cos, up is sin. you already know these.", 3)

        fill = {i: CS for i in S_COS}
        fill.update({i: SS for i in S_SIN})
        nxt = self.make_eq(active=S_COS + S_SIN, also=fill)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(card, shift=0.6 * UP),
                  run_time=self.T(3))
        self.say("four slots filled, for free.", 2.5)
        self.pad_to(END_RECALL)

    # ==================================================================
    # The point itself is the only thing left to measure.
    # ==================================================================
    def stage_drag(self):
        self.play(self.zoom.animate.set_value(0.96), run_time=self.T(1.5))
        self.drag_into(self.xnum.get_center(), S_X, XS, 22, fly=2.5, settle=1.5)
        self.drag_into(self.ynum.get_center(), S_Y, YS, 22, fly=2.5, settle=1.5)
        self.say("the equation is full. read it out.", 2.5)
        self.pad_to(END_DRAG)

    # ==================================================================
    # 2.4 − 2.4 = 0, and 1.8 + 3.2 = 5. Dead straight up.
    # ==================================================================
    def stage_turn(self):
        self.play(self.zoom.animate.set_value(0.93), run_time=self.T(1.5))
        self.show_wrk(f"{dec(P_XC)} {MINUS} {dec(P_YS)}", 2.5, GOLD)
        self.say("the same number, twice. it cancels.", 2.5, GOLD)
        self.ans = txt(f"new x = {NXS}", 30, GOLD, w=3.4)
        self.ans.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.ans, scale=1.12), run_time=self.T(2),
                  rate_func=rush_from)
        self.say("THAT is what the minus is for.", 2.5)

        self.show_wrk(f"{dec(P_XS)} + {dec(P_YC)}", 2.5, GREEN)
        self.play(Transform(self.ans,
                            txt(f"new x = {NXS}     new y = {NYS}", 29, GREEN,
                                w=4.4).move_to(np.array([0, ANS_Y, 0]))),
                  run_time=self.T(2.5))

        # and the arrow actually goes there
        newray = arrow(self.Q(0, 0), self.Q(NX, NY), GREEN, 4.2)
        ghost = dashed(self.Q(X, Y), self.Q(NX, NY), GREY, 2.0, 9)
        self.pic.add(newray, ghost)
        self.say("across 0, up 5. dead straight up.", 2.5, GREEN)
        self.play(ShowCreation(ghost), run_time=self.T(1.5))
        self.play(Transform(self.ray, newray), run_time=self.T(3),
                  rate_func=smooth)
        hit = Dot(self.Q(NX, NY), radius=0.11, fill_color=GREEN)
        self.pic.add(hit)
        self.play(FadeIn(hit, scale=2.0), run_time=self.T(1.5))
        self.say("5 long before. 5 long after. turning never stretches.", 4)
        self.pad_to(END_TURN)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.ans, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        self.wrk = None
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
