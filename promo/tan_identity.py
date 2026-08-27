"""
tan_identity — tan θ = sin θ / cos θ. 40.0s.

    BPM=150 manimgl tan_identity.py TanIdentity -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — same shell as soh_cah_toa.py, same
3-4-5 triangle. The equation is the spine, pinned at the TOP for the whole
video.

        tan θ = sin θ / cos θ

TAN ISN'T A FOURTH THING. sin and cos are already both ratios of the same
triangle. Divide one by the other and the hypotenuse cancels out — what's
left is exactly tan.

        sin θ = 3/5     cos θ = 4/5
        sin θ / cos θ = (3/5) / (4/5) = 3/4 = tan θ

VERIFIED AT IMPORT
    sin θ / cos θ == tan θ exactly (Fraction)   no rounding, no coincidence

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
OPP, ADJ, HYP = 3, 4, 5
assert OPP * OPP + ADJ * ADJ == HYP * HYP

SIN_TH, COS_TH, TAN_TH = Fraction(OPP, HYP), Fraction(ADJ, HYP), Fraction(OPP, ADJ)
assert SIN_TH / COS_TH == TAN_TH


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


class TanIdentity(Scene):
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
        self.stage_divide()
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

    def set_work(self, s, color, beats=2.5, size=22):
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
        big = txt("tan θ = sin θ / cos θ", 28, GOLD, w=4.5)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("tan isn't a fourth thing", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("it's the other two, divided.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("tan θ = sin θ / cos θ", 26, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_triangle(self):
        U = 0.48
        O = np.array([-1.35, -1.75, 0])

        def Q(x, y):
            return O + np.array([float(x) * U, float(y) * U, 0])

        A, B, C = Q(0, 0), Q(ADJ, 0), Q(ADJ, OPP)
        grid = VGroup()
        for k in range(0, ADJ + 2):
            grid.add(seg(Q(k, 0), Q(k, OPP + 1.4), FAINT, 1.4, 0.55))
        for k in range(0, OPP + 2):
            grid.add(seg(Q(0, k), Q(ADJ + 1.4, k), FAINT, 1.4, 0.55))
        edges = VGroup(seg(A, B, WHITE_, 3.2), seg(B, C, WHITE_, 3.2),
                       seg(C, A, GOLD, 3.2))
        rt = Square(side_length=0.14, stroke_color=WHITE_, stroke_width=2.0,
                   fill_opacity=0).move_to(B + np.array([-0.10, 0.10, 0]))
        thl = txt("θ", 22, GOLD, w=0.4).move_to(A + np.array([0.32, 0.20, 0]))
        oppl = txt(str(OPP), 20, WHITE_, w=0.5).move_to(
            (B + C) / 2 + np.array([0.26, 0, 0]))
        adjl = txt(str(ADJ), 20, WHITE_, w=0.5).move_to(
            (A + B) / 2 + np.array([0, -0.28, 0]))
        hypl = txt(str(HYP), 20, ROSE, w=0.5).move_to(
            (A + C) / 2 + np.array([-0.30, 0.18, 0]))
        self.pic = VGroup(grid, edges, rt, thl, oppl, adjl, hypl)

        self.play(FadeIn(grid), run_time=self.T(1))
        self.play(*[ShowCreation(e) for e in edges], run_time=self.T(2.5))
        self.play(FadeIn(rt), FadeIn(oppl), FadeIn(adjl), FadeIn(hypl),
                  run_time=self.T(1.5))
        self.play(FadeIn(thl), run_time=self.T(1))
        self.say("the same triangle. 3, 4, 5.", 2.5, GOLD)
        self.pad_to(END_TRI)

    # ==================================================================
    def stage_divide(self):
        self.say("sin θ over hypotenuse, cos θ over hypotenuse.", 3.5)
        self.set_work("sin θ = 3/5      cos θ = 4/5", GOLD, 2.5)
        self.say("divide one by the other.", 3)
        self.set_work("(3/5) / (4/5) = 3/4", SKY, 3)
        self.say("the hypotenuse cancels. it was never needed.", 3.5)
        self.set_work("3/4 = tan θ", GOLD, 3)
        self.say("opposite over adjacent — that IS tan θ.", 3.5, GOLD)
        self.pad_to(END_SWAP)

    # ==================================================================
    def stage_why(self):
        self.say("tan was never a separate ratio to memorise.", 2.5)
        self.set_work("tan θ = sin θ / cos θ, always", GOLD, 3)
        self.say('"rise over run" was hiding inside sin and cos the whole time.', 3.5)
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
