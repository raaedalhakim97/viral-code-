"""
illusion_of_logic — the long-form cut. 91 seconds.

This exists to answer a question the short videos cannot: does this audience
watch long-form at all? It is an experiment, and it is built so the result means
something — see LONG_FORM_TEST.md for what to measure.

Renders at 1080x1920, not 1440x2560. That is TikTok's native resolution, so
nothing is lost, and it roughly halves the grade pass on a 5,478-frame piece.

91s is deliberate and is NOT a compromised five minutes. The question this
experiment answers is "does this audience stay past a minute" — and if they do
not, a five-minute cut would have told you the same thing for four times the
render. Extend it only after the retention curve says people are still there
at 0:60.

    RES=1080x1920 manimgl illusion_of_logic.py IllusionOfLogic -w -r 1080x1920

RETENTION DEVICES, because five minutes of line art is where boredom lives:
  - a segmented progress bar and a chapter number, always on screen, so a
    viewer can see how much is left rather than guessing
  - an open loop planted in the first twenty seconds and not closed until the
    end
  - the strongest visual — the 59% to 4% cliff — placed early, not saved
  - the same cut discipline as the short pieces: nothing holds past ~2s

Sourced numbers:
  59% -> 4%   GPT-4, 3-digit vs 4-digit multiplication; cross-digit
              interactions scale O(n^2)
  tokenizers split numbers by language frequency, not digit structure
  counting is a fundamental failure even for reasoning models
  fixed depth: a transformer runs the same layer stack whatever the input

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    ShowCreation(make_thing()) leaves an orphan; draw, remove, then add the
    always_redraw version.
"""
import os

from manimlib import *
import numpy as np

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FRAME_H  = 9.0
SAFE_TOP = FRAME_H / 2 - 0.12 * FRAME_H
SAFE_BOT = -FRAME_H / 2 + 0.22 * FRAME_H
LINE_Y   = -2.00
HEAD_Y   = 2.30
BAR_Y    = 3.20

CHAPTERS = 7


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


def poly(pts, color=WHITE_, w=2.4, op=1.0, close=True):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners(list(pts) + ([pts[0]] if close else []))
    m.set_stroke(opacity=op)
    return m


