"""
law_of_sines — every side, divided by the sine of its own angle. 40.0s.

    BPM=150 manimgl law_of_sines.py LawOfSines -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — same shell as soh_cah_toa.py, same
30-60-90 triangle as triangle_30_60_90.py two episodes ago. The equation
is the spine, pinned at the TOP for the whole video.

        a/sin A = b/sin B = c/sin C

THREE DIFFERENT SIDES, THREE DIFFERENT ANGLES, ONE NUMBER. Divide any side
of a triangle by the sine of the angle across from it. Do it for all three
sides. Every triangle gives the same answer, all three times — on the
familiar 1 : √3 : 2 triangle, that number is exactly 2:

        a/sin A = 1/sin 30° = 2
        b/sin B = 2/sin 90° = 2
        c/sin C = √3/sin 60° = 2

VERIFIED AT IMPORT
    a/sinA == b/sinB == c/sinC == 2.0, all to 1e-9

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
import math

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_TRI, END_SWAP, END_WHY = 26, 62, 78
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
SIDE_A, ANG_A = 1.0, 30.0
SIDE_B, ANG_B = 2.0, 90.0
SIDE_C, ANG_C = math.sqrt(3.0), 60.0
assert abs(SIDE_A ** 2 + SIDE_C ** 2 - SIDE_B ** 2) < 1e-9

RA = SIDE_A / math.sin(math.radians(ANG_A))
RB = SIDE_B / math.sin(math.radians(ANG_B))
RC = SIDE_C / math.sin(math.radians(ANG_C))
assert abs(RA - 2.0) < 1e-9
assert abs(RB - 2.0) < 1e-9
assert abs(RC - 2.0) < 1e-9


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


class LawOfSines(Scene):
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
        self.stage_ratios()
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

    def set_work(self, s, color, beats=2.5, size=21):
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
        big = txt("a/sinA = b/sinB = c/sinC", 22, GOLD, w=4.6)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("the same triangle, again", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("three sides. one hidden number.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("a/sinA = b/sinB = c/sinC", 22, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_triangle(self):
        SHORT, LONG, HYP = SIDE_A, SIDE_C, SIDE_B
        TARGET_SPAN = 2.5
        U = TARGET_SPAN / max(SHORT, LONG)
        O = np.array([-1.35, -1.75, 0])

        def Q(x, y):
            return O + np.array([float(x) * U, float(y) * U, 0])

        A, Bv, C = Q(0, 0), Q(LONG, 0), Q(LONG, SHORT)
        grid = VGroup()
        for k in np.arange(0, LONG + 1.4, 0.5):
            grid.add(seg(Q(k, 0), Q(k, SHORT + 1.0), FAINT, 1.2, 0.5))
        for k in np.arange(0, SHORT + 1.4, 0.5):
            grid.add(seg(Q(0, k), Q(LONG + 1.0, k), FAINT, 1.2, 0.5))
        edges = VGroup(seg(A, Bv, WHITE_, 3.2), seg(Bv, C, WHITE_, 3.2),
                       seg(C, A, GOLD, 3.2))
        rt = Square(side_length=0.14, stroke_color=WHITE_, stroke_width=2.0,
                   fill_opacity=0).move_to(Bv + np.array([-0.10, 0.10, 0]))
        al = txt("A: 30°", 17, GOLD, w=1.1).move_to(A + np.array([0.55, 0.20, 0]))
        cl = txt("C: 60°", 17, SKY, w=1.1).move_to(C + np.array([-0.40, -0.34, 0]))
        al_side = txt("a=1", 18, ROSE, w=0.7).move_to(
            (Bv + C) / 2 + np.array([0.30, 0, 0]))
        cl_side = txt("c=√3", 18, ROSE, w=0.9).move_to(
            (A + Bv) / 2 + np.array([0, -0.28, 0]))
        bl_side = txt("b=2", 18, ROSE, w=0.7).move_to(
            (A + C) / 2 + np.array([-0.34, 0.20, 0]))
        self.pic = VGroup(grid, edges, rt, al, cl, al_side, cl_side, bl_side)

        self.play(FadeIn(grid), run_time=self.T(1))
        self.play(*[ShowCreation(e) for e in edges], run_time=self.T(2.5))
        self.play(FadeIn(rt), FadeIn(al_side), FadeIn(cl_side), FadeIn(bl_side),
                  run_time=self.T(1.5))
        self.play(FadeIn(al), FadeIn(cl), run_time=self.T(1))
        self.say("the same 1 : √3 : 2 triangle from before.", 2.5, GOLD)
        self.pad_to(END_TRI)

    # ==================================================================
    def stage_ratios(self):
        self.say("side a, divided by sin of its own angle A.", 3, GOLD)
        self.set_work("a/sinA = 1/sin30° = 2", GOLD, 3)
        self.say("now the right angle's side, b.", 2.5, SKY)
        self.set_work("b/sinB = 2/sin90° = 2", SKY, 3)
        self.say("and the third side, c.", 2, ROSE)
        self.set_work("c/sinC = √3/sin60° = 2", ROSE, 3)
        self.say("three different sides. the exact same number.", 3.5)
        self.pad_to(END_SWAP)

    # ==================================================================
    def stage_why(self):
        self.say("this isn't special to this triangle. it's every triangle.", 3.5)
        self.set_work("a/sinA is the SAME constant for any triangle, always", GOLD, 3.5)
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
