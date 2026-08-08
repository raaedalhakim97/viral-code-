"""
stadium_rave — a 3D Lissajous curve dancing liquid. Cut to SpongeBob's
"Stadium Rave".

    BPM=125 manimgl stadium_rave.py StadiumRave -w -r 1080x1920

60 beats = 15 bars = 28.800s at 125 BPM.

THE EQUATION IS THE DANCE. NOT A METAPHOR.

    x = A sin(a u + d)      y = B sin(b u)      z = C sin(c u + e)

The rave form in the Jellyfish Jam scene is LIQUID DANCING — the glowstick
dance out of the late-80s/90s underground. Its documented vocabulary is
figure eights handed from one hand to the other at the crossover, a wave that
passes between the arms, and wrist rolls layered on top. Every one of those is a
parameter of the equation above:

    move                      what it is in the equation
    ------------------------  --------------------------------------------
    arm circles               a:b = 1:1 with d = pi/2  (1:1 IS an ellipse,
                              a circle when A=B and d=pi/2)
    THE FIGURE EIGHT          a:b = 1:2  (a 1:2 ratio IS a figure eight)
    hand-to-hand hand-off     d, the phase offset — two tracers half a cycle
                              apart, one leading, one following
    wrist rolls / digits      higher ratios, 3:4 and 5:4 — more lobes, tighter
                              detail. a sets horizontal lobes, b vertical.

So walking the ratio walks the move list, and the phase term is the hand-off.
The dance's own two knobs and the equation's own two knobs are the same knobs.

The trail is drawn as a glowing head with a fading tail because liquid dance is
performed WITH GLOWSTICKS — that is historically what the motion looks like, not
a styling choice.

WHAT IS NOT VERIFIED
No frame-by-frame description of the SpongeBob animation exists in text and this
build cannot watch video, so the vocabulary above comes from liquid/rave dance
sources generally — the style that scene depicts — not from that animation.

THE TEMPO IS NOT 150 AND THAT MATTERS.
Every other scene here runs at 150 BPM, where a beat is 0.4s = exactly 24 frames
at 60fps. 125 BPM makes a beat 0.48s = 28.8 frames, NOT a whole frame, so
rounding each run_time on its own drifts and the loop stops closing. T() snaps
the CUMULATIVE position to the frame grid and returns the difference:

    f0 = round(used_before * B * FPS)
    f1 = round(used_after  * B * FPS)
    run_time = (f1 - f0) / FPS

Whole frames need a multiple of 5 beats, whole bars a multiple of 4, so the
total must be a multiple of 20. 60 beats: 15 bars, 1728 frames, 28.800000s.

VERIFY THE TEMPO BEFORE POSTING — TikTok sounds are often sped-up edits.

    python3 stadium_rave.py --click 125 click.wav
    ffmpeg -i videos/StadiumRave.mp4 -i click.wav -c:v copy -shortest check.mp4

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    ShowCreation(make_thing()) leaves an orphan copy in the scene
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

BPM = float(os.environ.get("BPM", 125.0))
FPS = 60
TOTAL = 60
BODY_END = 48

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
GOLD   = "#EBCB8B"

FRAME_H = 9.0
LINE_Y  = -2.05
NOTE_Y  = -2.30          # above TikTok's caption overlay, which starts ~-2.52
EQ_Y    = 3.45
RAT_Y   = 2.95

AX, AY, AZ = 1.35, 1.35, 0.95     # amplitudes; keeps x under 1.8 after perspective
CY = 0.30                          # curve centre on screen
EPS = 0.70                         # fixed z phase so the knot is never flat

CAM_D = 7.0
ORBIT = 0.09             # ring rotation, radians per beat
PITCH = 0.32             # look down; the + sign in project() matters, see below
DELTA = 0.35             # phase advance per beat — the wave travelling
TRACE_BEATS = 2.0        # one full trace of the curve every two beats
TRAIL = 0.42             # fraction of the cycle the glow tail covers
SEGS = 12                # tail sub-segments, so opacity can fade along it

# beat, a, b, c, name.  The ratio switches on the BAR line, which is where a
# dancer changes move. a sets horizontal lobes, b sets vertical.
MOVES = [
    (0,  1, 1, 1, "arm circles"),
    (8,  1, 2, 2, "the figure eight"),
    (16, 2, 3, 2, "the hand-off"),
    (24, 3, 4, 3, "wrist rolls"),
    (32, 5, 4, 3, "full liquid"),
    (40, 1, 2, 2, "back to the eight"),
]
assert MOVES[-1][0] + 8 == BODY_END


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def stroke(pts, color=WHITE_, w=5.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners(list(pts))
    m.set_stroke(opacity=op)
    return m


def project(p, theta):
    """Rotate about the vertical axis, pitch, then a perspective divide.

    Returns the 2D point and depth factor k (k > 1 nearer, k < 1 further).
    The pitch term is + zt * sp, not -. The other sign looks UP from beneath and
    turns the figure inside out.
    """
    x, y, z = p
    c, s = np.cos(theta), np.sin(theta)
    xr = x * c + z * s
    zt = -x * s + z * c
    cp, sp = np.cos(PITCH), np.sin(PITCH)
    yr = y * cp + zt * sp
    zr = y * sp + zt * cp
    k = CAM_D / (CAM_D + zr)
    return np.array([xr * k, CY + yr * k, 0.0]), k


def ratio_at(b):
    """Returns a, b, c and the beat the current move STARTED on.

    The phase is anchored to that start rather than to absolute time, so every
    move opens on its canonical shape: 1:1 at d=0 is a straight line that opens
    into a circle, and 1:2 at d=0 is a clean figure eight. Letting d run from
    absolute zero meant the closing 1:2 arrived at d=16.8 rad and read as two
    stacked ellipses instead of an eight.
    """
    cur = MOVES[0]
    for m in MOVES:
        if b >= m[0]:
            cur = m
    return cur[1], cur[2], cur[3], cur[0]


def eye_outline(color=WHITE_, w=5.0):
    """The almond, as ONE closed stroke, so the curve can become it directly."""
    top = [np.array([x, 0.92 * np.sin(np.pi * ((x + 1.7) / 3.4)), 0.0])
           for x in np.linspace(-1.7, 1.7, 60)]
    bot = [np.array([x, -0.92 * np.sin(np.pi * ((x + 1.7) / 3.4)), 0.0])
           for x in np.linspace(1.7, -1.7, 60)]
    return stroke(top + bot + [top[0]], color, w)


def eye_extras(color=WHITE_, w=5.0):
    g = VGroup()
    g.add(stroke([np.array([0.44 * np.cos(t), 0.44 * np.sin(t), 0.0])
                  for t in np.linspace(0, 2 * np.pi, 61)], color, w))
    g.add(stroke([np.array([0.13 * np.cos(t), 0.13 * np.sin(t), 0.0])
                  for t in np.linspace(0, 2 * np.pi, 20)], color, w * 1.7))
    for x, y in ((1.95, 0.34), (2.20, -0.30)):
        s = 0.11
        g.add(stroke([np.array([x - s, y - s, 0]), np.array([x + s, y - s, 0]),
                      np.array([x + s, y + s, 0]), np.array([x - s, y + s, 0]),
                      np.array([x - s, y - s, 0])], color, w * 0.6))
    return g


class StadiumRave(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.ghost = stroke([ORIGIN, RIGHT], GREY, 2.2, 0.22)
        self.tails = VGroup(*[stroke([ORIGIN, RIGHT], WHITE_, 4.0, 0.0)
                              for _ in range(2 * SEGS)])
        self.heads = VGroup(Dot(ORIGIN, radius=0.075, fill_color=WHITE_),
                            Dot(ORIGIN, radius=0.075, fill_color=GOLD))
        self.art = VGroup(self.ghost, self.tails, self.heads)
        self.moving = False
        self.art.add_updater(self.update_art)
        self.add(self.art)

        self.sequence()

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

    def beat_pos(self):
        return self.clock.get_value() / self.B

    # ------------------------------------------------------------------
    def pt(self, u, a, bq, c, delta, s, theta):
        p = np.array([AX * s * np.sin(a * u + delta),
                      AY * s * np.sin(bq * u),
                      AZ * s * np.sin(c * u + EPS)])
        return project(p, theta)

    def update_art(self, mob):
        if not self.moving:
            return
        b = self.beat_pos()
        a, bq, c, start = ratio_at(b)
        delta = DELTA * (b - start)
        theta = ORBIT * b
        # amplitude pulses on every beat — this is the bounce
        s = 1.0 + 0.10 * abs(np.sin(np.pi * b))

        us = np.linspace(0.0, 2 * np.pi, 361)
        self.ghost.set_points_as_corners(
            [self.pt(u, a, bq, c, delta, s, theta)[0] for u in us])
        self.ghost.set_stroke(GREY, width=2.2, opacity=0.22)

        # two tracers half a cycle apart: the hand-to-hand hand-off
        head_u = 2 * np.pi * (b / TRACE_BEATS)
        for j, (off, col) in enumerate(((0.0, WHITE_), (np.pi, GOLD))):
            for i in range(SEGS):
                f0 = TRAIL * (1.0 - (i + 1) / SEGS)
                f1 = TRAIL * (1.0 - i / SEGS)
                seg_us = np.linspace(head_u + off - f1 * 2 * np.pi,
                                     head_u + off - f0 * 2 * np.pi, 7)
                pts = [self.pt(u, a, bq, c, delta, s, theta)[0] for u in seg_us]
                m = self.tails[j * SEGS + i]
                m.set_points_as_corners(pts)
                bright = (i + 1) / SEGS          # 1 at the head, small at the tail
                m.set_stroke(col, width=1.6 + 5.4 * bright ** 1.6,
                             opacity=0.10 + 0.90 * bright ** 1.4)
            hp, hk = self.pt(head_u + off, a, bq, c, delta, s, theta)
            self.heads[j].move_to(hp)
            self.heads[j].set_opacity(1.0)

    def say(self, s, beats, color=WHITE_, size=26):
        new = txt(s, size, color, w=4.4)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.12 * UP),
                      FadeIn(new, shift=0.12 * UP), run_time=self.T(beats))
            self.note = new

    # ------------------------------------------------------------------
    def sequence(self):
        eq = txt("x = sin(au+d)   y = sin(bu)   z = sin(cu)", 21, GREY,
                 bold=False, w=4.5)
        eq.move_to(np.array([0, EQ_Y, 0]))
        self.add(eq)
        self.moving = True

        self.rat = None
        for k, (start, a, bq, c, name) in enumerate(MOVES):
            new = txt(f"a : b  =  {a} : {bq}", 27, GOLD, w=3.0)
            new.move_to(np.array([0, RAT_Y, 0]))
            lab = txt(name, 26, WHITE_, w=4.4)
            lab.move_to(np.array([0, NOTE_Y, 0]))
            # ratio and name change in ONE play. Separate plays put the label a
            # beat ahead of the name, which reads as a mismatch on screen.
            if self.rat is None:
                self.rat, self.note = new, lab
                self.play(FadeIn(new), FadeIn(lab), run_time=self.T(2))
            else:
                self.play(Transform(self.rat, new),
                          FadeOut(self.note, shift=0.12 * UP),
                          FadeIn(lab, shift=0.12 * UP), run_time=self.T(2))
                self.note = lab
            self.wait(self.T(6))

        # 48–52  the curve becomes the mark
        self.moving = False
        self.pad_to(BODY_END)
        outline = eye_outline().move_to(np.array([0, 0.95, 0])).scale(0.78)
        extras = eye_extras().move_to(np.array([0, 0.95, 0])).scale(0.78)
        extras.shift(outline.get_center() - extras.get_center())
        self.play(Transform(self.ghost, outline),
                  *[FadeOut(m) for m in self.tails],
                  FadeOut(self.heads), FadeOut(self.note), FadeOut(self.rat),
                  FadeOut(eq), run_time=self.T(3))
        self.note = None
        self.play(FadeIn(extras), run_time=self.T(1))

        # 52–60  the ask
        words = VGroup(txt("PAUSE", 21), txt("OBSERVE", 21), txt("LEARN", 21)) \
            .arrange(RIGHT, buff=0.44).move_to(np.array([0, -0.75, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(2))
        cta = txt("Follow for the math behind AI", 28)
        handle = txt("@observer.collapse", 22, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.20)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(2))
        self.pad_to(TOTAL - 2)
        self.clock.clear_updaters()
        self.art.clear_updaters()
        self.play(FadeOut(self.ghost), FadeOut(extras), FadeOut(words),
                  FadeOut(cg), run_time=self.T(2))