class IllusionOfLogic(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.hud = None

        self.ch0_open()
        self.ch1_cliff()
        self.ch2_how_you_do_it()
        self.ch3_what_it_sees()
        self.ch4_proximity()
        self.ch5_fixed_stack()
        self.ch6_distribution()
        self.ch7_payoff()

    # ------------------------------------------------------------------
    # Progress HUD. Swapped instantly at chapter boundaries so it costs no
    # time — a viewer who can see how much is left is a viewer who stays.
    # ------------------------------------------------------------------
    def set_chapter(self, n, title):
        if self.hud is not None:
            self.remove(self.hud)
        g = VGroup()
        w, gap = 0.46, 0.10
        total = CHAPTERS * w + (CHAPTERS - 1) * gap
        for i in range(CHAPTERS):
            r = Rectangle(width=w, height=0.055, stroke_width=0)
            done = i < n
            r.set_fill(GOLD if i == n - 1 else WHITE_,
                       opacity=0.85 if done else 0.14)
            r.move_to(np.array([-total / 2 + w / 2 + i * (w + gap), BAR_Y, 0]))
            g.add(r)
        lab = txt(f"{n} / {CHAPTERS}   {title}", 19, GREY, bold=False, w=4.2)
        lab.move_to(np.array([0, BAR_Y - 0.34, 0]))
        g.add(lab)
        self.hud = g
        self.add(g)

    def clear_all(self, *mobs):
        self.remove(*[m for m in mobs if m is not None])

    # ==================================================================
    # 0:00 - 0:22   THE OPEN. Subvert the cliché, then plant the question.
    # ==================================================================
    def ch0_open(self):
        self.set_chapter(1, "the claim")
        eq = txt("1 + 1 = 3", 74).move_to(np.array([0, 0.9, 0]))
        self.play(FadeIn(eq, scale=1.12), run_time=0.5, rate_func=rush_from)
        self.wait(0.9)

        strike = seg(np.array([-eq.get_width() / 2 - 0.15, 0.9, 0]),
                     np.array([eq.get_width() / 2 + 0.15, 0.9, 0]), GOLD, 5)
        no = txt("No AI says this.", 32).move_to(np.array([0, -0.5, 0]))
        self.play(ShowCreation(strike), run_time=0.3, rate_func=rush_into)
        self.play(FadeIn(no, shift=0.14 * UP), run_time=0.3)
        self.wait(1.2)
        self.clear_all(eq, strike, no)

        # the open loop — asked now, answered at the end
        q1 = txt("But ask it to multiply", 30)
        q2 = txt("two four-digit numbers", 30)
        q3 = txt("and it fails 96% of the time.", 30, GOLD)
        g = VGroup(q1, q2, q3).arrange(DOWN, buff=0.22)
        g.move_to(np.array([0, 0.6, 0]))
        for m in g:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=0.4)
        self.wait(1.4)

        why = txt("Not because it is bad at maths.", 25, GREY, bold=False)
        why.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(why), run_time=0.4)
        self.wait(1.6)
        why2 = txt("Because it is not doing maths.", 26)
        why2.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(why), run_time=0.25)
        self.play(FadeIn(why2), run_time=0.35)
        self.wait(1.8)
        self.clear_all(g, why2)

    # ==================================================================
    # 0:22 - 1:00   THE CLIFF. Strongest visual, placed early.
    # ==================================================================
    def ch1_cliff(self):
        self.set_chapter(2, "the cliff")
        head = txt("Ask GPT-4 to multiply", 26, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        base_y = -1.05
        bw = 1.25

        def bar(x, frac, color, op):
            h = 2.9 * frac
            r = Rectangle(width=bw, height=h, stroke_width=0)
            r.set_fill(color, opacity=op)
            r.move_to(np.array([x, base_y + h / 2, 0]))
            return r

        b1 = bar(-0.95, 0.59, WHITE_, 0.75)
        l1 = txt("3 digits", 24, GREY, bold=False)
        l1.move_to(np.array([-0.95, base_y - 0.34, 0]))
        v1 = txt("59%", 34).move_to(np.array([-0.95, base_y + 2.9 * 0.59 + 0.36, 0]))
        self.play(FadeIn(b1, shift=0.25 * UP), FadeIn(l1), run_time=0.6,
                  rate_func=rush_from)
        self.play(FadeIn(v1), run_time=0.3)
        self.wait(1.6)

        add = txt("add one digit", 26).move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(add), run_time=0.4)
        self.wait(1.0)

        b2 = bar(0.95, 0.04, GOLD, 0.85)
        l2 = txt("4 digits", 24, GREY, bold=False)
        l2.move_to(np.array([0.95, base_y - 0.34, 0]))
        v2 = txt("4%", 40, GOLD).move_to(np.array([0.95, base_y + 2.9 * 0.04 + 0.42, 0]))
        self.play(FadeIn(b2, shift=0.2 * UP), FadeIn(l2), run_time=0.5,
                  rate_func=rush_from)
        self.play(FadeIn(v2, scale=1.2), run_time=0.35, rate_func=rush_from)
        self.wait(2.0)

        self.play(FadeOut(add), run_time=0.25)
        for line in ("Nothing about the arithmetic got harder.",
                     "One more digit. Fifteen times worse."):
            t = txt(line, 24, GREY, bold=False).move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=0.35)
            self.wait(1.7)
            self.play(FadeOut(t), run_time=0.25)
        self.clear_all(head, b1, l1, v1, b2, l2, v2)

    # ==================================================================
    # 1:00 - 1:40   HOW YOU DO IT. A loop that runs as long as it needs.
    # ==================================================================
    def ch2_how_you_do_it(self):
        self.set_chapter(3, "how you do it")
        head = txt("You have an algorithm.", 28)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        # long multiplication, laid out the way it is taught
        rows = ["4 8 2 7", "×  3 6", "———————", "2 8 9 6 2", "1 4 4 8 1 ", "———————"]
        ys = [1.55, 1.05, 0.72, 0.22, -0.28, -0.62]
        mobs = []
        for r, y in zip(rows, ys):
            t = txt(r, 30, WHITE_ if "—" not in r else FAINT, bold=True, w=3.6)
            t.move_to(np.array([0.25, y, 0]))
            mobs.append(t)
            self.play(FadeIn(t, shift=0.1 * UP), run_time=0.35,
                      rate_func=rush_from)
        self.wait(0.8)

        carry = txt("carry, shift, carry, shift", 24, GOLD)
        carry.move_to(np.array([0, -1.35, 0]))
        self.play(FadeIn(carry), run_time=0.4)
        self.wait(1.4)

        pt = txt("The steps depend on the number.", 25, GREY, bold=False)
        pt.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(pt), run_time=0.4)
        self.wait(1.6)
        pt2 = txt("Bigger number, more steps. You just keep going.", 23,
                  GREY, bold=False)
        pt2.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(pt), run_time=0.25)
        self.play(FadeIn(pt2), run_time=0.35)
        self.wait(2.0)
        self.clear_all(head, carry, pt2, *mobs)

    # ==================================================================
    # 1:40 - 2:25   WHAT IT SEES. The number never arrives intact.
    # ==================================================================
    def ch3_what_it_sees(self):
        self.set_chapter(4, "what it sees")
        head = txt("It never sees the number.", 28)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        human = txt("4827", 60).move_to(np.array([0, 1.25, 0]))
        hl = txt("one quantity", 23, GREY, bold=False)
        hl.move_to(np.array([0, 0.5, 0]))
        self.play(FadeIn(human, scale=1.1), FadeIn(hl), run_time=0.5,
                  rate_func=rush_from)
        self.wait(1.3)

        arrow = seg(np.array([0, 0.18, 0]), np.array([0, -0.3, 0]), FAINT, 2.4)
        self.play(ShowCreation(arrow), run_time=0.3)

        boxes = VGroup()
        for i, c in enumerate(["48", "27"]):
            t = txt(c, 42)
            box = Rectangle(width=t.get_width() + 0.42, height=1.0,
                            stroke_width=2.2)
            box.set_stroke(GREY, opacity=0.8)
            g = VGroup(box, t).move_to(np.array([-0.85 + i * 1.7, -0.92, 0]))
            boxes.add(g)
        tl = txt("two symbols", 23, GREY, bold=False)
        tl.move_to(np.array([0, -1.72, 0]))
        self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in boxes],
                              lag_ratio=0.14), FadeIn(tl),
                  run_time=0.7, rate_func=rush_from)
        self.wait(1.8)

        for line in ("Tokenizers split numbers where language is common,",
                     "not where place value is.",
                     "The 8 in 4827 is worth 800. The model is not told that."):
            t = txt(line, 23, GREY, bold=False, w=4.2)
            t.move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=0.35)
            self.wait(1.7)
            self.play(FadeOut(t), run_time=0.25)
        self.clear_all(head, human, hl, arrow, boxes, tl)

    # ==================================================================
    # 2:25 - 3:10   PROXIMITY. Meaning by neighbourhood, not by rule.
    # ==================================================================
    def ch4_proximity(self):
        self.set_chapter(5, "meaning by proximity")
        head = txt("Meaning is a neighbourhood.", 28)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        pts = {
            "king":  np.array([-1.15, 1.15, 0]),
            "queen": np.array([-0.35, 1.45, 0]),
            "man":   np.array([-1.35, 0.25, 0]),
            "woman": np.array([-0.55, 0.55, 0]),
            "seven": np.array([1.15, -0.55, 0]),
            "eight": np.array([1.55, -0.15, 0]),
        }
        dots, labs = VGroup(), VGroup()
        for name, p in pts.items():
            d = Dot(p, radius=0.075, fill_color=WHITE_)
            l = txt(name, 20, GREY, bold=False)
            l.move_to(p + np.array([0, 0.32, 0]))
            dots.add(d)
            labs.add(l)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.07), FadeIn(labs),
                  run_time=0.9, rate_func=rush_from)
        self.wait(1.0)

        # the analogy their own pinned video already uses
        a1 = seg(pts["man"], pts["king"], GOLD, 2.6, 0.9)
        a2 = seg(pts["woman"], pts["queen"], GOLD, 2.6, 0.9)
        self.play(ShowCreation(a1), ShowCreation(a2), run_time=0.7)
        same = txt("the same step, twice", 24, GOLD)
        same.move_to(np.array([0, -1.45, 0]))
        self.play(FadeIn(same), run_time=0.4)
        self.wait(1.8)

        for line in ("Words that appear in the same places sit close together.",
                     "That is what the model learns. Not rules — neighbours.",
                     "It works beautifully for language."):
            t = txt(line, 23, GREY, bold=False, w=4.2)
            t.move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=0.35)
            self.wait(1.6)
            self.play(FadeOut(t), run_time=0.25)

        bad = txt("Numbers do not have neighbours.", 26)
        bad.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(bad), run_time=0.4)
        self.wait(1.8)
        self.clear_all(head, dots, labs, a1, a2, same, bad)

    # ==================================================================
    # 3:10 - 3:50   THE FIXED STACK. It cannot think longer.
    # ==================================================================
    def ch5_fixed_stack(self):
        self.set_chapter(6, "it cannot think longer")
        head = txt("And it can't carry.", 28)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        y0 = 1.15
        R = 0.6
        arc = VMobject(stroke_color=WHITE_, stroke_width=3.2)
        arc.set_points_as_corners([np.array([R * np.cos(a), y0 + R * np.sin(a), 0])
                                   for a in np.linspace(0.5, TAU + 0.2, 40)])
        yl = txt("you: repeat until done", 23, GREY, bold=False)
        yl.move_to(np.array([0, y0 - 1.0, 0]))
        self.play(ShowCreation(arc), FadeIn(yl), run_time=0.8, rate_func=rush_from)
        self.wait(1.4)

        layers = VGroup()
        for i in range(6):
            r = Rectangle(width=2.7, height=0.19, stroke_width=0)
            r.set_fill(WHITE_, opacity=0.28 + 0.06 * i)
            r.move_to(np.array([0, -0.72 - i * 0.28, 0]))
            layers.add(r)
        ml = txt("it: the same stack, every time", 23, GREY, bold=False)
        ml.move_to(np.array([0, -2.45, 0]))
        self.play(LaggedStart(*[FadeIn(r, shift=0.12 * UP) for r in layers],
                              lag_ratio=0.1), FadeIn(ml),
                  run_time=0.9, rate_func=rush_from)
        self.wait(1.8)

        for line in ("Two plus two gets the same amount of thinking",
                     "as four thousand times six thousand."):
            t = txt(line, 24, GREY, bold=False, w=4.2)
            t.move_to(np.array([0, LINE_Y + 0.62, 0]))
            self.play(FadeIn(t), run_time=0.35)
            self.wait(1.7)
            self.play(FadeOut(t), run_time=0.25)
        self.clear_all(head, arc, yl, layers, ml)

    # ==================================================================
    # 3:50 - 4:25   THE DISTRIBUTION. It ranks, it does not compute.
    # ==================================================================
    def ch6_distribution(self):
        self.set_chapter(7, "it ranks, it doesn't compute")
        head = txt("So what does it actually do?", 27)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        prompt = txt("4827 × 36 =", 34, GREY)
        prompt.move_to(np.array([0, 1.35, 0]))
        self.play(FadeIn(prompt), run_time=0.4)
        self.wait(0.9)

        cands = [("173772", 0.41), ("173,772", 0.22), ("172872", 0.14),
                 ("173782", 0.09), ("something else", 0.14)]
        rows = VGroup()
        for i, (label, p) in enumerate(cands):
            y = 0.45 - i * 0.52
            l = txt(label, 23, WHITE_ if i == 0 else GREY, bold=(i == 0))
            l.move_to(np.array([-1.35, y, 0]))
            b = Rectangle(width=max(p * 4.4, 0.06), height=0.24, stroke_width=0)
            b.set_fill(GOLD if i == 0 else WHITE_, opacity=0.8 if i == 0 else 0.35)
            b.move_to(np.array([0.35 + max(p * 4.4, 0.06) / 2, y, 0]))
            rows.add(VGroup(l, b))
        self.play(LaggedStart(*[FadeIn(r, shift=0.12 * RIGHT) for r in rows],
                              lag_ratio=0.1), run_time=1.0, rate_func=rush_from)
        self.wait(2.0)

        for line in ("It ranks what an answer would look like.",
                     "Then it picks the top one.",
                     "It never multiplied anything."):
            t = txt(line, 25, GREY if line[0] != "I" or "never" not in line
                    else WHITE_, bold=False, w=4.2)
            t.move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=0.35)
            self.wait(1.7)
            self.play(FadeOut(t), run_time=0.25)
        self.clear_all(head, prompt, rows)

    # ==================================================================
    # 4:25 - 4:50   PAYOFF. Close the loop opened at 0:15.
    # ==================================================================
    def ch7_payoff(self):
        a = txt("Our intelligence looks for truth", 26, GREY)
        b = txt("by following rules.", 26, GREY)
        c = txt("Its intelligence looks for", 27)
        d = txt("what usually comes next.", 28, GOLD)
        g = VGroup(a, b, c, d).arrange(DOWN, buff=0.22)
        g.move_to(np.array([0, 0.75, 0]))
        for m in g:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=0.4)
        self.wait(2.2)

        test = txt("Try it. Four digits. Watch it fold.", 24, GREY, bold=False)
        test.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(test), run_time=0.4)
        self.wait(1.8)
        self.play(FadeOut(g), FadeOut(test), run_time=0.5)
        if self.hud is not None:
            self.remove(self.hud)

        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.3, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=1.4)
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=0.5)

        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=0.5)
        self.wait(2.2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=0.9)


# ===========================================================================
def observer_eye(color):
    grp = VGroup()
    up = VMobject(color=color, stroke_width=2.2)
    up.set_points_smoothly([np.array([x, 0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
                            for x in np.linspace(-1.6, 1.6, 20)])
    dn = VMobject(color=color, stroke_width=2.2)
    dn.set_points_smoothly([np.array([x, -0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
                            for x in np.linspace(-1.6, 1.6, 20)])
    grp.add(up, dn)
    pupil = Circle(radius=0.42, stroke_color=color, stroke_width=2.2).move_to(ORIGIN)
    pupil_fill = Dot(ORIGIN, radius=0.12, fill_color=color)
    grp.add(pupil, pupil_fill)
    rng = np.random.default_rng(2)
    for _ in range(5):
        s = rng.uniform(0.05, 0.12)
        sq = Square(side_length=s, color=color, stroke_width=1.5)
        sq.move_to([rng.uniform(1.7, 2.4), rng.uniform(-0.6, 0.6), 0])
        sq.set_fill(color, opacity=0.5)
        grp.add(sq)
    return grp
