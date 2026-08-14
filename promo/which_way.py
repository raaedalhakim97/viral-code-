"""
which_way — which way is it spinning? 40.0s.

    BPM=150 manimgl which_way.py WhichWay -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

AN ARGUMENT VIDEO. Its job is comments, and the good kind: people arguing with
each other rather than with the page. A globe of dots turns on a vertical axis
with every depth cue removed, and it is genuinely bistable — half the room sees
it going left, half sees it going right, and BOTH ARE CORRECT.

THAT IS NOT A FIGURE OF SPEECH, IT IS PROVEN AT IMPORT. The dots sit on rings,
an even number to a ring, equally spaced in angle around it. Rotating about the
vertical axis by +a and by −a produce point sets whose flat projections are
identical — because each ring is symmetric under z -> −z, and an orthographic
projection throws z away. The measured difference between the two pictures is
2e-15 — float noise, not a visible quantity, over 132 dots and 96 angles. There
is nothing on screen to tell them apart.

    forward and backward are the SAME PICTURE. There is no fact of the matter
    on screen. Your brain supplies the missing sign.

THEN THE PAYOFF, WHICH IS THE HONEST BIT. Fade in one depth cue — near dots
brighter and larger — and the direction snaps into place. Flip that cue and it
snaps the other way, with the motion itself completely unchanged. The viewer
watches their own perception reverse while nothing about the animation does.

    a flat picture has no depth. your brain was guessing, and it never told you.

WHY THE DOTS MUST BE IDENTICAL. With the cue off, every dot is the same size,
colour and opacity. Any variation at all — a gradient, a connecting line, a
size cue — collapses the ambiguity and the video quietly stops being true.

VERIFIED AT IMPORT
    +a and -a project to identical pictures    to 2e-15, over 96 angles
    every latitude ring is angle-symmetric     which is why the above holds
    the poles sit on the axis                  they must not drift
    the rotation rate is constant              any wobble leaks the direction

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats), always a multiple of 0.25 beats
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN, END_ASK, END_BOTH = 8, 40, 56
END_REVEAL, END_WHY, END_FOLLOW = 78, 86, 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
TITLE_Y = 3.50
NOTE_Y  = -3.45
LINE_Y  = -2.05

# ------------------------------------------------------------------ the globe
# Dots per ring scale with the ring's circumference, so the density over the
# sphere is even and it reads as a solid turning body rather than as stacked
# rows. Every count is forced EVEN, which is what makes the ring symmetric
# under z -> -z, which is what makes the whole video true.
# The rings are spaced evenly in HEIGHT, not in latitude, so they land evenly
# on screen instead of bunching near the equator. Alternate rings are offset by
# half a step, which kills the vertical striping — and a half-step offset is
# exactly the one phase shift that leaves a ring symmetric under z -> -z, so
# the proof below survives it.
HEIGHTS = [-0.92, -0.69, -0.46, -0.23, 0.0, 0.23, 0.46, 0.69, 0.92]
EQUATOR_DOTS = 18
R_SCREEN = 2.12
SECONDS_PER_TURN = 4.0            # 10 beats. constant, always.


def ring_count(r):
    return max(6, 2 * int(round(EQUATOR_DOTS * r / 2)))


RING = []                          # (ring radius, height, start angle)
for _i, _y in enumerate(HEIGHTS):
    _r = float(np.sqrt(1.0 - _y * _y))
    _n = ring_count(_r)
    assert _n % 2 == 0, "an odd ring is not symmetric under z -> -z"
    _off = (np.pi / _n) * (_i % 2)
    for _j in range(_n):
        RING.append((_r, _y, _off + 2 * np.pi * _j / _n))
RING.append((0.0, 1.0, 0.0))       # poles
RING.append((0.0, -1.0, 0.0))
N = len(RING)

_ANG = np.array([p for _, _, p in RING])
_RAD = np.array([r for r, _, _ in RING])
_HGT = np.array([y for _, y, _ in RING])


def _project(a, sign):
    """Screen coordinates after rotating by sign*a about the vertical axis."""
    return _RAD * np.cos(_ANG + sign * a), _HGT


def _canonical(a, sign):
    """The picture as a set: points sorted so two identical pictures compare
    equal no matter which dot drew which."""
    x, y = _project(a, sign)
    return np.stack([x, y])[:, np.lexsort((x, y))]


_worst = 0.0
for _a in np.linspace(0, 2 * np.pi, 96):
    _worst = max(_worst,
                 float(np.abs(_canonical(_a, +1) - _canonical(_a, -1)).max()))

assert _worst < 1e-12, f"the two directions are distinguishable by {_worst}"
assert abs(_HGT[-1] + 1.0) < 1e-12 and abs(_HGT[-2] - 1.0) < 1e-12
assert _RAD[-1] == 0.0 and _RAD[-2] == 0.0, "the poles must sit on the axis"

DOT_R = 0.050


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


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


class WhichWay(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        # 0 = no depth cue at all (ambiguous). +1 = near dots brighter.
        # -1 = far dots brighter, which reverses what you see with the motion
        # itself completely unchanged.
        self.cue = ValueTracker(0.0)

        self.build()
        self.open_card()
        self.stage_ask()
        self.stage_both()
        self.stage_reveal()
        self.stage_why()
        self.stage_follow()
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

    def say(self, s, beats=2, color=WHITE_, size=26):
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    # ---------------------------------------------------------- the globe
    def angle(self):
        return 2 * np.pi * self.clock.get_value() / SECONDS_PER_TURN

    def build(self):
        self.dots = VGroup()
        for k in range(N):
            d = Dot(ORIGIN, radius=DOT_R, fill_color=WHITE_)

            def up(mo, k=k):
                a = self.angle() + _ANG[k]
                x = _RAD[k] * np.cos(a) * R_SCREEN
                y = _HGT[k] * R_SCREEN
                z = _RAD[k] * np.sin(a)          # depth, thrown away on screen
                mo.move_to(np.array([x, y, 0.0]))
                c = self.cue.get_value()
                # with c = 0 every dot is identical, which is the whole trick
                mo.set_opacity(float(np.clip(0.85 + 0.55 * c * z, 0.12, 1.0)))
                mo.set_width(2 * DOT_R * float(np.clip(1 + 0.5 * c * z, 0.4, 1.7)))

            d.add_updater(up)
            self.dots.add(d)

    # ------------------------------------------------------------------
    def open_card(self):
        self.title = VGroup(txt("WHICH WAY", 42, GOLD, w=3.8),
                            txt("IS IT SPINNING?", 34, WHITE_, w=4.4)) \
            .arrange(DOWN, buff=0.14).move_to(np.array([0, TITLE_Y, 0]))
        self.add(self.dots)
        self.play(FadeIn(self.title), FadeIn(self.dots), run_time=self.T(2.5))
        self.say("left, or right?", 3, GOLD)
        self.pad_to(END_OPEN)

    # ==================================================================
    # Let them look. Let them commit.
    # ==================================================================
    def stage_ask(self):
        self.say("pick one. out loud.", 4)
        self.pad_to(20)
        self.say("keep watching it.", 4)
        self.pad_to(32)
        self.say("still sure?", 4)
        self.pad_to(END_ASK)

    # ==================================================================
    # The line that starts the argument.
    # ==================================================================
    def stage_both(self):
        self.say("half of you said left.", 3.5, SKY)
        self.say("half of you said right.", 3.5, ROSE)
        self.say("you are both correct.", 4, GOLD)
        self.pad_to(END_BOTH)

    # ==================================================================
    # One cue. Then the same cue, flipped. The motion never changes.
    # ==================================================================
    def stage_reveal(self):
        self.say("watch. i am only changing the brightness.", 3.5)
        self.play(self.cue.animate.set_value(1.0), run_time=self.T(3),
                  rate_func=smooth)
        self.say("now it is obviously going one way.", 4)
        self.pad_to(67)
        self.play(self.cue.animate.set_value(-1.0), run_time=self.T(3.5),
                  rate_func=smooth)
        self.say("and now it is obviously going the other.", 4)
        self.say("the dots never changed direction. not once.", 3.5)
        self.pad_to(END_REVEAL)

    # ==================================================================
    # Why.
    # ==================================================================
    def stage_why(self):
        self.play(self.cue.animate.set_value(0.0), run_time=self.T(2),
                  rate_func=smooth)
        self.say("a flat picture has no depth.", 3)
        self.say("your brain guessed — and never told you.", 3)
        self.pad_to(END_WHY)

    # ==================================================================
    # The ask.
    # ==================================================================
    def stage_follow(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None

        f1 = txt("COMMENT WHICH WAY", 32, GOLD, w=4.5)
        f1.move_to(np.array([0, 0.90, 0]))
        f2 = txt("you saw it first", 27, WHITE_, w=4.2)
        f2.move_to(np.array([0, 0.24, 0]))
        f3 = txt("then follow, and check the replies", 22, GREY,
                 bold=False, w=4.4)
        f3.move_to(np.array([0, -0.52, 0]))
        self.card = VGroup(f1, f2, f3)
        self.play(FadeIn(f1, scale=1.12), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.play(FadeIn(f2), run_time=self.T(1))
        self.play(FadeIn(f3), run_time=self.T(1))
        self.pad_to(END_FOLLOW - 1.5)
        self.play(FadeOut(self.card), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.10, 0])).scale(0.74)
        self.play(ShowCreation(eye), run_time=self.T(2.5))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.42, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.5))
        cta = txt("@observer.collapse", 25, GREY, bold=False)
        cta.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cta, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cta),
                  run_time=self.T(1.5))
