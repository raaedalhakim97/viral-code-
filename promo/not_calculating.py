"""
not_calculating — "It isn't calculating. It's predicting."

The thesis of the submitted 1+1=3 script, with the mechanism corrected.

WHAT CHANGED AND WHY. The original said an AI might answer 1+1=3 because it saw
enough jokes and typos in training where "1 + 1 =" was followed by "3". That is
not true and not why models fail at maths:

  - No frontier model answers 1+1 wrongly. Building a video on a failure that
    does not happen invites the top comment to be a correction, which is the one
    thing a channel trading on credibility cannot afford.
  - The actual causes are architectural, not anecdotal. Tokenizers split numbers
    by *language* frequency rather than digit structure, so the model often
    never sees "347" as a quantity at all. And a transformer is fixed depth — it
    cannot run an unbounded carry loop, so it pattern-matches the shape of an
    answer instead of computing one.

So the hook survives as a SUBVERSION: show 1+1=3, then say no AI says this, and
pivot to a failure that is real, sourced and reproducible on the viewer's own
phone. Expecting the cliché and not getting it is a better hook than the cliché.

Sourced numbers on screen:
  59% -> 4%   GPT-4, 3-digit vs 4-digit multiplication; cross-digit
              interactions scale O(n^2)
  tokenizers split numbers by language frequency, not digit structure
  counting remains a fundamental failure even for reasoning models

~70s, narrated by Alan via narrate_scene.py — a silent video forfeits the
transcript, which is TikTok's strongest text signal.

manimgl traps, all silent failures:
    Text   -> fill_color= (color= and base_color= are both ignored)
    Circle -> stroke_color=
    Dot    -> fill_color=
    ShowCreation(make_thing()) leaves an orphan copy; draw it, remove it, then
    add the always_redraw version.
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
HEAD_Y   = 2.55


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


class NotCalculating(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)

        if os.environ.get("SAFE"):
            for y in (SAFE_TOP, SAFE_BOT):
                self.add(seg(np.array([-3, y, 0]), np.array([3, y, 0]),
                             "#FF00AA", 2))

        self.beat_hook()
        self.beat_cliff()
        self.beat_tokens()
        self.beat_depth()
        self.beat_payoff()
        self.beat_close()

    # ------------------------------------------------------------------
    # 0-9s  THE SUBVERSION. Show the cliché, then take it away.
    # ------------------------------------------------------------------
    def beat_hook(self):
        eq = txt("1 + 1 = 3", 74)
        eq.move_to(np.array([0, 0.9, 0]))
        self.play(FadeIn(eq, scale=1.12), run_time=0.45, rate_func=rush_from)
        self.wait(0.75)

        strike = seg(np.array([-eq.get_width() / 2 - 0.15, 0.9, 0]),
                     np.array([eq.get_width() / 2 + 0.15, 0.9, 0]), GOLD, 5)
        no = txt("No AI says this.", 32)
        no.move_to(np.array([0, -0.55, 0]))
        self.play(ShowCreation(strike), run_time=0.3, rate_func=rush_into)
        self.play(FadeIn(no, shift=0.14 * UP), run_time=0.3)
        self.wait(0.9)

        worse = txt("What it does get wrong", 27, GREY)
        worse2 = txt("is stranger.", 27, GREY)
        VGroup(worse, worse2).arrange(DOWN, buff=0.14) \
            .move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(worse), FadeIn(worse2), run_time=0.35)
        self.wait(1.0)
        self.play(*[FadeOut(m) for m in (eq, strike, no, worse, worse2)],
                  run_time=0.35)

    # ------------------------------------------------------------------
    # 9-26s  THE CLIFF. One extra digit and it falls off a wall.
    # ------------------------------------------------------------------
    def beat_cliff(self):
        head = txt("Ask GPT-4 to multiply", 26, GREY)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.35)

        base_y = -0.95
        bw = 1.25

        def bar(x, frac, color, op):
            h = 3.0 * frac
            r = Rectangle(width=bw, height=h, stroke_width=0)
            r.set_fill(color, opacity=op)
            r.move_to(np.array([x, base_y + h / 2, 0]))
            return r

        b1 = bar(-0.95, 0.59, WHITE_, 0.75)
        l1 = txt("3 digits", 24, GREY, bold=False)
        l1.move_to(np.array([-0.95, base_y - 0.34, 0]))
        v1 = txt("59%", 34)
        v1.move_to(np.array([-0.95, base_y + 3.0 * 0.59 + 0.36, 0]))

        self.play(FadeIn(b1, shift=0.25 * UP), FadeIn(l1),
                  run_time=0.55, rate_func=rush_from)
        self.play(FadeIn(v1), run_time=0.3)
        self.wait(1.4)

        add = txt("add one digit", 26)
        add.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(add), run_time=0.4)
        self.wait(0.7)

        b2 = bar(0.95, 0.04, GOLD, 0.85)
        l2 = txt("4 digits", 24, GREY, bold=False)
        l2.move_to(np.array([0.95, base_y - 0.34, 0]))
        v2 = txt("4%", 40, GOLD)
        v2.move_to(np.array([0.95, base_y + 3.0 * 0.04 + 0.42, 0]))
        self.play(FadeIn(b2, shift=0.2 * UP), FadeIn(l2),
                  run_time=0.5, rate_func=rush_from)
        self.play(FadeIn(v2, scale=1.2), run_time=0.35, rate_func=rush_from)
        self.wait(1.8)

        self.play(FadeOut(add), run_time=0.25)
        why = txt("Nothing about the maths got harder.", 24, GREY, bold=False)
        why.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(why), run_time=0.35)
        self.wait(1.6)
        self.play(*[FadeOut(m) for m in (head, b1, l1, v1, b2, l2, v2, why)],
                  run_time=0.4)

    # ------------------------------------------------------------------
    # 26-42s  REASON ONE. It never sees the number.
    # ------------------------------------------------------------------
    def beat_tokens(self):
        head = txt("It never sees the number.", 28)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        # a human reads one quantity
        human = txt("4827", 62)
        human.move_to(np.array([0, 1.15, 0]))
        hl = txt("what you see", 23, GREY, bold=False)
        hl.move_to(np.array([0, 0.35, 0]))
        self.play(FadeIn(human, scale=1.1), FadeIn(hl), run_time=0.5,
                  rate_func=rush_from)
        self.wait(1.2)

        # the tokenizer splits it where language frequency says, not where
        # place value says
        chunks = ["48", "27"]
        boxes = VGroup()
        for i, c in enumerate(chunks):
            t = txt(c, 44)
            box = Rectangle(width=t.get_width() + 0.42, height=1.0,
                            stroke_width=2.2)
            box.set_stroke(GREY, opacity=0.8)
            g = VGroup(box, t)
            g.move_to(np.array([-0.85 + i * 1.7, -1.05, 0]))
            boxes.add(g)
        tl = txt("what the model gets", 23, GREY, bold=False)
        tl.move_to(np.array([0, -1.95, 0]))

        arrow = seg(np.array([0, 0.05, 0]), np.array([0, -0.45, 0]), FAINT, 2.4)
        self.play(ShowCreation(arrow), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in boxes],
                              lag_ratio=0.14), FadeIn(tl),
                  run_time=0.7, rate_func=rush_from)
        self.wait(1.9)

        pt = txt("Tokenizers split numbers by", 23, GREY, bold=False)
        pt2 = txt("language, not by place value.", 23, GREY, bold=False)
        VGroup(pt, pt2).arrange(DOWN, buff=0.12) \
            .move_to(np.array([0, -2.75, 0]))
        self.play(FadeIn(pt), FadeIn(pt2), run_time=0.4)
        self.wait(2.0)
        self.play(*[FadeOut(m) for m in (head, human, hl, arrow, boxes, tl,
                                         pt, pt2)], run_time=0.4)

    # ------------------------------------------------------------------
    # 42-56s  REASON TWO. It cannot loop.
    # ------------------------------------------------------------------
    def beat_depth(self):
        head = txt("And it can't carry.", 28)
        head.move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=0.4)

        # you: a loop that runs as long as it needs
        y0 = 1.25
        loop = VGroup()
        R = 0.62
        pts = [np.array([R * np.cos(a), y0 + R * np.sin(a), 0])
               for a in np.linspace(0.5, TAU + 0.2, 40)]
        arc = VMobject(stroke_color=WHITE_, stroke_width=3.2)
        arc.set_points_as_corners(pts)
        loop.add(arc)
        yl = txt("you: repeat until done", 23, GREY, bold=False)
        yl.move_to(np.array([0, y0 - 1.05, 0]))
        self.play(ShowCreation(arc), FadeIn(yl), run_time=0.8,
                  rate_func=rush_from)
        self.wait(1.2)

        # the model: a fixed stack of layers, however hard the sum is
        layers = VGroup()
        for i in range(5):
            r = Rectangle(width=2.7, height=0.20, stroke_width=0)
            r.set_fill(WHITE_, opacity=0.30 + 0.06 * i)
            r.move_to(np.array([0, -0.85 - i * 0.30, 0]))
            layers.add(r)
        ml = txt("the model: the same fixed stack, every time", 22, GREY,
                 bold=False)
        ml.move_to(np.array([0, -2.55, 0]))
        self.play(LaggedStart(*[FadeIn(r, shift=0.12 * UP) for r in layers],
                              lag_ratio=0.1), FadeIn(ml),
                  run_time=0.9, rate_func=rush_from)
        self.wait(2.4)
        self.play(*[FadeOut(m) for m in (head, arc, yl, layers, ml)],
                  run_time=0.4)

    # ------------------------------------------------------------------
    # 56-64s  THE PAYOFF
    # ------------------------------------------------------------------
    def beat_payoff(self):
        a = txt("So it doesn't compute the answer.", 27, GREY)
        b = txt("It predicts what an answer", 30)
        c = txt("would look like.", 30, GOLD)
        g = VGroup(a, b, c).arrange(DOWN, buff=0.26)
        g.move_to(np.array([0, 0.6, 0]))
        for m in g:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=0.4)
        self.wait(1.6)

        test = txt("Try it. Four digits. Watch it fold.", 24, GREY, bold=False)
        test.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(test), run_time=0.4)
        self.wait(1.6)
        self.play(FadeOut(g), FadeOut(test), run_time=0.45)

    # ------------------------------------------------------------------
    def beat_close(self):
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.3, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=1.3)

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
        self.wait(1.8)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=0.8)


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
