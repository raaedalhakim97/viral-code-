"""
equation_ladder — the climb from 1+1=2 to attention, one equation per bar.

Same beat-locked contract as beat_dance.py. Renders SILENT; the montagem goes on
in the TikTok editor.

    BPM=150 manimgl equation_ladder.py EquationLadder -w
    python3 equation_ladder.py --click 150 click.wav

Tempo comes from the BPM environment variable, NOT a --bpm flag: manimgl parses
sys.argv itself and hard-errors on any argument it does not recognise, so a
custom flag is not available to a scene file. An env var sidesteps argv
entirely.

Default is 150 BPM because that is where funk montagem sits — the modern
Brazilian funk wave is a 150 BPM genre. At 150 the piece is 40 beats = 16.0s,
which fits every sound in the reference list including the 18s ones.

No LaTeX in this container, so the equations are Unicode text rather than Tex
mobjects. Every glyph below is checked against DejaVu Sans Bold before use — if
you add an equation, check its glyphs too, because a missing one renders as a
blank box and nobody notices until it is posted.

COLOUR ON TEXT USES fill_color=, NEVER color=. StringMobject, which Text
inherits from, hardcodes fill_color=WHITE and base_color=WHITE in its
signature, and both beat a color= passed by the caller. Text(color=GOLD)
renders WHITE and raises nothing. This is the same trap as Circle (hardcodes
stroke_color=RED) and Dot (hardcodes fill_color=WHITE). base_color= does not
work either — only fill_color= does.

Exactly ONE gold accent per piece, and here it is spent on the last line: the
whole ladder is white, and the equation that actually runs a model is the only
thing that glows.
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

BPM = float(os.environ.get("BPM", 150.0))   # funk montagem sits at 150

# Beat budget — 40 beats = 10 bars = 16.0s at 150 BPM.
#   open    4B  (1 bar)   the title lands
#   ladder 28B  (7 bars)  7 equations, one per bar
#   close   8B  (2 bars)  eye, signature, follow CTA
TOTAL_BEATS = 40

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

FRAME_H  = 9.0
SAFE_TOP = FRAME_H / 2 - 0.12 * FRAME_H      # +3.42
SAFE_BOT = -FRAME_H / 2 + 0.22 * FRAME_H     # -2.52
STAGE_Y  = -1.30                             # where the new equation lands
LINE_Y   = -2.10

# The ladder. Each rung is a real step in what a model actually does, and the
# order is the order you would learn them — which is the whole point: the last
# line is not magic, it is the fifth thing after a straight line.
LADDER = [
    ("1 + 1 = 2",                              "arithmetic"),
    ("y = mx + b",                             "a straight line"),
    ("ŷ = w · x + b",                          "a prediction"),
    ("J = ½ Σ (ŷ − y)²",                       "how wrong it is"),
    ("w ← w − α ∂J/∂w",                        "learning"),
    ("σ(z) = exp(z) / Σ exp(z)",               "turning it into a choice"),
    ("Attention(Q,K,V) = softmax(QKᵀ/√d)V",    "and this runs your AI"),
]

# Stack slots above the stage, nearest first. Anything older than four rungs
# falls off the top — five lines on screen is already the readable limit on a
# phone held at arm's length.
SLOTS = [0.05, 0.78, 1.51, 2.24]


def fit(mob, w=4.35):
    if mob.get_width() > w:
        mob.set_width(w)
    return mob


class EquationLadder(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)

        self.bpm = BPM
        self.B = 60.0 / self.bpm

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open()
        self.climb()
        self.close()

    def kick(self):
        """Montagem hits hard, so this is a harder spike than beat_dance's."""
        t = self.clock.get_value()
        phase = (t % self.B) / self.B
        return float(np.exp(-((phase / 0.13) ** 2)))

    # ------------------------------------------------------------------
    # 4 beats — the title, punched in on beat 1
    # ------------------------------------------------------------------
    def open(self):
        B = self.B
        t1 = Text("EVERYTHING", fill_color=WHITE_, font_size=46, weight=BOLD)
        t2 = Text("STARTS WITH", fill_color=GREY, font_size=30, weight=BOLD)
        t3 = Text("MATH", fill_color=WHITE_, font_size=70, weight=BOLD)
        g = VGroup(t1, t2, t3).arrange(DOWN, buff=0.16)
        fit(g, 4.2).move_to(np.array([0, 0.4, 0]))

        self.play(FadeIn(t1, scale=1.15), run_time=B, rate_func=rush_from)
        self.play(FadeIn(t2), run_time=B, rate_func=rush_from)
        self.play(FadeIn(t3, scale=1.25), run_time=B, rate_func=rush_from)
        self.play(FadeOut(g, shift=0.3 * UP), run_time=B)
        self.title = g

    # ------------------------------------------------------------------
    # 28 beats — 7 equations, one per bar. Each lands centre-stage on the
    # downbeat, then gets pushed up the stack by the next one.
    # ------------------------------------------------------------------
    def climb(self):
        B = self.B
        stack = []          # most recent first

        # a pulsing bar under the stage, so the beat is visible between hits
        def make_pulse():
            k = self.kick()
            w = 1.1 + 2.4 * k
            r = Rectangle(width=w, height=0.045, stroke_width=0)
            r.set_fill(WHITE_, opacity=0.20 + 0.55 * k)
            r.move_to(np.array([0, STAGE_Y - 0.72, 0]))
            return r

        pulse = always_redraw(make_pulse)
        self.add(pulse)

        for i, (eq, gloss) in enumerate(LADDER):
            last = i == len(LADDER) - 1
            e = Text(eq, fill_color=GOLD if last else WHITE_,
                     font_size=34 if not last else 30, weight=BOLD)
            fit(e).move_to(np.array([0, STAGE_Y, 0]))
            g = Text(gloss, fill_color=GREY, font_size=21)
            fit(g, 4.0).move_to(np.array([0, LINE_Y, 0]))

            # push the existing stack up one slot; drop anything past the top
            moves = []
            for j, old in enumerate(stack):
                if j + 1 < len(SLOTS):
                    tgt = np.array([0, SLOTS[j + 1], 0])
                    moves.append(old.animate.move_to(tgt)
                                 .scale(0.88)
                                 .set_opacity(max(0.5 - 0.12 * j, 0.14)))
                else:
                    moves.append(FadeOut(old, shift=0.2 * UP))

            prev = stack[0] if stack else None
            if prev is not None:
                # the outgoing equation climbs from the stage into slot 0
                moves[0] = prev.animate.move_to(np.array([0, SLOTS[0], 0])) \
                                       .scale(0.62).set_opacity(0.55)

            self.play(*moves,
                      FadeIn(e, scale=1.18),
                      FadeIn(g),
                      run_time=B, rate_func=rush_from)
            self.gloss_out = g
            self.play(FadeOut(g), run_time=B)
            self.wait(2 * B)

            stack = [e] + [m for m in stack if m in self.mobjects]

        self.stack = VGroup(*[m for m in stack if m in self.mobjects])
        self.pulse = pulse

    # ------------------------------------------------------------------
    # 8 beats — clear updaters, then the signature and the ask
    # ------------------------------------------------------------------
    def close(self):
        B = self.B
        self.clock.clear_updaters()
        self.pulse.clear_updaters()
        self.play(FadeOut(self.pulse), FadeOut(self.stack), run_time=B)

        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=2 * B)

        words = VGroup(
            Text("PAUSE", fill_color=WHITE_, font_size=20, weight=BOLD),
            Text("OBSERVE", fill_color=WHITE_, font_size=20, weight=BOLD),
            Text("LEARN", fill_color=WHITE_, font_size=20, weight=BOLD),
        ).arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=B)

        cta = Text("Follow for the math behind AI",
                   fill_color=WHITE_, font_size=27, weight=BOLD)
        handle = Text("@observer.collapse", fill_color=GREY, font_size=21)
        cg = fit(VGroup(cta, handle).arrange(DOWN, buff=0.18), 4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=B)
        self.wait(2 * B)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=B)


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
