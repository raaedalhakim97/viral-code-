"""
net_vs_gross — you can't take 5% off a 105% number. 40.0s.

    BPM=150 manimgl net_vs_gross.py NetVsGross -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE OF "WHERE MATH ACTUALLY GETS USED". The ANSWER is pinned at the
TOP for the whole video.

        net = gross ÷ 1.05

SUBTRACTING THE TAX AND REMOVING IT ARE DIFFERENT SUMS. Given a
tax-inclusive 40,000, almost everyone takes 5% off it:

        40,000 − 5%   =   38,000        <- wrong

The test that settles it costs nothing: put it back.

        38,000 × 1.05  =  39,900        100 short. the trip doesn't close.

The 5% was never 5% of the 40,000. It is 5% OF THE NET, and the gross is
already 105% of the net — so you divide, you don't subtract:

        40,000 ÷ 1.05  =  38,095.238…   ->  38,095.24
        tax            =   1,904.76
        38,095.24 × 1.05  =  40,000.00  <- closes exactly

Same money, two formulas, one right answer. The gap is 95.24 of
overpaid tax on a single 40,000 invoice — and the tax is exactly 1/21 of
the gross, not 1/20.

VERIFIED AT IMPORT
    every figure is exact Fraction arithmetic, nothing typed in by hand
    the wrong net really does come back 100 short, exactly
    the right net really does round-trip to 40,000, exactly
    38,095.24 and 1,904.76 are the true cent-roundings of 800000/21 and 40000/21
    tax / gross == Fraction(1, 21)

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
END_WRONG, END_TEST = 26, 46
END_RIGHT, END_CHECK = 64, 78
END_TAKE, END_SHARE = 88, 92

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
GROSS = Fraction(40000)
RATE  = Fraction(5, 100)

WRONG_TAX = GROSS * RATE                       # 2000
WRONG_NET = GROSS - WRONG_TAX                  # 38000
assert WRONG_NET == 38000 and WRONG_TAX == 2000

BACK = WRONG_NET * (1 + RATE)                  # 39900 — the trip doesn't close
SHORT = GROSS - BACK
assert BACK == 39900 and SHORT == 100

NET = GROSS / (1 + RATE)
TAX = GROSS - NET
assert NET == Fraction(800000, 21)
assert TAX == Fraction(40000, 21)
assert NET * (1 + RATE) == GROSS               # the trip closes, exactly

NET_2DP = round(float(NET), 2)
TAX_2DP = round(float(TAX), 2)
assert NET_2DP == 38095.24 and TAX_2DP == 1904.76
assert round(float(NET), 3) == 38095.238
assert round(NET_2DP * 1.05, 2) == 40000.00    # still closes at cent precision

OVERPAID = WRONG_TAX - TAX
assert OVERPAID == Fraction(2000, 21)
assert round(float(OVERPAID), 2) == 95.24

assert TAX / GROSS == Fraction(1, 21)          # 1 in 21 of the gross, not 1 in 20

_M = Fraction(1000000)
MILLION_OVER = _M * RATE - (_M - _M / (1 + RATE))
assert round(float(MILLION_OVER), 2) == 2380.95

# ------------------------------------------------------------------ layout
SLOT_Y = (1.50, 0.10, -1.30)
BOX_W, BOX_H = 2.25, 0.66
MARK_X = 1.62


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


def money_box(label, color, slot, tag=None):
    """A framed amount in one of the three vertical slots."""
    y = SLOT_Y[slot]
    g = VGroup()
    g.add(Rectangle(width=BOX_W, height=BOX_H, stroke_color=color,
                    stroke_width=2.4, fill_color=color,
                    fill_opacity=0.12).move_to(np.array([0, y, 0])))
    g.add(txt(label, 30, color, w=BOX_W - 0.28).move_to(np.array([0, y, 0])))
    if tag:
        # tags go LEFT of the box, not above it: above collides with the
        # working line on slot 0 and with the incoming arrow on slot 1.
        g.add(txt(tag, 17, DIM, bold=False, w=0.95).move_to(
            np.array([-(BOX_W / 2 + 0.62), y, 0])))
    return g


def step_arrow(op, color, a, b):
    """Vertical arrow from slot a down to slot b, operator on the right."""
    y0 = SLOT_Y[a] - BOX_H / 2 - 0.06
    y1 = SLOT_Y[b] + BOX_H / 2 + 0.06
    g = VGroup(seg(np.array([0, y0, 0]), np.array([0, y1, 0]), color, 2.2),
               seg(np.array([-0.10, y1 + 0.16, 0]), np.array([0, y1, 0]), color, 2.2),
               seg(np.array([0.10, y1 + 0.16, 0]), np.array([0, y1, 0]), color, 2.2))
    lab = txt(op, 24, color, w=1.3)
    lab.move_to(np.array([0.92, (y0 + y1) / 2, 0]))
    g.add(lab)
    return g


def tick(color, y):
    return VGroup(
        seg(np.array([MARK_X - 0.16, y + 0.01, 0]),
            np.array([MARK_X - 0.05, y - 0.13, 0]), color, 4.0),
        seg(np.array([MARK_X - 0.05, y - 0.13, 0]),
            np.array([MARK_X + 0.20, y + 0.19, 0]), color, 4.0))


def cross(color, y):
    d = 0.17
    return VGroup(
        seg(np.array([MARK_X - d, y - d, 0]), np.array([MARK_X + d, y + d, 0]),
            color, 4.0),
        seg(np.array([MARK_X - d, y + d, 0]), np.array([MARK_X + d, y - d, 0]),
            color, 4.0))


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


class NetVsGross(Scene):
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
        self.stage_wrong()
        self.stage_test()
        self.stage_right()
        self.stage_check()
        self.takeaway("Subtracting takes 5% of the gross.",
                      "The tax was 5% of the net.")
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
        big = txt("40,000", 46, GOLD, w=3.0)
        big.move_to(np.array([0, 1.30, 0]))
        q = txt("tax included at 5%.", 27, WHITE_, w=4.5)
        q.move_to(np.array([0, 0.25, 0]))
        sub = txt("what's the net?", 27, GREY, bold=False, w=3.0)
        sub.move_to(np.array([0, -0.45, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.2)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("net = gross ÷ 1.05", 24, GOLD, w=4.3)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.play(FadeOut(q), FadeOut(sub), FadeOut(big),
                  FadeIn(self.eq), FadeIn(self.title), run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_wrong(self):
        self.say("almost everyone takes 5% off the 40,000.", 2.5, GREY)
        self.gross = money_box("40,000", GOLD, 0, tag="GROSS")
        self.play(FadeIn(self.gross), run_time=self.T(2))
        self.set_work("40,000 × 5%  =  2,000", ROSE, 2.5)

        self.a1 = step_arrow("− 5%", ROSE, 0, 1)
        self.b1 = money_box("38,000", ROSE, 1)
        self.play(ShowCreation(self.a1), FadeIn(self.b1), run_time=self.T(2.5))
        self.set_work("40,000 − 2,000  =  38,000", ROSE, 2.5)
        self.say("looks finished. it isn't.", 3, ROSE)
        self.pad_to(END_WRONG)

    # ==================================================================
    def stage_test(self):
        self.say("test it for free — put the tax back on.", 3, SKY)
        self.a2 = step_arrow("× 1.05", SKY, 1, 2)
        self.b2 = money_box("39,900", ROSE, 2)
        self.play(ShowCreation(self.a2), FadeIn(self.b2), run_time=self.T(2.5))
        self.set_work("38,000 × 1.05  =  39,900", SKY, 2.5)

        self.x1 = cross(ROSE, SLOT_Y[2])
        self.play(ShowCreation(self.x1), run_time=self.T(1.5))
        self.say("39,900. you started at 40,000.", 3.5, ROSE)
        self.set_work("100 short. so 38,000 was never the net.", ROSE, 3)
        self.say("the round trip has to close. this one doesn't.", 3, ROSE)
        self.pad_to(END_TEST)

    # ==================================================================
    def stage_right(self):
        self.play(FadeOut(self.a1), FadeOut(self.b1), FadeOut(self.a2),
                  FadeOut(self.b2), FadeOut(self.x1), run_time=self.T(1.5))
        self.say("the 5% was never 5% of the 40,000.", 3, GOLD)
        self.a3 = step_arrow("÷ 1.05", GOLD, 0, 1)
        self.b3 = money_box("38,095.24", GOLD, 1, tag="NET")
        self.play(ShowCreation(self.a3), FadeIn(self.b3), run_time=self.T(2.5))
        self.set_work("40,000 ÷ 1.05  =  38,095.238…", GOLD, 3)
        self.set_work("tax  =  1,904.76        not  2,000", GOLD, 3)
        self.say("the gross is already 105% of the net.", 3, GOLD)
        self.pad_to(END_RIGHT)

    # ==================================================================
    def stage_check(self):
        self.a4 = step_arrow("× 1.05", GREEN, 1, 2)
        self.b4 = money_box("40,000.00", GREEN, 2)
        self.play(ShowCreation(self.a4), FadeIn(self.b4), run_time=self.T(2.5))
        self.t1 = tick(GREEN, SLOT_Y[2])
        self.play(ShowCreation(self.t1), run_time=self.T(1.5))
        self.set_work("38,095.24 × 1.05  =  40,000.00", GREEN, 2.5)
        self.say("straight back. that's how you know it's the net.", 3, GREEN)
        self.say("the tax is 1/21 of the gross. not 1/20.", 3, GOLD)
        self.pad_to(END_CHECK)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 26, WHITE_, w=4.5).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 26, GOLD, w=4.5).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to whoever does", 27, WHITE_, w=4.5)
        s2 = txt("your invoices", 27, GOLD, w=4.5)
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
