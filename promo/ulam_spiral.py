"""
ulam_spiral — write the numbers in a spiral, circle the primes. 60.0s.

    BPM=150 manimgl ulam_spiral.py UlamSpiral -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

"SATISFYING MATH" episode — entertainment lane. Built to be watched.

THE SETUP. Write 1, 2, 3, 4, ... in a square spiral. Mark every prime.
Primes are supposed to be the unpredictable ones — no formula generates
them, the gaps between them are erratic. So the marks should look like
noise. They don't. They fall onto clear diagonal lines.

Stanislaw Ulam noticed this in 1963, doodling through a boring talk.

THE NUMBERS ON SCREEN, all computed and checked at import:
    45 x 45 spiral = 2025 numbers, of which 306 are prime -> 15.1% overall
    the diagonal x + y = -2 runs 43 cells and holds 21 primes -> 48.8%
    that one line is more than three times as prime-dense as the average

Nobody has explained the lines. The quadratics that run along spiral
diagonals (4n^2 + bn + c) are known to be unusually prime-rich, but *why*
some are so much richer than others is open.

VERIFIED AT IMPORT
    every spiral cell is distinct                 the walk never repeats
    the 5x5 layout matches the standard Ulam arrangement
    306 primes below 2025, 21 of them on the highlighted diagonal
    the highlighted diagonal really is >3x the overall prime density

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    LaggedStartMap rebuilds the group; only safe when nothing needs updaters
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 10
END_SMALL, END_BIG, END_LINE = 40, 100, 120
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
def spiral_cells(n_max):
    x = y = 0
    pts = [(0, 0)]
    dirs = [(1, 0), (0, 1), (-1, 0), (0, -1)]
    d = 0
    step = 1
    n = 1
    while n < n_max:
        for _ in range(2):
            dx, dy = dirs[d % 4]
            for _ in range(step):
                if n >= n_max:
                    break
                x += dx
                y += dy
                n += 1
                pts.append((x, y))
            d += 1
        step += 1
    return pts


def is_prime(v):
    if v < 2:
        return False
    if v < 4:
        return True
    if v % 2 == 0:
        return False
    f = 3
    while f * f <= v:
        if v % f == 0:
            return False
        f += 2
    return True


SIDE = 45
N_MAX = SIDE * SIDE
CELLS = spiral_cells(N_MAX)
assert len(set(CELLS)) == N_MAX

# the standard Ulam arrangement, as a spot-check on the walk
_g = {p: i + 1 for i, p in enumerate(CELLS)}
assert [_g[(x, 0)] for x in (-2, -1, 0, 1, 2)] == [19, 6, 1, 2, 11]
assert [_g[(x, 1)] for x in (-2, -1, 0, 1, 2)] == [18, 5, 4, 3, 12]

PRIMES = [n for n in range(1, N_MAX + 1) if is_prime(n)]
POS = {i + 1: CELLS[i] for i in range(N_MAX)}
assert len(PRIMES) == 306

DIAG_C = -2                      # the highlighted diagonal, x + y = DIAG_C
DIAG_CELLS = [n for n in range(1, N_MAX + 1) if sum(POS[n]) == DIAG_C]
DIAG_PRIMES = [n for n in DIAG_CELLS if is_prime(n)]
assert len(DIAG_CELLS) == 43 and len(DIAG_PRIMES) == 21

RATE_ALL = len(PRIMES) / N_MAX
RATE_DIAG = len(DIAG_PRIMES) / len(DIAG_CELLS)
assert abs(RATE_ALL - 0.151) < 0.001
assert abs(RATE_DIAG - 0.488) < 0.001
assert RATE_DIAG > 3 * RATE_ALL

SMALL_SIDE = 5
SMALL_MAX = SMALL_SIDE * SMALL_SIDE

BIG_SPAN = 4.30
BIG_U = BIG_SPAN / SIDE
BIG_C = np.array([0.0, -0.55, 0])
SMALL_U = 0.62
SMALL_C = np.array([0.0, -0.55, 0])


def big_xy(cell):
    return BIG_C + np.array([cell[0] * BIG_U, cell[1] * BIG_U, 0])


def small_xy(cell):
    return SMALL_C + np.array([cell[0] * SMALL_U, cell[1] * SMALL_U, 0])


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


class UlamSpiral(Scene):
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
        self.stage_small()
        self.stage_big()
        self.stage_line()
        self.takeaway("Nobody knows why the lines are there.",
                      "Sixty years, still open.")
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
        big = txt("primes aren't random.", 30, GOLD, w=4.5)
        big.move_to(np.array([0, 0.85, 0]))
        q = txt("write them in a spiral", 26, WHITE_, w=4.6)
        q.move_to(np.array([0, -0.10, 0]))
        sub = txt("and the lines show up.", 22, GREY, bold=False)
        sub.move_to(np.array([0, -0.80, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.play(FadeOut(big), FadeOut(q), FadeOut(sub),
                  FadeIn(self.title), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_small(self):
        nums = VGroup()
        self.small_primes = VGroup()
        for n in range(1, SMALL_MAX + 1):
            t = txt(str(n), 24, DIM, w=0.45)
            t.move_to(small_xy(POS[n]))
            nums.add(t)
            if is_prime(n):
                self.small_primes.add(t)
        self.small = nums
        self.play(LaggedStartMap(FadeIn, nums, lag_ratio=0.03),
                  run_time=self.T(2.5))
        self.say("1, 2, 3, 4 — spiralling outward.", 3)
        self.pad_to(22)

        self.play(*[t.animate.set_color(GOLD).scale(1.15)
                    for t in self.small_primes], run_time=self.T(2))
        self.say("now light up the primes.", 3, GOLD)
        self.pad_to(END_SMALL)

    # ==================================================================
    def stage_big(self):
        self.play(FadeOut(self.small), run_time=self.T(1.5))
        self.say("same thing, for two thousand numbers.", 3.5)

        dots = VGroup()
        self.diag_dots = VGroup()
        for n in PRIMES:
            d = Dot(big_xy(POS[n]), radius=0.040, fill_color=GOLD)
            dots.add(d)
            if sum(POS[n]) == DIAG_C:
                self.diag_dots.add(d)
        self.dots = dots
        self.play(LaggedStartMap(FadeIn, dots, lag_ratio=0.004),
                  run_time=self.T(5))
        self.pad_to(62)
        self.say("primes are the unpredictable ones.", 3)
        self.pad_to(78)
        self.say("so why are they sitting on diagonals?", 3.5, GOLD)
        self.pad_to(END_BIG)

    # ==================================================================
    def stage_line(self):
        lo = min(DIAG_CELLS, key=lambda n: POS[n][0])
        hi = max(DIAG_CELLS, key=lambda n: POS[n][0])
        line = seg(big_xy(POS[lo]), big_xy(POS[hi]), SKY, 2.2, 0.75)
        self.play(ShowCreation(line), run_time=self.T(2))
        self.say("21 of the 43 numbers on this line are prime.", 4, SKY)
        self.eq = txt("49% prime.   average: 15%.", 25, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeIn(self.eq), run_time=self.T(2))
        self.pad_to(END_LINE)

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
        s1 = txt("Send this to someone who thinks", 26, WHITE_, w=4.5)
        s2 = txt("maths is finished", 26, GOLD, w=4.6)
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
