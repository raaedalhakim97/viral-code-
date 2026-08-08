"""
stadium_rave — the line dances. Promo, cut to SpongeBob's "Stadium Rave".

    BPM=125 manimgl stadium_rave.py StadiumRave -w -r 1080x1920

60 beats = 15 bars = 28.800s at 125 BPM.

THE TEMPO IS NOT 150 AND THAT MATTERS.
Every other scene in this repo runs at 150 BPM, where one beat is 0.4s = exactly
24 frames at 60fps. "Stadium Rave" is 125 BPM: one beat is 0.48s = 28.8 frames,
which is NOT a whole frame. Rounding each run_time on its own would drift by a
frame here and there and the loop would not close.

T() therefore snaps the CUMULATIVE position to the frame grid and returns the
difference, so error can never accumulate:

    f0 = round(used_before * B * FPS)
    f1 = round(used_after  * B * FPS)
    run_time = (f1 - f0) / FPS

At 125 BPM a whole number of frames needs a multiple of 5 beats, and a whole
number of bars needs a multiple of 4 — so the total has to be a multiple of 20.
60 beats satisfies both: 15 bars, 1728 frames, 28.800000s exactly.

VERIFY THE TEMPO BEFORE POSTING. TikTok sounds are frequently sped-up edits, and
a sped-up "Stadium Rave" will not be 125. Check with:

    python3 stadium_rave.py --click 125 click.wav
    ffmpeg -i videos/StadiumRave.mp4 -i click.wav -c:v copy -shortest check.mp4

If the clicks drift against the dance, re-render with the real BPM — nothing in
this file is hard-coded to 125.

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

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
GOLD   = "#EBCB8B"

FRAME_H = 9.0
LINE_Y  = -2.05
NOTE_Y  = -2.30          # feet reach ~-1.9; TikTok's caption overlay starts
                         # around -2.52, so -2.72 would have been under it

SCALE = 1.55             # figure is ~3.4 units tall, ~38% of frame
BASE_Y = -0.20           # hips at rest


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def stroke(pts, color=WHITE_, w=7.5):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners(list(pts))
    return m


def polar(o, ang, r):
    return o + np.array([r * np.cos(ang), r * np.sin(ang), 0.0])


# --------------------------------------------------------------------------
def dancer_points(b):
    """Pose at beat position b. Six point-lists: head, torso, arms, legs.

    bounce = |sin(pi*b)| hits once per beat; sway = sin(pi*b) reverses each beat,
    so the figure rocks over two beats while bouncing on one.

    Exaggeration is the whole job here. The first pass used small amplitudes and
    folded the forearms back across the head, which read as a stick figure
    fidgeting rather than dancing. Arms now go up and OUT, clear of the head,
    and the forearms punch toward vertical on every beat.
    """
    bounce = abs(np.sin(np.pi * b))
    sway = np.sin(np.pi * b)
    S = SCALE

    hip = np.array([0.20 * sway * S, (BASE_Y + 0.30 * bounce) * S, 0.0])
    lean = 0.26 * sway
    up = np.array([-np.sin(lean), np.cos(lean), 0.0])

    squash = 1.0 - 0.12 * (1.0 - bounce)
    sh = hip + up * (0.92 * S * squash)
    head_c = sh + up * (0.47 * S)

    # upper arms sit at ~140 deg / 40 deg so the elbows clear the head;
    # forearms swing from splayed to near-vertical as the beat lands
    uL = np.pi * 0.80 + 0.12 * sway
    uR = np.pi * 0.20 + 0.12 * sway
    fL = np.pi * 0.72 - 0.55 * bounce + 0.12 * sway
    fR = np.pi * 0.28 + 0.55 * bounce + 0.12 * sway
    eL, eR = polar(sh, uL, 0.48 * S), polar(sh, uR, 0.48 * S)
    hL, hR = polar(eL, fL, 0.46 * S), polar(eR, fR, 0.46 * S)

    # one knee drives up on each half of the sway
    kickL, kickR = 0.75 * max(0.0, sway), 0.75 * max(0.0, -sway)
    tL = -np.pi / 2 - 0.52 + kickL
    tR = -np.pi / 2 + 0.52 - kickR
    kL, kR = polar(hip, tL, 0.52 * S), polar(hip, tR, 0.52 * S)
    fLo = polar(kL, tL + 0.20 - 0.90 * kickL, 0.50 * S)
    fRo = polar(kR, tR - 0.20 + 0.90 * kickR, 0.50 * S)

    ring = [head_c + np.array([0.24 * S * np.cos(t), 0.24 * S * np.sin(t), 0.0])
            for t in np.linspace(0, 2 * np.pi, 26)]
    return [ring, [hip, sh], [sh, eL, hL], [sh, eR, hR],
            [hip, kL, fLo], [hip, kR, fRo]]


def sine_parts(color=WHITE_, amp=1.05, cycles=1.6, w=6.0):
    """Six arcs of a sine wave — one per body part, so the dancer unfolds."""
    g = VGroup()
    xs = np.linspace(-2.10, 2.10, 6 * 12 + 1)
    ys = amp * np.sin(cycles * np.pi * xs / 2.10)
    for k in range(6):
        seg = [np.array([xs[i], ys[i] + 0.10, 0.0])
               for i in range(k * 12, k * 12 + 13)]
        g.add(stroke(seg, color, w))
    return g


def square_parts(color=WHITE_, harmonics=7, amp=1.05, w=6.0):
    """The same six arcs, but the curve is a real odd-harmonic partial sum —
    the square wave from the Fourier video, so the promo quotes the page."""
    g = VGroup()
    xs = np.linspace(-2.10, 2.10, 6 * 24 + 1)
    t = np.pi * xs / 1.05
    ys = np.zeros_like(xs)
    for n in range(1, harmonics * 2, 2):
        ys += np.sin(n * t) / n
    ys *= amp * 4 / np.pi / 1.18
    for k in range(6):
        seg = [np.array([xs[i], ys[i] + 0.10, 0.0])
               for i in range(k * 24, k * 24 + 25)]
        g.add(stroke(seg, color, w))
    return g


def eye_parts(color=WHITE_, w=5.0):
    """Six parts again: two lids, pupil ring, pupil, two drifting squares."""
    g = VGroup()
    for sign in (1, -1):
        g.add(stroke([np.array([x, sign * 0.92 * np.sin(np.pi * ((x + 1.7) / 3.4)),
                                0.0]) for x in np.linspace(-1.7, 1.7, 40)], color, w))
    g.add(stroke([np.array([0.44 * np.cos(t), 0.44 * np.sin(t), 0.0])
                  for t in np.linspace(0, 2 * np.pi, 30)], color, w))
    g.add(stroke([np.array([0.13 * np.cos(t), 0.13 * np.sin(t), 0.0])
                  for t in np.linspace(0, 2 * np.pi, 16)], color, w * 1.6))
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

        self.body = VGroup(*[stroke(p) for p in dancer_points(0.0)])
        self.dancing = False
        self.body.add_updater(self.update_pose)
        self.add(self.body)

        self.sequence()

    # ------------------------------------------------------------------
    def T(self, beats):
        """Cumulative frame snap. At 125 BPM a beat is 28.8 frames, so rounding
        each interval independently would drift; this cannot."""
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

    def update_pose(self, mob):
        if not self.dancing:
            return
        for part, pts in zip(mob, dancer_points(self.beat_pos())):
            part.set_points_as_corners(pts)

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

    def morph(self, target, beats):
        """Freeze the pose, fly the six strokes into the shape."""
        self.dancing = False
        self.play(Transform(self.body, target), run_time=self.T(beats))

    def resume(self, beats):
        """Back to the dancer. The updater rewrites the points every frame, so
        the Transform only has to land near the pose, not on it."""
        self.play(Transform(self.body,
                            VGroup(*[stroke(p) for p in
                                     dancer_points(self.beat_pos())])),
                  run_time=self.T(beats))
        self.dancing = True

    # ------------------------------------------------------------------
    def sequence(self):
        # 0–12  the hook: nothing but the dance
        self.dancing = True
        self.wait(self.T(12))

        # 12–20  name what it is
        self.say("every video here is one line", 4, GREY, 25)
        self.wait(self.T(4))

        # 20–28  it unfolds into a wave
        self.morph(sine_parts(), 3)
        self.say("moving to the beat", 2, WHITE_, 26)
        self.wait(self.T(1))
        self.resume(2)

        # 28–36  the square wave, quoting the Fourier video
        self.morph(square_parts(), 3)
        self.say("7 harmonics", 2, GOLD, 26)
        self.wait(self.T(1))
        self.resume(2)

        # 36–44  the pitch
        self.say("math you can watch move", 4, WHITE_, 28)
        self.wait(self.T(4))

        # 44–52  collapse into the mark
        self.morph(eye_parts(), 4)
        self.play(self.body.animate.move_to(np.array([0, 0.95, 0])).scale(0.80),
                  FadeOut(self.note), run_time=self.T(2))
        self.note = None
        words = VGroup(txt("PAUSE", 21), txt("OBSERVE", 21), txt("LEARN", 21)) \
            .arrange(RIGHT, buff=0.44).move_to(np.array([0, -0.75, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(2))

        # 52–60  the ask
        cta = txt("Follow for the math behind AI", 28)
        handle = txt("@observer.collapse", 22, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.20)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(2))
        self.pad_to(TOTAL - 2)
        self.clock.clear_updaters()
        self.body.clear_updaters()
        self.play(FadeOut(self.body), FadeOut(words), FadeOut(cg),
                  run_time=self.T(2))
