"""
what_does_it_mean — how AI knows what "it" means. 40.0s.

    BPM=150 manimgl what_does_it_mean.py WhatDoesItMean -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

THIS CLOSES A LOOP THE RED BALL VIDEOS OPENED. Both of them end by naming
attention — "that limit is called attention, it is the one idea inside every
AI" — and neither shows what it actually is. This does, and it costs almost
nothing to explain, because attention IS the dot product from the cos episode
doing exactly one job: choosing what to look at.

        score  =  it · word

    the cat sat on the mat because IT was warm

Every word is an arrow (episode 2 established that). To work out what "it"
points at, the model takes the arrow for "it" and dot-products it against every
other word. Highest score wins.

        it   = (3, 4)
        mat  = (0, 5)    ->  3(0) + 4(5)  =  20      <- winner
        cat  = (5, 0)    ->  3(5) + 4(0)  =  15
        sat  = (1, 1)    ->  3(1) + 4(1)  =  7

THE CAT SCORING SECOND IS THE POINT. "The cat" is what most people answer, and
it loses by five. A winner that beats the obvious wrong answer narrowly is a
far better watch than one that wins by a mile — and it is the honest shape of
what a model actually computes: not a certainty, a ranking.

NO SOFTMAX HERE, ON PURPOSE. Turning those scores into percentages needs e^x,
which puts the first rounded number in the whole series on screen. The ranking
is the idea; the percentages are a detail, and they can have their own episode
where the rounding is the subject rather than a smudge.

VERIFIED AT IMPORT
    every score is an integer          countable straight off the grid
    mat wins                           or the sentence's answer is wrong
    cat is second                      the near-miss the video depends on
    the gap is small but decisive      5 points, not 1 and not 15

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats), and always a multiple of 0.25 beats
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN, END_SENTENCE, END_ARROWS = 8, 24, 44
END_SCORES, END_ANSWER = 72, 82
END_TAKE, END_SHARE = 88, 92

SERIES = "THE MATH BEHIND AI"

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
GREEN  = "#A3BE8C"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.05
SENT_Y = 3.16
EQ_Y   = 2.36
NOTE_Y = -3.20
LINE_Y = -2.05

# ------------------------------------------------------------------ numbers
SENTENCE = ["the", "cat", "sat", "on", "the", "mat", "because", "it", "was", "warm"]
QUERY = "it"
IT = (3, 4)
WORDS = [("mat", (0, 5)), ("cat", (5, 0)), ("sat", (1, 1))]

SCORE = {w: IT[0] * v[0] + IT[1] * v[1] for w, v in WORDS}
RANKED = sorted(SCORE.items(), key=lambda kv: -kv[1])
WINNER, TOP = RANKED[0]
SECOND, RUNNER = RANKED[1]

assert all(isinstance(s, int) for s in SCORE.values()), "scores must be countable"
assert WINNER == "mat", f"the sentence's answer is the mat, not the {WINNER}"
assert SECOND == "cat", "the near-miss has to be the cat — it is what people guess"
assert 3 <= TOP - RUNNER <= 8, f"gap of {TOP - RUNNER} is either a tie or a rout"
assert min(SCORE.values()) > 0

BASE = ["score", "=", "it", "·", "word"]
S_WORD = 4


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


class WhatDoesItMean(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.filled = {}
        self.marks = {}

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
        self.stage_sentence()
        self.stage_arrows()
        self.stage_scores()
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
    def make_eq(self, active=None, also=None, size=36):
        fill = dict(self.filled)
        if also:
            fill.update(also)
        g = VGroup()
        for i, base in enumerate(BASE):
            s = fill.get(i, base)
            if i == active:
                col, sz = GOLD, int(size * 1.14)
            elif i in fill:
                col, sz = GOLD, size
            elif i == S_WORD:
                col, sz = DIM, size
            else:
                col, sz = WHITE_, size
            g.add(txt(s, sz, col, w=1.7))
        g.arrange(RIGHT, buff=0.14)
        if g.get_width() > 4.5:
            g.set_width(4.5)
        return g.move_to(np.array([0, EQ_Y, 0]))

    # ------------------------------------------------------------------
    def open_card(self):
        big = txt("score = it · word", 40, GOLD, w=4.4)
        big.move_to(np.array([0, 1.05, 0]))
        q = VGroup(txt("how does AI know", 32, WHITE_, w=4.6),
                   txt("what \"it\" means?", 32, WHITE_, w=4.6)) \
            .arrange(DOWN, buff=0.18).move_to(np.array([0, -0.14, 0]))
        sub = txt("one dot product. that is the whole trick.", 21, GREY,
                  bold=False, w=4.5)
        sub.move_to(np.array([0, -1.06, 0]))
        self.add(big, q, sub)
        self.wait(self.T(5))

        self.title = txt(SERIES, 19, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.88, 0]))
        self.eq = self.make_eq()
        self.play(FadeOut(q), FadeOut(sub), Transform(big, self.eq),
                  FadeIn(self.title), run_time=self.T(3))
        self.remove(big)
        self.add(self.eq)
        self.pad_to(END_OPEN)

    # ==================================================================
    # The sentence, and the word nobody can resolve without looking back.
    # ==================================================================
    def stage_sentence(self):
        self.sent = VGroup()
        for w in SENTENCE:
            self.sent.add(txt(w, 24, WHITE_ if w != QUERY else GOLD, w=1.4))
        self.sent.arrange(RIGHT, buff=0.13)
        if self.sent.get_width() > 4.7:
            self.sent.set_width(4.7)
        self.sent.move_to(np.array([0, SENT_Y, 0]))
        self.play(FadeIn(self.sent), run_time=self.T(2.5))

        i = SENTENCE.index(QUERY)
        self.it_word = self.sent[i]
        ring = Circle(radius=0.20, stroke_color=GOLD, stroke_width=2.6)
        ring.move_to(self.it_word.get_center())
        self.it_ring = ring
        self.play(ShowCreation(ring), run_time=self.T(1.5))
        self.say("\"it\". what is it?", 2.5, GOLD)
        self.say("the cat? the mat? you know. the machine does not.", 3.5)
        self.say("so it measures.", 2)
        self.pad_to(END_SENTENCE)

    # ==================================================================
    # Every word is an arrow — the thing episode 2 already established.
    # ==================================================================
    def stage_arrows(self):
        self.U = 0.40
        self.O = np.array([-0.95, -1.85, 0])

        def Q(x, y):
            return self.O + np.array([float(x) * self.U, float(y) * self.U, 0])

        self.Q = Q
        grid = VGroup()
        for k in range(0, 7):
            grid.add(seg(Q(k, 0), Q(k, 6), FAINT, 1.7, 0.75))
            grid.add(seg(Q(0, k), Q(6, k), FAINT, 1.7, 0.75))
        axes = VGroup(seg(Q(0, 0), Q(6.2, 0), GREY, 2.2, 0.85),
                      seg(Q(0, 0), Q(0, 6.2), GREY, 2.2, 0.85))
        self.pic = VGroup(grid, axes)
        self.play(FadeIn(grid), ShowCreation(axes), run_time=self.T(2))
        self.say("every word is an arrow. that is all a word ever is.", 3)

        self.itray = arrow(Q(0, 0), Q(*IT), GOLD, 4.2)
        ilab = txt("it", 22, GOLD, w=0.6).move_to(
            Q(*IT) + np.array([0.24, 0.18, 0]))
        self.pic.add(self.itray, ilab)
        self.play(ShowCreation(self.itray), FadeIn(ilab), run_time=self.T(2.5))

        self.rays = {}
        for w, v in WORDS:
            r = arrow(Q(0, 0), Q(*v), SKY, 3.4)
            lab = txt(w, 20, SKY, w=0.9).move_to(
                Q(*v) + np.array([0.30, 0.20, 0]))
            self.rays[w] = (r, lab)
            self.pic.add(r, lab)
            self.play(ShowCreation(r), FadeIn(lab), run_time=self.T(1.5))
        self.say("now compare \"it\" against each one.", 2.5)
        self.pad_to(END_ARROWS)

    # ==================================================================
    # Three dot products. Multiply matching, add. That is the score.
    # ==================================================================
    def stage_scores(self):
        self.play(self.zoom.animate.set_value(0.96), run_time=self.T(1.5))
        self.board = VGroup()
        for n, (w, v) in enumerate(WORDS):
            self.filled = {S_WORD: w}
            nxt = self.make_eq(active=S_WORD)
            self.play(Transform(self.eq, nxt), run_time=self.T(1.5))

            ray, lab = self.rays[w]
            self.play(ray.animate.set_stroke(GOLD), run_time=self.T(1))

            work = txt(f"{IT[0]}({v[0]}) + {IT[1]}({v[1]})  =  {SCORE[w]}",
                       26, GOLD, w=4.3)
            work.move_to(np.array([0, 1.62, 0]))
            self.play(FadeIn(work), run_time=self.T(2))

            chip = txt(f"{w}  {SCORE[w]}", 22,
                       GREEN if w == WINNER else SKY, w=1.5)
            chip.move_to(np.array([1.62, 1.0 - 0.52 * n, 0]))
            self.board.add(chip)
            self.play(FadeIn(chip, shift=0.10 * LEFT), FadeOut(work),
                      ray.animate.set_stroke(SKY), run_time=self.T(2))
        self.say("multiply the matching numbers, add. same as always.", 3)
        self.pad_to(END_SCORES)

    # ==================================================================
    # Highest wins. That is attention.
    # ==================================================================
    def stage_answer(self):
        ray, lab = self.rays[WINNER]
        self.play(ray.animate.set_stroke(GREEN).set_stroke(width=4.6),
                  lab.animate.set_color(GREEN),
                  self.board[0].animate.scale(1.25),
                  run_time=self.T(2))
        self.say(f"{TOP} beats {RUNNER}. \"it\" is the {WINNER}.", 3, GREEN)
        self.say(f"the {SECOND} came close. it usually does.", 2)
        self.say("that is attention. a dot product, choosing.", 3, SKY)
        self.pad_to(END_ANSWER)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        keep = (self.clock, self.title, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed],
                  self.zoom.animate.set_value(1.0), run_time=self.T(1.5))
        self.note = None
        self.l1 = txt(a, 29, WHITE_, w=4.4).move_to(np.array([0, 0.10, 0]))
        self.play(FadeIn(self.l1, shift=0.12 * UP), run_time=self.T(2),
                  rate_func=rush_from)
        self.l2 = txt(b, 27, GOLD, w=4.5).move_to(np.array([0, -0.62, 0]))
        self.play(FadeIn(self.l2), run_time=self.T(1.5))
        self.pad_to(END_TAKE)

    def share(self):
        s1 = txt("Send this to your school friend", 27, WHITE_, w=4.5)
        s2 = txt("and tell them THIS is how it's solved", 25, GOLD, w=4.6)
        grp = VGroup(s1, s2).arrange(DOWN, buff=0.20)
        grp.move_to(np.array([0, -0.26, 0]))
        self.play(FadeOut(self.l1), FadeOut(self.l2), run_time=self.T(1))
        self.play(FadeIn(grp, shift=0.12 * UP), run_time=self.T(1.5),
                  rate_func=rush_from)
        self.pad_to(END_SHARE - 1.5)
        self.play(FadeOut(grp), FadeOut(self.title), run_time=self.T(1.5))

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
