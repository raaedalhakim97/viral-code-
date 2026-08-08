"""
stadium_rave — lines dancing in x, y, z. Promo, cut to SpongeBob's "Stadium Rave".

    BPM=125 manimgl stadium_rave.py StadiumRave -w -r 1080x1920

60 beats = 15 bars = 28.800s at 125 BPM.

NO FIGURE. The subject is 18 straight lines standing in a ring in 3D, and the
dance is applied to them directly: each line bobs on Y, leans on X and Z, and
stretches along its own length. Nothing is a body.

WHAT THE MOTION IS BASED ON
The source is the "Jellyfish Jam" rave (SpongeBob S1E7b, 1999) — the track is
"Stadium Rave" by Mark Govener, APM stock techno from Clubmix, in the same lane
as 2 Unlimited's "Get Ready For This". No frame-by-frame choreography for that
scene exists in text, and this build could not watch the footage, so what is
reproduced here is the motion CHARACTER of four-on-the-floor rave, not a
transcription of specific moves:

    bounce  |sin(pi*b)|     one hard hit per beat, on Y
    sway     sin(pi*b)      reverses every beat, so the rock spans two beats
    lean    radial, driven by sway, on X and Z together
    stretch  each line grows on the beat and settles between

    phase offset  2*i/N     the same motion delayed around the ring, so a wave
                            travels through the formation instead of all 18
                            lines moving as one block

The two rhythms are the point. One alone is a metronome; bouncing on the beat
while rocking across two is what makes it read as dancing.

DEPTH IS REAL, NOT FAKED
The projection is done here rather than with manimgl's 3D camera — a rotation
about the vertical axis, then a perspective divide, then per-line stroke width
and opacity from the resulting depth. Near lines are thick and bright, far lines
thin and dim, and the ring orbits about one turn over the video.

THE TEMPO IS NOT 150 AND THAT MATTERS.
Every other scene in this repo runs at 150 BPM, where one beat is 0.4s = exactly
24 frames at 60fps. 125 BPM makes a beat 0.48s = 28.8 frames, NOT a whole frame,
so rounding each run_time on its own drifts and the loop stops closing. T()
snaps the CUMULATIVE position to the frame grid and returns the difference:

    f0 = round(used_before * B * FPS)
    f1 = round(used_after  * B * FPS)
    run_time = (f1 - f0) / FPS

At 125 BPM whole frames need a multiple of 5 beats and whole bars a multiple of
4, so the total must be a multiple of 20. 60 beats: 15 bars, 1728 frames,
28.800000s exactly.

VERIFY THE TEMPO BEFORE POSTING. TikTok sounds are frequently sped-up edits.

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

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
GOLD   = "#EBCB8B"

FRAME_H = 9.0
LINE_Y  = -2.05
NOTE_Y  = -2.30          # above TikTok's caption overlay, which starts ~-2.52

N = 18                   # lines in the ring, and parts in every target shape
CAM_D = 7.0              # eye distance for the perspective divide
ORBIT = 0.10             # radians of ring rotation per beat (~1 turn / video)
PITCH = 0.35             # look DOWN on the ring by 20 deg. Without this the
                         # camera sits level with the ring, it projects to a
                         # flat band, and the circle is invisible.
RAD = 1.45               # ring radius; front lines reach x ~2.39 of 2.53


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def stroke(pts, color=WHITE_, w=6.0):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners(list(pts))
    return m


def split_curve(pts, k):
    """Cut a polyline into k pieces so k lines can fly into it."""
    pts = list(pts)
    n = len(pts) - 1
    out = []
    for j in range(k):
        a = int(round(j * n / k))
        c = max(int(round((j + 1) * n / k)), a + 1)
        out.append(pts[a:c + 1])
    return out


# --------------------------------------------------------------------------
def project(p, theta):
    """Rotate about the vertical axis, then a perspective divide.

    Returns the 2D point and the depth factor k — k > 1 is nearer than the ring
    centre, k < 1 is further. Stroke width and opacity both come off k, which is
    what actually sells the three dimensions on a flat phone screen.
    """
    x, y, z = p
    c, s = np.cos(theta), np.sin(theta)
    xr = x * c + z * s
    zt = -x * s + z * c
    cp, sp = np.cos(PITCH), np.sin(PITCH)
    # + zt here, not -. Looking DOWN puts the near side of the ring LOWER on
    # screen and the far side higher; the other sign looks up from below and
    # inverts the whole formation.
    yr = y * cp + zt * sp
    zr = y * sp + zt * cp
    k = CAM_D / (CAM_D + zr)
    return np.array([xr * k, yr * k, 0.0]), k


def ring_pose(b):
    """The dance, as 24 lines. Returns (points, depth) per line."""
    theta = ORBIT * b
    out = []
    for i in range(N):
        a = 2 * np.pi * i / N
        r = RAD
        bi = b - 2.0 * i / N                   # the wave travels round the ring
        bounce = abs(np.sin(np.pi * bi))
        sway = np.sin(np.pi * bi)

        foot_y = -1.05 + 0.45 * bounce
        length = 2.90 + 0.85 * bounce          # stretches on the hit
        lean = 0.35 * sway                     # radial, so X and Z together

        foot = np.array([r * np.cos(a), foot_y, r * np.sin(a)])
        head = foot + np.array([lean * np.cos(a), length, lean * np.sin(a)])
        p0, k0 = project(foot, theta)
        p1, k1 = project(head, theta)
        out.append(([p0, p1], 0.5 * (k0 + k1)))
    return out


def sine_parts(color=WHITE_, amp=1.05, cycles=1.6, w=6.0):
    xs = np.linspace(-2.10, 2.10, 241)
    ys = amp * np.sin(cycles * np.pi * xs / 2.10)
    pts = [np.array([x, y + 0.10, 0.0]) for x, y in zip(xs, ys)]
    return VGroup(*[stroke(p, color, w) for p in split_curve(pts, N)])


def square_parts(color=WHITE_, harmonics=7, amp=1.05, w=6.0):
    """A real odd-harmonic partial sum, so the overshoot at each edge is genuine
    Gibbs ringing — and it is the figure from the Fourier video already posted."""
    xs = np.linspace(-2.10, 2.10, 481)
    t = np.pi * xs / 1.05
    ys = np.zeros_like(xs)
    for n in range(1, harmonics * 2, 2):
        ys += np.sin(n * t) / n
    ys *= amp * 4 / np.pi / 1.18
    pts = [np.array([x, y + 0.10, 0.0]) for x, y in zip(xs, ys)]
    return VGroup(*[stroke(p, color, w) for p in split_curve(pts, N)])


def eye_parts(color=WHITE_, w=5.0):
    """18 pieces: 5 + 5 on the lids, 5 on the pupil ring, 1 pupil, 2 chips."""
    g = VGroup()
    for sign in (1, -1):
        lid = [np.array([x, sign * 0.92 * np.sin(np.pi * ((x + 1.7) / 3.4)), 0.0])
               for x in np.linspace(-1.7, 1.7, 81)]
        for piece in split_curve(lid, 5):
            g.add(stroke(piece, color, w))
    ring = [np.array([0.44 * np.cos(t), 0.44 * np.sin(t), 0.0])
            for t in np.linspace(0, 2 * np.pi, 61)]
    for piece in split_curve(ring, 5):
        g.add(stroke(piece, color, w))
    g.add(stroke([np.array([0.13 * np.cos(t), 0.13 * np.sin(t), 0.0])
                  for t in np.linspace(0, 2 * np.pi, 16)], color, w * 1.6))
    for x, y in ((1.95, 0.34), (2.20, -0.30)):
        s = 0.11
        g.add(stroke([np.array([x - s, y - s, 0]), np.array([x + s, y - s, 0]),
                      np.array([x + s, y + s, 0]), np.array([x - s, y + s, 0]),
                      np.array([x - s, y - s, 0])], color, w * 0.6))
    assert len(g) == N, f"eye has {len(g)} parts, needs {N}"
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

        self.lines = VGroup(*[stroke(p) for p, _ in ring_pose(0.0)])
        self.dancing = False
        self.lines.add_updater(self.update_lines)
        self.add(self.lines)

        self.sequence()

    # ------------------------------------------------------------------
    def T(self, beats):
        """Cumulative frame snap — at 125 BPM a beat is 28.8 frames, so rounding
        each interval on its own would drift. This cannot."""
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

    def update_lines(self, mob):
        if not self.dancing:
            return
        for part, (pts, k) in zip(mob, ring_pose(self.beat_pos())):
            part.set_points_as_corners(pts)
            part.set_stroke(width=4.4 * k ** 2.2,
                            opacity=float(np.clip(0.45 + 1.05 * (k - 0.80), 0.34, 1.0)))

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
        """Freeze the ring, fly all 24 lines into the shape."""
        self.dancing = False
        self.play(Transform(self.lines, target), run_time=self.T(beats))

    def resume(self, beats):
        """Back to the ring. The updater rewrites every point each frame, so the
        Transform only has to land near the pose, not on it."""
        snap = VGroup()
        for pts, k in ring_pose(self.beat_pos()):
            s = stroke(pts, WHITE_, 4.4 * k ** 2.2)
            s.set_stroke(opacity=float(np.clip(0.45 + 1.05 * (k - 0.80), 0.34, 1.0)))
            snap.add(s)
        self.play(Transform(self.lines, snap), run_time=self.T(beats))
        self.dancing = True

    # ------------------------------------------------------------------
    def sequence(self):
        # 0–14  the hook: 24 lines, nothing else
        self.dancing = True
        self.wait(self.T(14))

        # 14–20  name it
        self.say("every video here is one line", 3, GREY, 25)
        self.wait(self.T(3))

        # 20–28  the ring flattens into a wave
        self.morph(sine_parts(), 3)
        self.say("moving on the beat", 2, WHITE_, 26)
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
        self.play(self.lines.animate.move_to(np.array([0, 0.95, 0])).scale(0.80),
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
        self.lines.clear_updaters()
        self.play(FadeOut(self.lines), FadeOut(words), FadeOut(cg),
                  run_time=self.T(2))
