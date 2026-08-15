"""
the_delay — you are always ahead of where anyone sees you. 40.0s.
OBSERVER COLLAPSE 02.

    BPM=150 manimgl the_delay.py TheDelay -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

AN AWARENESS VIDEO. It is meant to be felt, not solved. Second person, slow,
dark, and it asks the viewer to look up from the phone at the room they are
actually sitting in.

THE PICTURE. Every wall sends out lines. Where they cross there is a point, and
every point is a vector. You are standing inside that field. As you move — as
you BREATHE — you break the points behind you and make new ones on your own
surface. The observer sits in a corner and never sees you at all: it sees what
comes back.

THE NUMBER NOBODY EXPECTS. Everyone assumes the delay is the speed of light.
It is not. In a 4 metre room, light goes there and back in

        8 m / c  =  26.7 nanoseconds

which is nothing. But the observer only LOOKS thirty times a second, so one
look is 33.3 milliseconds — one and a quarter MILLION times longer than the
light it is using. Between two looks a walking body moves 4.7 cm.

        the light was never the slow part. the observer is.

WHAT IS EXACT AND WHAT IS NOT. The two times and their ratio are computed from
c and the frame rate and are exact. Walking speed (1.4 m/s) is a stated
assumption, not a measurement, and the 4.7 cm gap is drawn MAGNIFIED and
labelled as such — at true room scale it is 0.05 screen units and would be
invisible. Nothing is exaggerated without saying so.

VERIFIED AT IMPORT
    light round trip from c and 4 m               26.7 ns
    one look from the frame rate                  33.3 ms
    the ratio                                     ~1.25 million
    the gap from the stated walking speed         4.7 cm

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

END_OPEN, END_FIELD, END_YOU = 10, 26, 44
END_BOUNCE, END_DELAY, END_TURN = 58, 76, 86
END_FOLLOW = 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
TITLE_Y = 3.05
NOTE_Y  = -3.55
LINE_Y  = -2.05

# ------------------------------------------------------------------ the maths
C_LIGHT = 299_792_458.0            # m/s, exact by definition
ROOM_M = 4.0                       # a four by four metre room
TRIP_M = 2 * ROOM_M                # there and back
T_LIGHT = TRIP_M / C_LIGHT         # 26.7 nanoseconds
OBS_FPS = 30                       # how often the observer looks
T_LOOK = 1.0 / OBS_FPS             # 33.3 milliseconds
RATIO = T_LOOK / T_LIGHT           # ~1.25 million
WALK_MS = 1.4                      # m/s. a stated assumption, not a measurement
GAP_M = WALK_MS * T_LOOK           # 4.7 cm

NS = f"{T_LIGHT * 1e9:.1f} ns"
MS = f"{T_LOOK * 1e3:.1f} ms"
CM = f"{GAP_M * 100:.1f} cm"

assert abs(T_LIGHT * 1e9 - 26.7) < 0.05, NS
assert abs(T_LOOK * 1e3 - 33.3) < 0.05, MS
assert 1.24e6 < RATIO < 1.26e6, RATIO
assert abs(GAP_M * 100 - 4.7) < 0.05, CM
assert (NS, MS, CM) == ("26.7 ns", "33.3 ms", "4.7 cm")

# ------------------------------------------------------------------ the room
ROOM_HALF = 2.15                   # screen units for half the room
S = 2 * ROOM_HALF / ROOM_M         # screen units per metre
ROOM_C = np.array([0.0, -0.22, 0.0])

NL = 9                             # laser lines per wall
LPOS = np.linspace(0.4, ROOM_M - 0.4, NL)
EYE_M = (0.36, 0.36)               # the observer, in a corner

R_SHADOW = 0.30                    # screen units. how wide your shadow is
DRIFT_X, DRIFT_Y = 6.4, 9.6        # seconds per drift cycle. deliberately
BREATH_S = 4.0                     # coprime-ish so the path never repeats


def rp(x, y):
    """Room metres -> screen."""
    return ROOM_C + np.array([(x - ROOM_M / 2) * S, (y - ROOM_M / 2) * S, 0.0])


CROSS = [(px, py) for px in LPOS for py in LPOS]
assert len(CROSS) == NL * NL == 81


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def small_eye(color, width=0.60):
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


class TheDelay(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.frozen = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * (1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                2 * np.pi * self.clock.get_value() / (BREATH_BEATS * self.B))))))

        # 0 = the field does not know you are there. 1 = you cast a shadow.
        self.cue = ValueTracker(0.0)
        # A master dimmer for the whole point field, so the measurement callout
        # can sit on near-black instead of on top of 81 lit points.
        self.field = ValueTracker(1.0)

        self.build()
        self.open_card()
        self.stage_field()
        self.stage_you()
        self.stage_bounce()
        self.stage_delay()
        self.stage_turn()
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

    # ---------------------------------------------------------- you, drifting
    def you_at(self):
        """Where you are. Slow, never repeating, and breathing."""
        if self.frozen is not None:
            return self.frozen
        t = self.clock.get_value()
        return rp(2.0 + 0.62 * np.sin(2 * np.pi * t / DRIFT_X),
                  2.0 + 0.44 * np.sin(2 * np.pi * t / DRIFT_Y + 1.1))

    def breath(self):
        t = self.clock.get_value()
        return 1.0 + 0.16 * np.sin(2 * np.pi * t / BREATH_S)

    def shade(self, q):
        """How lit a point is, given that you are standing in the way.

        Your shadow WIDENS with distance, the way a real shadow from a point
        source does: at distance L along the ray the shadow has radius
        R_SHADOW * L / t, where t is how far along that ray you are standing.
        A constant-width shadow would read as a stripe rather than a cone."""
        e, p = rp(*EYE_M), self.you_at()
        d = q - e
        L = float(np.linalg.norm(d))
        if L < 1e-9:
            return 1.0
        u = d / L
        t = float(np.dot(p - e, u))
        if t <= 1e-6 or t >= L:
            return 1.0
        perp = float(np.linalg.norm((p - e) - t * u))
        f = float(np.clip(perp / (R_SHADOW * L / t), 0.0, 1.0))
        return 1.0 - self.cue.get_value() * (1.0 - f)

    def build(self):
        self.walls = Square(side_length=2 * ROOM_HALF, color=GREY,
                            stroke_width=2.2).move_to(ROOM_C)
        self.walls.set_stroke(opacity=0.45)

        self.lasers = VGroup()
        for v in LPOS:
            for a, b in ((rp(v, 0.0), rp(v, ROOM_M)), (rp(0.0, v), rp(ROOM_M, v))):
                ln = Line(a, b, stroke_color=SKY, stroke_width=1.2)
                ln.set_stroke(opacity=0.13)
                self.lasers.add(ln)

        self.points = VGroup()
        for (px, py) in CROSS:
            q = rp(px, py)
            d = Dot(q, radius=0.035, fill_color=WHITE_)

            def up(mo, q=q):
                mo.set_opacity((0.16 + 0.62 * self.shade(q))
                               * self.field.get_value())

            d.add_updater(up)
            self.points.add(d)

    # ==================================================================
    # Look up.
    # ==================================================================
    def open_card(self):
        self.hook = VGroup(txt("LOOK UP", 40, GOLD, w=3.0),
                           txt("FROM THIS SCREEN", 26, WHITE_, w=4.2)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, TITLE_Y, 0]))
        self.play(FadeIn(self.hook), run_time=self.T(3))
        self.say("at the room you are actually in.", 3.5)
        self.play(ShowCreation(self.walls), run_time=self.T(3.5))
        self.pad_to(END_OPEN)

    # ==================================================================
    # Every wall is sending out lines.
    # ==================================================================
    def stage_field(self):
        self.play(LaggedStart(*[ShowCreation(l) for l in self.lasers],
                              lag_ratio=0.02), run_time=self.T(4))
        self.say("every wall is sending out lines.", 3.5, SKY)
        self.add(self.points)
        self.play(LaggedStart(*[FadeIn(d) for d in self.points],
                              lag_ratio=0.012), run_time=self.T(3.5))
        self.say("where they cross, there is a point.", 2.5)
        self.say("every point is a vector.", 2.5, GOLD)
        self.pad_to(END_FIELD)

    # ==================================================================
    # You are standing in it, and you are breaking it.
    # ==================================================================
    def stage_you(self):
        self.you = Dot(self.you_at(), radius=0.15, fill_color=GOLD)
        self.you.add_updater(
            lambda m: m.move_to(self.you_at()).set_width(0.30 * self.breath()))
        self.play(FadeIn(self.you, scale=1.8), run_time=self.T(2))
        self.say("you are standing in it.", 3, GOLD)

        self.eye = small_eye(SKY).move_to(rp(*EYE_M))
        self.play(FadeIn(self.eye), run_time=self.T(2))
        self.say("and something is reading it.", 3, SKY)

        self.play(self.cue.animate.set_value(1.0), run_time=self.T(2.5),
                  rate_func=smooth)
        self.say("you break the points behind you.", 3)
        self.say("even breathing moves them.", 2.5, GOLD)
        self.pad_to(END_YOU)

    # ==================================================================
    # It never sees you. It sees what comes back.
    # ==================================================================
    def stage_bounce(self):
        self.say("it never sees you.", 3, SKY)
        self.say("it sees what comes back.", 3)

        p0, p1 = rp(*EYE_M), self.you_at()
        beam = Line(p0, p1, stroke_color=GOLD, stroke_width=1.6)
        beam.set_stroke(opacity=0.32)
        pulse = Dot(p0, radius=0.075, fill_color=GOLD)

        def travel(mo, a):
            mo.move_to(interpolate(p0, p1, a * 2) if a < 0.5
                       else interpolate(p1, p0, (a - 0.5) * 2))

        self.add(beam, pulse)
        self.play(UpdateFromAlphaFunc(pulse, travel), run_time=self.T(3))
        self.remove(pulse)

        self.tlight = txt(NS, 34, GOLD, w=2.4)
        self.tlight.move_to(np.array([0, TITLE_Y, 0]))
        self.play(FadeOut(self.hook, shift=0.15 * UP),
                  FadeIn(self.tlight, shift=0.15 * UP), run_time=self.T(2.5))
        self.say("four metres, there and back.", 2.5)
        self.beam = beam
        self.pad_to(END_BOUNCE)

    # ==================================================================
    # The light was never the slow part.
    # ==================================================================
    def stage_delay(self):
        self.say("but it only looks thirty times a second.", 3.5)
        tlook = txt(MS, 34, ROSE, w=2.4).move_to(np.array([0, TITLE_Y, 0]))
        self.play(FadeOut(self.tlight, shift=0.15 * UP),
                  FadeIn(tlook, shift=0.15 * UP), run_time=self.T(2.5))
        self.tlook = tlook
        self.say("between two looks, you have moved.", 3)

        # Freeze, dim the room, and measure the gap as a magnified callout —
        # at true room scale 4.7 cm is 0.05 screen units and invisible.
        self.frozen = self.you_at()
        self.you.clear_updaters()
        self.play(self.field.animate.set_value(0.09),
                  self.lasers.animate.set_stroke(opacity=0.03),
                  self.walls.animate.set_stroke(opacity=0.10),
                  FadeOut(self.beam), FadeOut(self.you), FadeOut(self.eye),
                  run_time=self.T(1))

        a = Dot(np.array([-0.85, -0.30, 0]), radius=0.115, fill_color=GOLD)
        b = Dot(np.array([0.85, -0.30, 0]), radius=0.115, fill_color=GREY)
        bar = Line(a.get_center(), b.get_center(),
                   stroke_color=GREY, stroke_width=2.0)
        lab = txt(CM, 32, GOLD, w=2.0).move_to(np.array([0, 0.34, 0]))
        la = txt("you", 21, GOLD, bold=False, w=1.2).move_to(np.array([-0.85, -0.82, 0]))
        lb = txt("it", 21, GREY, bold=False, w=1.2).move_to(np.array([0.85, -0.82, 0]))
        cap = txt("magnified", 17, GREY, bold=False, w=1.7)
        cap.move_to(np.array([0, -1.36, 0]))
        self.gap = VGroup(bar, a, b, lab, la, lb, cap)
        self.play(FadeIn(self.gap), run_time=self.T(2))

        self.say("one and a quarter million times longer.", 3.5, ROSE)
        self.pad_to(END_DELAY)

    # ==================================================================
    # The turn.
    # ==================================================================
    def stage_turn(self):
        self.say("the light was never the slow part.", 3.5)
        self.say("the observer is.", 3, GOLD)
        self.say("you are always ahead of where anyone sees you.", 3.5, GOLD)
        self.pad_to(END_TURN)

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
        f2 = txt("02 — the delay", 26, WHITE_, w=3.4)
        f2.move_to(np.array([0, 0.26, 0]))
        f3 = txt("follow — nobody has seen you yet", 21, GREY, bold=False, w=4.5)
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
