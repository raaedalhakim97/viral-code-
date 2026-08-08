"""
calculator_vs_ai — a calculator computes, a model predicts. 28.8s.

    BPM=150 manimgl calculator_vs_ai.py CalculatorVsAI -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

THE SPINE OF THE VIDEO, AND BOTH HALVES ARE VERIFIED

A calculator adds with a ripple-carry chain of full adders:

    S    = A xor B xor Cin
    Cout = (A and B) or (Cin and (A xor B))

Eight rows of a truth table, exhaustively checked in this file at import. It
MUST start at the smallest digit, because every carry propagates UPWARD — bit 0
decides the carry into bit 1, and so on. Low to high is not a convention, it is
forced by the arithmetic.

A language model writes left to right, so the FIRST token it emits for a product
is the HIGHEST place value — the one that depends on everything it has not
computed yet. That is not a nitpick, and here is the proof, also asserted at
import:

    317 x 315 =  99,855      leading digit 9, five digits
    317 x 316 = 100,172      leading digit 1, SIX digits

Change the LAST digit of the input and the FIRST digit of the answer flips, and
the answer grows a place. You cannot know the first digit without having already
done the last one. The model has to answer before the work that decides the
answer exists.

The measured consequence, GPT-4 on n-digit multiplication:

    3 digits  59%      4 digits  4%      5 digits  0%

from Goat: Fine-tuned LLaMA Outperforms GPT-4 on Arithmetic Tasks,
arXiv:2305.14201. Quoted, not measured here — the only figure in the file that
is not computed at build time, and it is attributed on screen.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 72
BODY_END = 56
TAKE_END = 62

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
TOP_Y   = 3.30
CAP_Y   = 1.78
NOTE_Y  = -1.62

# ---------------------------------------------------------------- verified
def full_adder(a, b, cin):
    return (a ^ b ^ cin), ((a & b) | (cin & (a ^ b)))


for _a in (0, 1):
    for _b in (0, 1):
        for _c in (0, 1):
            _s, _co = full_adder(_a, _b, _c)
            assert _s + 2 * _co == _a + _b + _c

OP_A, OP_B = 0b1101, 0b1011                      # 13 + 11 = 24 = 0b11000
assert OP_A + OP_B == 24

assert 317 * 315 == 99855 and len(str(317 * 315)) == 5
assert 317 * 316 == 100172 and len(str(317 * 316)) == 6
assert str(317 * 315)[0] == "9" and str(317 * 316)[0] == "1"

GPT4_MULT = [("3 digits", 59), ("4 digits", 4), ("5 digits", 0)]


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, w=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=w)
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


COLS = [-1.60, -0.80, 0.00, 0.80, 1.60]          # five bit columns, LSB at right


class CalculatorVsAI(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.stage = []

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open_card()
        self.ch1_calculator()
        self.ch2_leading_digit()
        self.ch3_numbers()
        self.ch4_payoff()
        self.close("One computes the answer.", "The other predicts it.")

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

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.055):
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def say(self, s, beats=2, color=WHITE_, size=23):
        new = txt(s, size, color, bold=False, w=4.4)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def clear_stage(self, beats=1):
        if self.stage:
            for m in self.stage:
                m.clear_updaters()
            self.play(*[FadeOut(m) for m in self.stage], run_time=self.T(beats))
            self.stage = []
        else:
            self.wait(self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        self.title = txt("CALCULATOR vs AI", 48, WHITE_, w=4.6)
        self.title.move_to(np.array([0, 1.05, 0]))
        self.sub = txt("why one of them can't multiply", 23, GOLD, bold=False)
        self.sub.move_to(np.array([0, 0.35, 0]))
        self.add(self.title, self.sub)
        self.wait(self.T(2))
        self.mark = txt("OBSERVER COLLAPSE", 18, GREY, bold=False, w=3.0)
        self.mark.move_to(np.array([0, TOP_Y, 0]))
        self.play(FadeIn(self.mark), run_time=self.T(1))
        self.play(self.title.animate.set_height(
                      self.title.get_height() * 0.52).move_to(np.array([0, 2.62, 0])),
                  self.sub.animate.set_height(
                      self.sub.get_height() * 0.88).move_to(np.array([0, 2.18, 0])),
                  run_time=self.T(1))

    def close(self, a, b):
        self.pad_to(BODY_END)
        keep = self.stage + ([self.note] if self.note else [])
        for m in keep:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in keep], run_time=self.T(1))
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(TAKE_END)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.title),
                  FadeOut(self.sub), FadeOut(self.mark), run_time=self.T(1))
        self.signature()

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
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
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))

    # ==================================================================
    # 1 — the calculator: a ripple-carry adder, forced to go low to high
    # ==================================================================
    def ch1_calculator(self):
        head = txt("13  +  11", 34, WHITE_)
        head.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.stage.append(head)
        self.say("a calculator does not know the answer", 1)

        rowA, rowB = VGroup(), VGroup()
        for j in range(4):
            x = COLS[j + 1]
            a = txt(str((OP_A >> (3 - j)) & 1), 30, WHITE_, w=0.4)
            a.move_to(np.array([x, 1.02, 0]))
            b = txt(str((OP_B >> (3 - j)) & 1), 30, WHITE_, w=0.4)
            b.move_to(np.array([x, 0.42, 0]))
            rowA.add(a)
            rowB.add(b)
        rule = seg(np.array([-2.0, 0.10, 0]), np.array([2.0, 0.10, 0]), FAINT, 2.4)
        self.play(FadeIn(rowA), FadeIn(rowB), ShowCreation(rule), run_time=self.T(2))
        self.stage += [rowA, rowB, rule]
        self.wait(self.T(1))

        gate = txt("S = A ⊕ B ⊕ C", 22, GREY, bold=False, w=3.0)
        gate.move_to(np.array([0, -0.95, 0]))
        self.play(FadeIn(gate), run_time=self.T(1))
        self.stage.append(gate)
        self.say("it starts at the smallest digit", 2, GOLD)

        # the real ripple: bit 0 first, carry pushing left
        # The highlight follows the carry, one column per step. Fading the
        # previous one inside the same play avoids a run_time=0 call, which
        # manim tolerates but should not be relied on.
        carry, prev = 0, None
        for i in range(4):
            j = 3 - i                                  # column index, right to left
            s, carry = full_adder((OP_A >> i) & 1, (OP_B >> i) & 1, carry)
            d = txt(str(s), 32, GOLD, w=0.4)
            d.move_to(np.array([COLS[j + 1], -0.32, 0]))
            hl = seg(np.array([COLS[j + 1], 1.30, 0]),
                     np.array([COLS[j + 1], -0.10, 0]), GOLD, 2.0, 0.45)
            anims = [FadeIn(d), ShowCreation(hl)]
            if prev is not None:
                anims.append(FadeOut(prev))
            self.play(*anims, run_time=self.T(1.5))
            self.stage.append(d)
            prev = hl
        co = txt(str(carry), 32, GOLD, w=0.4)
        co.move_to(np.array([COLS[0], -0.32, 0]))
        self.play(FadeIn(co, scale=1.4), FadeOut(prev), run_time=self.T(1))
        self.stage.append(co)

        res = txt("= 24", 30, WHITE_)
        res.move_to(np.array([0, -1.02, 0]))
        self.play(FadeOut(gate), FadeIn(res), run_time=self.T(1))
        self.stage.remove(gate)
        self.stage.append(res)
        self.say("every carry moves left. it has no choice.", 2)
        self.wait(self.T(1))

    # ==================================================================
    # 2 — the model must emit the digit that depends on everything else
    # ==================================================================
    def ch2_leading_digit(self):
        self.clear_stage(1)
        head = txt("now multiply", 24, GREY, bold=False)
        head.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.stage.append(head)

        # Built as five pieces per row so the two digits that matter are their
        # own mobjects and can turn gold on cue. A single marker line landed on
        # the equals sign and pointed at nothing.
        def row(tail, lead, rest, y):
            g = VGroup(txt("317 × 31", 30), txt(tail, 30), txt("=", 30),
                       txt(lead, 30), txt(rest, 30)).arrange(RIGHT, buff=0.10)
            if g.get_width() > 4.4:
                g.set_width(4.4)
            return g.move_to(np.array([0, y, 0]))

        l1 = row("5", "9", "9,855", 0.85)
        self.play(FadeIn(l1), run_time=self.T(2))
        l2 = row("6", "1", "00,172", 0.15)
        self.play(FadeIn(l2), run_time=self.T(2))
        self.stage += [l1, l2]
        self.wait(self.T(1))

        self.play(*[l[i].animate.set_color(GOLD) for l in (l1, l2) for i in (1, 3)],
                  run_time=self.T(1))
        self.say("one digit changes at the end", 2, GOLD)
        self.say("and the FIRST digit of the answer flips", 2, GOLD)
        self.wait(self.T(1))

        t = txt("a model writes left to right", 26, WHITE_, w=4.4)
        t.move_to(np.array([0, -0.85, 0]))
        self.play(FadeIn(t), run_time=self.T(1))
        self.stage.append(t)
        self.say("so it says that digit first — before the work", 2)

    # ==================================================================
    # 3 — the measured consequence
    # ==================================================================
    def ch3_numbers(self):
        self.clear_stage(1)
        head = txt("GPT-4, multiplication", 26, WHITE_)
        head.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.stage.append(head)

        rows = VGroup()
        for i, (lab, pct) in enumerate(GPT4_MULT):
            y = 0.85 - i * 0.72
            name = txt(lab, 23, GREY, bold=False, w=1.3)
            name.move_to(np.array([-1.65, y, 0]))
            bar = Rectangle(width=max(3.0 * pct / 100.0, 0.02), height=0.26,
                            stroke_width=0)
            bar.set_fill(GOLD if pct > 20 else COOL, opacity=0.9)
            bar.move_to(np.array([-0.95 + max(3.0 * pct / 100.0, 0.02) / 2, y, 0]))
            val = txt(f"{pct}%", 24, WHITE_ if pct else GREY, w=0.9)
            val.move_to(np.array([1.95, y, 0]))
            row = VGroup(name, bar, val)
            self.play(FadeIn(row, shift=0.1 * RIGHT), run_time=self.T(1.5),
                      rate_func=rush_from)
            rows.add(row)
        self.stage.append(rows)
        src = txt("Goat, arXiv:2305.14201", 17, GREY, bold=False, w=3.0)
        src.move_to(np.array([0, -1.18, 0]))
        self.play(FadeIn(src), run_time=self.T(1))
        self.stage.append(src)
        self.say("five digits: zero out of a hundred", 2, GOLD)
        self.wait(self.T(0.5))

    # ==================================================================
    # 4 — and so it stopped trying
    # ==================================================================
    def ch4_payoff(self):
        self.clear_stage(1)
        a = txt("the calculator is right", 27, WHITE_, w=4.4)
        a.move_to(np.array([0, 1.05, 0]))
        a2 = txt("by construction", 27, GOLD, w=4.4)
        a2.move_to(np.array([0, 0.50, 0]))
        self.play(FadeIn(a), run_time=self.T(1))
        self.play(FadeIn(a2), run_time=self.T(1))

        b = txt("the model is right", 27, WHITE_, w=4.4)
        b.move_to(np.array([0, -0.30, 0]))
        b2 = txt("by resemblance", 27, GOLD, w=4.4)
        b2.move_to(np.array([0, -0.85, 0]))
        self.play(FadeIn(b), run_time=self.T(1))
        self.play(FadeIn(b2), run_time=self.T(1))
        self.stage += [a, a2, b, b2]
        self.say("which is why it now just calls a calculator", 2)
