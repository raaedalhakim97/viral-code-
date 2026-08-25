"""
route_consolidation — the law of cosines skips the warehouse. 60.0s.

    BPM=150 manimgl route_consolidation.py RouteConsolidation -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE 5 OF "WHERE MATH ACTUALLY GETS USED". Same shell: the number is
the spine, pinned at the TOP for the whole video. Callback: this is the
same formula proved on video from `law_of_cosines.py` — here it's the
actual tool logistics companies run to consolidate two stops into one leg.

A hub H has two stops: A is 8 km out, B is 5 km out, and the angle between
those two routes (measured at the hub) is 60°. Instead of driving back to
the hub between them, go straight from A to B:

    d² = a² + b² − 2ab cos C = 8² + 5² − 2·8·5·cos 60° = 89 − 40 = 49
    d = 7 km

Via the hub: 8 + 5 = 13 km. Direct: 7 km. A 46% shorter route, and the
integers are not a coincidence — 8, 5, 60°, 7 is a whole-number solution
to the law of cosines, chosen so this stays exact.

VERIFIED AT IMPORT
    d² == 49 exactly (as a Fraction, cos 60° = 1/2)
    d == 7 exactly           saved == 6 km == 46.2% of the via-hub trip
"""
import os
import math
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 12
END_A, END_B = 44, 96
END_WHY, END_TAKE, END_SHARE = 117, 132, 138

SERIES = "WHERE MATH ACTUALLY GETS USED"

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
EQ_Y   = 3.08
WORK_Y = 2.30
NOTE_Y = -3.30
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
HA, HB, ANG = 8, 5, 60
COSC = Fraction(1, 2)
assert abs(math.cos(math.radians(ANG)) - float(COSC)) < 1e-9

D2 = Fraction(HA * HA + HB * HB) - 2 * HA * HB * COSC
assert D2 == 49
D = 7
assert D * D == D2

VIA_HUB = HA + HB
SAVED = VIA_HUB - D
assert VIA_HUB == 13 and SAVED == 6
PCT = Fraction(SAVED, VIA_HUB)
assert abs(float(PCT) - 0.46153846153846156) < 1e-9


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


class RouteConsolidation(Scene):
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
        self.stage_hub()
        self.stage_direct()
        self.stage_why()
        self.takeaway("This is why we learned the law of cosines.",
                      "Logistics companies run on it, daily.")
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
        big = txt("d² = a² + b² − 2ab cos C", 22, GOLD, w=4.6)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("two delivery stops, one warehouse", 24, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("skip the hub. save the trip.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("d² = a² + b² − 2ab cos C", 22, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_hub(self):
        H = np.array([0.0, 0.35, 0])
        angA = math.radians(200)
        angB = math.radians(200 - ANG)
        U = 0.145
        A_pt = H + np.array([math.cos(angA), math.sin(angA), 0]) * HA * U
        B_pt = H + np.array([math.cos(angB), math.sin(angB), 0]) * HB * U

        self.H, self.A_pt, self.B_pt = H, A_pt, B_pt
        hub_dot = Dot(H, radius=0.12, fill_color=WHITE_)
        leg_a = seg(H, A_pt, SKY, 3.6)
        leg_b = seg(H, B_pt, ROSE, 3.6)
        a_dot = Dot(A_pt, radius=0.11, fill_color=SKY)
        b_dot = Dot(B_pt, radius=0.11, fill_color=ROSE)
        hub_lbl = txt("hub", 18, WHITE_, w=0.9).move_to(H + UP * 0.36)
        a_lbl = txt("A: 8 km", 18, SKY, w=1.1).move_to(
            A_pt + (A_pt - H) / np.linalg.norm(A_pt - H) * 0.35)
        b_lbl = txt("B: 5 km", 18, ROSE, w=1.1).move_to(
            B_pt + (B_pt - H) / np.linalg.norm(B_pt - H) * 0.35)

        self.pic = VGroup(leg_a, leg_b, hub_dot, a_dot, b_dot, hub_lbl, a_lbl, b_lbl)
        self.play(FadeIn(hub_dot), FadeIn(hub_lbl), run_time=self.T(1))
        self.play(ShowCreation(leg_a), FadeIn(a_dot), FadeIn(a_lbl), run_time=self.T(2))
        self.play(ShowCreation(leg_b), FadeIn(b_dot), FadeIn(b_lbl), run_time=self.T(2))
        self.say("hub to A: 8 km. hub to B: 5 km. angle: 60°.", 4.5)
        self.set_work("via hub: 8 + 5 = 13 km", WHITE_, 2.5)
        self.say("out and back through the warehouse every time.", 3.5)
        self.pad_to(END_A)

    def stage_direct(self):
        direct = seg(self.A_pt, self.B_pt, GOLD, 4.2)
        self.say("skip the hub. drive A straight to B.", 4)
        self.play(ShowCreation(direct), run_time=self.T(2.5))
        self.set_work("8² + 5² − 2·8·5·cos 60° = 49", GOLD, 3.5)
        self.say("cos 60° is exactly one half. the algebra is exact.", 4)
        self.set_work("d = √49 = 7 km", GOLD, 2.5)
        self.say("thirteen kilometers becomes seven.", 3.5)
        self.set_work("46% shorter, same two stops", GREEN, 3)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("8, 5, 60°, 7 — a whole-number solution, not luck.", 3.5)
        self.set_work("this is literally route optimization", GOLD, 3.5)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 27, WHITE_, w=4.5).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 25, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is where it's used", 25, GOLD, w=4.6)
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
