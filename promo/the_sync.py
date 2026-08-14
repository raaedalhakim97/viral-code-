"""
the_sync — fifteen dots that always come back. 40.0s.

    BPM=150 manimgl the_sync.py TheSync -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

A SPECTACLE VIDEO, NOT A LESSON. Its job is to be watched twice and followed,
not to teach anything. Fifteen dots start in a perfect vertical line, break
apart into travelling waves, twist into something that looks completely random —
and then snap back into a straight line at an exact instant. Then do it again.

NOTHING IS FAKED, AND THAT IS WHY IT WORKS. Dot k swings at

        omega_k  =  2 pi (K0 + k) / T

so the slowest one makes 10 swings per cycle and the fastest makes 24 — each
one exactly ONE more than the dot above it. Every omega is a whole number of
cycles per T, so at t = 0, T, 2T every single sine is zero simultaneously. The
alignment is arithmetic, not animation: measured max |sin| at the realignment
instants is 2e-14, which is float noise, not a fudge.

    T          12.8 s  =  32 beats
    motion     beat 6 -> 70  =  25.6 s  =  exactly two cycles
    aligned at beats 6, 38, 70

THE REVEAL IS THE NUMBERS THEMSELVES. At the end the dots freeze in line and
each is labelled with its swing count: 10, 11, 12 ... 24. The reason becomes
visible without a word of explanation — they were never random, they were
counting.

VERIFIED AT IMPORT
    every dot is exactly at centre at t = 0, T and 2T     to 1e-12
    the swing counts are consecutive integers
    the motion window is a whole number of cycles         or it ends mid-chaos
    no two dots share a frequency                         or they never separate

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

BEAT_GO = 6           # the dots start moving
BEAT_MID = 38         # first realignment
BEAT_STOP = 70        # second realignment, and everything freezes
END_REVEAL, END_FOLLOW = 84, 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.04
TITLE_Y = 3.55
NOTE_Y  = -3.45
LINE_Y  = -2.05

# ------------------------------------------------------------------ the maths
N = 15                # how many dots
K0 = 10               # the slowest dot's swing count per cycle
B_SEC = 60.0 / BPM
T_SYNC = (BEAT_MID - BEAT_GO) * B_SEC          # 12.8 s
T_RUN = (BEAT_STOP - BEAT_GO) * B_SEC          # 25.6 s

SWINGS = [K0 + k for k in range(N)]
OMEGA = np.array([2 * np.pi * s / T_SYNC for s in SWINGS])

assert SWINGS == list(range(K0, K0 + N)), "swing counts must be consecutive"
assert len(set(SWINGS)) == N, "two dots with the same frequency never separate"
for _t in (0.0, T_SYNC, 2 * T_SYNC):
    assert np.abs(np.sin(OMEGA * _t)).max() < 1e-12, f"not aligned at {_t}s"
assert abs(T_RUN / T_SYNC - round(T_RUN / T_SYNC)) < 1e-12, \
    "the motion window must be a whole number of cycles"
assert round(T_RUN / T_SYNC) == 2

AMP = 1.92            # how far each dot swings, in screen units
TOP_Y, BOT_Y = 2.42, -2.42
YS = np.linspace(TOP_Y, BOT_Y, N)


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


class TheSync(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.build()
        self.open_card()
        self.stage_run()
        self.stage_reveal()
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

    # ---------------------------------------------------------- the dots
    def t_motion(self):
        """Seconds since the dots were released, held at the end so the last
        frame is the aligned one rather than wherever the clock happened to
        stop."""
        t = self.clock.get_value() - BEAT_GO * self.B
        return float(np.clip(t, 0.0, T_RUN))

    def xs(self):
        return AMP * np.sin(OMEGA * self.t_motion())

    def build(self):
        self.dots = VGroup()
        for k in range(N):
            c = interpolate_color(GOLD, SKY, k / (N - 1))
            d = Dot(np.array([0.0, YS[k], 0.0]), radius=0.075, fill_color=c)

            def up(mo, k=k):
                mo.move_to(np.array([self.xs()[k], YS[k], 0.0]))

            d.add_updater(up)
            self.dots.add(d)

        self.wave = VMobject(stroke_width=2.6)

        def wup(mo):
            pts = [np.array([x, y, 0.0]) for x, y in zip(self.xs(), YS)]
            mo.set_points_smoothly(pts)
            mo.set_stroke(SKY, opacity=0.42)

        self.wave.add_updater(wup)

    # ------------------------------------------------------------------
    def open_card(self):
        self.title = txt("WAIT FOR IT", 40, GOLD, w=3.4)
        self.title.move_to(np.array([0, TITLE_Y, 0]))
        self.add(self.wave, self.dots)
        self.play(FadeIn(self.title), FadeIn(self.dots), run_time=self.T(2))
        self.say("fifteen dots. one straight line.", 2.5)
        self.pad_to(BEAT_GO)

    # ==================================================================
    # Two full cycles. Apart, chaos, back together. Twice.
    # ==================================================================
    def stage_run(self):
        self.say("watch what happens.", 3)
        self.pad_to(BEAT_MID - 6)
        self.say("keep watching. they are coming back.", 4)
        self.pad_to(BEAT_MID)
        self.say("there.", 2.5, GOLD)
        self.say("again —", 2.5)
        self.pad_to(BEAT_STOP - 5)
        self.say("wait for it —", 3)
        self.pad_to(BEAT_STOP)

    # ==================================================================
    # Why. The numbers were the answer the whole time.
    # ==================================================================
    def stage_reveal(self):
        self.say("they were never random.", 2.5, GOLD)
        nums = VGroup()
        for k in range(N):
            lab = txt(str(SWINGS[k]), 17, GREY, bold=False, w=0.5)
            lab.move_to(np.array([0.46, YS[k], 0.0]))
            nums.add(lab)
        self.nums = nums
        self.play(LaggedStart(*[FadeIn(l, shift=0.08 * LEFT) for l in nums],
                              lag_ratio=0.10), run_time=self.T(3))
        self.say("each one swings once more than the one above.", 3.5)
        self.say("so they can only meet in one place.", 3)
        self.pad_to(END_REVEAL)

    # ==================================================================
    # The ask.
    # ==================================================================
    def stage_follow(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1.5))
        self.note = None

        f1 = txt("FOLLOW", 54, GOLD, w=3.0)
        f1.move_to(np.array([0, 0.85, 0]))
        f2 = txt("and the next one is better", 27, WHITE_, w=4.4)
        f2.move_to(np.array([0, 0.05, 0]))
        f3 = txt("@observer.collapse", 24, GREY, bold=False, w=3.6)
        f3.move_to(np.array([0, -0.70, 0]))
        self.card = VGroup(f1, f2, f3)
        self.play(FadeIn(f1, scale=1.15), run_time=self.T(2),
                  rate_func=rush_from)
        self.play(FadeIn(f2), run_time=self.T(1.5))
        self.play(FadeIn(f3), run_time=self.T(1.5))
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
        cta = txt("the math behind AI", 27)
        cta.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cta, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cta),
                  run_time=self.T(1.5))
