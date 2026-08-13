"""
map_bearing — sin and cos, on a real map. 40.0s.

    BPM=150 manimgl map_bearing.py MapBearing -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 8, AND THE FIRST OF THE "WHERE YOU ACTUALLY USE IT" COMPANIONS —
episode 5's formula, run on a problem a person actually has.

        east   =  r · cos θ
        north  =  r · sin θ

SAME SPINE AS EPISODE 5, WITH THE LETTERS RENAMED TO WHAT THEY ARE. x and y
were never abstract. On a map they are east and north, and that renaming is
most of the lesson: the formula did not change, the words did.

THE REAL PROBLEM. Your phone tells you a distance and a direction — "5 km, that
way". A map is a grid; it only speaks east and north. Those are two different
languages for the same place, and sin and cos are the translation. Nothing else
does that job.

        distance   5 km
        direction  cos θ = 0.8, sin θ = 0.6      (earned in episode 5)

        east  = 5 · 0.8 = 4 km
        north = 5 · 0.6 = 3 km

WHY THE VIDEO ENDS ON 4 + 3 vs 5. Walking 4 east then 3 north gets you to the
same place as going 5 straight — but you walked 7 km to do it. That comparison
is free (the picture is already on screen), it is the difference between
distance and displacement, and it is the moment the whole thing stops being
arithmetic and becomes something the viewer has physically done before.

VERIFIED AT IMPORT
    cos² + sin² == 1                  exactly, as Fractions
    5·cos == 4 and 5·sin == 3         whole km, no square roots on screen
    the legs really do reach it       4² + 3² == 5², in integers
    the detour is longer              4 + 3 > 5, which is the closing beat

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from fractions import Fraction

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN = 8
END_MAP, END_FILL, END_ANSWER = 28, 56, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "WHERE YOU ACTUALLY USE IT"

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
EQ_Y   = 2.66
ANS_Y  = 1.50
NOTE_Y = -3.14
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
COS = Fraction(4, 5)          # 0.8   — episode 5's numbers, unchanged
SIN = Fraction(3, 5)          # 0.6
R   = 5                       # km

EAST, NORTH = R * COS, R * SIN        # 4 and 3, exactly

assert COS * COS + SIN * SIN == 1
assert (EAST, NORTH) == (4, 3), (EAST, NORTH)
assert EAST * EAST + NORTH * NORTH == R * R, "the legs must actually reach it"
assert EAST + NORTH > R, "the closing beat depends on the detour being longer"

_th = float(np.arccos(float(COS)))
assert abs(np.cos(_th) - float(COS)) < 1e-12
assert abs(np.sin(_th) - float(SIN)) < 1e-12

CS, SS = "0.8", "0.6"
RS, ES, NS = str(R), str(EAST), str(NORTH)
DETOUR = EAST + NORTH
assert DETOUR == 7

ROWS = [["east",  "=", "r", "·", "cos θ"],
        ["north", "=", "r", "·", "sin θ"]]
NCOL = len(ROWS[0])
S_R   = (2, 7)
S_COS = (4,)
S_SIN = (9,)
SLOTS = S_R + S_COS + S_SIN

for _g, _w in ((S_R, "r"), (S_COS, "cos θ"), (S_SIN, "sin θ")):
    for _i in _g:
        assert ROWS[_i // NCOL][_i % NCOL] == _w, (_i, _w)


def rc(slot):
    return divmod(slot, NCOL)


# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners([np.asarray(a, float), np.asarray(b, float)])
    m.set_stroke(opacity=op)
    return m


def dashed(a, b, color=GOLD, wid=2.4, n=12):
    g = VGroup()
    a, b = np.asarray(a, float), np.asarray(b, float)
    for i in range(n):
        t0, t1 = i / n, (i + 0.55) / n
        g.add(seg(a + (b - a) * t0, a + (b - a) * t1, color, wid, 0.9))
    return g


def arrow(a, b, color=GOLD, wid=4.0):
    a, b = np.asarray(a, float), np.asarray(b, float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0], 0.0])
    h = min(0.20, 0.32 * L)
    g = VGroup(seg(a, b - u * h * 0.55, color, wid))
    head = VMobject(stroke_width=0)
    head.set_points_as_corners([b, b - u * h + n * h * 0.46,
                                b - u * h - n * h * 0.46, b])
    head.set_fill(color, 1.0)
    g.add(head)
    return g


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


class MapBearing(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.ans = None
        self.filled = {}

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.zoom = ValueTracker(1.0)
        self.camera.frame.add_updater(lambda m: m.set_height(
            FRAME_H * self.zoom.get_value() * (
                1.0 - BREATH_AMT * 0.5 * (1 - np.cos(
                    2 * np.pi * self.clock.get_value()
                    / (BREATH_BEATS * self.B))))))

        self.open_card()
        self.stage_map()
        self.stage_fill()
        self.stage_answer()
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

    # ---------------------------------------------------- the equation
    def make_eq(self, active=(), also=None, size=34):
        active = active if isinstance(active, (tuple, list)) else (active,)
        fill = dict(self.filled)
        if also:
            fill.update(also)
        rows = VGroup()
        for r, row in enumerate(ROWS):
            g = VGroup()
            for c, base in enumerate(row):
                i = r * NCOL + c
                s = fill.get(i, base)
                if i in active:
                    col, sz = GOLD, int(size * 1.14)
                elif i in fill:
                    col, sz = GOLD, size
                elif i in SLOTS:
                    col, sz = DIM, size
                else:
                    col, sz = WHITE_, size
                g.add(txt(s, sz, col, w=1.6))
            g.arrange(RIGHT, buff=0.11)
            rows.add(g)
        rows.arrange(DOWN, buff=0.20)
        rows[1].shift(RIGHT * (rows[0][1].get_center()[0]
                               - rows[1][1].get_center()[0]))
        if rows.get_width() > 4.55:
            rows.set_width(4.55)
        return rows.move_to(np.array([0, EQ_Y, 0]))

    def drag_into(self, source_point, slots, value, size, fly=2.5, settle=1.5):
        fill = {i: value for i in slots}
        nxt = self.make_eq(active=slots, also=fill)
        r, c = rc(slots[0])
        target = nxt[r][c]
        flier = txt(value, size, GOLD, w=1.6).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("east  = r · cos θ", 36, GOLD, w=4.3),
                     txt("north = r · sin θ", 36, GOLD, w=4.3)) \
            .arrange(DOWN, buff=0.20).move_to(np.array([0, 1.18, 0]))
        q = VGroup(txt("your map is a grid.", 31, WHITE_, w=4.6),
                   txt("the world is not.", 31, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.16, 0]))
        sub = txt("sin and cos are the translation", 22, GREY, bold=False)
        sub.move_to(np.array([0, -1.06, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.62, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # The map, you on it, and the place you are trying to get to.
    # ==================================================================
    def stage_map(self):
        self.U = 0.42
        self.O = np.array([-1.00, -1.62, 0])

        def Q(x, y):
            return self.O + np.array([float(x) * self.U, float(y) * self.U, 0])

        self.Q = Q
        grid = VGroup()
        for k in range(0, 7):
            grid.add(seg(Q(k, 0), Q(k, 6), FAINT, 1.7, 0.75))
            grid.add(seg(Q(0, k), Q(6, k), FAINT, 1.7, 0.75))
        axes = VGroup(seg(Q(0, 0), Q(6.2, 0), GREY, 2.4, 0.85),
                      seg(Q(0, 0), Q(0, 6.2), GREY, 2.4, 0.85))
        elab = txt("EAST", 18, GREY, bold=False, w=1.0)
        elab.move_to(Q(6.2, 0) + np.array([-0.10, -0.28, 0]))
        nlab = txt("NORTH", 18, GREY, bold=False, w=1.2)
        nlab.move_to(Q(0, 6.2) + np.array([0.52, 0.02, 0]))
        ticks = VGroup()
        for k in (2, 4):
            ticks.add(txt(str(k), 15, GREY, bold=False, w=0.4)
                      .move_to(Q(k, 0) + np.array([0, -0.22, 0])))
            ticks.add(txt(str(k), 15, GREY, bold=False, w=0.4)
                      .move_to(Q(0, k) + np.array([-0.24, 0, 0])))
        self.pic = VGroup(grid, axes, elab, nlab, ticks)
        self.play(FadeIn(grid), ShowCreation(axes), run_time=self.T(2.5))
        self.play(FadeIn(elab), FadeIn(nlab), FadeIn(ticks), run_time=self.T(1.5))

        you = Dot(Q(0, 0), radius=0.10, fill_color=WHITE_)
        ylab = txt("you", 19, WHITE_, bold=False, w=0.8)
        ylab.move_to(Q(0, 0) + np.array([-0.38, -0.22, 0]))
        there = Dot(Q(EAST, NORTH), radius=0.10, fill_color=ROSE)
        tlab = txt("there", 19, ROSE, bold=False, w=1.0)
        tlab.move_to(Q(EAST, NORTH) + np.array([0.46, 0.16, 0]))
        self.ray = arrow(Q(0, 0), Q(EAST, NORTH), GOLD, 4.0)
        self.pic.add(you, ylab, there, tlab, self.ray)
        self.play(FadeIn(you, scale=1.8), FadeIn(ylab), run_time=self.T(1.5))
        self.play(ShowCreation(self.ray), FadeIn(there, scale=1.8),
                  FadeIn(tlab), run_time=self.T(2.5))

        self.rlab = txt(f"{RS} km", 22, GOLD, w=1.2).move_to(
            Q(EAST, NORTH) * 0.5 + Q(0, 0) * 0.5 + np.array([-0.42, 0.30, 0]))
        self.pic.add(self.rlab)
        self.play(FadeIn(self.rlab), run_time=self.T(1.5))
        self.say("your phone says: 5 km, that way.", 3)
        self.say("but a map only speaks east and north.", 3)
        self.pad_to(END_MAP)

    # ==================================================================
    # The direction, recalled from episode 5, and the distance.
    # ==================================================================
    def stage_fill(self):
        self.say("two languages. sin and cos translate.", 2.5, SKY)
        card = VGroup(txt("that direction, in numbers:", 21, GREY,
                          bold=False, w=3.4),
                      txt(f"cos θ = {CS}      sin θ = {SS}", 25, SKY, w=4.3)) \
            .arrange(DOWN, buff=0.16).move_to(np.array([0, 0.60, 0]))
        self.play(FadeIn(card, shift=0.10 * UP), run_time=self.T(2.5))
        self.say("how far across one turn goes, and how far up.", 3)

        fill = {i: CS for i in S_COS}
        fill.update({i: SS for i in S_SIN})
        nxt = self.make_eq(active=S_COS + S_SIN, also=fill)
        self.filled.update(fill)
        self.play(Transform(self.eq, nxt), FadeOut(card, shift=0.6 * UP),
                  run_time=self.T(3))
        self.say("that is the direction, handled.", 2.5)

        self.play(self.zoom.animate.set_value(0.96), run_time=self.T(1.5))
        self.say("now the distance. it is r, and it is 5.", 2.5, GOLD)
        self.drag_into(self.rlab.get_center(), S_R, RS, 22, fly=3, settle=2)
        self.say("both rows. one journey, two answers.", 3)
        self.pad_to(END_FILL)

    # ==================================================================
    # 4 km east, 3 km north — and what that actually costs you.
    # ==================================================================
    def stage_answer(self):
        self.ans = txt(f"east {ES} km      north {NS} km", 28, GOLD, w=4.4)
        self.ans.move_to(np.array([0, ANS_Y, 0]))
        self.play(FadeIn(self.ans, scale=1.10), run_time=self.T(2.5),
                  rate_func=rush_from)

        Q = self.Q
        leg_e = seg(Q(0, 0), Q(EAST, 0), GREEN, 4.4)
        e_lab = txt(f"{ES} km east", 20, GREEN, w=1.6).move_to(
            Q(EAST / 2, 0) + np.array([0, -0.30, 0]))
        self.pic.add(leg_e, e_lab)
        self.play(ShowCreation(leg_e), FadeIn(e_lab), run_time=self.T(2.5))
        self.say("5 times 0.8. four kilometres east.", 2.5, GREEN)

        leg_n = seg(Q(EAST, 0), Q(EAST, NORTH), GREEN, 4.4)
        n_lab = txt(f"{NS} km north", 20, GREEN, w=1.8).move_to(
            Q(EAST, NORTH / 2) + np.array([0.72, 0, 0]))
        self.pic.add(leg_n, n_lab)
        self.play(ShowCreation(leg_n), FadeIn(n_lab), run_time=self.T(2.5))
        self.say("5 times 0.6. three kilometres north.", 2.5, GREEN)

        self.say("go 4 east, then 3 north. same place.", 3)
        self.say(f"but that walk is {DETOUR} km, not {RS}.", 3, ROSE)
        self.say("the straight line was always shorter.", 2)
        self.say("that is every sat-nav, every delivery app,", 2.5)
        self.say("and every game character that walks somewhere.", 3)
        self.pad_to(END_ANSWER)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.ans, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, -0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.82, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is how it's solved", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.40, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.eq), FadeOut(self.ans),
                  FadeOut(self.title), run_time=self.T(1.5))

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
