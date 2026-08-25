"""
crane_rigging — sin θ is the sideways force that tips a crane. 60.0s.

    BPM=150 manimgl crane_rigging.py CraneRigging -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE 2 OF "WHERE MATH ACTUALLY GETS USED". Same shell: the number is
the spine, pinned at the TOP for the whole video.

A crane's lifting cable has tension T. If the cable leans θ from true
vertical, that tension splits into two components: T cos θ holds the load
up, and T sin θ pulls the load — and the crane — SIDEWAYS. Riggers must
calculate this before every lift, because sideways force is what tips an
unanchored crane or swings an uncontrolled load into something expensive.

    straight up,  θ =  0°:  sideways = T sin  0° = 0        ->    0 kg
    leaning,      θ = 30°:  sideways = T sin 30° = 0.5T     ->  500 kg

sin 30° is exactly one half. On a 1,000 kg lift, a 30° lean means 500 kg of
pure sideways pull on the rigging — half the entire load, doing nothing to
hold it up.

VERIFIED AT IMPORT
    sin 30 deg == 0.5 to 1e-9         sin  0 deg == 0.0 to 1e-9
    sideways force at 30deg == 500    exactly half the 1000kg load

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
SIN0 = math.sin(math.radians(0))
SIN30 = math.sin(math.radians(30))
assert abs(SIN0 - 0.0) < 1e-9
assert abs(SIN30 - 0.5) < 1e-9

LOAD_KG = 1000
SIDE_0 = LOAD_KG * SIN0
SIDE_30 = LOAD_KG * SIN30
assert abs(SIDE_0 - 0) < 1e-6
assert abs(SIDE_30 - 500) < 1e-6


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


def crane_diagram(lean_deg, theta_label, side_label):
    anchor = np.array([-1.0, 1.55, 0])
    vert = seg(anchor, anchor + DOWN * 2.75, GREY, 1.6, 0.55)

    tl = math.radians(lean_deg)
    cable_dir = np.array([math.sin(tl), -math.cos(tl), 0])
    hook = anchor + cable_dir * 2.6
    cable = seg(anchor, hook, WHITE_, 4.2)

    load = Square(side_length=0.42, stroke_color=ROSE, stroke_width=3.0,
                  fill_color=ROSE, fill_opacity=0.35).move_to(hook + DOWN * 0.32)

    grp = VGroup(vert, cable, load)
    if lean_deg > 0.5:
        side_arrow = seg(hook, hook + RIGHT * 1.0, GOLD, 3.2)
        grp.add(side_arrow)
        sl = txt(side_label, 18, GOLD, w=1.4)
        sl.move_to(hook + RIGHT * 1.35 + DOWN * 0.05)
        grp.add(sl)

    tlbl = txt(theta_label, 20, SKY, w=1.2)
    tlbl.move_to(anchor + DOWN * 0.55 + RIGHT * (0.35 if lean_deg > 0.5 else 0.35))
    grp.add(tlbl)
    return grp


class CraneRigging(Scene):
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
        self.stage_vertical()
        self.stage_lean()
        self.stage_why()
        self.takeaway("This is why we learned sin θ.",
                      "Riggers calculate it before every lift.")
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
        big = txt("sideways = T sin θ", 28, GOLD, w=4.6)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("a 1,000 kg crane lift", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("one angle decides if it tips.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("sideways = T sin θ", 26, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_vertical(self):
        self.pic = crane_diagram(0, "θ=0°", "")
        self.play(FadeIn(self.pic), run_time=self.T(2.5))
        self.say("cable straight up. no lean at all.", 3.5)
        self.set_work("sin 0° = 0", SKY, 2.5)
        self.say("every kilogram of tension holds the load up.", 3.5)
        self.set_work("sideways force = 0 kg", SKY, 2.5)
        self.say("nothing pulling the crane off balance.", 3)
        self.pad_to(END_A)

    def stage_lean(self):
        new_pic = crane_diagram(30, "θ=30°", "500 kg")
        self.say("now the cable leans 30° off vertical.", 4)
        self.play(FadeOut(self.pic), FadeIn(new_pic), run_time=self.T(2.5))
        self.pic = new_pic
        self.set_work("sin 30° = 0.5", GOLD, 2.5)
        self.say("half the tension now pulls sideways.", 3.5)
        self.set_work("sideways force = 500 kg", GOLD, 3)
        self.say("half the load's weight, doing nothing to hold it up.", 4)
        self.set_work("that's what tips an unanchored crane", ROSE, 3.5)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("sin 30° is exactly one half.", 2.5)
        self.set_work("θ = 0 -> 30°  =  0 -> 500 kg sideways", GOLD, 3)
        self.say("riggers run this number before every single lift.", 3.5)
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
