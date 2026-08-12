"""
neuron — one neuron is y = mx + b with a switch on the end. 40.0s.

    BPM=150 manimgl neuron.py Neuron -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

EPISODE 3 OF "WHY DID WE LEARN THIS?" — same shell as sales_line.py and
cosine_similarity.py: the equation is the spine, it sits at the top for the
whole video, it starts EMPTY, and every number is dragged into its slot off
the picture.

    z  =  w · x  +  b               the line from episode 1, renamed
    y  =  max( 0, z )               and one switch on the end

THAT IS THE ENTIRE CALLBACK. `z = w·x + b` is character-for-character the shape
of `y = m·x + b` — the same slots, the same drag, the same picture logic. The
only new thing in the whole video is the switch, and the switch is the reason a
stack of these can do anything a straight line cannot.

    w  ←  2      how much this input matters
    x  ←  3      what came in
    b  ←  −4     how hard the neuron is to set off
    z  =  2·3 + (−4)  =  2      positive, so it goes through: y = 2

Then the payoff, which is the same neuron and one different input:

    x  ←  1
    z  =  2·1 + (−4)  =  −2     negative, so the switch shuts: y = 0

SAME NUMBER DISCIPLINE AS EPISODE 1. Every number on screen is a small integer,
one arrives per stage, and the two results are exact: 2 and 0. The bias is
negative on purpose — it is what makes the second case shut off, and "b = −4
means the input has to beat 4" is a sentence a fourteen-year-old can hold.

VERIFIED AT IMPORT
    z1 == 2 and y1 == 2        the firing case, in integers
    z2 == -2 and y2 == 0       the silent case — the switch actually does work
    every number shown is a whole number
    relu really is max(0, z)   checked against both branches

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

END_OPEN = 8
END_PARTS, END_FILL, END_FIRE, END_SILENT = 26, 46, 64, 82
END_TAKE = 90

SERIES = "WHY DID WE LEARN THIS?"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
LEAF   = "#A3BE8C"
RUST   = "#BF616A"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
LINE_Y  = -2.05
EQ_Y    = 2.44
SW_Y    = 1.82          # the switch line, under the spine
ANS_Y   = 1.20          # and the working under that
NOTE_Y  = -2.34

W, X1, Bi = 2, 3, -4
X2 = 1


def relu(v):
    return max(0, v)


Z1 = W * X1 + Bi
Y1 = relu(Z1)
Z2 = W * X2 + Bi
Y2 = relu(Z2)

assert (Z1, Y1) == (2, 2), (Z1, Y1)          # fires
assert (Z2, Y2) == (-2, 0), (Z2, Y2)         # and the switch really shuts
assert all(float(v).is_integer() for v in (W, X1, X2, Bi, Z1, Y1, Z2, Y2))
assert relu(-7) == 0 and relu(7) == 7        # both branches

# a proper minus, and the bias parenthesised in the slot: the "+" piece is
# fixed, so a bare -4 would render as "+ -4"
MINUS = "\u2212"
WS = str(W)
BW = f"{MINUS}{abs(Bi)}"          # on the wire
BS_ = f"({BW})"                   # in the slot, after the +
X1S, X2S = str(X1), str(X2)
Z1S, Y1S, Y2S = str(Z1), str(Y1), str(Y2)
Z2S = f"{MINUS}{abs(Z2)}"

# the spine: z = w · x + b   (deliberately the shape of episode 1's line)
BASE = ["z", "=", "w", "·", "x", "+", "b"]
IDX_W, IDX_X, IDX_B = 2, 4, 6

# the neuron on stage
IN_P   = np.array([-1.62, -0.35, 0.0])
BODY_P = np.array([0.16, -0.35, 0.0])
OUT_P  = np.array([1.72, -0.35, 0.0])
BODY_R = 0.42


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, wid=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=wid)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    return m


def wire(a, b, color=GREY, wid=3.4):
    """A wire with an arrowhead, so the direction of travel is never in doubt."""
    n = (b - a) / (np.linalg.norm(b - a) + 1e-9)
    perp = np.array([-n[1], n[0], 0.0])
    g = VGroup(seg(a, b - n * 0.08, color, wid))
    head = VMobject(stroke_width=0)
    head.set_points_as_corners([b, b - n * 0.24 + perp * 0.10,
                                b - n * 0.24 - perp * 0.10, b])
    head.set_fill(color, opacity=1.0)
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


class Neuron(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.filled = {}
        self.ans = None
        self.sw = None

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
        self.stage_parts()
        self.stage_fill()
        self.stage_fire()
        self.stage_silent()
        self.takeaway("We learned this at school.",
                      "Nobody ever said what for.")
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
    def make_eq(self, active=None, also=None, size=40):
        fill = dict(self.filled)
        if also:
            fill.update(also)
        g = VGroup()
        for i, base in enumerate(BASE):
            s = fill.get(i, base)
            done = i in fill
            if i == active:
                col, sz = GOLD, int(size * 1.14)
            elif done:
                col, sz = GOLD, size
            elif i in (IDX_W, IDX_X, IDX_B):
                col, sz = DIM, size
            else:
                col, sz = WHITE_, size
            g.add(txt(s, sz, col, w=1.8))
        g.arrange(RIGHT, buff=0.13)
        if g.get_width() > 4.5:
            g.set_width(4.5)
        return g.move_to(np.array([0, EQ_Y, 0]))

    def relight(self, active, beats, extra=()):
        self.play(Transform(self.eq, self.make_eq(active)), *extra,
                  run_time=self.T(beats))

    def drag_into(self, source_point, slot, value, size, fly=2.5, settle=1.5,
                  shown=None):
        """`shown` differs from `value` when the slot needs dressing — the
        bias flies as −4 and lands as (−4), because the spine's "+" is fixed."""
        shown = shown if shown is not None else value
        nxt = self.make_eq(active=slot, also={slot: shown})
        target = nxt[slot]
        flier = txt(value, size, GOLD, w=1.8).move_to(source_point)
        self.add(flier)
        self.play(flier.animate.move_to(target.get_center())
                  .set_height(target.get_height()),
                  run_time=self.T(fly), rate_func=smooth)
        self.filled[slot] = shown
        self.play(Transform(self.eq, nxt), FadeOut(flier),
                  run_time=self.T(settle))

    def show_ans(self, s, beats, color=WHITE_, size=32):
        new = txt(s, size, color, w=4.2).move_to(np.array([0, ANS_Y, 0]))
        if self.ans is None:
            self.ans = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(Transform(self.ans, new), run_time=self.T(beats))

    def show_switch(self, s, beats, color=WHITE_, size=32):
        new = txt(s, size, color, w=4.2).move_to(np.array([0, SW_Y, 0]))
        if self.sw is None:
            self.sw = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(Transform(self.sw, new), run_time=self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("one neuron", 46, WHITE_, w=4.6),
                     txt("is y = mx + b", 46, GOLD, w=4.6)) \
            .arrange(DOWN, buff=0.24)
        big.move_to(np.array([0, 0.80, 0]))
        sub = txt("with one switch on the end", 23, GREY, bold=False)
        sub.move_to(np.array([0, -0.30, 0]))
        self.add(big, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.35, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # the picture: one input, one wire, one body, one output
    # ==================================================================
    def stage_parts(self):
        self.win = wire(IN_P, BODY_P - np.array([BODY_R, 0, 0]), GREY)
        self.body = Circle(radius=BODY_R, stroke_color=GREY, stroke_width=3.4)
        self.body.set_fill(BLACK, 1.0).move_to(BODY_P)
        self.wout = wire(BODY_P + np.array([BODY_R, 0, 0]), OUT_P, GREY)
        self.indot = Dot(IN_P, radius=0.10, fill_color=GREY)
        self.play(FadeIn(self.indot), ShowCreation(self.win),
                  ShowCreation(self.body), ShowCreation(self.wout),
                  run_time=self.T(2.5))
        self.say("one neuron. that is the whole thing.", 2)

        self.lx = txt("x", 28, GOLD, w=0.5).move_to(IN_P + np.array([0, -0.40, 0]))
        self.play(FadeIn(self.lx), Transform(self.eq, self.make_eq(IDX_X)),
                  self.win.animate.set_stroke(GOLD), run_time=self.T(2))
        self.say("x is what comes in.", 2)

        self.lw = txt("w", 28, SKY, w=0.5).move_to(
            (IN_P + BODY_P) / 2 + np.array([-0.10, 0.34, 0]))
        self.play(FadeIn(self.lw), Transform(self.eq, self.make_eq(IDX_W)),
                  self.win.animate.set_stroke(SKY), run_time=self.T(2))
        self.say("w is how much it matters.", 2)

        self.lb = txt("b", 28, LEAF, w=0.5).move_to(BODY_P)
        self.play(FadeIn(self.lb), Transform(self.eq, self.make_eq(IDX_B)),
                  self.body.animate.set_stroke(LEAF), run_time=self.T(2))
        self.say("b is how hard it is to set off.", 2)
        self.pad_to(END_PARTS)

    # ==================================================================
    # put real numbers on the wires and drag them in
    # ==================================================================
    def stage_fill(self):
        self.relight(IDX_W, 1.0, extra=[self.zoom.animate.set_value(0.95)])
        nw = txt(WS, 26, SKY, w=0.6).move_to(self.lw.get_center()
                                             + np.array([0.34, 0, 0]))
        self.play(FadeIn(nw, scale=1.3), run_time=self.T(1))
        self.drag_into(nw.get_center(), IDX_W, WS, 26)

        self.relight(IDX_X, 1.0)
        self.nx = txt(X1S, 26, GOLD, w=0.6).move_to(self.lx.get_center()
                                                    + np.array([0.34, 0, 0]))
        self.play(FadeIn(self.nx, scale=1.3), run_time=self.T(1))
        self.drag_into(self.nx.get_center(), IDX_X, X1S, 26)

        self.relight(IDX_B, 1.0)
        nb = txt(BW, 26, LEAF, w=0.9).move_to(BODY_P + np.array([0, -0.68, 0]))
        self.play(FadeIn(nb, scale=1.3), run_time=self.T(1))
        self.drag_into(nb.get_center(), IDX_B, BW, 26, shown=BS_)

        self.wirenums = VGroup(nw, nb)
        self.say("minus four means the input has to beat 4.", 2, LEAF)
        self.pad_to(END_FILL)

    # ==================================================================
    # it fires
    # ==================================================================
    def stage_fire(self):
        self.show_ans(f"{WS} · {X1S} + {BS_}", 2.5)
        self.say("two times three is six.", 2)
        self.show_ans(f"6 {MINUS} 4  =  {Z1S}", 2.5, GOLD)

        self.show_switch(f"y = max( 0, {Z1S} )", 2.5)
        self.say("positive, so it goes straight through.", 2)

        self.outn = txt(Y1S, 34, GOLD, w=0.8).move_to(OUT_P
                                                      + np.array([0.10, 0.44, 0]))
        self.play(self.wout.animate.set_stroke(GOLD),
                  self.body.animate.set_stroke(GOLD, 5.0),
                  FadeIn(self.outn, scale=1.6), run_time=self.T(2.5))
        self.say("the neuron fires. output 2.", 2)
        self.pad_to(END_FIRE)

    # ==================================================================
    # same neuron, one different input — and it shuts up
    # ==================================================================
    def stage_silent(self):
        self.say("same neuron. change only what comes in.", 2,
                 extra=[self.zoom.animate.set_value(0.93)])

        nx2 = txt(X2S, 26, GOLD, w=0.6).move_to(self.nx.get_center())
        self.play(Transform(self.nx, nx2),
                  Transform(self.eq, self.make_eq(IDX_X, also={IDX_X: X2S})),
                  run_time=self.T(2.5))
        self.filled[IDX_X] = X2S

        self.show_ans(f"{WS} · {X2S} + {BS_}", 2)
        self.show_ans(f"2 {MINUS} 4  =  {Z2S}", 2.5, RUST)
        self.show_switch(f"y = max( 0, {Z2S} )", 2.5, RUST)
        self.say("negative. nothing gets through.", 2, RUST)

        zero = txt(Y2S, 34, DIM, w=0.8).move_to(self.outn.get_center())
        self.play(Transform(self.outn, zero),
                  self.wout.animate.set_stroke(FAINT),
                  self.body.animate.set_stroke(DIM, 3.4), run_time=self.T(2.5))
        self.say("same neuron. silent.", 2)
        self.pad_to(END_SILENT)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.eq, self.sw, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(2))
        self.note = None
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2.5),
                  rate_func=rush_from)
        l2 = txt(b, 27, GOLD, w=4.5)
        l2.move_to(np.array([0, -0.65, 0]))
        self.play(FadeIn(l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.eq), FadeOut(self.sw),
                  FadeOut(self.title), run_time=self.T(1.5))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3.5))
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
