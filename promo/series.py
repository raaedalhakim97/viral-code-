"""
series — THE MATH BEHIND AI, in seven parts.

One file, seven videos. PART selects which:

    PART=3 BPM=150 manimgl series.py Series -w
    python3 series.py --click 150 click.wav

Each part is 32 beats = 8 bars = 12.800s at 150 BPM — same length, every one
ending on a bar line, all of them inside an 18-second sound. Renders silent.

12.8s is chosen for completion rate. A short video watched to the end (and
often twice) is a far stronger signal than a long one abandoned at 40%.

Why a series and not seven one-offs: a like costs nothing, a follow is a bet
that you will make more of what they just watched. "PART 3 / 7" on the end card
makes that bet for them. It is the difference between 2,645 likes and 101
followers.

Shared contract with the other beat-locked scenes:
    run_time ALWAYS via self.T(beats) — a raw n*B is not on a frame boundary
        (1.5 * 60/150 = 0.6000000000000001) and manim's arange buys an extra
        frame, drifting the piece off the track.
    Text     -> fill_color=, never color= or base_color= (both are ignored)
    Circle   -> stroke_color=
    Dot      -> fill_color=
    ShowCreation(make_thing()) leaves an orphan copy in the scene; draw the
        static one, self.remove it, then self.add the always_redraw version.
"""
import sys

if "--click" in sys.argv:
    import wave
    import numpy as _np

    _i = sys.argv.index("--click")
    _bpm = float(sys.argv[_i + 1])
    _out = sys.argv[_i + 2] if _i + 2 < len(sys.argv) else "click.wav"
    _SR, _dur = 44100, 40.0
    _sig = _np.zeros(int(_SR * _dur), _np.float32)
    _beat = 60.0 / _bpm
    for _n in range(int(_dur / _beat)):
        _s = int(_n * _beat * _SR)
        _e = min(_s + int(0.04 * _SR), len(_sig))
        _env = _np.exp(-_np.linspace(0, 8, _e - _s))
        _f = 1600 if _n % 4 == 0 else 900
        _sig[_s:_e] += _np.sin(2 * _np.pi * _f * _np.arange(_e - _s) / _SR) * _env * 0.6
    with wave.open(_out, "wb") as _w:
        _w.setnchannels(1)
        _w.setsampwidth(2)
        _w.setframerate(_SR)
        _w.writeframes((_np.clip(_sig, -1, 1) * 32767).astype(_np.int16).tobytes())
    print(f"{_out}  {_bpm:g} bpm  {_dur:g}s")
    sys.exit(0)

import os

from manimlib import *
import numpy as np

BPM  = float(os.environ.get("BPM", 150.0))
PART = int(os.environ.get("PART", 1))
PARTS = 7

# 32 beats = 8 bars = 12.800s at 150 BPM. Every part is the same length and
# every part ends ON a bar line — the first cut came out at 28/29/30/33/35
# beats and four of the seven ended mid-bar, which shows the moment you lay
# them against a track. self.pad_to() enforces it now rather than trusting the
# arithmetic to come out right.
TOTAL_BEATS = 32
CLOSE_BEATS = 8

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FPS     = 60          # must match custom_config.yml
FRAME_H = 9.0
SYM_Y   = 2.78
NAME_Y  = -2.10
PLOT_C  = np.array([0.0, 0.45, 0.0])
PLOT_W, PLOT_H = 4.05, 3.05

# Hook line and title for each part. The hook is a question or a claim, never a
# topic label — "Why is it called least squares?" earns a second of attention;
# "Least squares" does not.
HOOKS = {
    1: ("Two numbers make every line there is.",  "THE LINE"),
    2: ("A line stops being a shape and starts being a guess.", "THE PREDICTION"),
    3: ("It's called least squares because of the squares.", "THE ERROR"),
    4: ("Learning is just rolling downhill.", "LEARNING"),
    5: ("How does a model choose?", "THE CHOICE"),
    6: ("This is the one running your AI.", "ATTENTION"),
    7: ("Six steps from a straight line to a language model.", "THE CLIMB"),
}

