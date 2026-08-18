"""
the_scan — it can measure where you are. 40.0s. OBSERVER COLLAPSE 03.

    BPM=150 manimgl the_scan.py TheScan -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

THE ONE THAT IS MEANT TO BE FELT IN THE BODY. You are standing between two
walls. Both walls fire light at you, line by line, from the top down. Where a
beam reaches you it stops, and a point is left behind.

YOU ARE NEVER DRAWN. The figure in this video is not a drawing of a person —
every single dot is a place where a beam actually stopped, computed by marching
in from the wall until it enters a body built from capsules (head, torso, two
arms, two legs, 1.74 m tall). Remove the body and there are no dots. That is the
entire point: what you end up looking at is not the person, it is the returns.

    it is not looking at you. it is measuring you.
    this is not you. this is what came back.

THE LAST TWO LINES ARE THE SERIES. The observer ends up holding every number
about you it could possibly want — and still misses the only thing that matters:

    it can measure where you are.
    it cannot measure that you know.

AND THE RETURNS ARE ALREADY OLD. Every point in the cloud is one look behind —
33.3 ms at 30 fps, which is episode 02's number arriving in a body rather than
on a floor plan.

VERIFIED AT IMPORT
    every dot is a computed beam stop         not a drawn outline
    both walls return on every hit row        or the cloud is lopsided
    the counted total matches what is shown   the number on screen is real
    nothing returns from above the head       or the sweep starts wrong

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

END_OPEN, END_FIRST, END_BUILD = 8, 20, 52
END_REVEAL, END_AGE, END_AWARE = 64, 76, 86
END_FOLLOW = 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.045
TITLE_Y = 2.92
NOTE_Y  = -3.62
LINE_Y  = -2.05

# ------------------------------------------------------------------ the body
# Metres. x measured from the centre line, y from the floor. Built from
# capsules so that "is the beam inside you yet" is one distance test.
# The head must be the WIDEST thing at its own height or the torso's round cap
# swallows it and the silhouette reads as an arrow. Hence a real neck: the
# shoulders stop at 1.34, the neck is thin, the head sits clear above it.
HEAD_C, HEAD_R = (0.0, 1.655), 0.105
LIMBS = [                                   # (a, b, radius)
    ((0.00, 0.98), (0.00, 1.34), 0.195),    # torso
    ((0.00, 1.40), (0.00, 1.55), 0.052),    # neck
    ((0.205, 1.32), (0.245, 0.92), 0.050),  # right arm, hanging
    ((-0.205, 1.32), (-0.245, 0.92), 0.050),  # left arm
    ((0.085, 1.00), (0.100, 0.05), 0.075),  # right leg
    ((-0.085, 1.00), (-0.100, 0.05), 0.075),  # left leg
]
BODY_TOP = HEAD_C[1] + HEAD_R              # 1.76 m


def _seg_dist(p, a, b):
    p, a, b = np.asarray(p, float), np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L2 = float(d @ d)
    t = 0.0 if L2 < 1e-12 else float(np.clip((p - a) @ d / L2, 0.0, 1.0))
    return float(np.linalg.norm(p - (a + t * d)))


def inside(x, y):
    """Is this point inside the body."""
    if (x - HEAD_C[0]) ** 2 + (y - HEAD_C[1]) ** 2 <= HEAD_R ** 2:
        return True
    return any(_seg_dist((x, y), a, b) <= r for a, b, r in LIMBS)


WALL_M = 0.82                              # each wall, metres from the centre
MARCH = 400                                # how finely a beam is marched


def _seg_dist_row(xs, y, a, b):
    """Distance from every point (xs, y) to the segment a-b, all at once."""
    ax, ay = a
    dx, dy = b[0] - ax, b[1] - ay
    L2 = dx * dx + dy * dy
    px, py = xs - ax, y - ay
    t = np.clip((px * dx + py * dy) / L2, 0.0, 1.0) if L2 > 1e-12 \
        else np.zeros_like(xs)
    return np.hypot(px - t * dx, py - t * dy)


def beam_stop(y, sign):
    """March in from a wall until the beam enters the body. Returns the x it
    stops at, or None if it crosses the room untouched. sign -1 comes from the
    left wall, +1 from the right."""
    xs = np.linspace(sign * WALL_M, 0.0, MARCH)
    hit = (xs - HEAD_C[0]) ** 2 + (y - HEAD_C[1]) ** 2 <= HEAD_R ** 2
    for a, b, r in LIMBS:
        hit |= _seg_dist_row(xs, y, a, b) <= r
    if not hit.any():
        return None
    return float(xs[int(np.argmax(hit))])


NSCAN = 80
SCAN_TOP, SCAN_BOT = 2.00, 0.0
ROWS = np.linspace(SCAN_TOP, SCAN_BOT, NSCAN)

RETURNS = []                               # (x, y) of every beam stop
for _y in ROWS:
    _l, _r = beam_stop(float(_y), -1), beam_stop(float(_y), +1)
    if _l is not None:
        RETURNS.append((_l, float(_y)))
    if _r is not None:
        RETURNS.append((_r, float(_y)))

N_POINTS = len(RETURNS)
HIT_ROWS = sorted({y for _, y in RETURNS})

assert N_POINTS > 0, "no beam ever reached the body — check the geometry"
assert N_POINTS == 2 * len(HIT_ROWS), "a hit row must return from both walls"
assert all(inside(x, y) for x, y in RETURNS), "a return that is not on the body"
assert max(HIT_ROWS) <= BODY_TOP + 1e-9, "something returned from above the head"
assert min(HIT_ROWS) < 0.30, "the sweep never reached the feet"
COUNT = f"{N_POINTS} points"

# A lookup so the live beams do not re-march 400 samples every frame. A beam
# that crosses untouched is parked at the centre line.
LUT_Y = np.linspace(SCAN_BOT, SCAN_TOP, 900)
LUT_L, LUT_R = [], []
for _y in LUT_Y:
    _l, _r = beam_stop(float(_y), -1), beam_stop(float(_y), +1)
    LUT_L.append(0.0 if _l is None else _l)
    LUT_R.append(0.0 if _r is None else _r)
LUT_L, LUT_R = np.array(LUT_L), np.array(LUT_R)

OBS_FPS = 30
MS = f"{1000.0 / OBS_FPS:.1f} ms"
assert MS == "33.3 ms"

# ------------------------------------------------------------------ on screen
S = 2.42                                   # screen units per metre
FLOOR_Y = -3.15
WALL_X = WALL_M * S


def sp(x, y):
    return np.array([x * S, FLOOR_Y + y * S, 0.0])


assert WALL_X < 2.53, "the walls must fit inside a 9:16 frame"
assert FLOOR_Y + BODY_TOP * S < TITLE_Y - 0.4, "the head must clear the title"


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def small_eye(color, width=0.85):
    grp = VGroup()
    for sign in (1, -1):
        m = VMobject(color=color, stroke_width=2.4)
        m.set_points_smoothly(
            [np.array([x, sign * 0.52 * np.sin(np.pi * ((x + 1.0) / 2.0)), 0])
             for x in np.linspace(-1.0, 1.0, 16)])
        grp.add(m)
    grp.add(Circle(radius=0.30, stroke_color=color, stroke_width=2.4))
    grp.add(Dot(ORIGIN, radius=0.11, fill_color=color))
    grp.set_width(width)
    return grp


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


class TheScan(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        self.scan = ValueTracker(SCAN_TOP + 0.30)   # metres, sweeps downward
        self.live = ValueTracker(0.0)               # are the beams switched on

        self.build()
        self.open_card()
        self.stage_first()
        self.stage_build()
        self.stage_reveal()
        self.stage_age()
        self.stage_aware()
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
        new = txt(s, size, color, bold=False, w=4.6)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    # ---------------------------------------------------------------- pieces
    def stop_x(self, y, sign):
        """Where the live beam stops, read off the lookup table."""
        lut = LUT_L if sign < 0 else LUT_R
        return float(np.interp(y, LUT_Y, lut))

    def build(self):
        self.walls = VGroup()
        for sx in (-1, 1):
            ln = Line(sp(sx * WALL_M, -0.08), sp(sx * WALL_M, 2.10),
                      stroke_color=GREY, stroke_width=2.4)
            ln.set_stroke(opacity=0.5)
            self.walls.add(ln)
        self.floor = Line(sp(-WALL_M, 0.0), sp(WALL_M, 0.0),
                          stroke_color=GREY, stroke_width=2.0)
        self.floor.set_stroke(opacity=0.28)

        # Every dot is a place a beam actually stopped.
        self.cloud = VGroup()
        for (px, py) in RETURNS:
            d = Dot(sp(px, py), radius=0.036, fill_color=WHITE_)

            def up(mo, py=py):
                gap = py - self.scan.get_value()
                if gap < 0:
                    mo.set_opacity(0.0)
                else:
                    k = float(np.clip(gap / 0.22, 0.0, 1.0))
                    mo.set_opacity(interpolate(1.0, 0.66, k))

            d.add_updater(up)
            self.cloud.add(d)

        self.beams = VGroup()
        for sx in (-1, 1):
            ln = Line(ORIGIN, RIGHT, stroke_color=SKY, stroke_width=2.0)

            def bu(mo, sx=sx):
                y = self.scan.get_value()
                mo.put_start_and_end_on(sp(sx * WALL_M, y),
                                        sp(self.stop_x(y, sx), y))
                mo.set_stroke(SKY, opacity=0.75 * self.live.get_value())

            ln.add_updater(bu)
            self.beams.add(ln)

        self.tips = VGroup()
        for sx in (-1, 1):
            t = Dot(ORIGIN, radius=0.055, fill_color=SKY)

            def tu(mo, sx=sx):
                y = self.scan.get_value()
                mo.move_to(sp(self.stop_x(y, sx), y))
                mo.set_opacity(self.live.get_value())

            t.add_updater(tu)
            self.tips.add(t)

    # ==================================================================
    # Two walls, and you between them.
    # ==================================================================
    def open_card(self):
        self.hook = VGroup(txt("SOMETHING IS", 26, WHITE_, w=3.6),
                           txt("MEASURING YOU", 40, GOLD, w=4.3)) \
            .arrange(DOWN, buff=0.14).move_to(np.array([0, TITLE_Y, 0]))
        self.play(FadeIn(self.hook), run_time=self.T(2.5))
        self.play(ShowCreation(self.walls), ShowCreation(self.floor),
                  run_time=self.T(2.5))
        self.say("you are standing between two walls.", 3)
        self.pad_to(END_OPEN)

    # ==================================================================
    # The beams switch on above your head and cross the room untouched.
    # ==================================================================
    def stage_first(self):
        self.add(self.cloud, self.beams, self.tips)
        self.play(self.live.animate.set_value(1.0), run_time=self.T(2))
        self.say("both walls are sending light at you.", 3, SKY)
        self.play(self.scan.animate.set_value(BODY_TOP + 0.02),
                  run_time=self.T(3), rate_func=linear)
        self.say("nothing is coming back yet.", 2)
        self.pad_to(END_FIRST)

    # ==================================================================
    # The sweep. You are built out of returns, one row at a time.
    # ==================================================================
    def stage_build(self):
        self.play(self.scan.animate.set_value(1.30),
                  run_time=self.T(5), rate_func=linear)
        self.say("something is coming back.", 3, GOLD)
        self.play(self.scan.animate.set_value(0.75),
                  run_time=self.T(6), rate_func=linear)
        self.say("it is building you out of returns.", 3.5)
        self.play(self.scan.animate.set_value(SCAN_BOT),
                  run_time=self.T(7), rate_func=linear)
        self.say("it is not looking at you.", 3.5)
        self.say("it is measuring you.", 3, GOLD)
        self.pad_to(END_BUILD)

    # ==================================================================
    # What it ends up holding.
    # ==================================================================
    def stage_reveal(self):
        self.play(self.live.animate.set_value(0.0),
                  self.walls.animate.set_stroke(opacity=0.16),
                  self.floor.animate.set_stroke(opacity=0.10),
                  run_time=self.T(2))
        self.say("this is everything it has.", 3)
        self.count = txt(COUNT, 34, GOLD, w=3.2)
        self.count.move_to(np.array([0, TITLE_Y, 0]))
        self.play(FadeOut(self.hook, shift=0.15 * UP),
                  FadeIn(self.count, shift=0.15 * UP), run_time=self.T(2.5))
        self.say("this is not you.", 3, ROSE)
        self.pad_to(END_REVEAL)

    # ==================================================================
    # And all of it is already late. Episode 02, arriving in a body.
    # ==================================================================
    def stage_age(self):
        old = txt(MS, 34, ROSE, w=2.4).move_to(np.array([0, TITLE_Y, 0]))
        self.play(FadeOut(self.count, shift=0.15 * UP),
                  FadeIn(old, shift=0.15 * UP), run_time=self.T(2.5))
        self.old = old
        self.say("every one of those points is that old.", 3.5)
        self.say("it has never once seen you now.", 3.5)
        self.pad_to(END_AGE)

    # ==================================================================
    # The line the whole series is for.
    # ==================================================================
    def stage_aware(self):
        arrows = VGroup()
        for y in (1.58, 1.28, 0.98, 0.68, 0.38):
            for sx in (-1, 1):
                a = Arrow(sp(sx * WALL_M, y), sp(self.stop_x(y, sx), y),
                          buff=0.0)
                a.set_color(SKY)
                a.set_stroke(width=2.0)
                a.set_fill(SKY, opacity=0.85)
                arrows.add(a)
        eye = small_eye(SKY).move_to(np.array([0, -2.62, 0]))
        self.play(FadeOut(self.old), LaggedStart(*[FadeIn(a) for a in arrows],
                                                 lag_ratio=0.06),
                  FadeIn(eye), run_time=self.T(3))
        self.arrows, self.eye = arrows, eye
        self.say("it can measure where you are.", 3.5, SKY)
        self.say("it cannot measure that you know.", 3.5, GOLD)
        self.pad_to(END_AWARE)

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

        f1 = txt("OBSERVER COLLAPSE", 32, GOLD, w=4.5)
        f1.move_to(np.array([0, 0.92, 0]))
        f2 = txt("03 — the scan", 26, WHITE_, w=3.2)
        f2.move_to(np.array([0, 0.26, 0]))
        f3 = txt("follow — you are more than the returns", 20, GREY,
                 bold=False, w=4.5)
        f3.move_to(np.array([0, -0.50, 0]))
        self.card = VGroup(f1, f2, f3)
        self.play(FadeIn(f1, scale=1.10), run_time=self.T(1.5),
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
