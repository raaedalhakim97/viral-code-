"""
soh_cah_toa — SOH CAH TOA is three divisions, not a spell. 40.0s.

    BPM=150 manimgl soh_cah_toa.py SohCahToa -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — same shell as angle_to_place.py: the
equation is the spine, it sits at the TOP for the whole video so every number
is legible the instant it lands, and every value is dragged into its slot off
the triangle rather than typed on top of it.

        sin θ = opp / hyp
        cos θ = adj / hyp
        tan θ = opp / adj

ONE TRIANGLE, THREE RATIOS. A 3-4-5 right triangle — the smallest whole-number
right triangle there is — with θ at the vertex where the legs of length 4 and
5 meet the hypotenuse. Its sides are counted straight off a grid, exactly like
angle_to_place counted a point straight off a circle:

    opposite = 3     adjacent = 4     hypotenuse = 5

THREE DRAGS FILL SIX SLOTS. "3" fills sin's numerator AND tan's numerator at
once. "5" fills sin's AND cos's denominator at once. "4" fills cos's AND tan's
remaining slot. Every one of the three "scary" ratios is full before the video
is half over, and every fraction it produces is exact:

    sin θ = 3/5 = 0.6      cos θ = 4/5 = 0.8      tan θ = 3/4 = 0.75

WHY THIS TRIANGLE, AGAIN. 3-4-5 is the same triangle angle_to_place measured on
the unit circle (cos = 0.8, sin = 0.6) — same numbers, different lens: there it
was a point on a circle, here it is a ratio of sides. That is not a coincidence
worth hiding; SOH CAH TOA and the circle definition are the same fact.

VERIFIED AT IMPORT
    3*3 + 4*4 == 5*5                     it really is a right triangle
    the three ratios are exact fractions  reduces to 0.6, 0.8, 0.75, no rounding
    tan == sin / cos                     the three are not independent facts

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
END_TRI, END_FILL, END_WHY = 34, 70, 77
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
EQ_Y   = 2.62           # three rows, pinned at the top for the whole video
NOTE_Y = -3.30
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
OPP, ADJ, HYP = 3, 4, 5
assert OPP * OPP + ADJ * ADJ == HYP * HYP, "not a right triangle"

SIN = Fraction(OPP, HYP)
COS = Fraction(ADJ, HYP)
TAN = Fraction(OPP, ADJ)
assert (float(SIN), float(COS), float(TAN)) == (0.6, 0.8, 0.75)
assert TAN == SIN / COS, "the three ratios are not independent facts"

OS_, AS_, HS_ = str(OPP), str(ADJ), str(HYP)
SIN_S, COS_S, TAN_S = "0.6", "0.8", "0.75"

_th = float(np.arctan2(OPP, ADJ))
assert abs(np.tan(_th) - float(TAN)) < 1e-12
assert 25 < np.degrees(_th) < 65

# the spine: three rows of five pieces — flat slots 0..14
ROWS = [["sin θ", "=", "opp", "/", "hyp"],
        ["cos θ", "=", "adj", "/", "hyp"],
        ["tan θ", "=", "opp", "/", "adj"]]
FLAT = [p for row in ROWS for p in row]
S_SIN_O, S_SIN_H = 2, 4
S_COS_A, S_COS_H = 7, 9
S_TAN_O, S_TAN_A = 12, 14
SLOTS = (S_SIN_O, S_SIN_H, S_COS_A, S_COS_H, S_TAN_O, S_TAN_A)


def rc(slot):
    return divmod(slot, 5)


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


def dashed(a, b, color=GOLD, wid=2.4, n=10):
    g = VGroup()
    a, b = np.asarray(a, float), np.asarray(b, float)
    for i in range(n):
        t0, t1 = i / n, (i + 0.55) / n
        g.add(seg(a + (b - a) * t0, a + (b - a) * t1, color, wid, 0.9))
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


class SohCahToa(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.filled = {}
        self.collapsed = set()

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_triangle()
        self.stage_fill()
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

    # ---------------------------------------------------- the equation
    def make_eq(self, active=None, also=None):
        fill = dict(self.filled)
        if also:
            fill.update(also)
        rows = VGroup()
        for r, row in enumerate(ROWS):
            g = VGroup()
            if r in self.collapsed:
                dec = (SIN_S, COS_S, TAN_S)[r]
                g.add(txt(row[0], 27, GOLD, w=1.5))
                g.add(txt("=", 27, WHITE_, w=0.4))
                g.add(txt(dec, 27, GOLD, w=1.3))
            else:
                for c, base in enumerate(row):
                    i = r * 5 + c
                    s = fill.get(i, base)
                    if i == active:
                        col, sz = GOLD, 31
                    elif i in fill:
                        col, sz = GOLD, 27
                    elif i in SLOTS:
                        col, sz = DIM, 27
                    else:
                        col, sz = WHITE_, 27
                    g.add(txt(s, sz, col, w=1.4))
            g.arrange(RIGHT, buff=0.12)
            rows.add(g)
        rows.arrange(DOWN, buff=0.20)
        for r in (1, 2):
            rows[r].shift(RIGHT * (rows[0][1].get_center()[0]
                                   - rows[r][1].get_center()[0]))
        if rows.get_width() > 4.6:
            rows.set_width(4.6)
        return rows.move_to(np.array([0, EQ_Y, 0]))

    def drag_into(self, source_point, slot, value, also=None, fly=2.5, settle=1.5):
        fill = {slot: value}
        if also:
            fill.update(also)
        nxt = self.make_eq(active=slot, also=fill)
        r, c = rc(slot)
        target = nxt[r][c]
        flier = txt(value, 26, GOLD, w=1.6).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(flier), run_time=self.T(settle))

    def collapse(self, row, beats=2.5):
        self.collapsed.add(row)
        self.play(Transform(self.eq, self.make_eq()), run_time=self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("SOH", 44, GOLD, w=4.0),
                     txt("CAH", 44, SKY, w=4.0),
                     txt("TOA", 44, ROSE, w=4.0)) \
            .arrange(RIGHT, buff=0.35).move_to(np.array([0, 1.15, 0]))
        q = txt("what does it actually mean?", 28, WHITE_, w=4.6)
        q.move_to(np.array([0, -0.05, 0]))
        sub = txt("three ratios. one triangle.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.85, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(big), FadeOut(q), FadeOut(sub),
                  FadeIn(self.eq), FadeIn(self.title), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    # One right triangle. Count the sides straight off the grid.
    # ==================================================================
    def stage_triangle(self):
        self.U = 0.58
        self.O = np.array([-1.05, -1.55, 0])

        def Q(x, y):
            return self.O + np.array([float(x) * self.U, float(y) * self.U, 0])

        self.Q = Q
        grid = VGroup()
        for k in range(0, 6):
            grid.add(seg(Q(k, 0), Q(k, 4.4), FAINT, 1.6, 0.6))
        for k in range(0, 5):
            grid.add(seg(Q(0, k), Q(5.2, k), FAINT, 1.6, 0.6))
        self.pic = VGroup(grid)
        self.play(FadeIn(grid), run_time=self.T(1.5))

        A, B, C = Q(0, 0), Q(4, 0), Q(4, 3)
        tri = VGroup(seg(A, B, WHITE_, 3.4), seg(B, C, WHITE_, 3.4),
                     seg(C, A, GOLD, 3.4))
        self.pic.add(tri)
        self.play(*[ShowCreation(s) for s in tri], run_time=self.T(3))
        self.say("one right triangle. that's the whole set-up.", 3)

        tl = txt("θ", 24, GOLD, w=0.4).move_to(A + np.array([0.32, 0.20, 0]))
        rt = Square(side_length=0.16, stroke_color=WHITE_, stroke_width=2.2,
                   fill_opacity=0).move_to(B + np.array([-0.12, 0.12, 0]))
        self.pic.add(tl, rt)
        self.play(FadeIn(tl), ShowCreation(rt), run_time=self.T(1.5))
        self.say("θ sits here. the square marks the right angle.", 2.5)

        oppl = txt(OS_, 22, GOLD, w=0.5).move_to(
            (B + C) / 2 + np.array([0.28, 0, 0]))
        adjl = txt(AS_, 22, SKY, w=0.5).move_to(
            (A + B) / 2 + np.array([0, -0.30, 0]))
        hypl = txt(HS_, 22, ROSE, w=0.5).move_to(
            (A + C) / 2 + np.array([-0.30, 0.18, 0]))
        self.opp_pt, self.adj_pt, self.hyp_pt = oppl, adjl, hypl
        self.pic.add(oppl, adjl, hypl)
        self.play(FadeIn(oppl, scale=1.4), run_time=self.T(1.25))
        self.say("opposite θ: 3.", 2, GOLD)
        self.play(FadeIn(adjl, scale=1.4), run_time=self.T(1.25))
        self.say("next to θ: 4.", 2, SKY)
        self.play(FadeIn(hypl, scale=1.4), run_time=self.T(1.25))
        self.say("across from the right angle: 5.", 2.25, ROSE)

        self.chk = txt("3² + 4² = 5²   (9 + 16 = 25)", 19, GREY, bold=False, w=3.6)
        self.chk.move_to(np.array([0, -2.55, 0]))
        self.pic.add(self.chk)
        self.play(FadeIn(self.chk), run_time=self.T(1.5))
        self.say("check: nine plus sixteen is twenty-five.", 2.5)
        self.pad_to(END_TRI)

    # ==================================================================
    # Three drags fill six slots. Three collapses turn them into numbers.
    # ==================================================================
    def stage_fill(self):
        self.say("watch these numbers fill in three ratios at once.", 3)
        self.drag_into(self.opp_pt.get_center(), S_SIN_O, OS_,
                       also={S_TAN_O: OS_})
        self.drag_into(self.hyp_pt.get_center(), S_SIN_H, HS_,
                       also={S_COS_H: HS_})
        self.say("sin θ is filled. three divided by five.", 2.5)
        self.collapse(0)
        self.say("sin θ = 0.6.", 2, GOLD)

        self.drag_into(self.adj_pt.get_center(), S_COS_A, AS_,
                       also={S_TAN_A: AS_})
        self.say("cos θ was already half full.", 2.25)
        self.collapse(1)
        self.say("cos θ = 0.8.", 2, GOLD)

        self.say("tan θ never needed a new number.", 2.5)
        self.collapse(2)
        self.say("tan θ = 0.75.", 2, GOLD)
        self.pad_to(END_FILL)

    # ==================================================================
    def stage_why(self):
        self.say("SOH CAH TOA isn't a spell to memorise.", 3)
        self.say("it's three divisions, done on one triangle.", 3.5)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
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
