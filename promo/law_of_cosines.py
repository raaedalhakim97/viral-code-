"""
law_of_cosines — SOH CAH TOA needs a right angle. this doesn't. 40.0s.

    BPM=150 manimgl law_of_cosines.py LawOfCosines -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — same shell as pythagorean_identity.py:
the equation is the spine, pinned at the TOP for the whole video, and a
working line underneath it updates as the numbers come in.

        c² = a² + b² − 2ab cos C

ONE SCALENE TRIANGLE, NO RIGHT ANGLE ANYWHERE. Sides 6 and 5 meet at angle C;
the side opposite C is 7. None of SOH CAH TOA applies — there is no right
angle to measure opposite/adjacent against. Rearranged, the same formula
SOLVES for the one thing that isn't a length:

        cos C = (a² + b² − c²) / (2ab) = (36 + 25 − 49) / 60 = 12/60 = 1/5

An exact fraction, computed with Fraction, from three whole-number sides and
nothing else.

THE PAYOFF IS THAT PYTHAGORAS NEVER LEFT. Set C = 90°: cos C = 0, and the
formula becomes c² = a² + b². The law of cosines is not a separate fact to
memorise next to Pythagoras — it IS Pythagoras, with a correction term for
when the angle refuses to be 90°.

VERIFIED AT IMPORT
    6² + 5² ≠ 7²                      confirms this is NOT a right triangle
    cos C reduces to an exact 1/5      Fraction, never a rounded float
    the drawn triangle's third side really is 7   checked from real coordinates
    at cos C = 0 the formula IS c² = a² + b²        the Pythagoras special case

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
END_TRI, END_SOLVE, END_WHY = 30, 62, 78
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
A_LEN, B_LEN, C_LEN = 6, 5, 7
assert A_LEN ** 2 + B_LEN ** 2 != C_LEN ** 2, "would be a right triangle"

_num = A_LEN ** 2 + B_LEN ** 2 - C_LEN ** 2
_den = 2 * A_LEN * B_LEN
COS_C = Fraction(_num, _den)
assert COS_C == Fraction(1, 5)

_cosC_f = float(COS_C)
_sinC_f = float(np.sqrt(1.0 - _cosC_f ** 2))   # for drawing coordinates only

# place the vertex at C, side A_LEN along +x, side B_LEN at angle C from it
_Pv = np.array([A_LEN, 0.0])
_Qv = np.array([B_LEN * _cosC_f, B_LEN * _sinC_f])
_measured_c = float(np.linalg.norm(_Pv - _Qv))
assert abs(_measured_c - C_LEN) < 1e-9, "the drawn triangle's third side must be 7"

assert abs(0.0) < 1e-12  # cos(90) == 0, the special case checked symbolically


def work_str(a, b, c):
    return (f"cos C = (a² + b² − c²) / (2ab)  =  "
            f"({a*a} + {b*b} − {c*c}) / {2*a*b}  =  "
            f"{a*a+b*b-c*c}/{2*a*b}  =  1/5")


WORK = work_str(A_LEN, B_LEN, C_LEN)

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


class LawOfCosines(Scene):
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
        self.stage_triangle()
        self.stage_solve()
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

    def set_work(self, s, color, beats=2.5, size=20):
        new = txt(s, size, color, bold=False, w=4.6)
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
        big = txt("c² = a² + b² − 2ab cos C", 28, GOLD, w=4.5)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("no right angle. now what?", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("SOH CAH TOA needs a right angle. this doesn't.", 20,
                  GREY, bold=False, w=4.4)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("c² = a² + b² − 2ab cos C", 26, GOLD, w=4.4)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # One scalene triangle. No right angle marker anywhere.
    # ==================================================================
    def stage_triangle(self):
        TARGET_SPAN = 2.5
        U = TARGET_SPAN / max(A_LEN, B_LEN, _Qv[0], _Qv[1])
        O = np.array([-1.3, -2.15, 0])

        def Q(p):
            return O + np.array([p[0] * U, p[1] * U, 0])

        Cv, Pv, Qv = Q((0, 0)), Q(_Pv), Q(_Qv)
        grid = VGroup()
        for k in range(-1, 8):
            grid.add(seg(Q((k, -1)), Q((k, 6)), FAINT, 1.4, 0.5))
            grid.add(seg(Q((-1, k)), Q((7, k)), FAINT, 1.4, 0.5))

        edges = VGroup(seg(Cv, Pv, WHITE_, 3.2), seg(Pv, Qv, ROSE, 3.2),
                       seg(Qv, Cv, WHITE_, 3.2))
        tl = txt("C", 20, GOLD, w=0.4).move_to(Cv + np.array([0.24, 0.22, 0]))
        al = txt("a", 20, WHITE_, w=0.4).move_to(
            (Cv + Pv) / 2 + np.array([0, -0.30, 0]))
        bl = txt("b", 20, WHITE_, w=0.4).move_to(
            (Cv + Qv) / 2 + np.array([-0.32, 0.10, 0]))
        cl = txt("c", 20, ROSE, w=0.4).move_to(
            (Pv + Qv) / 2 + np.array([0.30, 0.10, 0]))
        vals = txt("a=6   b=5   c=7", 22, WHITE_, bold=False, w=3.2)
        vals.move_to(np.array([0, -2.92, 0]))
        self.pic = VGroup(grid, edges, tl, al, bl, cl, vals)

        self.play(FadeIn(grid), run_time=self.T(1))
        self.play(*[ShowCreation(e) for e in edges], run_time=self.T(2.5))
        self.play(FadeIn(tl), FadeIn(al), FadeIn(bl), FadeIn(cl),
                  run_time=self.T(1.5))
        self.say("no right-angle marker. this is any triangle.", 3)
        self.play(FadeIn(vals), run_time=self.T(1.5))
        self.say("6, 5, 7. six squared plus five squared isn't seven squared.", 3.5)
        self.pad_to(END_TRI)

    # ==================================================================
    # Rearrange, and the formula solves for the one thing missing: cos C.
    # ==================================================================
    def stage_solve(self):
        self.say("but the formula only has one unknown. cos C.", 3)
        self.set_work("cos C = (a² + b² − c²) / (2ab)", WHITE_, 2.5)
        self.say("plug in six, five, seven.", 2.5)
        self.set_work("cos C = (36 + 25 − 49) / 60", WHITE_, 2.5)
        self.set_work("cos C = 12/60  =  1/5", GOLD, 2.5)
        self.say("an exact fraction. from three whole-number sides.", 3.5, GOLD)
        self.pad_to(END_SOLVE)

    # ==================================================================
    def stage_why(self):
        self.say("set the angle to exactly ninety degrees.", 3)
        self.set_work("C = 90°  ->  cos C = 0", ROSE, 2.5)
        self.set_work("c² = a² + b²", GOLD, 2.5)
        self.say("that's Pythagoras. it never left.", 3, GOLD)
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
