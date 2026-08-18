"""
wordle_bits — the smart Wordle guess doesn't feel smart. 40.0s.

    BPM=150 manimgl wordle_bits.py WordleBits -w -r 1080x1920

100 beats = 25 bars = 40.000s at 150 BPM.

A CLOSED WORLD OF 16 REAL FIVE-LETTER WORDS, on purpose. Real Wordle has 2,315
possible answers, which is too many numbers to put on a phone screen. Sixteen
is small enough that every count is checkable by eye, and log2(16) = 4.000 is a
clean ceiling — this video is honest that it is a toy version of the real game,
not the real game.

THE FEEDBACK RULE IS THE REAL WORDLE RULE, duplicate letters and all: green if
the letter is in that exact spot, yellow if it appears elsewhere in the secret
word (with correct handling of repeated letters via a shrinking counter), grey
otherwise.

TWO GUESSES, SAME SIXTEEN WORDS.

    AUDIO -> splits the 16 into only 5 groups. The worst group has 6 words that
             all look IDENTICAL on screen: only the A registers, everywhere
             else grey. That is the guess that "feels" smart — four vowels,
             surely that's informative — and it barely tells you anything.

    CRANE -> splits the 16 into 16 groups. Every single word produces a
             different five-tile pattern. That is not a good result, it is
             THE BEST POSSIBLE RESULT: log2(16) = 4.000 bits, the theoretical
             ceiling for sixteen options, hit exactly.

INFORMATION GAIN, NOT VIBES. The number under each guess is Shannon entropy in
bits: -sum p*log2(p) over the resulting groups. It is the same quantity a
decision tree or a language model is scored on when it has to decide what to
ask, or what token to predict, next.

VERIFIED AT IMPORT
    the feedback rule handles duplicate letters       tested against known cases
    AUDIO's worst group has the size the caption uses  6 of 16, computed
    CRANE reaches the theoretical ceiling exactly       log2(16) = 4.000
    AUDIO's entropy is lower than CRANE's               or the whole point is wrong

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats), always a multiple of 0.25 beats
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
"""
import os
from collections import Counter

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 100

END_OPEN, END_WORLD, END_A, END_B = 8, 20, 44, 68
END_WHY, END_FOLLOW = 80, 92

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"      # wordle "yellow" — present, wrong spot
GREEN  = "#8FBF8F"      # wordle "green"  — correct spot
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
BREATH_BEATS = 32.0
BREATH_AMT   = 0.035
TITLE_Y = 3.42
NOTE_Y  = -3.60
LINE_Y  = -2.05

# ------------------------------------------------------------------ the maths
WORDS = ["CRANE", "STONE", "GRAPE", "PLANT", "BRICK", "FLAME", "GHOST", "LEMON",
         "MUSIC", "PRIZE", "SNAKE", "TIGER", "WATER", "CANDY", "DREAM", "FROST"]
GUESS_FEEL, GUESS_SMART = "AUDIO", "CRANE"
N = len(WORDS)
assert N == 16 and len(set(WORDS)) == N
assert all(len(w) == 5 for w in WORDS + [GUESS_FEEL, GUESS_SMART])


def feedback(guess, secret):
    """The real Wordle rule. Green first, then yellow from what is left over,
    so a repeated letter can never be counted twice."""
    g, s = list(guess), list(secret)
    res = ["B"] * 5
    left = Counter(s)
    for i in range(5):
        if g[i] == s[i]:
            res[i] = "G"
            left[g[i]] -= 1
    for i in range(5):
        if res[i] == "G":
            continue
        if left.get(g[i], 0) > 0:
            res[i] = "Y"
            left[g[i]] -= 1
    return "".join(res)


# duplicate-letter sanity checks — a wrong feedback rule invalidates the video.
# SPEED has two E's against ERASE's two E's: both register, neither in place.
assert feedback("SPEED", "ERASE") == "YBYYB"
# ALLOY is an anagram of LOYAL: every letter present, none in its own spot.
assert feedback("ALLOY", "LOYAL") == "YYYYY"
assert feedback("CRANE", "CRANE") == "GGGGG"


