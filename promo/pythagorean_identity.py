"""
pythagorean_identity — sin²θ + cos²θ = 1 is just Pythagoras, divided. 40.0s.

    BPM=150 manimgl pythagorean_identity.py PythagoreanIdentity -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — same shell as soh_cah_toa.py: the
equation is the spine, it sits at the TOP for the whole video, and it never
moves once it lands, so every working line underneath it stays legible.

        sin² θ + cos² θ = 1

TWO TRIANGLES, NOT ONE. A single worked example can always be a coincidence,
so this proves it twice on triangles that share nothing but being right
triangles:

    3-4-5:    sin θ = 3/5,  cos θ = 4/5    ->  9/25  + 16/25  = 25/25  = 1
    5-12-13:  sin θ = 5/13, cos θ = 12/13  ->  25/169 + 144/169 = 169/169 = 1

Every fraction is exact — computed with Fraction, never a rounded float — so
"= 1" on screen means exactly one, not 0.999999.

WHY IT IS ALWAYS ONE. Divide the Pythagorean theorem itself, a² + b² = c², by
c² on both sides: (a/c)² + (b/c)² = 1. But a/c and b/c ARE sin θ and cos θ —
soh_cah_toa said so. The identity is not a new fact to memorise. It is
Pythagoras, wearing sin and cos as initials.

VERIFIED AT IMPORT
    3-4-5 and 5-12-13 are both genuine Pythagorean triples
    both triangles' sin² + cos² equal exactly Fraction(1, 1)
    the two triangles do not share a ratio                or the "different
                                                             triangle" claim is false

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
END_TRI_A, END_TRI_B, END_WHY = 38, 68, 80
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
EQ_Y   = 3.08
WORK_Y = 2.30
NOTE_Y = -3.30
LINE_Y = -2.05


# ------------------------------------------------------------------ numbers
def tri(opp, adj, hyp):
    assert opp * opp + adj * adj == hyp * hyp, (opp, adj, hyp)
    s, c = Fraction(opp, hyp), Fraction(adj, hyp)
    assert s * s + c * c == 1
    return opp, adj, hyp, s, c


A_OPP, A_ADJ, A_HYP, A_SIN, A_COS = tri(3, 4, 5)
B_OPP, B_ADJ, B_HYP, B_SIN, B_COS = tri(5, 12, 13)
assert (A_SIN, A_COS) != (B_SIN, B_COS), "the two triangles must not agree"


def work_str(s, c):
    s2, c2 = s * s, c * c
    total = s2 + c2
    assert total == 1
    return (f"({s.numerator}/{s.denominator})² + ({c.numerator}/{c.denominator})²"
            f"  =  {s2.numerator}/{s2.denominator} + {c2.numerator}/{c2.denominator}"
            f"  =  1")


WORK_A = work_str(A_SIN, A_COS)
WORK_B = work_str(B_SIN, B_COS)

_thA = float(np.arctan2(A_OPP, A_ADJ))
_thB = float(np.arctan2(B_OPP, B_ADJ))


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


class PythagoreanIdentity(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.work = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_triangle(A_OPP, A_ADJ, A_HYP, _thA, WORK_A, GOLD, first=True)
        self.stage_triangle(B_OPP, B_ADJ, B_HYP, _thB, WORK_B, SKY, first=False)
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

    def set_work(self, s, color, beats=2.5):
        new = txt(s, 21, color, bold=False, w=4.6)
        new.move_to(np.array([0, WORK_Y, 0]))
        if self.work is None:
            self.work = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            old, self.work = self.work, new
            self.play(FadeOut(old), FadeIn(new), run_time=self.T(beats))
            self.work = new

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("sin² θ + cos² θ = 1", 34, GOLD, w=4.4)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("the identity that looks scary", 26, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("it's one triangle, squared twice.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("sin² θ + cos² θ = 1", 32, GOLD, w=4.2)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_triangle(self, opp, adj, hyp, th, work, col, first):
        end = END_TRI_A if first else END_TRI_B
        if hasattr(self, "pic"):
            self.play(FadeOut(self.pic), run_time=self.T(1.5))
        # A constant on-screen span regardless of the triangle's real side
        # lengths — 5-12-13 at the same scale as 3-4-5 would run clean off
        # the right edge of a 9:16 frame.
        TARGET_SPAN = 2.5
        U = TARGET_SPAN / max(opp, adj)
        O = np.array([-adj * U / 2 - 0.35, -2.05, 0])

        def Q(x, y):
            return O + np.array([float(x) * U, float(y) * U, 0])

        grid = VGroup()
        for k in range(0, int(adj) + 2):
            grid.add(seg(Q(k, 0), Q(k, opp + 1.4), FAINT, 1.4, 0.55))
        for k in range(0, int(opp) + 2):
            grid.add(seg(Q(0, k), Q(adj + 1.4, k), FAINT, 1.4, 0.55))

        Av, Bv, Cv = Q(0, 0), Q(adj, 0), Q(adj, opp)
        edges = VGroup(seg(Av, Bv, WHITE_, 3.2), seg(Bv, Cv, WHITE_, 3.2),
                       seg(Cv, Av, col, 3.2))
        tl = txt("θ", 20, col, w=0.4).move_to(Av + np.array([0.28, 0.18, 0]))
        rt = Square(side_length=0.14, stroke_color=WHITE_, stroke_width=2.0,
                   fill_opacity=0).move_to(Bv + np.array([-0.10, 0.10, 0]))
        oppl = txt(str(opp), 20, col, w=0.5).move_to(
            (Bv + Cv) / 2 + np.array([0.26, 0, 0]))
        adjl = txt(str(adj), 20, col, w=0.5).move_to(
            (Av + Bv) / 2 + np.array([0, -0.28, 0]))
        hypl = txt(str(hyp), 20, ROSE, w=0.5).move_to(
            (Av + Cv) / 2 + np.array([-0.30, 0.16, 0]))
        self.pic = VGroup(grid, edges, tl, rt, oppl, adjl, hypl)
        self.play(FadeIn(grid), run_time=self.T(1))
        self.play(*[ShowCreation(e) for e in edges], run_time=self.T(2))
        self.play(FadeIn(tl), ShowCreation(rt), FadeIn(oppl), FadeIn(adjl),
                  FadeIn(hypl), run_time=self.T(2))

        if first:
            self.say(f"triangle one: {opp}, {adj}, {hyp}.", 2.5)
            self.set_work(f"sin θ = {opp}/{hyp}     cos θ = {adj}/{hyp}", WHITE_, 2.5)
        else:
            self.say(f"a totally different triangle: {opp}, {adj}, {hyp}.", 3)
            self.set_work(f"sin θ = {opp}/{hyp}     cos θ = {adj}/{hyp}", WHITE_, 2.5)
        self.say("square each one. add them.", 2.5)
        self.set_work(work, col, 3)
        self.say("exactly one. not almost.", 2.5, GOLD)
        self.pad_to(end)

    # ==================================================================
    def stage_why(self):
        self.say("that is not a coincidence.", 2.5)
        gen = txt("a² + b² = c²     ÷ c²     (a/c)² + (b/c)² = 1", 19,
                  WHITE_, bold=False, w=4.5)
        gen.move_to(np.array([0, WORK_Y, 0]))
        self.play(FadeOut(self.work), FadeIn(gen), run_time=self.T(2.5))
        self.work = gen
        self.say("a/c and b/c are just cos θ and sin θ.", 3)
        self.say("this identity IS Pythagoras. divided.", 3.5, GOLD)
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
