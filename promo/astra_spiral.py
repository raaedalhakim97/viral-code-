"""
astra_spiral — the real Astra headline, and an honest 2D packing spiral. 60.0s.

    BPM=150 manimgl astra_spiral.py AstraSpiral -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

STANDALONE NEWS-HOOK EPISODE. NOT part of the regular series shells, but
reuses the same house pattern (equation pinned at the TOP for the whole
video, silent, beat-locked).

THE REAL NEWS (sourced, not invented): OpenAI's next model family, Astra,
produced Lean-verified solutions to ten open problems in math and
theoretical CS, several unsolved for decades. One of them: the general
upper bound on high-dimensional sphere-packing density, unmoved since the
Kabatiansky-Levenshtein bound of 1978 (~2^-0.599d). Astra's result pushes
that bound to roughly 2^-0.61d, via the Cohn-Elkies linear-programming
method. Sources (checked at build time via WebSearch): DataCamp, the
Decoder, Hacker News (item 49143688), Forbes, SiliconANGLE, MindStudio.

THIS VIDEO DOES NOT SHOW ASTRA'S ACTUAL PROOF — nobody could animate a
Cohn-Elkies LP bound in high dimensions honestly in 60 seconds, and no
source describes Astra using a "spiral" at all. What this video shows
instead, and says so on screen: an honest, self-contained 2D packing
puzzle solved by a real spiral construction — the golden-angle spiral
used in phyllotaxis — as a small, correct taste of why packing problems
are hard and how a spiral can do serious work on one.

THE PUZZLE: place N points outward along a spiral (radius ~ sqrt(index)),
one step angle at a time, then draw the biggest non-overlapping circle at
every point. Two angles, same N, same layout rule:

    a "reasonable-looking" angle, 90°           -> packs terribly
    the golden angle, 137.5077901...°            -> packs almost optimally

VERIFIED AT IMPORT
    both spirals: zero circle overlaps, by construction (checked pairwise)
    golden-angle packing density > 50%, 90-degree packing density < 2%
    density ratio > 50x, both computed from the same N and scale

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
END_A, END_B = 44, 88
END_WHY, END_TAKE, END_SHARE = 107, 122, 132

SERIES = "THE REAL MATH BEHIND THE HEADLINES"

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
N = 120
PHI = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE = 2 * math.pi * (1 - 1 / PHI)
BAD_ANGLE = math.pi / 2
assert abs(math.degrees(GOLDEN_ANGLE) - 137.50776405) < 1e-6


def spiral_points(n, angle, c=1.0):
    idx = np.arange(1, n + 1)
    r = c * np.sqrt(idx)
    th = idx * angle
    return np.stack([r * np.cos(th), r * np.sin(th)], axis=1)


def min_pairwise_dist(pts):
    diff = pts[:, None, :] - pts[None, :, :]
    d = np.sqrt((diff ** 2).sum(axis=2))
    np.fill_diagonal(d, np.inf)
    return float(d.min())


def assert_no_overlap(pts, rad):
    diff = pts[:, None, :] - pts[None, :, :]
    d = np.sqrt((diff ** 2).sum(axis=2))
    np.fill_diagonal(d, np.inf)
    assert d.min() >= 2 * rad - 1e-6, "circles overlap — packing is invalid"


PTS_GOOD = spiral_points(N, GOLDEN_ANGLE)
PTS_BAD = spiral_points(N, BAD_ANGLE)

RAD_GOOD = min_pairwise_dist(PTS_GOOD) / 2 * 0.995
RAD_BAD = min_pairwise_dist(PTS_BAD) / 2 * 0.995
assert_no_overlap(PTS_GOOD, RAD_GOOD)
assert_no_overlap(PTS_BAD, RAD_BAD)

R_PTS = float(np.sqrt((PTS_GOOD ** 2).sum(axis=1)).max())
assert abs(R_PTS - float(np.sqrt((PTS_BAD ** 2).sum(axis=1)).max())) < 1e-9

R_GOOD_TOTAL = R_PTS + RAD_GOOD
R_BAD_TOTAL = R_PTS + RAD_BAD

DENSITY_GOOD = N * math.pi * RAD_GOOD ** 2 / (math.pi * R_GOOD_TOTAL ** 2)
DENSITY_BAD = N * math.pi * RAD_BAD ** 2 / (math.pi * R_BAD_TOTAL ** 2)
assert DENSITY_GOOD > 0.5
assert DENSITY_BAD < 0.02
assert DENSITY_GOOD / DENSITY_BAD > 50

TARGET_SPAN = 1.9
U = TARGET_SPAN / R_GOOD_TOTAL
DISK_CENTER = np.array([0.0, -0.95, 0])


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


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


def build_disk(pts, rad, color, fill_op):
    grp = VGroup()
    r_screen = rad * U
    for p in pts:
        c = Circle(radius=r_screen, stroke_color=color, stroke_width=1.0,
                   fill_color=color, fill_opacity=fill_op)
        c.move_to(DISK_CENTER + np.array([p[0] * U, p[1] * U, 0]))
        grp.add(c)
    return grp


class AstraSpiral(Scene):
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
        self.stage_bad()
        self.stage_good()
        self.stage_why()
        self.takeaway("Real math didn't stop moving.",
                      "It just moved somewhere you didn't hear about.")
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

    def say(self, s, beats=2, color=WHITE_, size=24):
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
        big = txt("48 years. broken this week.", 27, GOLD, w=4.6)
        big.move_to(np.array([0, 1.15, 0]))
        q = txt("OpenAI's Astra just solved it", 26, WHITE_, w=4.6)
        q.move_to(np.array([0, 0.15, 0]))
        sub = txt("a sphere-packing record from 1978.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.55, 0]))
        self.add(big, q, sub)
        self.wait(self.T(6))

        self.title = txt(SERIES, 17, GREY, bold=False, w=4.2)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("137.5077901...°", 26, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(4))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_bad(self):
        self.say("same puzzle: pack circles as densely as you can.", 3.5)
        self.set_work("step outward. turn 90° every time.", WHITE_, 3)
        self.disk_bad = build_disk(PTS_BAD, RAD_BAD, DIM, 0.55)
        self.play(LaggedStartMap(FadeIn, self.disk_bad, lag_ratio=0.02),
                  run_time=self.T(4))
        self.say("a \"reasonable\" angle. look how much is wasted.", 3.5, ROSE)
        self.set_work("packing ≈ 0.8%", ROSE, 2.5)
        self.pad_to(END_A)

    def stage_good(self):
        self.say("same rule. one different angle.", 3)
        self.play(FadeOut(self.disk_bad), run_time=self.T(1.5))
        self.set_work("turn 137.5077901...° every time instead", GOLD, 3)
        self.disk_good = build_disk(PTS_GOOD, RAD_GOOD, GOLD, 0.7)
        self.play(LaggedStartMap(FadeIn, self.disk_good, lag_ratio=0.02),
                  run_time=self.T(5))
        self.say("no gaps. no overlaps. checked, not eyeballed.", 3.5, GOLD)
        self.set_work("packing ≈ 55.2%", GREEN, 2.5)
        self.say("same 120 circles. sixty-seven times denser.", 3.5)
        self.pad_to(END_B)

    # ==================================================================
    def stage_why(self):
        self.say("the golden angle never repeats as a simple fraction of a turn.", 3.5)
        self.set_work("so no two points ever line up and clump", GOLD, 3)
        self.say("this is the 2D toy version — not Astra's real proof.", 3.5, GREY)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 28, WHITE_, w=4.4).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 24, GOLD, w=4.6).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to someone who thinks", 27, WHITE_, w=4.5)
        s2 = txt("AI can't do real math", 27, GOLD, w=4.6)
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