def analyze(guess):
    buckets = Counter(feedback(guess, s) for s in WORDS)
    H = -sum((c / N) * np.log2(c / N) for c in buckets.values())
    return buckets, float(H)

BUCKETS_FEEL, H_FEEL = analyze(GUESS_FEEL)
BUCKETS_SMART, H_SMART = analyze(GUESS_SMART)
CEILING = float(np.log2(N))

assert len(BUCKETS_FEEL) == 5, "AUDIO must split the 16 into five groups"
assert max(BUCKETS_FEEL.values()) == 6, "the worst AUDIO group must hold six words"
assert len(BUCKETS_SMART) == N, "CRANE must give every word a distinct pattern"
assert max(BUCKETS_SMART.values()) == 1
assert CEILING == 4.0, "log2(16) must land on an exact float"
assert H_SMART == CEILING, "CRANE has to hit the ceiling exactly, not approach it"
assert H_FEEL < H_SMART - 1.5, "the contrast has to be large enough to see"

# a stable colour per bucket, ranked by size so the biggest group reads first
ORDER_FEEL = [p for p, _ in sorted(BUCKETS_FEEL.items(), key=lambda kv: -kv[1])]
FEEL_COLOR = {p: c for p, c in zip(ORDER_FEEL,
              [ROSE, SKY, GOLD, "#B48EAD", "#A3BE8C"])}
SMART_COLOR = WHITE_   # every pattern is unique — colour carries no information

GRID_COLS, GRID_ROWS = 4, 4
CELL_W, CELL_H = 1.12, 0.62
GRID_C = np.array([0.0, -0.30, 0.0])
TILE, TGAP = 0.135, 0.028


def cell_pos(i):
    r, c = divmod(i, GRID_COLS)
    x = (c - (GRID_COLS - 1) / 2) * CELL_W
    y = ((GRID_ROWS - 1) / 2 - r) * CELL_H
    return GRID_C + np.array([x, y, 0.0])


assert (GRID_COLS - 1) / 2 * CELL_W + 2.5 * (TILE + TGAP) < 2.45, \
    "the grid must fit inside a 9:16 frame with the camera breath"


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


def tile_row(pattern, colored, center):
    """Five small squares. colored=False draws every tile the same neutral
    grey — used before a guess has been scored."""
    row = VGroup()
    x0 = -(5 * TILE + 4 * TGAP) / 2 + TILE / 2
    for k, ch in enumerate(pattern):
        col = FAINT if not colored else \
            {"G": GREEN, "Y": GOLD, "B": FAINT}[ch]
        sq = Square(side_length=TILE, fill_color=col, fill_opacity=1.0,
                    stroke_width=0)
        sq.move_to(center + np.array([x0 + k * (TILE + TGAP), 0.0, 0.0]))
        row.add(sq)
    return row


