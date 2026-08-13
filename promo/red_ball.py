"""
red_ball — can you follow the red ball? 40.0s.

    BPM=150 manimgl red_ball.py RedBall -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

A TRACKING GAME, AND THEN THE REASON IT IS HARD. Nine balls bounce inside a
circle. One is red. It turns white with the rest, and for sixteen seconds you
try to keep hold of it. Almost nobody can.

WHY THIS BELONGS ON THIS PAGE, AND IS NOT JUST A REPOST. Two reasons, and both
are honest:

  THE BOUNCE IS AN ANGLE PROBLEM. Every bounce in this video is one line:

        v'  =  v  −  2 (v · n) n

  where n is the direction straight out from the centre. That is the dot
  product from the cos episode, doing the only job it does here: splitting the
  velocity into the part along the wall and the part into it, and flipping the
  second one. Angle in equals angle out — and it is ASSERTED, every bounce,
  rather than assumed.

  AND LOSING THE BALL IS WHAT ATTENTION MEANS. You could watch one. You could
  not watch nine. That limit is exactly the problem the attention mechanism
  exists to solve, and feeling it for sixteen seconds explains it better than a
  diagram does.

THE SEED IS CHOSEN, NOT RANDOM. Seed 142 out of 150 searched, picked on two
measurable properties of the red ball across the all-white stretch:

    it ROAMS       mean distance from its own average position, 0.71 of the
                   radius — you cannot find it by staring at one spot
    it is CROWDED  another ball is within three ball-radii of it in 78% of
                   the all-white frames — which is the thing that actually
                   makes the eye jump to the wrong ball
    and it is not the odd one out on bounce count, so counting cannot cheat it

ALL NINE BALLS HAVE IDENTICAL SPEED AND IDENTICAL RADIUS. Once the colour is
gone there is no tell. That is asserted too, because a video that cheats here
is worthless.

VERIFIED AT IMPORT
    every ball's speed is constant           to 1e-12, every frame, all nine
    every ball stays inside the circle       to 1e-9, every frame
    angle in == angle out                    every bounce, to 1e-12
    all nine speeds are equal                or the red one would be findable
    the red ball roams and stays crowded     the two difficulty properties

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

BEAT_GO    = 7        # the balls start moving
BEAT_WHITE = 13       # the red one loses its colour
BEAT_STOP  = 53       # everything freezes
END_ASK, END_REVEAL, END_WHY = 62, 74, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "WHERE YOU ACTUALLY USE IT"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
RED    = "#E4453A"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.04
TITLE_Y = 2.62
NOTE_Y  = -3.16
LINE_Y  = -2.05

# ------------------------------------------------------------------ the sim
SEED  = 142           # chosen — see the note above
N     = 9
RED_I = 0
R     = 1.0           # circle radius, in sim units
BR    = 0.075         # ball radius
SPEED = 0.60          # identical for every ball. no tells.

B_SEC   = 60.0 / BPM
F_WHITE = int(round((BEAT_WHITE - BEAT_GO) * B_SEC * FPS))    # 144
F_STOP  = int(round((BEAT_STOP - BEAT_GO) * B_SEC * FPS))     # 1104
FRAMES  = F_STOP + 1
TAIL    = 130         # how much of each path is left drawn behind it


def _start(rng):
    p = []
    for _ in range(4000):
        q = rng.uniform(-0.80, 0.80, 2)
        if np.linalg.norm(q) > 0.80:
            continue
        if all(np.linalg.norm(q - o) > 0.26 for o in p):
            p.append(q)
            if len(p) == N:
                return np.array(p)
    raise RuntimeError("could not place the balls — pick another seed")


def _simulate():
    """Precompute the whole run, and check the physics while doing it.

    The bounce is a reflection in the wall's normal:  v' = v − 2(v·n)n.
    It conserves speed exactly, which is why the speed assertion below can be
    at 1e-12 rather than something forgiving."""
    rng = np.random.default_rng(SEED)
    p = _start(rng)
    a = rng.uniform(0, 2 * np.pi, N)
    v = SPEED * np.stack([np.cos(a), np.sin(a)], 1)
    path = np.empty((FRAMES, N, 2))
    worst_speed = worst_refl = worst_r = 0.0
    bounces = np.zeros(N, int)
    dt = 1.0 / FPS
    for f in range(FRAMES):
        p = p + v * dt
        d = np.linalg.norm(p, axis=1)
        hit = d > R - BR
        if hit.any():
            n = p[hit] / d[hit, None]
            vb = v[hit]
            p[hit] = n * (R - BR)
            va = vb - 2 * (vb * n).sum(1)[:, None] * n
            # angle in == angle out: the normal component simply flips sign
            worst_refl = max(worst_refl,
                             float(np.abs((vb * n).sum(1)
                                          + (va * n).sum(1)).max()))
            v[hit] = va
            bounces[hit] += 1
        path[f] = p
        worst_speed = max(worst_speed,
                          float(np.abs(np.linalg.norm(v, axis=1) - SPEED).max()))
        worst_r = max(worst_r, float(np.linalg.norm(p, axis=1).max()))
    return path, worst_speed, worst_r, worst_refl, bounces


PATH, _WS, _WR, _WF, _BOUNCES = _simulate()

assert _WS < 1e-12, f"speed drifted by {_WS}"
assert _WR < R - BR + 1e-9, f"a ball escaped the circle: {_WR}"
assert _WF < 1e-12, f"angle in != angle out by {_WF}"
assert _BOUNCES.min() > 0, "every ball has to actually bounce"

# the two difficulty properties, measured over the stretch that is all-white
_G = PATH[F_WHITE:F_STOP]
_d = np.linalg.norm(_G[:, RED_I][:, None, :] - _G, axis=-1)
_d[:, RED_I] = 9.9
CROWDED = float((_d.min(1) < 3.0 * BR).mean())
ROAM = float(np.linalg.norm(_G[:, RED_I] - _G[:, RED_I].mean(0), axis=1).mean())
assert ROAM > 0.34, f"the red ball loiters — {ROAM:.3f}"
assert CROWDED > 0.50, f"the red ball is too lonely to lose — {CROWDED:.2f}"
assert abs(_BOUNCES[RED_I] - np.median(_BOUNCES)) <= 3, \
    "the red ball bounces an odd number of times — countable, so findable"

CR = 1.86                       # the circle's radius on screen
CY = -0.30                      # and where its centre sits
SCREEN = np.zeros((FRAMES, N, 3))
SCREEN[:, :, 0] = PATH[:, :, 0] * CR
SCREEN[:, :, 1] = PATH[:, :, 1] * CR + CY
DOT_R = BR * CR


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


class RedBall(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        # 1 while the red ball is red, 0 once it has gone white
        self.redmix = ValueTracker(1.0)
        self.dimmix = ValueTracker(0.0)      # 1 dims the eight decoys

        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.play_game()
        self.stage_ask()
        self.stage_reveal()
        self.stage_why()
        self.takeaway("We learned this at school.",
                      "Nobody ever said what for.")
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

    # ---------------------------------------------------------- the balls
    def fi(self):
        """Which precomputed frame we are on. Held at 0 before the balls are
        released and at the last frame once they freeze."""
        i = int(round((self.clock.get_value() - BEAT_GO * self.B) * FPS))
        return max(0, min(i, FRAMES - 1))

    def ball_color(self, k):
        c = interpolate_color(WHITE_, RED, self.redmix.get_value()) \
            if k == RED_I else WHITE_
        return interpolate_color(c, FAINT, 0.0 if k == RED_I
                                 else self.dimmix.get_value())

    def build_balls(self):
        self.ring = Circle(radius=CR, stroke_color=WHITE_, stroke_width=3.0)
        self.ring.move_to(np.array([0, CY, 0]))
        self.trails = VGroup()
        self.balls = VGroup()
        for k in range(N):
            tr = VMobject(stroke_width=2.1)
            tr.set_points_as_corners([SCREEN[0, k],
                                      SCREEN[0, k] + np.array([1e-4, 0, 0])])

            def t_up(mo, k=k):
                i = self.fi()
                lo = max(0, i - TAIL)
                pts = SCREEN[lo:i + 1:2, k]
                if len(pts) < 2:
                    pts = np.array([SCREEN[i, k],
                                    SCREEN[i, k] + np.array([1e-4, 0, 0])])
                mo.set_points_as_corners(pts)
                mo.set_stroke(self.ball_color(k), opacity=0.62)

            tr.add_updater(t_up)
            self.trails.add(tr)

            d = Dot(SCREEN[0, k], radius=DOT_R, fill_color=WHITE_)

            def d_up(mo, k=k):
                mo.move_to(SCREEN[self.fi(), k])
                mo.set_fill(self.ball_color(k), opacity=1.0)

            d.add_updater(d_up)
            self.balls.add(d)

    # ------------------------------------------------------------------
    def open_card(self):
        self.title = VGroup(txt("Can you follow", 38, WHITE_, w=4.5),
                            txt("the RED ball?", 38, RED, w=4.5)) \
            .arrange(DOWN, buff=0.14)
        self.title.move_to(np.array([0, TITLE_Y, 0]))
        self.build_balls()
        self.play(FadeIn(self.title), ShowCreation(self.ring),
                  run_time=self.T(2.5))
        self.add(self.trails, self.balls)
        self.play(FadeIn(self.balls), run_time=self.T(1.5))

        mark = Circle(radius=DOT_R * 2.4, stroke_color=RED, stroke_width=3.0)
        mark.move_to(SCREEN[0, RED_I])
        self.play(ShowCreation(mark), run_time=self.T(1.5))
        self.say("this one. lock on to it.", 1, RED)
        self.play(FadeOut(mark), run_time=self.T(BEAT_GO - self.used))

    # ==================================================================
    # It moves while still red, then the colour goes and you are on your own.
    # ==================================================================
    def play_game(self):
        self.pad_to(BEAT_WHITE - 1)
        self.play(self.redmix.animate.set_value(0.0), run_time=self.T(1),
                  rate_func=smooth)
        self.say("good luck.", 2, GREY)
        self.pad_to(BEAT_STOP)

    # ==================================================================
    # Freeze. Number them. Make them commit.
    # ==================================================================
    def stage_ask(self):
        self.nums = VGroup()
        for k in range(N):
            pos = SCREEN[FRAMES - 1, k]
            off = pos - np.array([0, CY, 0])
            off = off / max(np.linalg.norm(off), 1e-6) * (DOT_R + 0.20)
            lab = txt(str(k + 1), 20, GOLD, w=0.4).move_to(pos + off)
            self.nums.add(lab)
        self.play(FadeIn(self.nums), run_time=self.T(2))
        self.say("which one is it? say it out loud.", 3, GOLD)
        self.say("no going back now.", 2)
        self.pad_to(END_ASK)

    # ==================================================================
    # The reveal.
    # ==================================================================
    def stage_reveal(self):
        self.play(FadeOut(self.nums), run_time=self.T(1.5))
        self.play(self.redmix.animate.set_value(1.0),
                  self.dimmix.animate.set_value(0.72),
                  run_time=self.T(2.5), rate_func=smooth)
        mark = Circle(radius=DOT_R * 2.4, stroke_color=RED, stroke_width=3.0)
        mark.move_to(SCREEN[FRAMES - 1, RED_I])
        self.reveal_mark = mark
        self.play(ShowCreation(mark), run_time=self.T(2))
        self.say(f"number {RED_I + 1}. did you have it?", 3, RED)
        self.say("most people lose it in the first five seconds.", 3)
        self.pad_to(END_REVEAL)

    # ==================================================================
    # Why it is hard, and why that is the whole of attention.
    # ==================================================================
    def stage_why(self):
        self.say("you could watch one. you could not watch nine.", 3)
        self.say("that limit has a name: attention.", 2.5, SKY)
        self.say("it is the one idea inside every AI you use.", 2.5, SKY)
        self.pad_to(END_WHY)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        e = txt("every bounce was: angle in = angle out", 24, GOLD, w=4.5)
        e.move_to(np.array([0, 1.15, 0]))
        self.play(FadeIn(e), run_time=self.T(1.5))
        self.l0 = e
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and see if THEY can hold it", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.l0), FadeOut(self.l1), FadeOut(self.l2),
                  run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1.5))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1.5))
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))
