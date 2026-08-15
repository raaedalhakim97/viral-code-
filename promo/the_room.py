"""
the_room — what the observer cannot see. 40.0s. OBSERVER COLLAPSE 01.

    BPM=150 manimgl the_room.py TheRoom -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE ONE OF THE ACTUAL PAGE. Not a promo. The thesis is that an observer
never acts on the world — it acts on the part of the world that reached it, and
those are different objects.

THE ROOM. A 4x4 grid. You stand on it, so your position IS a vector. An
observer sits at (0,0). A box sits at (3,3). The observer can only know the box
because light travels the straight line between them, and you are standing in
the room that line crosses.

THE NUMBER THAT DECIDES IT. You block the box exactly when you are ON that
line, and "on the line" is a cross product:

        3x − 3y          (that is  x*Qy − y*Qx  with the box Q at (3,3))

Walk up the column x = 2 and it reads 6, then 3, then 0. At zero the box leaves
the observer's world. Not the room — the observer's world. THAT IS AN INTEGER
HITTING ZERO, not an effect: there is no rounding anywhere in this video.

WHICH SQUARES DO IT. Of the 16 squares, the observer holds one and the box
holds one, so you can stand in 14. Exactly 2 of them delete the box: (1,1) and
(2,2). Both are computed below, not typed in.

THE DOUBLE SLIT, HONESTLY. The bridge is NOT that a mind collapses anything —
put a which-path detector on the slits and never read it and the interference
still dies. The bridge is INFORMATION AVAILABILITY: the pattern depends on what
can be known, not on what is true. Occlusion is the everyday version of exactly
that, which is why the analogy is allowed to be drawn at all.

VERIFIED AT IMPORT
    the blocking squares are computed             not asserted by hand
    there are exactly two of them                 or "2 of 14" is a lie
    the walk reads 6, 3, 0                        integers, no rounding
    only the last step blocks                     or the reveal fires early

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

END_OPEN, END_YOU, END_SEE = 6, 18, 32
END_NUM, END_WALK, END_MODEL = 44, 60, 72
END_ACT, END_SLIT, END_FOLLOW = 79, 86, 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.035
TITLE_Y = 2.98
NOTE_Y  = -3.55
LINE_Y  = -2.05

# ------------------------------------------------------------------ the room
G = 4                              # a 4 x 4 room
EYE = (0, 0)                       # where the observer sits
BOX = (3, 3)                       # what it is watching
WALK = [(2, 0), (2, 1), (2, 2)]    # you, one square at a time


def cross(p):
    """How far off the eye-to-box line you are. Zero means you are on it.

    This is the 2D cross product of your position with the box's position,
    both measured from the observer. It is zero exactly for the points that
    lie along the observer's line of sight."""
    return p[0] * BOX[1] - p[1] * BOX[0]


def between(p):
    """True when p lies strictly between the observer and the box, rather than
    on the far side or behind the observer."""
    return 0 < p[0] * BOX[0] + p[1] * BOX[1] < BOX[0] ** 2 + BOX[1] ** 2


BLOCKERS = [(x, y) for x in range(G) for y in range(G)
            if (x, y) not in (EYE, BOX) and cross((x, y)) == 0 and between((x, y))]
VALUES = [cross(p) for p in WALK]
STANDABLE = G * G - 2              # the eye's square and the box's square

assert BLOCKERS == [(1, 1), (2, 2)], BLOCKERS
assert len(BLOCKERS) == 2, "the caption claims exactly two — count them"
assert STANDABLE == 14
assert VALUES == [6, 3, 0], VALUES
assert all(isinstance(v, int) for v in VALUES), "no rounding lives in this video"
assert WALK[-1] in BLOCKERS, "the walk has to end on a blocking square"
assert not any(p in BLOCKERS for p in WALK[:-1]), "the reveal must fire last"
assert cross(BOX) == 0 and not between(BOX), "the box is on the line, not blocking it"

CELL = 1.15
ROOM_C = np.array([0.0, -0.28, 0.0])


def cell(x, y):
    return ROOM_C + np.array([(x - 1.5) * CELL, (y - 1.5) * CELL, 0.0])


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def small_eye(color, width=0.62):
    """The observer, small enough to sit on one square."""
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