class WordleBits(Scene):
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
        self.stage_world()
        self.stage_guess(GUESS_FEEL, BUCKETS_FEEL, H_FEEL, FEEL_COLOR, feel=True)
        self.stage_guess(GUESS_SMART, BUCKETS_SMART, H_SMART,
                         {p: SMART_COLOR for p in BUCKETS_SMART}, feel=False)
        self.stage_why()
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
    def open_card(self):
        self.hook = VGroup(txt("YOUR FIRST GUESS", 30, WHITE_, w=4.2),
                           txt("IS PROBABLY WRONG", 38, GOLD, w=4.4)) \
            .arrange(DOWN, buff=0.14).move_to(np.array([0, 0.4, 0]))
        self.play(FadeIn(self.hook), run_time=self.T(2.5))
        self.say("not wrong as in a bad word.", 3)
        self.say("wrong as in it barely tells you anything.", 2.5)
        self.pad_to(END_OPEN)

    # ==================================================================
    # 16 real words. One of them is the answer. We don't know which.
    # ==================================================================
    def stage_world(self):
        self.play(FadeOut(self.hook), run_time=self.T(1))
        self.title = txt("16 possible answers", 27, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, TITLE_Y, 0]))
        self.words = VGroup()
        self.rows = VGroup()
        for i, w in enumerate(WORDS):
            p = cell_pos(i)
            lab = txt(w, 17, WHITE_, bold=False, w=1.0)
            lab.move_to(p + np.array([0, 0.20, 0]))
            row = tile_row("?????", False, p + np.array([0, -0.10, 0]))
            self.words.add(lab)
            self.rows.add(row)
        self.play(FadeIn(self.title), run_time=self.T(1.5))
        self.play(LaggedStart(*[FadeIn(w) for w in self.words], lag_ratio=0.05),
                  FadeIn(self.rows), run_time=self.T(3))
        self.say("one of these sixteen is the secret word.", 3)
        self.pad_to(END_WORLD)

    # ==================================================================
    def stage_guess(self, guess, buckets, H, colors, feel):
        end = END_A if feel else END_B
        gword = VGroup(*[txt(ch, 30, WHITE_, w=0.6) for ch in guess]) \
            .arrange(RIGHT, buff=0.10).move_to(np.array([0, TITLE_Y + 0.62, 0]))
        if feel:
            self.gword = gword
            self.play(FadeIn(gword, shift=0.1 * DOWN), run_time=self.T(2))
            self.say("what if you guess AUDIO — all vowels, feels thorough?", 4)
        else:
            newg = VGroup(*[txt(ch, 30, WHITE_, w=0.6) for ch in guess]) \
                .arrange(RIGHT, buff=0.10).move_to(gword.get_center())
            self.play(Transform(self.gword, newg), run_time=self.T(2))
            self.say("same sixteen words. new guess: CRANE.", 4)

        anims = []
        for i, w in enumerate(WORDS):
            pat = feedback(guess, w)
            new_row = tile_row(pat, True, cell_pos(i) + np.array([0, -0.10, 0]))
            anims.append(Transform(self.rows[i], new_row))
        self.play(*anims, run_time=self.T(3.5))

        if feel:
            self.say("look — six of them show the exact same thing.", 3.5, ROSE)
        else:
            self.say("look — every single one is different.", 3.5, GREEN)

        hlab = txt(f"{len(buckets)} distinct patterns", 25,
                   ROSE if feel else GREEN, w=3.8)
        hval = txt(f"{H:.3f} bits", 34, GOLD, w=2.6)
        readout = VGroup(hlab, hval).arrange(DOWN, buff=0.16)
        readout.move_to(np.array([0, -2.55, 0]))
        if feel:
            self.readout = readout
            self.play(FadeIn(readout), run_time=self.T(2))
            self.say("that number is how much you actually learned.", 3.5)
        else:
            newr = VGroup(txt(f"{len(buckets)} distinct patterns", 25, GREEN, w=3.8),
                          txt(f"{H:.3f} bits", 34, GOLD, w=2.6)) \
                .arrange(DOWN, buff=0.16).move_to(self.readout.get_center())
            self.play(Transform(self.readout, newr), run_time=self.T(2))
            self.say(f"log2(16) = {CEILING:.3f}. that is the maximum possible.", 4)
            self.say("CRANE hits the ceiling exactly.", 3, GREEN)
        self.pad_to(end)

    # ==================================================================
    def stage_why(self):
        self.say("you never had to know the secret word.", 3)
        self.say("you only had to know which guess teaches you more.", 3)
        self.say("that number is called information gain.", 3, GOLD)
        self.say("it's the same bit-count a model is scored on.", 3)
        self.pad_to(END_WHY)

    # ==================================================================
    def stage_follow(self):
        keep = (self.clock, self.camera.frame)
        doomed = [m for m in self.mobjects if m not in keep]
        for m in doomed:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in doomed], run_time=self.T(1))
        self.note = None

        f1 = txt("INFORMATION GAIN", 32, GOLD, w=4.5)
        f1.move_to(np.array([0, 0.92, 0]))
        f2 = txt("choose the guess that teaches you more", 22, WHITE_, w=4.4)
        f2.move_to(np.array([0, 0.24, 0]))
        f3 = txt("follow — the math behind AI", 21, GREY, bold=False, w=4.2)
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
