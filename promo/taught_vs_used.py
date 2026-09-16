"""
taught_vs_used — the maths they drilled vs the maths the shop counts on. 60.0s.

    BPM=150 manimgl taught_vs_used.py TaughtVsUsed -w -r 1080x1920

150 beats = 37.5 bars = 60.000s at 150 BPM.

EPISODE OF "WHY DID WE LEARN THIS?" — split screen, top half against
bottom half.

TOP — what they taught you: the quadratic formula, on x^2 - 5x + 6 = 0.
Discriminant 1, roots 2 and 3. Years of drilling.

BOTTOM — what you actually use: is the 3-pack cheaper? It looks like it
has to be. It isn't.

    one pack   400 g   £1.60   ->  40p per 100 g
    3-pack    1200 g   £5.28   ->  44p per 100 g

Three singles cost £4.80. The 3-pack costs £5.28. Buying the "bulk" option
costs you 48p for the same 1200 g. Bigger is not automatically cheaper —
the only way to know is the division nobody sat you down and taught.

Nothing here claims the quadratic formula is useless, or that multipacks
are always a con. The claim on screen is narrower and checkable: for these
numbers the bigger box is worse value, and per-unit price is the thing
that tells you.

VERIFIED AT IMPORT
    discriminant is 1 and both roots satisfy the equation exactly
    40p and 44p per 100 g are exact, via Fraction, not rounded
    the 3-pack really is the dearer option, by exactly 48p

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    LaggedStartMap rebuilds the group; only safe when nothing needs updaters
"""
import os
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 150

END_OPEN = 10
END_TAUGHT, END_SHOP, END_PUNCH = 36, 100, 120
END_TAKE, END_SHARE = 132, 138

SERIES = "WHY DID WE LEARN THIS?"

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

TOP_LABEL_Y = 2.95
TOP_FORM_Y  = 2.05
TOP_WORK_Y  = 1.30
TOP_TALLY_Y = 0.70
DIV_Y       = 0.25
BOT_LABEL_Y = -0.20
PACK_Y      = -1.30
UNIT_Y      = -2.45
NOTE_Y      = -3.35
LINE_Y      = -2.05

# ------------------------------------------------------------------ numbers
A, B, C = 1, -5, 6
DISC = B * B - 4 * A * C
assert DISC == 1
ROOT1 = Fraction(-B + 1, 2 * A)
ROOT2 = Fraction(-B - 1, 2 * A)
assert {ROOT1, ROOT2} == {Fraction(3), Fraction(2)}
for _r in (ROOT1, ROOT2):
    assert A * _r * _r + B * _r + C == 0

SINGLE_G, SINGLE_P = 400, 160        # grams, pence
PACK_N = 3
PACK_G, PACK_P = 1200, 528
assert PACK_G == PACK_N * SINGLE_G

PER100_SINGLE = Fraction(SINGLE_P, SINGLE_G) * 100
PER100_PACK = Fraction(PACK_P, PACK_G) * 100
assert PER100_SINGLE == 40 and PER100_PACK == 44

THREE_SINGLES = PACK_N * SINGLE_P
EXTRA = PACK_P - THREE_SINGLES
assert EXTRA == 48
assert PER100_PACK > PER100_SINGLE