class TheRoom(Scene):
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

        self.open_card()
        self.stage_you()
        self.stage_see()
        self.stage_number()
        self.stage_walk()
        self.stage_model()
        self.stage_act()
        self.stage_slit()
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

    # ==================================================================
    # A room, and a grid that knows where you are.
    # ==================================================================
    def open_card(self):
        self.hook = VGroup(txt("STAND HERE", 38, GOLD, w=3.6),
                           txt("AND THE BOX STOPS EXISTING", 24, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, TITLE_Y, 0]))

        grid = VGroup()
        for i in range(G + 1):
            d = (i - 2) * CELL
            grid.add(Line(ROOM_C + np.array([d, -2 * CELL, 0]),
                          ROOM_C + np.array([d, 2 * CELL, 0]),
                          stroke_color=FAINT, stroke_width=1.8))
            grid.add(Line(ROOM_C + np.array([-2 * CELL, d, 0]),
                          ROOM_C + np.array([2 * CELL, d, 0]),
                          stroke_color=FAINT, stroke_width=1.8))
        self.grid = grid
        self.marks = VGroup(*[Dot(cell(x, y), radius=0.028, fill_color=FAINT)
                              for x in range(G) for y in range(G)])

        self.play(FadeIn(self.hook), ShowCreation(self.grid, lag_ratio=0.04),
                  run_time=self.T(2.5))
        self.add(self.marks)
        self.say("a four by four room.", 3)
        self.pad_to(END_OPEN)

    # ==================================================================
    # You are not in the room. You are a vector on it.
    # ==================================================================
    def stage_you(self):
        self.you = Dot(cell(*WALK[0]), radius=0.155, fill_color=GOLD)
        self.play(FadeIn(self.you, scale=1.6), run_time=self.T(1.5))
        self.say("you are here.", 2.5, GOLD)

        self.pos = txt(f"({WALK[0][0]}, {WALK[0][1]})", 23, GOLD, bold=False, w=1.1)
        self.pos.move_to(cell(*WALK[0]) + np.array([0.66, 0.0, 0.0]))
        self.play(FadeIn(self.pos), run_time=self.T(2))
        self.say("so you are a vector.", 3.5)
        self.pad_to(END_YOU)

    # ==================================================================
    # The observer, the box, and the one line between them.
    # ==================================================================
    def stage_see(self):
        self.eye = small_eye(SKY).move_to(cell(*EYE))
        self.play(FadeIn(self.eye), run_time=self.T(2))
        self.say("an observer. it does not move.", 2.5, SKY)

        self.box = Square(side_length=0.52, color=ROSE, stroke_width=3.0)
        self.box.set_fill(ROSE, opacity=0.28).move_to(cell(*BOX))
        self.play(FadeIn(self.box, scale=1.4), run_time=self.T(2))
        self.say("and something it is watching.", 3, ROSE)

        self.sight = Line(cell(*EYE), cell(*BOX),
                          stroke_color=SKY, stroke_width=2.6)
        self.sight.set_stroke(opacity=0.55)
        self.play(ShowCreation(self.sight), run_time=self.T(2))
        self.say("it only knows what reaches it.", 2.5)
        self.pad_to(END_SEE)

    # ==================================================================
    # One integer decides whether the box exists for the observer.
    # ==================================================================
    def stage_number(self):
        eq = txt("3x − 3y", 30, WHITE_, w=2.1)
        val = txt(str(VALUES[0]), 30, WHITE_, w=0.6)
        self.spine = VGroup(eq, txt("=", 30, GREY, w=0.4), val) \
            .arrange(RIGHT, buff=0.28).move_to(np.array([0, TITLE_Y, 0]))
        self.val = val

        self.play(FadeOut(self.hook, shift=0.15 * UP),
                  FadeIn(self.spine, shift=0.15 * UP), run_time=self.T(2))
        self.say("how far off that line you are.", 3)
        self.play(Indicate(self.val, color=GOLD, scale_factor=1.35),
                  run_time=self.T(2))
        self.say("walk. watch it fall.", 3.5)
        self.pad_to(END_NUM)

    # ==================================================================
    # 6, 3, 0. The box leaves.
    # ==================================================================
    def step_to(self, p, beats):
        """One square. Move you, your vector, and the number together."""
        new_pos = txt(f"({p[0]}, {p[1]})", 23, GOLD, bold=False, w=1.1)
        new_pos.move_to(cell(*p) + np.array([0.66, 0.0, 0.0]))
        v = cross(p)
        new_val = txt(str(v), 30, GOLD if v == 0 else WHITE_, w=0.6)
        new_val.move_to(self.val.get_center())
        ghost = Dot(self.you.get_center(), radius=0.075, fill_color=GOLD)
        ghost.set_opacity(0.28)
        self.add(ghost)
        self.play(self.you.animate.move_to(cell(*p)),
                  Transform(self.pos, new_pos),
                  Transform(self.val, new_val),
                  run_time=self.T(beats))

    def stage_walk(self):
        self.step_to(WALK[1], 2.5)
        self.say("three.", 2, GREY)
        self.step_to(WALK[2], 2.5)
        self.say("zero. you are on the line.", 3, GOLD)

        cut = Line(cell(*EYE), cell(*WALK[2]),
                   stroke_color=SKY, stroke_width=2.6)
        cut.set_stroke(opacity=0.55)
        self.play(FadeOut(self.box, scale=0.7),
                  Transform(self.sight, cut), run_time=self.T(2))
        self.say("the box is gone.", 2.5, ROSE)
        self.pad_to(END_WALK)

    # ==================================================================
    # It never went anywhere. You were watching the model.
    # ==================================================================
    def stage_model(self):
        self.say("it did not move.", 2.5)
        self.ghostbox = Square(side_length=0.52, color=ROSE, stroke_width=2.2)
        self.ghostbox.set_fill(ROSE, opacity=0.16).move_to(cell(*BOX))
        self.ghostbox.set_stroke(opacity=0.58)
        self.play(FadeIn(self.ghostbox), run_time=self.T(2))
        self.say("you were watching the observer's model.", 3.5, SKY)
        self.say("not the room.", 2.5, GOLD)
        self.pad_to(END_MODEL)

    # ==================================================================
    # And it acts on the model, because that is all it has.
    # ==================================================================
    def stage_act(self):
        self.say("so it will act on a room with no box in it.", 4)
        self.say("same room. different world.", 3, GOLD)
        self.pad_to(END_ACT)

    # ==================================================================
    # The honest bridge: availability of information, not consciousness.
    # ==================================================================
    def stage_slit(self):
        self.say("the double slit does this too.", 3, SKY)
        self.say("the pattern depends on what can be known.", 4)
        self.pad_to(END_SLIT)

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
        f2 = txt("episode one of many", 26, WHITE_, w=4.0)
        f2.move_to(np.array([0, 0.26, 0]))
        f3 = txt("follow — you are on somebody's grid", 21, GREY,
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
