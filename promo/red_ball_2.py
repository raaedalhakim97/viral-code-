"""
red_ball_2 — the answer, and then the real trick. 40.0s.

    BPM=150 manimgl red_ball_2.py RedBall2 -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

IT IMPORTS PART 1 RATHER THAN REPEATING IT. The paths, the freeze frame, the
numbers on the balls, the answer itself and the physics engine all come from
`red_ball.py`. Nothing is retyped, so the two videos physically cannot disagree
about which ball was red or what it was called — the one mistake that would
destroy both at once, and the one a viewer who screenshots part 1 and pauses
part 2 would absolutely catch.

    it opens on part 1's exact final frame
    same trails, same nine balls, same numbers
    then number 5 turns red

AND THEN ROUND TWO, WHICH IS THE ACTUAL VIDEO. A fresh run, a fresh red ball —
and while the viewer is holding on to it, text starts appearing at the TOP of
the screen, well outside the circle:

        I'm telling you —
        you can't
        you're reading this
        aren't you
        that's the trick

Reading those words costs you the ball. Keeping the ball costs you the words.
There is no way to have both, and that is not a gimmick — it is the whole
definition of attention, demonstrated on the viewer instead of described at
them. Part 1 said "you could not watch nine". This one proves you could not
even watch two.

    "the ball, or the words. you had to choose."

TWO SEPARATE ROUNDS, TWO SEPARATE SEEDS.

    round 1   seed 142, red ball index 0, answer 5     (part 1's run)
    round 2   seed  50, red ball index 4, answer 3     crowded 84%, roam 0.48

Round 2's answer is deliberately NOT 5. Repeating the number would make the
whole thing look rigged, and the assertion below refuses to build if it does.

VERIFIED AT IMPORT
    part 1's constants are unchanged       seed, speed, ball count
    round 2's physics is exact             speed drift, containment, reflection
    round 2's answer differs from part 1's and is not 1 or 9
    both label sets are permutations of 1..9
    the taunts all land inside the tracking stretch

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
import sys

from manimlib import *
import numpy as np

# manimgl does not always put the scene file's own directory on the path, and
# this file is useless without part 1.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import red_ball as p1

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN, END_TENSION, END_REVEAL1 = 5, 10, 20
R2_GO, R2_WHITE, R2_STOP = 22, 27, 58
END_SETUP = 27
END_REVEAL2, END_TRICK = 68, 80
END_TAKE, END_SHARE = 88, 93

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
RED    = "#E4453A"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.04
TITLE_Y = 2.86          # the taunts live up here, well clear of the circle
NOTE_Y  = -3.16
LINE_Y  = -2.05

# ---------------------------------------------------- round 1, from part 1
N       = p1.N
RED1    = p1.RED_I
SCREEN1 = p1.SCREEN
LABEL1  = p1.LABEL
ANSWER1 = p1.ANSWER
FRAMES1 = p1.FRAMES
CR, CY  = p1.CR, p1.CY
DOT_R   = p1.DOT_R
TAIL    = p1.TAIL

assert (p1.SEED, p1.SPEED, p1.N) == (142, 0.82, 9), \
    "part 1 changed — re-render both, or the freeze frames will not match"
assert ANSWER1 == LABEL1[RED1]

# ---------------------------------------------------- round 2, its own run
SEED2 = 50              # chosen — same search, see red_ball_seed_search.py
RED2  = 4

B_SEC    = 60.0 / BPM
F2_WHITE = int(round((R2_WHITE - R2_GO) * B_SEC * FPS))
F2_STOP  = int(round((R2_STOP - R2_GO) * B_SEC * FPS))
FRAMES2  = F2_STOP + 1

PATH2, _WS2, _WR2, _WF2, _B2 = p1.simulate(seed=SEED2, frames=FRAMES2)

assert _WS2 < 1e-12, f"round 2 speed drifted by {_WS2}"
assert _WR2 < p1.R - p1.BR + 1e-9, f"a round 2 ball escaped: {_WR2}"
assert _WF2 < 1e-12, f"round 2 angle in != angle out by {_WF2}"

_G2 = PATH2[F2_WHITE:F2_STOP]
_d2 = np.linalg.norm(_G2[:, RED2][:, None, :] - _G2, axis=-1)
_d2[:, RED2] = 9.9
CROWDED2 = float((_d2.min(1) < 3.0 * p1.BR).mean())
ROAM2 = float(np.linalg.norm(_G2[:, RED2] - _G2[:, RED2].mean(0), axis=1).mean())
assert ROAM2 > 0.34, f"round 2's ball loiters — {ROAM2:.3f}"
assert CROWDED2 > 0.50, f"round 2's ball is too lonely to lose — {CROWDED2:.2f}"

LABEL2 = p1.label_order(PATH2)
ANSWER2 = int(LABEL2[RED2])

assert sorted(LABEL2.tolist()) == list(range(1, N + 1))
assert ANSWER2 not in (1, N), f"round 2's answer {ANSWER2} is on the edge"
assert ANSWER2 != ANSWER1, \
    "both rounds landing on the same number would look rigged"

SCREEN2 = np.zeros((FRAMES2, N, 3))
SCREEN2[:, :, 0] = PATH2[:, :, 0] * CR
SCREEN2[:, :, 1] = PATH2[:, :, 1] * CR + CY

A1, A2 = str(ANSWER1), str(ANSWER2)

# The taunts, and the beat each one arrives on. Every one has to land while the
# balls are white and moving, or it is not stealing anything.
TAUNTS = [(31, "I'm telling you —"),
          (36, "you can't"),
          (42, "you're reading this"),
          (47, "aren't you"),
          (52, "that's the trick")]
assert all(R2_WHITE < b < R2_STOP for b, _ in TAUNTS), \
    "a taunt lands outside the tracking stretch, where it costs nothing"
assert [b for b, _ in TAUNTS] == sorted(b for b, _ in TAUNTS)


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


class RedBall2(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.head = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        # 0 = white, exactly as part 1 left it. 1 = revealed.
        self.red1 = ValueTracker(0.0)
        self.dim1 = ValueTracker(0.0)
        self.red2 = ValueTracker(1.0)     # round 2 starts red, then loses it
        self.dim2 = ValueTracker(0.0)

        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_tension()
        self.stage_reveal1()
        self.stage_setup2()
        self.stage_round2()
        self.stage_reveal2()
        self.stage_trick()
        self.takeaway()
        self.share()
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

    def say(self, s, beats=2, color=WHITE_, size=25, extra=()):
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), *extra, run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), *extra,
                      run_time=self.T(beats))
            self.note = new

    def top(self, s, beats, color=WHITE_, size=34, w=4.4):
        """Text at the very top — the thing that steals the ball."""
        new = txt(s, size, color, w=w).move_to(np.array([0, TITLE_Y, 0]))
        if self.head is None:
            self.head = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.head, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.head = new

    # ---------------------------------------------------------- the balls
    def build_set(self, screen, frames, red_i, red_tracker, dim_tracker,
                  frame_fn):
        """One round's ring, trails, balls and (unplaced) numbers."""
        ring = Circle(radius=CR, stroke_color=WHITE_, stroke_width=3.0)
        ring.move_to(np.array([0, CY, 0]))
        trails, balls = VGroup(), VGroup()

        def colour(k):
            if k == red_i:
                return interpolate_color(WHITE_, RED, red_tracker.get_value())
            return interpolate_color(WHITE_, FAINT, dim_tracker.get_value())

        for k in range(N):
            tr = VMobject(stroke_width=2.1)
            tr.set_points_as_corners([screen[0, k],
                                      screen[0, k] + np.array([1e-4, 0, 0])])

            def t_up(mo, k=k):
                i = frame_fn()
                lo = max(0, i - TAIL)
                pts = screen[lo:i + 1:2, k]
                if len(pts) < 2:
                    pts = np.array([screen[i, k],
                                    screen[i, k] + np.array([1e-4, 0, 0])])
                mo.set_points_as_corners(pts)
                mo.set_stroke(colour(k), opacity=0.60)

            tr.add_updater(t_up)
            trails.add(tr)

            d = Dot(screen[frame_fn(), k], radius=DOT_R, fill_color=WHITE_)

            def d_up(mo, k=k):
                mo.move_to(screen[frame_fn(), k])
                mo.set_fill(colour(k), opacity=1.0)

            d.add_updater(d_up)
            balls.add(d)
        return ring, trails, balls

    def numbers(self, screen, frames, label):
        g = VGroup()
        for k in range(N):
            pos = screen[frames - 1, k]
            off = pos - np.array([0, CY, 0])
            off = off / max(np.linalg.norm(off), 1e-6) * (DOT_R + 0.20)
            g.add(txt(str(label[k]), 20, GOLD, w=0.4).move_to(pos + off))
        return g

    def fi1(self):
        return FRAMES1 - 1                       # part 1's freeze, always

    def fi2(self):
        i = int(round((self.clock.get_value() - R2_GO * self.B) * FPS))
        return max(0, min(i, FRAMES2 - 1))

    # ==================================================================
    # Open on part 1's exact last frame. Nothing has moved.
    # ==================================================================
    def open_card(self):
        self.ring1, self.tr1, self.ba1 = self.build_set(
            SCREEN1, FRAMES1, RED1, self.red1, self.dim1, self.fi1)
        self.num1 = self.numbers(SCREEN1, FRAMES1, LABEL1)
        # A hard cut, not a fade. The trails already carry a hundred frames of
        # path, and fading a mobject whose updater is rewriting its point count
        # every frame breaks the interpolation — but more importantly, landing
        # instantly on part 1's last frame IS the continuity gag.
        self.add(self.tr1, self.ba1, self.ring1, self.num1)
        self.top("PART 2", 1.5, RED, 42, 2.6)
        self.say("same nine balls. nothing has moved.", 2)
        self.pad_to(END_OPEN)

    def stage_tension(self):
        self.say("you picked a number.", 2.5, GOLD)
        self.say("no changing it now.", 2.5)
        self.pad_to(END_TENSION)

    # ==================================================================
    # The reveal everybody came for.
    # ==================================================================
    def stage_reveal1(self):
        others = VGroup(*[self.num1[k] for k in range(N) if k != RED1])
        win = self.num1[RED1]
        self.play(FadeOut(others),
                  self.red1.animate.set_value(1.0),
                  self.dim1.animate.set_value(0.62),
                  win.animate.set_color(RED).scale(1.5),
                  run_time=self.T(2.5), rate_func=smooth)
        self.mark1 = Circle(radius=DOT_R * 2.4, stroke_color=RED,
                            stroke_width=3.0)
        self.mark1.move_to(SCREEN1[FRAMES1 - 1, RED1])
        self.play(ShowCreation(self.mark1), run_time=self.T(1.5))
        self.top(f"NUMBER {A1}", 2, RED, 46, 3.6)
        self.say("that is the one you were following.", 2, RED)
        self.say("or thought you were.", 2)
        self.pad_to(END_REVEAL1)

    # ==================================================================
    # Round two. Same game, new ball — and one new thing.
    # ==================================================================
    def stage_setup2(self):
        # same reason: kill the updaters before anything fades them
        self.tr1.clear_updaters()
        self.ba1.clear_updaters()
        for _m in self.tr1:
            _m.clear_updaters()
        for _m in self.ba1:
            _m.clear_updaters()
        self.play(FadeOut(self.tr1), FadeOut(self.ba1), FadeOut(self.ring1),
                  FadeOut(self.num1), FadeOut(self.mark1),
                  run_time=self.T(1.5))
        self.remove(self.tr1, self.ba1, self.num1)

        self.ring2, self.tr2, self.ba2 = self.build_set(
            SCREEN2, FRAMES2, RED2, self.red2, self.dim2, self.fi2)
        self.add(self.tr2, self.ba2, self.ring2)
        self.top("ROUND 2", 1.5, GOLD, 40, 2.8)
        self.play(FadeIn(self.ring2), FadeIn(self.ba2), run_time=self.T(1))

        mark = Circle(radius=DOT_R * 2.4, stroke_color=RED, stroke_width=3.0)
        mark.move_to(SCREEN2[0, RED2])
        self.play(ShowCreation(mark), run_time=self.T(1))
        self.say("this one. lock on.", 1.5, RED)
        self.play(FadeOut(mark), run_time=self.T(END_SETUP - self.used))

    # ==================================================================
    # The trick. The words are at the top. The ball is not.
    # ==================================================================
    def stage_round2(self):
        self.play(self.red2.animate.set_value(0.0),
                  FadeOut(self.head), run_time=self.T(1.5))
        self.head = None
        self.note = None
        self.say("good luck.", 2, GREY)

        for beat, words in TAUNTS:
            self.pad_to(beat)
            self.top(words, 1.5, RED if "trick" in words else WHITE_, 34)
        self.pad_to(R2_STOP)

    # ==================================================================
    # Round two's answer.
    # ==================================================================
    def stage_reveal2(self):
        self.play(FadeOut(self.head), run_time=self.T(1))
        self.head = None
        self.num2 = self.numbers(SCREEN2, FRAMES2, LABEL2)
        self.play(FadeIn(self.num2), run_time=self.T(1.5))
        self.say("still got it?", 2, GOLD)

        others = VGroup(*[self.num2[k] for k in range(N) if k != RED2])
        win = self.num2[RED2]
        self.play(FadeOut(others),
                  self.red2.animate.set_value(1.0),
                  self.dim2.animate.set_value(0.62),
                  win.animate.set_color(RED).scale(1.5),
                  run_time=self.T(2.5), rate_func=smooth)
        self.mark2 = Circle(radius=DOT_R * 2.4, stroke_color=RED,
                            stroke_width=3.0)
        self.mark2.move_to(SCREEN2[FRAMES2 - 1, RED2])
        self.play(ShowCreation(self.mark2), run_time=self.T(1.5))
        self.top(f"NUMBER {A2}", 1.5, RED, 46, 3.6)
        self.pad_to(END_REVEAL2)

    # ==================================================================
    # And now the honest bit.
    # ==================================================================
    def stage_trick(self):
        self.say("you read all that, didn't you.", 3)
        self.say("that is exactly when you lost it.", 3, RED)
        self.say("the ball, or the words.", 2.5)
        self.say("you were never going to get both.", 3)
        self.pad_to(END_TRICK)

    # ------------------------------------------------------------------
    def takeaway(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(1.5))
        self.note = None
        self.head = None
        self.l1 = txt("choosing what to drop is called attention.", 25, SKY,
                      w=4.6).move_to(np.array([0, 0.86, 0]))
        self.play(FadeIn(self.l1, shift=0.10 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.l2 = txt("it is the one idea inside every AI.", 24, WHITE_, w=4.5)
        self.l2.move_to(np.array([0, 0.20, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.l3 = txt("We learned this at school.", 27, WHITE_, w=4.4)
        self.l3.move_to(np.array([0, -0.60, 0]))
        self.l4 = txt("Nobody ever said what for.", 26, GOLD, w=4.5)
        self.l4.move_to(np.array([0, -1.22, 0]))
        self.play(FadeIn(self.l3, shift=0.10 * UP), run_time=self.T(1.5))
        self.play(FadeIn(self.l4), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to whoever", 27, WHITE_, w=4.5)
        s2 = txt("said the wrong number", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.20, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), FadeOut(self.l3),
                  FadeOut(self.l4), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.10, 0])).scale(0.74)
        self.play(ShowCreation(eye), run_time=self.T(2.5))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.42, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.2))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1.3))
        self.pad_to(TOTAL - 1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg),
                  run_time=self.T(1.5))