def pounds(pence):
    return "£%d.%02d" % (pence // 100, pence % 100)


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


def pack_box(size_label, price_label, w, h, color):
    box = Rectangle(width=w, height=h, stroke_color=color, stroke_width=2.4)
    box.set_fill(color, opacity=0.10)
    top = txt(size_label, 19, GREY, bold=False, w=1.6)
    bot = txt(price_label, 26, color, w=1.4)
    grp = VGroup(top, box, bot).arrange(DOWN, buff=0.14)
    return grp


class TaughtVsUsed(Scene):
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
        self.stage_taught()
        self.stage_shop()
        self.stage_punch()
        self.takeaway("They drilled you on the hard one.",
                      "The shop is counting on the easy one.")
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

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("maths they taught you", 28, GOLD, w=4.6)
        big.move_to(np.array([0, 0.95, 0]))
        mid = txt("vs", 24, GREY, bold=False, w=1.0)
        mid.move_to(np.array([0, 0.15, 0]))
        sub = txt("maths you actually use", 28, WHITE_, w=4.6)
        sub.move_to(np.array([0, -0.62, 0]))
        self.add(big, mid, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.div = seg(np.array([-2.25, DIV_Y, 0]), np.array([2.25, DIV_Y, 0]),
                       FAINT, 2.0, 0.9)
        self.play(FadeOut(big), FadeOut(mid), FadeOut(sub),
                  FadeIn(self.title), ShowCreation(self.div),
                  run_time=self.T(3))
        self.pad_to(END_OPEN)

    # ==================================================================
    def stage_taught(self):
        lab = txt("WHAT THEY TAUGHT YOU", 19, GREY, bold=False, w=3.6)
        lab.move_to(np.array([0, TOP_LABEL_Y, 0]))
        self.play(FadeIn(lab), run_time=self.T(1.5))

        form = txt("x = ( −b ± √(b² − 4ac) ) / 2a", 22, GOLD, w=4.5)
        form.move_to(np.array([0, TOP_FORM_Y, 0]))
        self.play(FadeIn(form), run_time=self.T(2.5))
        self.say("solve x² − 5x + 6 = 0.", 3)

        work = txt("x = (5 ± 1) / 2   →   x = 2  or  3", 22, WHITE_, w=4.5)
        work.move_to(np.array([0, TOP_WORK_Y, 0]))
        self.play(FadeIn(work), run_time=self.T(2.5))
        self.say("fine. two and three.", 3)

        tally = txt("times you've used it since school:  0", 20, DIM,
                    bold=False, w=4.3)
        tally.move_to(np.array([0, TOP_TALLY_Y, 0]))
        self.play(FadeIn(tally), run_time=self.T(2.5))
        self.say("be honest.", 2.5, GREY)
        self.top = VGroup(lab, form, work, tally)
        self.pad_to(END_TAUGHT)

    # ==================================================================
    def stage_shop(self):
        lab = txt("WHAT YOU ACTUALLY USE", 19, GREY, bold=False, w=3.6)
        lab.move_to(np.array([0, BOT_LABEL_Y, 0]))
        self.play(FadeIn(lab), run_time=self.T(1.5))
        self.say("now this one.", 2.5)

        one = pack_box("%d g" % SINGLE_G, pounds(SINGLE_P), 0.62, 0.62, WHITE_)
        one.move_to(np.array([-1.20, PACK_Y, 0]))
        three = pack_box("%d × %d g" % (PACK_N, SINGLE_G), pounds(PACK_P),
                         1.02, 0.86, WHITE_)
        three.move_to(np.array([1.20, PACK_Y, 0]))
        three.align_to(one, DOWN)        # sit both price labels on one line
        self.packs = VGroup(one, three)
        self.play(FadeIn(one), FadeIn(three), run_time=self.T(3))
        self.say("one pack is 400 grams for £1.60.", 3.5)
        self.say("the 3-pack is £5.28.", 3)
        self.say("which one is cheaper?", 3, GOLD)
        self.pad_to(62)

        u1 = txt("%dp / 100g" % PER100_SINGLE, 24, GREEN, w=1.8)
        u1.move_to(np.array([-1.20, UNIT_Y, 0]))
        self.play(FadeIn(u1), run_time=self.T(2.5))
        u2 = txt("%dp / 100g" % PER100_PACK, 24, ROSE, w=1.8)
        u2.move_to(np.array([1.20, UNIT_Y, 0]))
        self.play(FadeIn(u2), run_time=self.T(2.5))
        self.units = VGroup(u1, u2)
        self.say("forty pence. against forty-four.", 3.5)
        self.pad_to(80)

        self.say("the big box is dearer per gram.", 3.5, ROSE)
        self.say("three singles save you %dp." % EXTRA, 3, GREEN)
        self.pad_to(END_SHOP)

    # ==================================================================
    def stage_punch(self):
        self.say("one of these you were drilled on for years.", 4)
        self.say("the other one, nobody ever mentioned.", 4, GOLD)
        self.pad_to(END_PUNCH)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.camera.frame)
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
        s1 = txt("Send this to someone", 27, WHITE_, w=4.5)
        s2 = txt("who buys the big box", 27, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.title), run_time=self.T(1.5))

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
