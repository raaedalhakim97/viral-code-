"""
collatz — pick any number. you always land on 1. 60.0s.

    BPM=150 manimgl collatz.py Collatz -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

"SATISFYING MATH" episode — entertainment lane. Built to be watched.

THE RULE, and it is the whole rule:
    even  ->  halve it
    odd   ->  triple it and add one

Start anywhere. 6 goes 6, 3, 10, 5, 16, 8, 4, 2, 1 — eight steps, done.
27 goes berserk: it climbs to 9,232 and takes 111 steps, and still lands
on 1. Every number anyone has ever tried lands on 1.

Nobody has proved it always does. It has been open since 1937. Erdos:
"mathematics is not yet ready for such problems."

THE NUMBERS ON SCREEN, all computed and checked at import:
    6  -> 8 steps
    27 -> 111 steps, peak 9232
    every start from 1 to 100000 reaches 1

VERIFIED AT IMPORT
    the two headline paths are recomputed from the rule, not hard-coded
    27's step count and peak are exactly 111 and 9232
    a brute-force sweep confirms every start up to 100000 terminates
    every plotted path ends on the value 1

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    LaggedStartMap rebuilds the group; only safe when nothing needs updaters
"""
import os
import math

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 10
END_SIX, END_27, END_MANY = 34, 76, 120
END_TAKE, END_SHARE = 132, 138

SERIES = "SATISFYING MATH"

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
NOTE_Y = -3.30
LINE_Y = -2.05


# ------------------------------------------------------------------ numbers
def collatz(n):
    s = [n]
    while n != 1:
        n = n // 2 if n % 2 == 0 else 3 * n + 1
        s.append(n)
    return s


SEQ6 = collatz(6)
SEQ27 = collatz(27)
assert SEQ6 == [6, 3, 10, 5, 16, 8, 4, 2, 1]
assert len(SEQ27) - 1 == 111
assert max(SEQ27) == 9232

# brute force: everything up to 100000 really does terminate
_seen = {1}
for _start in range(2, 100001):
    _n = _start
    _path = []
    while _n not in _seen:
        _path.append(_n)
        _n = _n // 2 if _n % 2 == 0 else 3 * _n + 1
    _seen.update(_path)
assert len(_seen) >= 100000

MANY = list(range(2, 101))
PATHS = [collatz(n) for n in MANY]
assert all(p[-1] == 1 for p in PATHS)
MAX_STEPS = max(len(p) - 1 for p in PATHS)
MAX_VAL = max(max(p) for p in PATHS)

# plot frame: x is step, y is log10(value), paths right-aligned on their 1
PLOT_X0, PLOT_X1 = -2.05, 2.05
PLOT_Y0, PLOT_Y1 = -2.45, 1.45
LOG_TOP = math.log10(MAX_VAL)


def plot_xy(step_from_end, value, total_from_end):
    """Right-align every path on its final 1, so they funnel to one point."""
    x = PLOT_X1 - (step_from_end / total_from_end) * (PLOT_X1 - PLOT_X0)
    y = PLOT_Y0 + (math.log10(value) / LOG_TOP) * (PLOT_Y1 - PLOT_Y0)
    return np.array([x, y, 0])


def path_points(seq, span):
    last = len(seq) - 1
    return [plot_xy(last - i, v, span) for i, v in enumerate(seq)]


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def poly(points, color=WHITE_, wid=2.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners(points)
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


class Collatz(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_six()
        self.stage_27()
        self.stage_many()
        self.takeaway("Every number ever tried lands on 1.",
                      "Nobody has proved it always does.")
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

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("pick any number.", 30, GOLD, w=4.5)
        big.move_to(np.array([0, 0.95, 0]))
        r1 = txt("even?  halve it.", 25, WHITE_, w=4.6)
        r1.move_to(np.array([0, -0.05, 0]))
        r2 = txt("odd?  triple it, add one.", 25, WHITE_, w=4.6)
        r2.move_to(np.array([0, -0.72, 0]))
        self.add(big, r1, r2)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("even ÷2    ·    odd ×3+1", 24, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(big), FadeOut(r1), FadeOut(r2),
                  FadeIn(self.title), FadeIn(self.eq), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_six(self):
        self.say("start with 6.", 2.5)
        chain = VGroup()
        for i, v in enumerate(SEQ6):
            t = txt(str(v), 34 if v == 1 else 30,
                    GOLD if v == 1 else WHITE_, w=1.1)
            chain.add(t)
        chain.arrange(RIGHT, buff=0.30)
        if chain.get_width() > 4.5:
            chain.set_width(4.5)
        chain.move_to(np.array([0, 0.15, 0]))
        self.chain = chain

        for i, t in enumerate(chain):
            self.play(FadeIn(t, shift=0.10 * RIGHT), run_time=self.T(1))
        self.say("eight steps. it hits 1.", 3, GOLD)
        self.pad_to(END_SIX)

    # ==================================================================
    def stage_27(self):
        self.play(FadeOut(self.chain), run_time=self.T(1.5))
        self.say("now try 27.", 2.5)

        base = poly([np.array([PLOT_X0, PLOT_Y0, 0]),
                     np.array([PLOT_X1, PLOT_Y0, 0])], FAINT, 1.6, 0.9)
        self.base = base
        self.play(FadeIn(base), run_time=self.T(1.5))

        span = len(SEQ27) - 1
        self.p27 = poly(path_points(SEQ27, span), GOLD, 2.6)
        self.dot27 = Dot(plot_xy(0, 1, span), radius=0.075, fill_color=GOLD)
        self.play(ShowCreation(self.p27), run_time=self.T(6))
        self.play(FadeIn(self.dot27), run_time=self.T(1))
        self.say("it climbs to nine thousand two hundred.", 3.5, ROSE)
        self.pad_to(60)
        self.say("111 steps. and it still comes back to 1.", 4, GOLD)
        self.pad_to(END_27)

    # ==================================================================
    def stage_many(self):
        self.say("every number does this.", 3)
        self.play(FadeOut(self.p27), run_time=self.T(1.5))

        fan = VGroup()
        for seq in PATHS:
            # each path spans the full width, same as 27's did — otherwise the
            # short ones collapse into a sliver on the right and 99 paths read
            # as two. x is progress along the path, y is log10(value).
            fan.add(poly(path_points(seq, len(seq) - 1), SKY, 1.3, 0.55))
        self.fan = fan
        self.play(LaggedStartMap(ShowCreation, fan, lag_ratio=0.012),
                  run_time=self.T(7))
        self.pad_to(100)
        self.say("ninety-nine starts. one ending.", 3.5, GOLD)
        self.pad_to(END_MANY)

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
        s1 = txt("Comment a number", 27, WHITE_, w=4.5)
        s2 = txt("and I'll run it", 27, GOLD, w=4.6)
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
