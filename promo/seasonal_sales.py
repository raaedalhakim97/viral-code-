"""
seasonal_sales — a sine wave predicts a year of inventory. 60.0s.

    BPM=150 manimgl seasonal_sales.py SeasonalSales -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE 4 OF "WHERE MATH ACTUALLY GETS USED". Same shell: the number is
the spine, pinned at the TOP for the whole video.

Retail demand that repeats every year — swimwear, heaters, holiday decor —
is modeled the same way a sound wave is: a sine curve. A baseline plus an
amplitude, oscillating over 12 months:

    sales(t) = 1000 + 400 · sin(2πt / 12)

At the peak month (sin = 1): 1,400 units. At the trough month (sin = -1):
600 units. A retailer who orders the flat average every month either runs
out during the peak or pays to warehouse 400 extra units during the trough.
The sine model tells them exactly how much to shift, and when.

VERIFIED AT IMPORT
    sales at sin=1  == 1400 exactly     sales at sin=-1 == 600 exactly
    amplitude accounts for the entire swing between them
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
BASE = 1000
AMP = 400
PEAK = BASE + AMP * math.sin(math.radians(90))
TROUGH = BASE + AMP * math.sin(math.radians(270))
assert PEAK == 1400
assert TROUGH == 600
SWING = PEAK - TROUGH
assert SWING == 800


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


def wave_curve(O, xU, yU, color=WHITE_, wid=3.5):
    pts = []
    for m in np.linspace(0, 12, 120):
        y = BASE + AMP * math.sin(2 * math.pi * m / 12)
        pts.append(O + np.array([m * xU, (y - BASE) * yU, 0]))
    curve = VMobject(stroke_color=color, stroke_width=wid)
    curve.set_points_smoothly(pts)
    return curve


class SeasonalSales(Scene):
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
        self.stage_flat()
        self.stage_wave()
        self.stage_why()
        self.takeaway("This is why we learned sine waves.",
                      "Retailers forecast entire seasons with it.")
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
        big = txt("sales(t) = 1000 + 400 sin(t)", 24, GOLD, w=4.6)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("a swimwear shop's whole year", 27, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("one curve. every order decided.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("sales(t) = 1000 + 400 sin(t)", 22, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_flat(self):
        O = np.array([-1.7, -1.1, 0])
        xU, yU = 0.27, 0.0028
        axis = seg(O, O + RIGHT * (12 * xU + 0.3), GREY, 1.6, 0.6)
        flat = seg(O, O + RIGHT * (12 * xU), DIM, 3.0, 0.9)
        self.axis, self.flat = axis, flat
        self.O, self.xU, self.yU = O, xU, yU
        lbl = txt("1,000 flat every month?", 20, GREY, bold=False, w=3.2)
        lbl.move_to(O + RIGHT * (6 * xU) + UP * 0.5)
        self.flatlbl = lbl
        self.play(FadeIn(axis), FadeIn(flat), FadeIn(lbl), run_time=self.T(2.5))
        self.say("order the same amount every single month?", 3.5)
        self.set_work("baseline = 1,000 units", WHITE_, 2.5)
        self.say("but demand doesn't stay flat all year.", 3.5)
        self.pad_to(END_A)

    def stage_wave(self):
        curve = wave_curve(self.O, self.xU, self.yU, GOLD, 3.8)
        self.say("real demand swings — a sine wave, not a line.", 4)
        self.play(FadeOut(self.flat), FadeOut(self.flatlbl),
                  ShowCreation(curve), run_time=self.T(3))
        self.curve = curve

        peak_pt = self.O + np.array([3 * self.xU, (PEAK - BASE) * self.yU, 0])
        trough_pt = self.O + np.array([9 * self.xU, (TROUGH - BASE) * self.yU, 0])
        peak_dot = Dot(peak_pt, radius=0.11, fill_color=GREEN)
        trough_dot = Dot(trough_pt, radius=0.11, fill_color=ROSE)
        peak_lbl = txt("1,400", 18, GREEN, w=1.0).move_to(peak_pt + UP * 0.32)
        trough_lbl = txt("600", 18, ROSE, w=1.0).move_to(trough_pt + DOWN * 0.32)
        self.play(FadeIn(peak_dot), FadeIn(peak_lbl), run_time=self.T(1.5))
        self.set_work("peak month: 1,000 + 400 = 1,400", GREEN, 2.5)
        self.play(FadeIn(trough_dot), FadeIn(trough_lbl), run_time=self.T(1.5))
        self.set_work("trough month: 1,000 − 400 = 600", ROSE, 2.5)
        self.say("an 800-unit swing between best and worst month.", 4)
        self.set_work("swing = 800 units, same shop", GOLD, 3)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("order flat, and you either stock out or overpay rent.", 4)
        self.set_work("the wave says exactly when to shift", GOLD, 3.5)
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