DATA = [(0.10, 0.26), (0.24, 0.30), (0.37, 0.47), (0.50, 0.44),
        (0.63, 0.63), (0.78, 0.66), (0.90, 0.83)]
BAD  = (0.42, 0.14)
GOOD = (0.66, 0.16)


def P(x, y):
    return PLOT_C + np.array([(x - 0.5) * PLOT_W, (y - 0.5) * PLOT_H, 0.0])


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


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


class Series(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM

        self.used = 0.0
        self.hook()
        [self.p1_line, self.p2_predict, self.p3_error, self.p4_learn,
         self.p5_choose, self.p6_attend, self.p7_climb][PART - 1]()
        self.pad_to(TOTAL_BEATS - CLOSE_BEATS)
        self.close()

    def T(self, beats):
        """run_time for N beats, snapped to whole frames. Never use raw n*B.

        Also the single place elapsed time is counted, which is what lets
        pad_to() land every part on the same bar line. Every timed call in this
        file goes through here — if one does not, the padding silently lies.
        """
        self.used += beats
        return round(beats * self.B * FPS) / FPS

    def pad_to(self, target):
        """Hold the payoff until the part has used exactly `target` beats.

        The leftover lands on the last line of the build, which is the line most
        worth leaving on screen. If it ever goes negative the part is too long
        and needs trimming, not padding — so say so rather than silently drift.
        """
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(
                f"PART {PART} overruns by {-rem:.2f} beats — trim it, do not pad")
        if rem > 0.01:
            self.wait(self.T(rem))

    # ------------------------------------------------------------------
    # 4 beats — the hook. Motion in the first frames or the scroll wins.
    # ------------------------------------------------------------------
    def hook(self):
        line, title = HOOKS[PART]
        tag = txt(f"PART {PART} / {PARTS}", 22, GREY)
        tag.move_to(np.array([0, 2.35, 0]))
        big = txt(title, 46, WHITE_)
        big.move_to(np.array([0, 0.95, 0]))
        sub = txt(line, 25, GREY, bold=False, w=4.1)
        sub.move_to(np.array([0, -0.15, 0]))

        self.play(FadeIn(big, scale=1.14), run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(sub), FadeIn(tag), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(1.5))
        self.play(FadeOut(big), FadeOut(sub), FadeOut(tag), run_time=self.T(0.5))
        self.remove(big, sub, tag)

    def label(self, symbol, name, gold=False):
        s = txt(symbol, 23, GREY, bold=False).move_to(np.array([0, SYM_Y, 0]))
        n = txt(name, 27, GOLD if gold else WHITE_).move_to(np.array([0, NAME_Y, 0]))
        return s, n

    def axes(self):
        return VGroup(seg(P(0, 0), P(1, 0), FAINT, 2.4),
                      seg(P(0, 0), P(0, 1), FAINT, 2.4))

    def regression(self, m, c):
        """Shared setup: axes, trackers, live line. Returns the axes group."""
        self.mt = ValueTracker(m)
        self.ct = ValueTracker(c)

        def make_line():
            return seg(P(0, self.ct.get_value()),
                       P(1, self.mt.get_value() + self.ct.get_value()),
                       WHITE_, 3.4)

        self.make_line = make_line
        self.line = always_redraw(make_line)
        return self.axes()

    def squares(self):
        def make():
            mm, cc = self.mt.get_value(), self.ct.get_value()
            g = VGroup()
            for x, y in DATA:
                r = y - (mm * x + cc)
                if abs(r) < 1e-4:
                    continue
                side = abs(r) * PLOT_H / PLOT_W
                d = 1.0 if x + side <= 1.0 else -1.0
                q = poly([P(x, y), P(x + d * side, y),
                          P(x + d * side, y - r), P(x, y - r)], WHITE_, 2.0, 0.75)
                q.set_fill(WHITE_, opacity=0.13)
                g.add(q)
            return g

        self.make_squares = make
        return always_redraw(make)

    # ==================================================================
    # PART 1 — the line. Two numbers, every line there is.
    # ==================================================================
    def p1_line(self):
        s, n = self.label("y = mx + b", "slope and intercept")
        ax = self.regression(0.55, 0.20)
        self.play(FadeIn(s), ShowCreation(ax), run_time=self.T(1))
        drawn = self.make_line()
        self.play(ShowCreation(drawn), run_time=self.T(1), rate_func=rush_from)
        self.remove(drawn)
        self.add(self.line)
        self.play(FadeIn(n), run_time=self.T(1))

        # m tilts it
        mlab = txt("m tilts it", 25, WHITE_).move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(n), FadeIn(mlab), run_time=self.T(1))
        self.play(self.mt.animate.set_value(0.15), run_time=self.T(2), rate_func=smooth)
        self.play(self.mt.animate.set_value(0.85), run_time=self.T(2), rate_func=smooth)
        self.play(self.mt.animate.set_value(0.55), run_time=self.T(1), rate_func=smooth)

        # b slides it
        blab = txt("b slides it", 25, WHITE_).move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(mlab), FadeIn(blab), run_time=self.T(1))
        self.play(self.ct.animate.set_value(0.05), run_time=self.T(2), rate_func=smooth)
        self.play(self.ct.animate.set_value(0.45), run_time=self.T(2), rate_func=smooth)
        self.play(self.ct.animate.set_value(0.20), run_time=self.T(2), rate_func=smooth)

        pay = txt("two numbers. every line.", 28, GOLD)
        pay.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(blab), FadeIn(pay), run_time=self.T(1))
        self.wait(self.T(3))
        self.remove(s, pay, ax, self.line)

    # ==================================================================
    # PART 2 — the same line, doing a different job.
    # ==================================================================
    def p2_predict(self):
        s, n = self.label("ŷ = w · x + b", "a guess about every x")
        ax = self.regression(*BAD)
        self.add(self.line)
        self.play(FadeIn(s), ShowCreation(ax), run_time=self.T(1))
        drawn = self.make_line()
        self.play(ShowCreation(drawn), run_time=self.T(1), rate_func=rush_from)
        self.remove(drawn)

        dots = VGroup(*[Dot(P(x, y), radius=0.075, fill_color=WHITE_)
                        for x, y in DATA])
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots],
                              lag_ratio=0.07), FadeIn(n), run_time=self.T(2))
        self.wait(self.T(1))

        # the measured value, the guessed value, the gap between them
        px, py = DATA[4]
        m, c = BAD
        pred = m * px + c
        drop = seg(P(px, py), P(px, pred), GOLD, 3.2)
        hit = Dot(P(px, pred), radius=0.07, fill_color=GOLD)
        g1 = txt("what happened", 22, GREY, bold=False)
        g1.move_to(P(px, py) + np.array([0, 0.42, 0]))
        g2 = txt("what it guessed", 22, GREY, bold=False)
        g2.move_to(P(px, pred) + np.array([0, -0.42, 0]))

        self.play(FadeIn(g1), run_time=self.T(1.5))
        self.play(FadeIn(hit), FadeIn(g2), run_time=self.T(1.5))
        self.play(ShowCreation(drop), run_time=self.T(1))
        gap = txt("the gap", 26, GOLD).move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(n), FadeIn(gap), run_time=self.T(1))
        self.wait(self.T(2))

        pay = txt("every gap, at once", 27, WHITE_).move_to(np.array([0, NAME_Y, 0]))
        drops = VGroup(*[seg(P(x, y), P(x, m * x + c), GREY, 2.2, 0.8)
                         for x, y in DATA])
        self.play(FadeOut(gap), FadeOut(g1), FadeOut(g2), FadeIn(pay),
                  LaggedStart(*[ShowCreation(d) for d in drops], lag_ratio=0.06),
                  run_time=self.T(3))
        self.wait(self.T(3))
        self.remove(s, pay, ax, self.line, dots, drop, hit, drops)

    # ==================================================================
    # PART 3 — least squares, and why it has that name.
    # ==================================================================
    def p3_error(self):
        s, n = self.label("J = ½ Σ (ŷ − y)²", "square the gap")
        ax = self.regression(*BAD)
        dots = VGroup(*[Dot(P(x, y), radius=0.075, fill_color=WHITE_)
                        for x, y in DATA])
        self.add(self.line)
        self.play(FadeIn(s), ShowCreation(ax), FadeIn(dots), run_time=self.T(1))

        m, c = BAD
        drops = VGroup(*[seg(P(x, y), P(x, m * x + c), GREY, 2.4, 0.85)
                         for x, y in DATA])
        self.play(LaggedStart(*[ShowCreation(d) for d in drops], lag_ratio=0.06),
                  FadeIn(n), run_time=self.T(2))
        self.wait(self.T(1))

        # each gap becomes a square with that gap as its side
        sq = self.squares()
        drawn = self.make_squares()
        why = txt("each gap becomes a square", 25, WHITE_)
        why.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(n), FadeIn(why),
                  ShowCreation(drawn, lag_ratio=0.12), FadeOut(drops),
                  run_time=self.T(3), rate_func=rush_from)
        self.remove(drawn)
        self.add(sq)
        self.wait(self.T(2))

        area = txt("the error IS the white area", 25, WHITE_)
        area.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(why), FadeIn(area), run_time=self.T(1.5))
        self.wait(self.T(2.5))

        pay = txt("least squares = smallest area", 25, GOLD)
        pay.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(area), FadeIn(pay), run_time=self.T(1))
        self.wait(self.T(2))
        self.remove(s, pay, ax, self.line, dots, sq)

    # ==================================================================
    # PART 4 — gradient descent. The line moves, the area shrinks.
    # ==================================================================
    def p4_learn(self):
        s, n = self.label("w ← w − α ∂J/∂w", "roll downhill")
        ax = self.regression(*BAD)
        dots = VGroup(*[Dot(P(x, y), radius=0.075, fill_color=WHITE_)
                        for x, y in DATA])
        sq = self.squares()
        self.add(self.line, sq)
        self.play(FadeIn(s), ShowCreation(ax), FadeIn(dots), FadeIn(n),
                  run_time=self.T(2))
        self.wait(self.T(1))

        step = txt("one step", 25, WHITE_).move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(n), FadeIn(step), run_time=self.T(1))

        # three visible steps, so it reads as iteration and not as a dissolve
        m0, c0 = BAD
        m1, c1 = GOOD
        for k, f in enumerate((0.4, 0.75, 1.0)):
            self.play(self.mt.animate.set_value(m0 + (m1 - m0) * f),
                      self.ct.animate.set_value(c0 + (c1 - c0) * f),
                      run_time=self.T(2), rate_func=rush_into)
            self.wait(self.T(1))

        alpha = txt("α is how big a step", 25, WHITE_)
        alpha.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(step), FadeIn(alpha), run_time=self.T(1))
        self.wait(self.T(2))

        pay = txt("that's all training is", 27, GOLD)
        pay.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(alpha), FadeIn(pay), run_time=self.T(1))
        self.wait(self.T(3))
        self.remove(s, pay, ax, self.line, dots, sq)

    # ==================================================================
    # PART 5 — softmax. Three scores become three probabilities.
    # ==================================================================
    def p5_choose(self):
        s, n = self.label("σ(z) = exp(z) / Σ exp(z)", "three scores")
        z = np.array([1.9, 0.7, 1.2])
        p = np.exp(z) / np.exp(z).sum()
        bw, gap = 0.62, 0.36
        xs = [-(bw + gap), 0.0, (bw + gap)]
        base = PLOT_C[1] - 1.25

        bars = VGroup()
        for i, x in enumerate(xs):
            h = z[i] * 0.62
            r = Rectangle(width=bw, height=h, stroke_width=0)
            r.set_fill(WHITE_, opacity=0.5)
            r.move_to(np.array([x, base + h / 2, 0]))
            bars.add(r)
        self.play(FadeIn(s),
                  LaggedStart(*[FadeIn(b, shift=0.2 * UP) for b in bars],
                              lag_ratio=0.08), FadeIn(n), run_time=self.T(2))
        self.wait(self.T(1))

        # exponentiate: the gaps get stretched
        e = np.exp(z)
        ex = txt("exp stretches the gaps", 25, WHITE_)
        ex.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(n), FadeIn(ex),
                  *[bars[i].animate.stretch_to_fit_height(e[i] * 0.42)
                    .move_to(np.array([xs[i], base + e[i] * 0.21, 0]))
                    for i in range(3)],
                  run_time=self.T(3), rate_func=rush_into)
        self.wait(self.T(2))

        # normalise: they now add to one
        nm = txt("divide by the total", 25, WHITE_)
        nm.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(ex), FadeIn(nm),
                  *[bars[i].animate.stretch_to_fit_height(p[i] * 2.7)
                    .move_to(np.array([xs[i], base + p[i] * 1.35, 0]))
                    .set_fill(WHITE_, opacity=0.3 + 0.5 * p[i])
                    for i in range(3)],
                  run_time=self.T(3), rate_func=rush_into)

        pcts = VGroup(*[txt(f"{int(round(p[i] * 100))}%", 23, GREY, bold=False)
                        .move_to(np.array([xs[i], base - 0.4, 0])) for i in range(3)])
        self.play(FadeIn(pcts), run_time=self.T(1))
        self.wait(self.T(1))

        pay = txt("scores became a choice", 26, GOLD)
        pay.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(nm), FadeIn(pay), run_time=self.T(1))
        self.wait(self.T(3))
        self.remove(s, pay, bars, pcts)

    # ==================================================================
    # PART 6 — attention. What the model decides to look at.
    # ==================================================================
    def p6_attend(self):
        s, n = self.label("Attention(Q,K,V)", "what should I look at?", gold=True)
        O = PLOT_C + np.array([0, -0.65, 0])

        def arrow(vec, color, w=3.2, op=1.0):
            tip = O + vec
            d = vec / (np.linalg.norm(vec) + 1e-9)
            perp = np.array([-d[1], d[0], 0.0])
            head = poly([tip, tip - d * 0.26 + perp * 0.13,
                         tip - d * 0.26 - perp * 0.13], color, w * 0.7, op)
            head.set_fill(color, opacity=op)
            return VGroup(seg(O, tip, color, w, op), head)

        q = np.array([0.0, 1.65, 0.0])
        keys = [np.array([-1.4, 0.8, 0.0]),
                np.array([0.32, 1.5, 0.0]),
                np.array([1.5, 0.35, 0.0])]
        qn = q / np.linalg.norm(q)
        wts = np.array([max(np.dot(k / np.linalg.norm(k), qn), 0.0) for k in keys])
        wts = wts / wts.sum()

        qa = arrow(q, WHITE_, 3.8)
        ql = txt("the question", 22, GREY, bold=False)
        ql.move_to(O + q + np.array([0, 0.34, 0]))
        self.play(FadeIn(s), ShowCreation(qa), FadeIn(ql), run_time=self.T(2))

        ka = VGroup(*[arrow(k, GREY, 2.6, 0.7) for k in keys])
        kl = txt("everything it could look at", 23, WHITE_)
        kl.move_to(np.array([0, NAME_Y, 0]))
        self.play(LaggedStart(*[ShowCreation(a) for a in ka], lag_ratio=0.1),
                  FadeOut(n), FadeIn(kl), run_time=self.T(2))
        self.wait(self.T(1))

        lean = txt("how much each one agrees", 23, WHITE_)
        lean.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(kl), FadeIn(lean),
                  *[a.animate.set_stroke(width=2.0 + 7.5 * wts[i],
                                         opacity=0.3 + 0.65 * wts[i])
                    for i, a in enumerate(ka)],
                  run_time=self.T(3), rate_func=rush_into)
        self.wait(self.T(2))

        out = sum(wts[i] * keys[i] for i in range(3))
        oa = arrow(out, GOLD, 4.6)
        ans = txt("the answer is the blend", 26, GOLD)
        ans.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeOut(lean), FadeIn(ans), ShowCreation(oa),
                  run_time=self.T(2), rate_func=rush_from)
        self.wait(self.T(4))
        self.remove(s, ans, qa, ql, ka, oa)

    # ==================================================================
    # PART 7 — the whole climb, fast.
    # ==================================================================
    def p7_climb(self):
        rungs = [
            ("y = mx + b",              "a line"),
            ("ŷ = w · x + b",           "a guess"),
            ("J = ½ Σ (ŷ − y)²",        "how wrong"),
            ("w ← w − α ∂J/∂w",         "learning"),
            ("σ(z) = exp(z) / Σ exp(z)", "a choice"),
            ("Attention(Q,K,V)",        "your AI"),
        ]
        slots = [0.15, 0.85, 1.55, 2.25]
        stack = []
        for i, (eq, gl) in enumerate(rungs):
            last = i == len(rungs) - 1
            e = txt(eq, 32 if not last else 30, GOLD if last else WHITE_)
            e.move_to(np.array([0, -1.15, 0]))
            g = txt(gl, 22, GREY, bold=False).move_to(np.array([0, NAME_Y, 0]))

            moves = []
            for j, old in enumerate(stack):
                if j + 1 < len(slots):
                    moves.append(old.animate.move_to(np.array([0, slots[j + 1], 0]))
                                 .scale(0.88)
                                 .set_opacity(max(0.5 - 0.12 * j, 0.14)))
                else:
                    moves.append(FadeOut(old, shift=0.2 * UP))
            if stack:
                moves[0] = stack[0].animate.move_to(np.array([0, slots[0], 0])) \
                                           .scale(0.64).set_opacity(0.55)

            self.play(*moves, FadeIn(e, scale=1.16), FadeIn(g),
                      run_time=self.T(1), rate_func=rush_from)
            self.play(FadeOut(g), run_time=self.T(1))
            self.wait(self.T(1))
            stack = [e] + [m for m in stack if m in self.mobjects]

        pay = txt("none of it is magic", 28, WHITE_)
        pay.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeIn(pay), run_time=self.T(1))
        self.wait(self.T(1))
        self.remove(pay, *stack)

    # ==================================================================
    # 8 beats — signature, the part number, the ask
    # ==================================================================
    def close(self):
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.3, 0])).scale(0.76)
        self.play(ShowCreation(eye), run_time=self.T(2))

        words = VGroup(
            txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20),
        ).arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.5, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1))

        nxt = (f"PART {PART} / {PARTS}" if PART == PARTS
               else f"PART {PART} / {PARTS}  ·  part {PART + 1} next")
        tag = txt(nxt, 23, GOLD)
        tag.move_to(np.array([0, -1.42, 0]))
        cta = txt("Follow for the math behind AI", 26, WHITE_)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.17)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, NAME_Y - 0.28, 0]))

        self.play(FadeIn(tag, shift=0.08 * UP), FadeIn(cg, shift=0.08 * UP),
                  run_time=self.T(1))
        self.wait(self.T(3))
        self.play(FadeOut(eye), FadeOut(words), FadeOut(tag), FadeOut(cg),
                  run_time=self.T(1))


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
