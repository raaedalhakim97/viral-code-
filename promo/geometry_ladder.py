"""
geometry_ladder — the same climb as equation_ladder, drawn instead of typed.

Every rung is a construction, not a string. A line is a line. Squared error is
literally squares. Learning is the line moving and the squares shrinking. The
symbol still appears, small and grey at the top, so the picture and the notation
are tied together — but the picture is what carries it.

    BPM=150 manimgl geometry_ladder.py GeometryLadder -w
    python3 geometry_ladder.py --click 150 click.wav

Tempo is an ENVIRONMENT VARIABLE, not a flag — manimgl parses sys.argv itself
and hard-errors on arguments it does not recognise.

40 beats = 10 bars = 16.000s at 150 BPM, which fits the 18s sound with room.

manimgl traps that fail silently, all three of which cost a re-render to find:
    Text(color=X)    ignored — StringMobject hardcodes fill_color=WHITE.
                     base_color= does not work either. Use fill_color=.
    Circle(color=X)  ignored — hardcodes stroke_color=RED. Use stroke_color=.
    Dot(color=X)     ignored — hardcodes fill_color=WHITE. Use fill_color=.
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

BPM = float(os.environ.get("BPM", 150.0))

# Beat budget — 40 beats = 10 bars.
#   open    4B   title
#   rungs  28B   7 constructions, one bar each
#   close   8B   signature + follow ask
TOTAL_BEATS = 40

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FPS = 60          # must match custom_config.yml
FRAME_H = 9.0
SYM_Y   = 2.72      # the symbol, small and grey
NAME_Y  = -2.10     # what the picture is called
PLOT_C  = np.array([0.0, 0.45, 0.0])
PLOT_W, PLOT_H = 4.05, 3.05


def P(x, y):
    """Unit-square data coords -> screen."""
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


def sym(t):
    return Text(t, fill_color=GREY, font_size=23)


def name(t, color=WHITE_):
    x = Text(t, fill_color=color, font_size=27, weight=BOLD)
    if x.get_width() > 4.3:
        x.set_width(4.3)
    return x


# Seven points that sit near a line but not on it — the residuals have to be
# visible enough to become squares you can actually see.
DATA = [(0.10, 0.26), (0.24, 0.30), (0.37, 0.47), (0.50, 0.44),
        (0.63, 0.63), (0.78, 0.66), (0.90, 0.83)]
BAD  = (0.42, 0.14)     # a deliberately wrong line: slope, intercept
GOOD = (0.66, 0.16)     # close to least squares for DATA


class GeometryLadder(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM

        self.open()
        self.rung_count()
        self.rung_line()
        self.rung_fit()
        self.rung_error()
        self.rung_learn()
        self.rung_choose()
        self.rung_attend()
        self.close()

    def T(self, beats):
        """run_time for N beats, snapped to a whole number of frames.

        Do NOT pass a raw multiple of B. 1.5 * (60/150) is 0.6000000000000001,
        and manim builds its frame list with arange(0, run_time, 1/fps), so that
        trailing bit buys an extra step: 37 frames where the beat wants 36. Three
        such calls put this scene at 963 frames instead of 960 - a sixteenth of a
        second of drift against the track, from nothing but float error.
        """
        return round(beats * self.B * FPS) / FPS

    # ------------------------------------------------------------------
    # 4 beats — the title
    # ------------------------------------------------------------------
    def open(self):
        B = self.B
        t1 = Text("EVERY", fill_color=GREY, font_size=30, weight=BOLD)
        t2 = Text("EQUATION", fill_color=WHITE_, font_size=52, weight=BOLD)
        t3 = Text("IS A PICTURE", fill_color=WHITE_, font_size=34, weight=BOLD)
        g = VGroup(t1, t2, t3).arrange(DOWN, buff=0.18)
        if g.get_width() > 4.2:
            g.set_width(4.2)
        g.move_to(np.array([0, 0.5, 0]))
        self.play(FadeIn(t1, scale=1.12), run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(t2, scale=1.18), run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(t3), run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(1))
        self.remove(g, t1, t2, t3)

    # ------------------------------------------------------------------
    def caption(self, symbol, label, gold=False):
        """The two text lines that frame every rung."""
        s = sym(symbol).move_to(np.array([0, SYM_Y, 0]))
        n = name(label, GOLD if gold else WHITE_)
        n.move_to(np.array([0, NAME_Y, 0]))
        return s, n

    # ------------------------------------------------------------------
    # 1 — counting. Two unit lengths laid end to end.
    # ------------------------------------------------------------------
    def rung_count(self):
        B = self.B
        s, n = self.caption("1 + 1 = 2", "length")
        y = PLOT_C[1]
        a = seg(np.array([-1.9, y, 0]), np.array([-0.1, y, 0]))
        b = seg(np.array([0.1, y, 0]), np.array([1.9, y, 0]))
        ticks = VGroup(*[seg(np.array([x, y - 0.16, 0]), np.array([x, y + 0.16, 0]),
                             GREY, 2.2) for x in (-1.9, -0.1, 0.1, 1.9)])

        self.play(FadeIn(s), ShowCreation(a), run_time=self.T(1), rate_func=rush_from)
        self.play(ShowCreation(b), FadeIn(ticks), run_time=self.T(1), rate_func=rush_from)
        self.play(FadeIn(n), run_time=self.T(1))
        self.wait(self.T(1))
        self.remove(s, n, a, b, ticks)

    # ------------------------------------------------------------------
    # 2 — a straight line, with the slope triangle that defines it.
    # ------------------------------------------------------------------
    def rung_line(self):
        B = self.B
        s, n = self.caption("y = mx + b", "a straight line")
        m, c = BAD
        self.axes = VGroup(
            seg(P(0, 0), P(1, 0), FAINT, 2.4),
            seg(P(0, 0), P(0, 1), FAINT, 2.4),
        )
        self.mt = ValueTracker(m)
        self.ct = ValueTracker(c)

        def make_line():
            mm, cc = self.mt.get_value(), self.ct.get_value()
            return seg(P(0, cc), P(1, mm + cc), WHITE_, 3.4)

        self.line = always_redraw(make_line)

        self.play(FadeIn(s), ShowCreation(self.axes), run_time=self.T(1), rate_func=rush_from)
        drawn = make_line()
        self.play(ShowCreation(drawn), run_time=self.T(1), rate_func=rush_from)
        self.remove(drawn)
        self.add(self.line)

        # rise over run, drawn
        x0, x1 = 0.30, 0.62
        tri = poly([P(x0, m * x0 + c), P(x1, m * x0 + c), P(x1, m * x1 + c)],
                   GREY, 2.2, 0.85)
        self.play(ShowCreation(tri), FadeIn(n), run_time=self.T(1))
        self.wait(self.T(1))
        self.remove(tri, s, n)

    # ------------------------------------------------------------------
    # 3 — the data arrives. The line is now a claim about it.
    # ------------------------------------------------------------------
    def rung_fit(self):
        B = self.B
        s, n = self.caption("ŷ = w · x + b", "a prediction")
        self.dots = VGroup(*[Dot(P(x, y), radius=0.075, fill_color=WHITE_)
                             for x, y in DATA])
        self.play(FadeIn(s),
                  LaggedStart(*[FadeIn(d, scale=0.3) for d in self.dots],
                              lag_ratio=0.07),
                  run_time=self.T(1), rate_func=rush_from)

        # one prediction picked out: drop from the point to the line
        px, py = DATA[4]
        m, c = BAD
        drop = seg(P(px, py), P(px, m * px + c), GREY, 2.4, 0.8)
        hit = Dot(P(px, m * px + c), radius=0.07, fill_color=GREY)
        self.play(ShowCreation(drop), FadeIn(hit), FadeIn(n),
                  run_time=self.T(1), rate_func=rush_from)
        self.wait(self.T(2))
        self.remove(drop, hit, s, n)

    # ------------------------------------------------------------------
    # 4 — squared error, drawn as actual squares. This is the whole video.
    # ------------------------------------------------------------------
    def rung_error(self):
        B = self.B
        s, n = self.caption("J = ½ Σ (ŷ − y)²", "the error, squared")

        def make_squares():
            mm, cc = self.mt.get_value(), self.ct.get_value()
            g = VGroup()
            for x, y in DATA:
                r = y - (mm * x + cc)
                if abs(r) < 1e-4:
                    continue
                # side of the square is the residual, in data units, so the
                # picture and the arithmetic are the same object
                side_x = abs(r) * PLOT_H / PLOT_W
                # flip the square inward rather than let it leave the frame -
                # the rightmost point's residual is wide enough to run off
                d = 1.0 if x + side_x <= 1.0 else -1.0
                x2 = x + d * side_x
                pts = [P(x, y), P(x2, y), P(x2, y - r), P(x, y - r)]
                q = poly(pts, WHITE_, 2.0, 0.75)
                q.set_fill(WHITE_, opacity=0.13)
                g.add(q)
            return g

        self.squares = always_redraw(make_squares)
        self.play(FadeIn(s), run_time=self.T(0.5))
        drawn = make_squares()
        self.play(ShowCreation(drawn, lag_ratio=0.12), FadeIn(n),
                  run_time=self.T(1.5), rate_func=rush_from)
        self.remove(drawn)
        self.add(self.squares)
        self.wait(self.T(2))
        self.remove(s, n)

    # ------------------------------------------------------------------
    # 5 — learning. The line moves and the squares shrink. Nothing else.
    # ------------------------------------------------------------------
    def rung_learn(self):
        B = self.B
        s, n = self.caption("w ← w − α ∂J/∂w", "learning")
        self.play(FadeIn(s), FadeIn(n), run_time=self.T(0.5))
        self.play(self.mt.animate.set_value(GOOD[0]),
                  self.ct.animate.set_value(GOOD[1]),
                  run_time=self.T(2.5), rate_func=smooth)
        self.wait(self.T(1))
        self.remove(s, n, self.squares, self.dots, self.line, self.axes)

    # ------------------------------------------------------------------
    # 6 — softmax. Three heights become three shares of one bar.
    # ------------------------------------------------------------------
    def rung_choose(self):
        B = self.B
        s, n = self.caption("σ(z) = exp(z) / Σ exp(z)", "turning it into a choice")
        z = np.array([1.9, 0.7, 1.2])
        p = np.exp(z) / np.exp(z).sum()

        bw, gap = 0.62, 0.34
        xs = [-(bw + gap), 0.0, (bw + gap)]
        base = PLOT_C[1] - 1.15

        bars = VGroup()
        for i, x in enumerate(xs):
            h = z[i] * 0.62
            r = Rectangle(width=bw, height=h, stroke_width=0)
            r.set_fill(WHITE_, opacity=0.55)
            r.move_to(np.array([x, base + h / 2, 0]))
            bars.add(r)

        self.play(FadeIn(s),
                  LaggedStart(*[FadeIn(b, shift=0.2 * UP) for b in bars],
                              lag_ratio=0.08),
                  run_time=self.T(1), rate_func=rush_from)

        # they rescale so the three of them add to one
        anims = []
        for i, b in enumerate(bars):
            h = p[i] * 2.6
            anims.append(b.animate.stretch_to_fit_height(h)
                          .move_to(np.array([xs[i], base + h / 2, 0]))
                          .set_fill(WHITE_, opacity=0.30 + 0.5 * p[i]))
        self.play(*anims, FadeIn(n), run_time=self.T(1.5), rate_func=rush_into)

        total = Text("they add to 1", fill_color=GREY, font_size=22)
        total.move_to(np.array([0, base - 0.42, 0]))
        self.play(FadeIn(total), run_time=self.T(0.5))
        self.wait(self.T(1))
        self.remove(s, n, bars, total)

    # ------------------------------------------------------------------
    # 7 — attention, as vectors. Keys lean toward or away from the query;
    #     how much they lean is the weight; the answer is the weighted sum.
    #     The one gold thing in the piece.
    # ------------------------------------------------------------------
    def rung_attend(self):
        B = self.B
        s, n = self.caption("Attention(Q,K,V)", "asking which parts matter", gold=True)
        O = PLOT_C + np.array([0, -0.55, 0])

        def arrow(vec, color, w=3.2, op=1.0):
            tip = O + vec
            body = seg(O, tip, color, w, op)
            d = vec / (np.linalg.norm(vec) + 1e-9)
            perp = np.array([-d[1], d[0], 0.0])
            head = poly([tip, tip - d * 0.26 + perp * 0.13,
                         tip - d * 0.26 - perp * 0.13], color, w * 0.7, op)
            head.set_fill(color, opacity=op)
            return VGroup(body, head)

        q = np.array([0.0, 1.55, 0.0])
        keys = [np.array([-1.35, 0.75, 0.0]),
                np.array([0.35, 1.45, 0.0]),
                np.array([1.45, 0.35, 0.0])]
        # weight = how closely each key points the way the query does
        qn = q / np.linalg.norm(q)
        wts = np.array([max(np.dot(k / np.linalg.norm(k), qn), 0.0) for k in keys])
        wts = wts / wts.sum()

        qa = arrow(q, WHITE_, 3.6)
        self.play(FadeIn(s), ShowCreation(qa), run_time=self.T(1), rate_func=rush_from)

        ka = VGroup(*[arrow(k, GREY, 2.6, 0.75) for k in keys])
        self.play(LaggedStart(*[ShowCreation(a) for a in ka], lag_ratio=0.1),
                  run_time=self.T(1), rate_func=rush_from)

        # each key thickens in proportion to its weight
        self.play(*[a.animate.set_stroke(width=2.0 + 7.0 * wts[i],
                                         opacity=0.35 + 0.6 * wts[i])
                    for i, a in enumerate(ka)],
                  FadeIn(n), run_time=self.T(1), rate_func=rush_into)

        out = sum(wts[i] * keys[i] for i in range(3))
        oa = arrow(out, GOLD, 4.4)
        self.play(ShowCreation(oa), run_time=self.T(1), rate_func=rush_from)
        self.remove(qa, ka, oa, s, n)

    # ------------------------------------------------------------------
    def close(self):
        B = self.B
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(2))

        words = VGroup(
            Text("PAUSE", fill_color=WHITE_, font_size=20, weight=BOLD),
            Text("OBSERVE", fill_color=WHITE_, font_size=20, weight=BOLD),
            Text("LEARN", fill_color=WHITE_, font_size=20, weight=BOLD),
        ).arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1))

        cta = Text("Follow for the math behind AI",
                   fill_color=WHITE_, font_size=27, weight=BOLD)
        handle = Text("@observer.collapse", fill_color=GREY, font_size=21)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, NAME_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1))
        self.wait(self.T(3))
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(1))


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
