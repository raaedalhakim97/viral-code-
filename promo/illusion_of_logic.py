"""
illusion_of_logic — the long-form cut, silent and beat-locked. 89.6s.

REBUILT WITHOUT NARRATION. The first version carried a TTS read and it sounded
like one. Every Piper tier reachable from this container is 16-22kHz and flat;
the good British voice lives on HuggingFace, which the egress policy blocks. So
the voice is gone and the argument is carried the way this channel is actually
good at carrying things — construction, not commentary.

WHAT THAT COSTS, stated plainly: TikTok transcribes audio and indexes the
transcript, so a silent video gives up the platform's strongest text signal.
Two things have to make up for it, and both are done here:
  - every searchable term is ON SCREEN as text: tokenizer, place value,
    attention, transformer, probability
  - the caption carries the rest (see LONG_FORM_TEST.md)

BEAT-LOCKED so a track can go under it in the TikTok editor:
  7 chapters x 32 beats = 224 beats = 56 bars = 89.600s at 150 BPM.
  pad_to() enforces each chapter, so every one ends on a bar line and a
  re-render at another tempo stays locked.

THE EQUATIONS DANCE. A kick derived from one clock drives a scale pulse on
every equation and a breath on the geometry, so the frame is never static even
while a viewer is reading. That is the difference between cinematic and a
slideshow.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats); a raw n*B misses the frame grid
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
CHAPTERS = 7
CH_BEATS = 32

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FRAME_H = 9.0
LINE_Y  = -2.05
HEAD_Y  = 2.35
BAR_Y   = 3.22
PLOT_C  = np.array([0.0, 0.35, 0.0])
PLOT_W, PLOT_H = 4.05, 3.0


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


def P(x, y):
    return PLOT_C + np.array([(x - 0.5) * PLOT_W, (y - 0.5) * PLOT_H, 0.0])


class IllusionOfLogic(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.hud = None

        # One clock. The kick, the breath and every pulse read off it, which is
        # what keeps them locked to each other and to the track.
        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        # Each chapter calls self.finish(n, ...) itself. Padding from out here
        # would hold on a black frame, because the chapter has already cleared
        # its visuals by the time it returns — chapter 1 sat on 8 beats of
        # nothing, chapter 6 on 11.
        for fn in (self.ch1_claim, self.ch2_cliff, self.ch3_algorithm,
                   self.ch4_tokens, self.ch5_proximity, self.ch6_stack,
                   self.ch7_rank):
            fn()

    # ------------------------------------------------------------------
    def T(self, beats):
        self.used += beats
        return round(beats * self.B * FPS) / FPS

    def pad_to(self, target):
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(f"chapter overruns by {-rem:.2f} beats — trim it")
        if rem > 0.01:
            self.wait(self.T(rem))

    def finish(self, n, *mobs):
        """Hold the last visual until the chapter's bar line, THEN clear."""
        self.pad_to(n * CH_BEATS)
        self.drop(*mobs)

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.055):
        """Make a mobject breathe on the beat. This is the 'dancing' — the
        frame is never dead even while someone is reading it."""
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def still(self, *mobs):
        for m in mobs:
            if m is not None:
                m.clear_updaters()

    def drop(self, *mobs):
        self.still(*mobs)
        self.remove(*[m for m in mobs if m is not None])

    def chapter(self, n, title):
        if self.hud is not None:
            self.remove(self.hud)
        g = VGroup()
        w, gap = 0.46, 0.10
        total = CHAPTERS * w + (CHAPTERS - 1) * gap
        for i in range(CHAPTERS):
            r = Rectangle(width=w, height=0.055, stroke_width=0)
            r.set_fill(GOLD if i == n - 1 else WHITE_,
                       opacity=0.85 if i < n else 0.14)
            r.move_to(np.array([-total / 2 + w / 2 + i * (w + gap), BAR_Y, 0]))
            g.add(r)
        lab = txt(f"{n} / {CHAPTERS}   {title}", 19, GREY, bold=False, w=4.2)
        lab.move_to(np.array([0, BAR_Y - 0.33, 0]))
        g.add(lab)
        self.hud = g
        self.add(g)

    # ==================================================================
    # 1 — THE CLAIM
    # ==================================================================
    def ch1_claim(self):
        self.chapter(1, "the claim")
        eq = self.dance(txt("1 + 1 = 3", 74).move_to(np.array([0, 0.95, 0])), 0.07)
        self.play(FadeIn(eq, scale=1.14), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))

        strike = seg(np.array([-eq.get_width() / 2 - 0.2, 0.95, 0]),
                     np.array([eq.get_width() / 2 + 0.2, 0.95, 0]), GOLD, 5)
        self.play(ShowCreation(strike), run_time=self.T(1), rate_func=rush_into)
        no = txt("No AI says this.", 32).move_to(np.array([0, -0.6, 0]))
        self.play(FadeIn(no, shift=0.14 * UP), run_time=self.T(1))
        self.wait(self.T(3))
        self.drop(eq, strike, no)

        q = VGroup(txt("ask it to multiply", 29, GREY),
                   txt("two 4-digit numbers", 32),
                   txt("it fails 96% of the time", 30, GOLD)) \
            .arrange(DOWN, buff=0.24).move_to(np.array([0, 0.7, 0]))
        for m in q:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=self.T(1),
                      rate_func=rush_from)
        self.dance(q[2], 0.06)
        self.wait(self.T(4))

        because = txt("It is not bad at maths.", 25, GREY, bold=False)
        because.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(because), run_time=self.T(1))
        self.wait(self.T(3))
        b2 = txt("It is not doing maths.", 27).move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(because), FadeIn(b2), run_time=self.T(1))
        self.wait(self.T(4))
        self.finish(1, q, b2)

    # ==================================================================
    # 2 — THE CLIFF
    # ==================================================================
    def ch2_cliff(self):
        self.chapter(2, "the cliff")
        head = txt("GPT-4, multiplying", 26, GREY).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        base_y, bw = -1.15, 1.25

        def bar(x, frac, color, op):
            h = max(2.9 * frac, 0.05)
            r = Rectangle(width=bw, height=h, stroke_width=0)
            r.set_fill(color, opacity=op)
            r.move_to(np.array([x, base_y + h / 2, 0]))
            return r

        b1 = bar(-0.95, 0.59, WHITE_, 0.75)
        l1 = txt("3 digits", 24, GREY, bold=False)
        l1.move_to(np.array([-0.95, base_y - 0.36, 0]))
        v1 = self.dance(txt("59%", 36).move_to(
            np.array([-0.95, base_y + 2.9 * 0.59 + 0.4, 0])))
        self.play(FadeIn(b1, shift=0.3 * UP), FadeIn(l1),
                  run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(v1), run_time=self.T(1))
        self.wait(self.T(4))

        add = txt("add ONE digit", 27).move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(add), run_time=self.T(1))
        self.wait(self.T(2))

        b2 = bar(0.95, 0.04, GOLD, 0.9)
        l2 = txt("4 digits", 24, GREY, bold=False)
        l2.move_to(np.array([0.95, base_y - 0.36, 0]))
        v2 = self.dance(txt("4%", 42, GOLD).move_to(
            np.array([0.95, base_y + 0.44, 0])), 0.09)
        self.play(FadeIn(b2, shift=0.2 * UP), FadeIn(l2),
                  run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(v2, scale=1.25), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(5))

        self.play(FadeOut(add), run_time=self.T(1))
        note = txt("nothing about the arithmetic got harder", 23, GREY,
                   bold=False, w=4.2)
        note.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(note), run_time=self.T(1))
        self.wait(self.T(6))
        self.finish(2, head, b1, l1, v1, b2, l2, v2, note)

    # ==================================================================
    # 3 — HOW YOU DO IT.  Carries drawn as arcs, so it reads as a process.
    # ==================================================================
    def ch3_algorithm(self):
        self.chapter(3, "your algorithm")
        head = txt("you have an algorithm", 27).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        rows = ["4 8 2 7", "×    3 6", "2 8 9 6 2", "1 4 4 8 1", "1 7 3 7 7 2"]
        ys = [1.55, 1.02, 0.20, -0.32, -1.15]
        mobs = []
        for i, (r, y) in enumerate(zip(rows, ys)):
            t = txt(r, 32 if i < 4 else 34, GOLD if i == 4 else WHITE_, w=3.7)
            t.move_to(np.array([0.2, y, 0]))
            mobs.append(t)

        rule1 = seg(np.array([-1.5, 0.63, 0]), np.array([1.9, 0.63, 0]), FAINT, 2.2)
        rule2 = seg(np.array([-1.5, -0.72, 0]), np.array([1.9, -0.72, 0]), FAINT, 2.2)

        self.play(FadeIn(mobs[0], shift=0.1 * UP), run_time=self.T(1),
                  rate_func=rush_from)
        self.play(FadeIn(mobs[1], shift=0.1 * UP), ShowCreation(rule1),
                  run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(mobs[2], shift=0.1 * UP), run_time=self.T(1),
                  rate_func=rush_from)
        self.play(FadeIn(mobs[3], shift=0.1 * UP), ShowCreation(rule2),
                  run_time=self.T(1), rate_func=rush_from)

        # the carries, drawn as arcs hopping right to left
        arcs = VGroup()
        for i in range(4):
            x0 = 1.35 - i * 0.52
            pts = [np.array([x0 - 0.5 * (1 - np.cos(np.pi * u)) * 0.52,
                             2.02 + 0.24 * np.sin(np.pi * u), 0])
                   for u in np.linspace(0, 1, 18)]
            arcs.add(poly(pts, GOLD, 2.2, 0.85, close=False))
        self.play(LaggedStart(*[ShowCreation(a) for a in arcs], lag_ratio=0.2),
                  run_time=self.T(2), rate_func=rush_from)
        carry = txt("carry, shift, carry, shift", 24, GOLD)
        carry.move_to(np.array([0, LINE_Y + 0.6, 0]))
        self.play(FadeIn(carry), run_time=self.T(1))
        self.wait(self.T(2))

        self.play(FadeIn(mobs[4], scale=1.15), run_time=self.T(1),
                  rate_func=rush_from)
        self.dance(mobs[4], 0.06)
        self.wait(self.T(3))

        pt = txt("bigger number  →  more steps", 24, GREY, bold=False)
        pt.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(carry), FadeIn(pt), run_time=self.T(1))
        self.wait(self.T(5))
        self.finish(3, head, rule1, rule2, arcs, pt, *mobs)

    # ==================================================================
    # 4 — WHAT IT SEES.  Place value built, then destroyed.
    # ==================================================================
    def ch4_tokens(self):
        self.chapter(4, "what it sees")
        head = txt("it never sees the number", 27).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        digits = ["4", "8", "2", "7"]
        places = ["1000", "100", "10", "1"]
        cols = VGroup()
        for i, (d, p) in enumerate(zip(digits, places)):
            x = -1.35 + i * 0.9
            dt = txt(d, 46).move_to(np.array([x, 1.25, 0]))
            pl = txt(p, 20, GREY, bold=False).move_to(np.array([x, 0.55, 0]))
            tick = seg(np.array([x, 0.92, 0]), np.array([x, 0.78, 0]), FAINT, 2)
            cols.add(VGroup(dt, pl, tick))
        self.play(LaggedStart(*[FadeIn(c, shift=0.14 * UP) for c in cols],
                              lag_ratio=0.12), run_time=self.T(2),
                  rate_func=rush_from)
        pv = txt("place value", 23, GREY, bold=False)
        pv.move_to(np.array([0, 0.02, 0]))
        self.play(FadeIn(pv), run_time=self.T(1))
        self.wait(self.T(3))

        # the tokenizer cuts somewhere else entirely
        cut = seg(np.array([-0.0, 1.9, 0]), np.array([0.0, 0.3, 0]), GOLD, 3.4)
        self.play(ShowCreation(cut), run_time=self.T(1), rate_func=rush_into)
        self.wait(self.T(1))

        boxes = VGroup()
        for i, c in enumerate(["48", "27"]):
            t = txt(c, 40)
            bx = Rectangle(width=t.get_width() + 0.44, height=1.0, stroke_width=2.2)
            bx.set_stroke(GREY, opacity=0.85)
            boxes.add(VGroup(bx, t).move_to(np.array([-0.9 + i * 1.8, -1.15, 0])))
        arrow = seg(np.array([0, 0.2, 0]), np.array([0, -0.5, 0]), FAINT, 2.2)
        self.play(ShowCreation(arrow), run_time=self.T(1))
        self.play(LaggedStart(*[FadeIn(b, scale=0.72) for b in boxes],
                              lag_ratio=0.15), run_time=self.T(1),
                  rate_func=rush_from)
        for b in boxes:
            self.dance(b, 0.05)
        self.play(FadeOut(pv), FadeOut(cols), run_time=self.T(1))
        self.wait(self.T(2))

        for line, size in (("the tokenizer splits by language,", 23),
                           ("not by place value", 25)):
            t = txt(line, size, GREY if size == 23 else WHITE_,
                    bold=(size != 23), w=4.2)
            t.move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=self.T(1))
            self.wait(self.T(3))
            self.play(FadeOut(t), run_time=self.T(1))
        self.finish(4, head, cut, arrow, boxes)

    # ==================================================================
    # 5 — PROXIMITY.  The analogy as an actual parallelogram.
    # ==================================================================
    def ch5_proximity(self):
        self.chapter(5, "meaning by proximity")
        head = txt("what it learned instead", 27).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        pts = {"man": P(0.18, 0.22), "king": P(0.18, 0.72),
               "woman": P(0.62, 0.22), "queen": P(0.62, 0.72)}
        dots, labs = VGroup(), VGroup()
        for n, p in pts.items():
            dots.add(Dot(p, radius=0.075, fill_color=WHITE_))
            labs.add(txt(n, 20, GREY, bold=False).move_to(p + np.array([0, 0.3, 0])))
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.08), FadeIn(labs),
                  run_time=self.T(2), rate_func=rush_from)
        self.wait(self.T(2))

        a1 = seg(pts["man"], pts["king"], GOLD, 3.0)
        a2 = seg(pts["woman"], pts["queen"], GOLD, 3.0)
        self.play(ShowCreation(a1), run_time=self.T(1), rate_func=rush_from)
        self.play(ShowCreation(a2), run_time=self.T(1), rate_func=rush_from)
        same = txt("the same step, twice", 25, GOLD)
        same.move_to(np.array([0, LINE_Y + 0.55, 0]))
        self.play(FadeIn(same), run_time=self.T(1))
        self.dance(same, 0.05)
        self.wait(self.T(3))

        close = poly([pts["man"], pts["woman"], pts["queen"], pts["king"]],
                     FAINT, 2.0, 0.9)
        self.play(ShowCreation(close), run_time=self.T(1))
        self.wait(self.T(2))

        for line in ("meaning is a neighbourhood, not a rule",
                     "it works beautifully for language"):
            t = txt(line, 23, GREY, bold=False, w=4.2)
            t.move_to(np.array([0, LINE_Y, 0]))
            self.play(FadeIn(t), run_time=self.T(1))
            self.wait(self.T(2))
            self.play(FadeOut(t), run_time=self.T(1))

        bad = txt("numbers have no neighbours", 26)
        bad.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(bad), run_time=self.T(1))
        self.wait(self.T(4))
        self.finish(5, head, dots, labs, a1, a2, same, close, bad)

    # ==================================================================
    # 6 — THE FIXED STACK.  A spiral that can keep going, against a wall
    #     of layers that cannot.
    # ==================================================================
    def ch6_stack(self):
        self.chapter(6, "it cannot think longer")
        head = txt("and it cannot carry", 27).move_to(np.array([0, HEAD_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))

        # your loop: a spiral, drawn outward — it can always go one more turn
        pts, n = [], 150
        for i in range(n):
            u = i / (n - 1)
            a = u * TAU * 2.4
            r = 0.16 + u * 0.72
            pts.append(np.array([r * np.cos(a), 1.25 + r * np.sin(a), 0]))
        spiral = poly(pts, WHITE_, 3.0, close=False)
        self.play(ShowCreation(spiral), run_time=self.T(3), rate_func=smooth)
        yl = txt("you: one more step, as many as it takes", 22, GREY,
                 bold=False, w=4.2)
        yl.move_to(np.array([0, 0.05, 0]))
        self.play(FadeIn(yl), run_time=self.T(1))
        self.wait(self.T(3))

        layers = VGroup()
        for i in range(6):
            r = Rectangle(width=2.8, height=0.18, stroke_width=0)
            r.set_fill(WHITE_, opacity=0.26 + 0.07 * i)
            r.move_to(np.array([0, -0.55 - i * 0.27, 0]))
            layers.add(r)
        self.play(LaggedStart(*[FadeIn(r, shift=0.12 * UP) for r in layers],
                              lag_ratio=0.1), run_time=self.T(2),
                  rate_func=rush_from)
        ml = txt("it: the same stack, every time", 22, GREY, bold=False)
        ml.move_to(np.array([0, -2.42, 0]))
        self.play(FadeIn(ml), run_time=self.T(1))
        self.wait(self.T(4))

        # This has to replace ml rather than sit above it — the layer stack
        # occupies y -0.55 down to -1.90, so anything at LINE_Y + 0.62 lands
        # on top of the layers and cannot be read.
        pt = txt("2 + 2 gets the same thinking as 4827 × 36", 22, WHITE_,
                 bold=False, w=4.3)
        pt.move_to(np.array([0, -2.42, 0]))
        self.play(FadeOut(ml), run_time=self.T(1))
        self.play(FadeIn(pt), run_time=self.T(1))
        self.wait(self.T(4))
        self.finish(6, head, spiral, yl, layers, pt)

    # ==================================================================
    # 7 — IT RANKS, IT DOESN'T COMPUTE.  Then the signature.
    # ==================================================================
    def ch7_rank(self):
        self.chapter(7, "it ranks, it doesn't compute")
        prompt = self.dance(txt("4827 × 36 =", 34, GREY)
                            .move_to(np.array([0, 1.85, 0])))
        self.play(FadeIn(prompt), run_time=self.T(1))

        cands = [("173772", 0.41), ("173,772", 0.22), ("172872", 0.14),
                 ("173782", 0.09), ("something else", 0.14)]
        rows = VGroup()
        for i, (label, p) in enumerate(cands):
            y = 0.95 - i * 0.5
            l = txt(label, 22, WHITE_ if i == 0 else GREY, bold=(i == 0))
            l.move_to(np.array([-1.35, y, 0]))
            b = Rectangle(width=max(p * 4.2, 0.06), height=0.22, stroke_width=0)
            b.set_fill(GOLD if i == 0 else WHITE_, opacity=0.85 if i == 0 else 0.32)
            b.move_to(np.array([0.35 + max(p * 4.2, 0.06) / 2, y, 0]))
            rows.add(VGroup(l, b))
        self.play(LaggedStart(*[FadeIn(r, shift=0.14 * RIGHT) for r in rows],
                              lag_ratio=0.12), run_time=self.T(2),
                  rate_func=rush_from)
        self.wait(self.T(3))

        pay = txt("it never multiplied anything", 26, GOLD)
        pay.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(pay), run_time=self.T(1))
        self.dance(pay, 0.05)
        self.wait(self.T(4))
        self.drop(prompt, rows, pay)

        line = VGroup(txt("we look for truth", 26, GREY),
                      txt("it looks for", 26, GREY),
                      txt("what usually comes next", 28)) \
            .arrange(DOWN, buff=0.2).move_to(np.array([0, 0.7, 0]))
        for m in line:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=self.T(1),
                      rate_func=rush_from)
        self.wait(self.T(3))
        self.play(FadeOut(line), run_time=self.T(1))

        # updaters off before the ending fade — inviolable
        self.clock.clear_updaters()
        if self.hud is not None:
            self.remove(self.hud)

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
        self.pad_to(CHAPTERS * CH_BEATS - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))


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
