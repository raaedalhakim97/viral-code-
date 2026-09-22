"""
times_table_dance — the times tables, drawn on a circle. 40.0s.

    BPM=150 manimgl times_table_dance.py TimesTableDance -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

"MATH THAT DANCES" — the third in the lane after dancing_equation.py (a
2x2 matrix) and dancing_fourier.py (epicycles). Different mechanism: no
arrows, no matrix, just 200 dots and one multiplication.

THE INSTRUCTION, and it is the whole instruction:

    put 200 dots round a circle, numbered 0 to 199
    join every dot n to dot k*n
    that's it

k = 2 gives a cardioid. k = 3 gives a nephroid. And the pattern is
absurdly simple:

        the k times table  ->  k - 1 lobes

BEAT-LOCKED DANCE. k is driven by a ValueTracker and every step lands on
a downbeat, so the figure smears while k is between integers and SNAPS
into a clean shape exactly on the beat. That is the dance, and it is why
this one is silent by design — whatever track gets dropped on it, the
shapes land on the count.

VERIFIED AT IMPORT
    the envelope of the chords is computed numerically and its cusps
    counted, for every k the video shows: the count is always k - 1
    the envelope's inner radius is checked against (k-1)/(k+1)
    the ring is asserted to sit inside the platform safe box

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    AnimationGroup rebuilds a VGroup of its children, so a group carrying
    an updater must be self.add()ed, never introduced by LaggedStartMap
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_HOOK, END_BUILD = 5, 24
END_THREE, END_RULE = 40, 56
END_DANCE, END_TAKE, END_SHARE = 80, 88, 92

SERIES = "MATH THAT DANCES"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"
GREEN  = "#A3BE8C"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
EQ_Y   = 3.08
WORK_Y = 2.30
NOTE_Y = -2.36
LINE_Y = -2.05

# platform safe zone, 1080x1920: TikTok/Reels cover ~320px of the bottom
# and ~160px on the right for the action rail.
SAFE_X, SAFE_BOT = 1.68, -2.58
assert NOTE_Y - 0.20 >= SAFE_BOT

# ------------------------------------------------------------------ numbers
N = 200
K_FIRST, K_LAST = 2, 12
DANCE = list(range(5, 13))                # the beat-locked march, 5 -> 12


def _envelope(k, M=40000):
    """Envelope of the chord family, solved as F = dF/dtheta = 0."""
    th = np.linspace(0, 2 * np.pi, M, endpoint=False)
    ax, ay = np.cos(th), np.sin(th)
    bx, by = np.cos(k * th), np.sin(k * th)
    a, b = -(by - ay), (bx - ax)
    c = (by - ay) * ax - (bx - ax) * ay
    da = -(k * np.cos(k * th) - np.cos(th))
    db = -k * np.sin(k * th) + np.sin(th)
    dc = ((k * np.cos(k * th) - np.cos(th)) * ax + (by - ay) * (-np.sin(th))
          - (-k * np.sin(k * th) + np.sin(th)) * ay - (bx - ax) * np.cos(th))
    det = a * db - b * da
    ok = np.abs(det) > 1e-9
    d = np.where(ok, det, 1.0)
    return np.stack([((-c * db + b * dc) / d)[ok],
                     ((-a * dc + c * da) / d)[ok]], 1)


def _lobes(k):
    """Cusps of the envelope = points where it is traced at zero speed."""
    e = np.diff(_envelope(k), axis=0)
    sp = np.hypot(e[:, 0], e[:, 1])
    low = sp < sp.mean() * 0.05
    return int(np.sum((low.astype(int) - np.roll(low, 1).astype(int)) == 1))


for _k in range(K_FIRST, K_LAST + 1):
    assert _lobes(_k) == _k - 1, (_k, _lobes(_k))          # the on-screen claim
    _r = np.hypot(*_envelope(_k).T)
    assert abs(_r.min() - (_k - 1) / (_k + 1)) < 5e-3
    assert abs(_r.max() - 1.0) < 5e-3

# ------------------------------------------------------------------ layout
RING_C = np.array([0.0, 0.05, 0])
R = 1.55
assert R <= SAFE_X - 0.08
assert RING_C[1] - R - 0.12 > NOTE_Y + 0.20        # ring clears the caption
assert RING_C[1] + R + 0.12 < WORK_Y - 0.16        # ...and the working line


def P(u):
    """Dot number u (may be fractional while k is mid-step), from the top."""
    a = 2 * np.pi * u / N + np.pi / 2
    return RING_C + R * np.array([np.cos(a), np.sin(a), 0])


def wheel(n):
    """Gold -> rose -> sky -> gold, once round the ring."""
    stops = [GOLD, ROSE, SKY, GOLD]
    t = (n / N) * 3.0
    i = min(int(t), 2)
    return interpolate_color(stops[i], stops[i + 1], t - i)


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


class TimesTableDance(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.work = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.kt = ValueTracker(float(K_FIRST))
        self.shown = ValueTracker(float(N))
        self.build_chords()

        self.hook()
        self.stage_build()
        self.stage_three()
        self.stage_rule()
        self.stage_dance()
        self.takeaway("One circle. One times table.",
                      "That's the whole instruction.")
        self.share()
        self.signature()

    # ------------------------------------------------------------------
    def build_chords(self):
        self.chords = VGroup(*[
            VMobject(stroke_color=wheel(n), stroke_width=1.15)
            for n in range(N)])

        def upd(grp):
            k = self.kt.get_value()
            s = self.shown.get_value()
            for n, m in enumerate(grp):
                m.set_points_as_corners([P(n), P(n * k)])
                m.set_stroke(opacity=0.62 * float(np.clip(s - n, 0.0, 1.0)))

        self.chords.add_updater(upd)
        upd(self.chords)
        # the group carries the updater, so it must be added directly —
        # an AnimationGroup would rebuild it and the updater would never fire
        self.add(self.chords)

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

    def say(self, s, beats=2, color=WHITE_, size=25):
        new = txt(s, size, color, bold=False, w=2 * SAFE_X - 0.15)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def set_work(self, s, color, beats=2.5, size=23):
        new = txt(s, size, color, bold=False, w=4.3)
        new.move_to(np.array([0, WORK_Y, 0]))
        if self.work is None:
            self.work = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            old, self.work = self.work, new
            self.play(FadeOut(old), FadeIn(new), run_time=self.T(beats))
            self.work = new

    # ------------------------------------------------------------------
    def hook(self):
        """Frame 1 is the finished shape. The question comes after it."""
        self.title = txt(SERIES, 21, GOLD, w=3.2)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = txt("the k times table  →  k − 1 lobes", 23, GREY,
                      bold=False, w=4.2)
        self.eq.move_to(np.array([0, EQ_Y, 0]))
        self.note = txt("the 2 times table drew this.", 27, WHITE_,
                        bold=False, w=2 * SAFE_X - 0.15)
        self.note.move_to(np.array([0, NOTE_Y, 0]))
        self.add(self.title, self.eq, self.note)
        self.wait(self.T(END_HOOK))

    # ==================================================================
    def stage_build(self):
        self.dots = VGroup(*[Dot(P(n), radius=0.019, fill_color=wheel(n))
                             for n in range(N)])
        self.play(self.shown.animate.set_value(0.0),
                  FadeIn(self.dots), run_time=self.T(2.5))
        self.say("200 dots. numbered 0 to 199.", 2.5, SKY)
        self.set_work("join every dot n to dot 2n", GOLD, 2.5)
        self.play(self.shown.animate.set_value(float(N)),
                  run_time=self.T(4), rate_func=linear)
        self.say("that is the entire instruction.", 2.5, GOLD)
        self.say("nobody drew the curve. it just turns up.", 2.5)
        self.pad_to(END_BUILD)

    # ==================================================================
    def stage_three(self):
        self.say("now the 3 times table.", 2.5, SKY)
        self.set_work("join every dot n to dot 3n", SKY, 2.5)
        self.play(self.kt.animate.set_value(3.0),
                  run_time=self.T(3), rate_func=smooth)
        self.say("two lobes.", 2.5, SKY)
        self.say("watch what the 4 does.", 2.5)
        self.pad_to(END_THREE)

    # ==================================================================
    def stage_rule(self):
        self.play(self.kt.animate.set_value(4.0),
                  run_time=self.T(2.5), rate_func=smooth)
        self.set_work("4  →  three lobes", GOLD, 2.5)
        self.play(self.kt.animate.set_value(5.0),
                  run_time=self.T(2.5), rate_func=smooth)
        self.set_work("5  →  four lobes", GOLD, 2.5)
        self.say("always one less than the times table.", 3, GOLD)
        self.pad_to(END_RULE)

    # ==================================================================
    def stage_dance(self):
        """k lands on an integer exactly on the beat — that is the dance."""
        old, self.work = self.work, None
        live = VGroup(txt("×", 30, WHITE_, w=0.3),
                      Integer(DANCE[0], font_size=42).set_fill(GOLD))
        live[0].move_to(np.array([-0.40, WORK_Y, 0]))
        live[1].add_updater(lambda m: (
            m.set_value(int(round(self.kt.get_value()))),
            m.move_to(np.array([0.10, WORK_Y, 0]))))
        self.play(FadeOut(old), FadeIn(live[0]), run_time=self.T(1.5))
        self.add(live)
        self.live = live
        self.say("so let it count.", 2.5, GOLD)

        # the march must divide the remaining beats into quarter-beat steps,
        # or k stops landing on the downbeat and the snap goes out of time
        step = (END_DANCE - self.used) / len(DANCE)
        assert abs(step * 4 - round(step * 4)) < 1e-9      # stays on the grid
        for k in DANCE:
            self.play(self.kt.animate.set_value(float(k)),
                      run_time=self.T(step), rate_func=smooth)
        self.pad_to(END_DANCE)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        self.chords.clear_updaters()
        keep = (self.clock, self.title, self.eq, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 28, WHITE_, w=2 * SAFE_X - 0.15)
        self.l1.move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 26, GOLD, w=2 * SAFE_X - 0.15)
        self.l2.move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Comment a times table", 27, WHITE_, w=2 * SAFE_X - 0.15)
        s2 = txt("and I'll run it", 27, GOLD, w=2 * SAFE_X - 0.15)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.eq), FadeOut(self.title),
                  run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(2))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 2 * SAFE_X - 0.15:
            cg.set_width(2 * SAFE_X - 0.15)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1))
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(1.5))
