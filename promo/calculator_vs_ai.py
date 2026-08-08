"""
calculator_vs_ai — three clearly signposted stages. 35.2s.

    BPM=150 manimgl calculator_vs_ai.py CalculatorVsAI -w -r 1080x1920

88 beats = 22 bars = 35.200s at 150 BPM.

STRUCTURE IS THE POINT OF THIS CUT.
The first version ran the calculator, the AI and the comparison together as one
stream. Everything was true and nobody could tell which part they were in. This
one is three stages with a FULL-SCREEN CARD between each, and a live "1 / 3"
marker in the header so the stage is on screen at every moment:

    1  THE CALCULATOR   how a normal calculator adds. Nothing about AI.
    2  THE AI           how a model produces digits. Nothing about gates.
    3  SIDE BY SIDE     the two, in a table, one row at a time.

Each section pads to a fixed beat, so slack is absorbed at the section end
rather than by hand-counting every animation.

BOTH HALVES ARE VERIFIED

A calculator adds with a ripple-carry chain of full adders:

    S    = A xor B xor Cin
    Cout = (A and B) or (Cin and (A xor B))

Eight rows of a truth table, checked exhaustively at import. It MUST start at
the smallest digit: bit 0 decides the carry into bit 1, and so on. Low to high
is forced by the arithmetic, not chosen.

A language model writes left to right, so the FIRST token it emits for a product
is the HIGHEST place value — the one that depends on everything it has not
computed yet. Proof, also asserted at import:

    317 x 315 =  99,855      leading digit 9, five digits
    317 x 316 = 100,172      leading digit 1, SIX digits

Change the LAST digit of the input and the FIRST digit of the answer flips, and
the answer grows a place.

The measured consequence, GPT-4 on n-digit multiplication:

    3 digits  59%      4 digits  4%      5 digits  0%

from Goat: Fine-tuned LLaMA Outperforms GPT-4 on Arithmetic Tasks,
arXiv:2305.14201. Quoted, not measured here — the only figure in the file not
computed at build time, and it is attributed on screen.

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
TOTAL = 88

# every section ends on a fixed beat; slack is absorbed there, not counted by hand
END_OPEN, END_CARD1, END_CALC = 4, 8, 28
END_CARD2, END_AI = 32, 54
END_CARD3, END_CMP = 58, 72
END_TAKE = 78

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

COMPARE = [("smallest digit first", "biggest digit first"),
           ("logic gates", "prediction"),
           ("always exact", "0% at 5 digits"),
           ("by construction", "by resemblance")]

COLS = [-1.60, -0.80, 0.00, 0.80, 1.60]          # five bit columns, LSB at right


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


class CalculatorVsAI(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.stage = []
        self.marker = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open_card()
        self.section_card(1, "THE CALCULATOR", END_CARD1)
        self.part1_calculator()
        self.section_card(2, "THE AI", END_CARD2)
        self.part2_ai()
        self.section_card(3, "SIDE BY SIDE", END_CARD3)
        self.part3_compare()
        self.takeaway("One computes the answer.", "The other predicts it.")
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
        keep = self.stage + ([self.note] if self.note else [])
        if keep:
            for m in keep:
                m.clear_updaters()
            self.play(*[FadeOut(m) for m in keep], run_time=self.T(beats))
            self.stage, self.note = [], None
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
        self.play(self.title.animate.set_height(
                      self.title.get_height() * 0.50).move_to(np.array([0, 3.30, 0])),
                  FadeOut(self.sub), run_time=self.T(1))
        self.pad_to(END_OPEN)

    def section_card(self, n, name, end):
        """A full-screen stage marker. This is the thing the first cut lacked —
        without it every section blended into the last."""
        self.clear_stage(1)
        big = VGroup(txt(f"{n}", 74, GOLD),
                     txt(name, 34, WHITE_, w=4.4)).arrange(DOWN, buff=0.30)
        big.move_to(np.array([0, 0.35, 0]))
        self.play(FadeIn(big, scale=1.12), run_time=self.T(1), rate_func=rush_from)

        # the small live marker that then stays up for the whole section
        new = txt(f"{n} / 3   {name}", 20, GOLD, bold=False, w=3.6)
        new.move_to(np.array([0, 2.62, 0]))
        self.pad_to(end - 1)
        if self.marker is None:
            self.marker = new
            self.play(FadeOut(big), FadeIn(new), run_time=self.T(1))
        else:
            self.play(FadeOut(big), Transform(self.marker, new),
                      run_time=self.T(1))

    # ==================================================================
    # 1 — THE CALCULATOR.  Only the calculator.
    # ==================================================================
    def part1_calculator(self):
        head = txt("13  +  11", 34, WHITE_)
        head.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.stage.append(head)

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
        self.say("in binary, with logic gates", 2)

        gate = txt("S = A ⊕ B ⊕ C", 22, GREY, bold=False, w=3.0)
        gate.move_to(np.array([0, -0.95, 0]))
        self.play(FadeIn(gate), run_time=self.T(1))
        self.stage.append(gate)
        self.say("it starts at the SMALLEST digit", 2, GOLD)

        carry, prev = 0, None
        for i in range(4):
            j = 3 - i                                  # column, right to left
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
        self.pad_to(END_CALC)

    # ==================================================================
    # 2 — THE AI.  Only the model.
    # ==================================================================
    def part2_ai(self):
        t0 = txt("a model writes left to right", 27, WHITE_, w=4.4)
        t0.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(t0), run_time=self.T(1))
        self.stage.append(t0)
        self.say("so it says the BIGGEST digit first", 2, GOLD)

        # five pieces per row so the two digits that matter can turn gold
        def row(tail, lead, rest, y):
            g = VGroup(txt("317 × 31", 30), txt(tail, 30), txt("=", 30),
                       txt(lead, 30), txt(rest, 30)).arrange(RIGHT, buff=0.10)
            if g.get_width() > 4.4:
                g.set_width(4.4)
            return g.move_to(np.array([0, y, 0]))

        l1 = row("5", "9", "9,855", 0.55)
        self.play(FadeIn(l1), run_time=self.T(2))
        l2 = row("6", "1", "00,172", -0.15)
        self.play(FadeIn(l2), run_time=self.T(2))
        self.stage += [l1, l2]

        self.play(*[l[i].animate.set_color(GOLD) for l in (l1, l2) for i in (1, 3)],
                  run_time=self.T(1))
        self.say("change the LAST digit going in", 2, GOLD)
        self.say("and the FIRST digit coming out flips", 2.5, GOLD)

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
            wdt = max(3.0 * pct / 100.0, 0.02)
            bar = Rectangle(width=wdt, height=0.26, stroke_width=0)
            bar.set_fill(GOLD if pct > 20 else COOL, opacity=0.9)
            bar.move_to(np.array([-0.95 + wdt / 2, y, 0]))
            val = txt(f"{pct}%", 24, WHITE_ if pct else GREY, w=0.9)
            val.move_to(np.array([1.95, y, 0]))
            r = VGroup(name, bar, val)
            self.play(FadeIn(r, shift=0.1 * RIGHT), run_time=self.T(1.5),
                      rate_func=rush_from)
            rows.add(r)
        self.stage.append(rows)
        src = txt("Goat, arXiv:2305.14201", 17, GREY, bold=False, w=3.0)
        src.move_to(np.array([0, -1.18, 0]))
        self.play(FadeIn(src), run_time=self.T(1))
        self.stage.append(src)
        self.say("five digits: zero out of a hundred", 2, GOLD)
        self.pad_to(END_AI)

    # ==================================================================
    # 3 — SIDE BY SIDE.  A real table, one row at a time.
    # ==================================================================
    def part3_compare(self):
        hL = txt("CALCULATOR", 22, WHITE_, w=2.0)
        hL.move_to(np.array([-1.20, 1.55, 0]))
        hR = txt("AI", 22, GOLD, w=2.0)
        hR.move_to(np.array([1.20, 1.55, 0]))
        div = seg(np.array([0, 1.30, 0]), np.array([0, -1.45, 0]), FAINT, 2.2)
        line = seg(np.array([-2.2, 1.28, 0]), np.array([2.2, 1.28, 0]), FAINT, 2.2)
        self.play(FadeIn(hL), FadeIn(hR), ShowCreation(div), ShowCreation(line),
                  run_time=self.T(2))
        self.stage += [hL, hR, div, line]

        for i, (left, right) in enumerate(COMPARE):
            y = 0.85 - i * 0.62
            a = txt(left, 20, WHITE_, bold=False, w=2.0)
            a.move_to(np.array([-1.20, y, 0]))
            b = txt(right, 20, GOLD, bold=False, w=2.0)
            b.move_to(np.array([1.20, y, 0]))
            self.play(FadeIn(a, shift=0.08 * RIGHT), FadeIn(b, shift=0.08 * LEFT),
                      run_time=self.T(2), rate_func=rush_from)
            self.stage += [a, b]
        self.pad_to(END_CMP)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        self.clear_stage(1)
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(END_TAKE)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.title),
                  FadeOut(self.marker), run_time=self.T(1))

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
