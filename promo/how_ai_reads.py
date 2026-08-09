"""
how_ai_reads — chunks and threads. 32.0s.

    BPM=150 manimgl how_ai_reads.py HowAIReads -w -r 1080x1920

80 beats = 20 bars = 32.000s at 150 BPM.

TWO STAGES ONLY. The first draft had three (tokens, numbers, threads) and was
too dense to be fun. "Every token becomes a row of numbers" is true and it is
the part nobody needed, so it is gone.

    1  CHUNKS    watch a word get built out of letters, then broken into pieces
    2  THREADS   which word does "it" point at, and what changes the answer

STAGE 1 IS A REAL BPE, TRAINED AT BUILD TIME.
tiktoken installs here but its vocabulary lives behind a blocked host, so rather
than quote GPT's splits from memory this file IMPLEMENTS byte-pair encoding and
trains it on the corpus below. Every merge on screen is one the algorithm
actually made, in the order it made it:

    e + r    -> er        b + er -> ber      berr + y -> berry
    s + t    -> st        st + ra -> stra    stra + w -> straw

Nobody told it about "straw" or "berry". It merged whatever pair was most
frequent and those fell out. The result:

    strawberry -> [straw][berry]      2 chunks, and the word contains 3 r's

which is the joke and also the honest reason letter-counting is hard: the model
is not looking at letters, it is looking at two pieces.

WHAT IS NOT CLAIMED. This is BPE — the algorithm GPT-style tokenizers use —
trained on a toy corpus. The splits are this tokenizer's, not OpenAI's, and the
video says "a tokenizer", never "GPT splits it this way".

STAGE 2's WEIGHT IS A COMPUTED SOFTMAX, NOT A MEASURED ATTENTION HEAD. The
scores are stated as an example and the weights are their exact softmax,
asserted to sum to 1. No model was run and the video does not imply one was.
The sentence is the standard Winograd-style pair: swapping "tired" for "wide"
moves what "it" refers to from the animal to the street. That is a fact about
English, not a measurement.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import os
from collections import Counter

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 80

END_OPEN, END_CARD1, END_CHUNK = 4, 8, 36
END_CARD2, END_THREAD = 40, 66
END_TAKE = 70

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
CAP_Y   = 1.78
NOTE_Y  = -1.62

# ------------------------------------------------------------ real BPE
CORPUS = ("the cat sat on the mat and the dog sat on the log "
          "strawberry blueberry blackberry raspberry berry berries "
          "straw strawberries strawberry jam strawberry cake "
          "she is reading a reader and he is teaching a teacher "
          "running walking talking reading teaching learning "
          "unbelievable unhappy unusual unable undo unlock "
          "believable readable teachable lovable movable "
          "the teacher is teaching the reader is reading ") * 8
N_MERGES = 32          # tuned: enough to learn straw and berry, not to fuse them


def train_bpe(corpus, n_merges):
    vocab = Counter(tuple(w) + ("_",) for w in corpus.split())
    merges = []
    for _ in range(n_merges):
        pairs = Counter()
        for w, f in vocab.items():
            for i in range(len(w) - 1):
                pairs[(w[i], w[i + 1])] += f
        if not pairs:
            break
        best, cnt = pairs.most_common(1)[0]
        if cnt < 2:
            break
        merges.append((best, cnt))
        nv = Counter()
        for w, f in vocab.items():
            out, i = [], 0
            while i < len(w):
                if i < len(w) - 1 and (w[i], w[i + 1]) == best:
                    out.append(w[i] + w[i + 1]); i += 2
                else:
                    out.append(w[i]); i += 1
            nv[tuple(out)] += f
        vocab = nv
    return merges


def bpe_states(word, merges):
    """Every distinct chunking of `word` as the merges apply, in order."""
    w = tuple(word) + ("_",)
    vis = lambda t: [x.replace("_", "") for x in t if x != "_"]
    states = [vis(w)]
    for (a, b), _ in merges:
        out, i = [], 0
        while i < len(w):
            if i < len(w) - 1 and w[i] == a and w[i + 1] == b:
                out.append(a + b); i += 2
            else:
                out.append(w[i]); i += 1
        w = tuple(out)
        if vis(w) != states[-1]:
            states.append(vis(w))
    return states


MERGES = train_bpe(CORPUS, N_MERGES)
STATES = bpe_states("strawberry", MERGES)
RARE = bpe_states("zqvfth", MERGES)[-1]

assert STATES[0] == list("strawberry"), STATES[0]
assert STATES[-1] == ["straw", "berry"], STATES[-1]
assert "strawberry".count("r") == 3
assert len(RARE) >= 5, RARE            # an unseen word stays in pieces

# ------------------------------------------------------------ real softmax
ATT_SCORES = np.array([4.2, 2.1, 0.8, 0.3])     # stated example, not measured
_e = np.exp(ATT_SCORES - ATT_SCORES.max())
ATT_W = _e / _e.sum()
assert abs(ATT_W.sum() - 1.0) < 1e-9
TOP_PCT = int(round(ATT_W[0] * 100))
assert TOP_PCT == 85, TOP_PCT

SENT1 = ["the", "animal", "didn't", "cross", "the", "street"]
SENT2 = ["because", "it", "was", "too", "tired"]


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def chip(s, color=WHITE_, size=24, pad=0.15, h=0.52):
    t = txt(s, size, color, bold=False, w=2.4)
    box = Rectangle(width=t.get_width() + pad * 2, height=h, stroke_width=2.2)
    box.set_stroke(color, opacity=0.9)
    box.set_fill(color, opacity=0.10)
    return VGroup(box, t.move_to(box.get_center()))


def chip_row(tokens, color=WHITE_, size=24, buff=0.10, y=0.55, maxw=4.6):
    g = VGroup(*[chip(t, color, size) for t in tokens]).arrange(RIGHT, buff=buff)
    if g.get_width() > maxw:
        g.set_width(maxw)
    return g.move_to(np.array([0, y, 0]))


def thread(a, b, color=GOLD, w=3.0, op=0.9):
    """A STRAIGHT link with a dot at each end.

    The first cut used a sagging curve, but the two text lines sit ~1 unit apart
    and the sag dipped below both endpoints — the threads read as underlines
    scribbled through the sentence rather than as links between words.
    """
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    g = VGroup(m)
    for p in (a, b):
        g.add(Dot(p, radius=0.055 + 0.012 * w, fill_color=color).set_opacity(op))
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


class HowAIReads(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.stage = []
        self.marker = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open_card()
        self.section_card(1, "CHUNKS", END_CARD1)
        self.part1_chunks()
        self.section_card(2, "THREADS", END_CARD2)
        self.part2_threads()
        self.takeaway("It never reads a word.", "It reads the pieces, and the links.")
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

    def say(self, s, beats=2, color=WHITE_, size=24):
        new = txt(s, size, color, bold=False, w=4.4)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def clear_stage(self, beats=1):
        keep = self.stage + ([self.note] if self.note else [])
        if keep:
            for m in keep:
                m.clear_updaters()
            self.play(*[FadeOut(m) for m in keep], run_time=self.T(beats))
            self.stage, self.note = [], None
        else:
            self.wait(self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        self.title = txt("HOW AI READS", 50, WHITE_, w=4.6)
        self.title.move_to(np.array([0, 1.05, 0]))
        self.sub = txt("it can't see letters", 24, GOLD, bold=False)
        self.sub.move_to(np.array([0, 0.35, 0]))
        self.add(self.title, self.sub)
        self.wait(self.T(2))
        self.play(self.title.animate.set_height(
                      self.title.get_height() * 0.50).move_to(np.array([0, 3.30, 0])),
                  FadeOut(self.sub), run_time=self.T(1))
        self.pad_to(END_OPEN)

    def section_card(self, n, name, end):
        self.clear_stage(1)
        big = VGroup(txt(f"{n}", 74, GOLD),
                     txt(name, 36, WHITE_, w=4.4)).arrange(DOWN, buff=0.30)
        big.move_to(np.array([0, 0.35, 0]))
        self.play(FadeIn(big, scale=1.12), run_time=self.T(1), rate_func=rush_from)
        new = txt(f"{n} / 2   {name}", 20, GOLD, bold=False, w=3.6)
        new.move_to(np.array([0, 2.62, 0]))
        self.pad_to(end - 1)
        if self.marker is None:
            self.marker = new
            self.play(FadeOut(big), FadeIn(new), run_time=self.T(1))
        else:
            self.play(FadeOut(big), Transform(self.marker, new), run_time=self.T(1))

    # ==================================================================
    # 1 — CHUNKS.  A real BPE glueing letters together, live.
    # ==================================================================
    def part1_chunks(self):
        head = txt("watch it learn to read", 26, WHITE_, w=4.4)
        head.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.stage.append(head)

        row = chip_row(STATES[0], WHITE_, 24, y=0.55)
        self.play(FadeIn(row), run_time=self.T(1))
        self.stage.append(row)
        self.say("it glues the most common pair, over and over", 2)

        # every state is one the algorithm really passed through
        per = (END_CHUNK - 8 - 12.0) / max(len(STATES) - 1, 1)
        per = max(round(per * 2) / 2, 0.5)
        for st in STATES[1:]:
            nxt = chip_row(st, GOLD if st == STATES[-1] else WHITE_, 24, y=0.55)
            self.play(Transform(row, nxt), run_time=self.T(per))

        self.say("nobody told it “straw” or “berry”", 2, GOLD)

        cnt = VGroup(txt("3 r's", 40, WHITE_), txt("2 chunks", 40, GOLD)) \
            .arrange(RIGHT, buff=0.45)
        if cnt.get_width() > 4.4:
            cnt.set_width(4.4)
        cnt.move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(cnt, scale=1.15), run_time=self.T(2), rate_func=rush_from)
        self.stage.append(cnt)
        self.say("so ask it to count the r's and watch", 2, GOLD)
        self.pad_to(END_CHUNK)

    # ==================================================================
    # 2 — THREADS.  Which word is "it"?  Then change one word.
    # ==================================================================
    def part2_threads(self):
        def line(words, y):
            g = VGroup(*[txt(w, 25, WHITE_, bold=False, w=1.4) for w in words])
            g.arrange(RIGHT, buff=0.17)
            if g.get_width() > 4.6:
                g.set_width(4.6)
            return g.move_to(np.array([0, y, 0]))

        l1 = line(SENT1, 1.60)
        l2 = line(SENT2, 0.58)
        self.play(FadeIn(l1), FadeIn(l2), run_time=self.T(2))
        self.stage += [l1, l2]

        it = l2[1]
        self.play(it.animate.set_color(GOLD), run_time=self.T(1))
        self.say("which one is “it”?", 3, GOLD)

        anchor = it.get_center() + np.array([0, 0.26, 0])
        t_animal = thread(anchor, l1[1].get_center() + np.array([0, -0.26, 0]),
                          GOLD, 6.0, 0.95)
        t_street = thread(anchor, l1[5].get_center() + np.array([0, -0.26, 0]),
                          COOL, 1.8, 0.45)
        self.play(ShowCreation(t_animal), ShowCreation(t_street), run_time=self.T(2))
        self.stage += [t_animal, t_street]
        ans = txt(f"the animal — {TOP_PCT}%", 28, GOLD, w=4.4)
        ans.move_to(np.array([0, -0.45, 0]))
        self.play(FadeIn(ans), run_time=self.T(1))
        self.stage.append(ans)
        self.say("because tired is a thing animals are", 2)

        # the twist: one word at the end moves the whole link
        new_last = txt("wide", 25, GOLD, bold=False, w=1.4)
        new_last.move_to(l2[4].get_center())
        self.play(Transform(l2[4], new_last), run_time=self.T(2))
        self.say("change ONE word at the end", 2, GOLD)

        t2_street = thread(anchor, l1[5].get_center() + np.array([0, -0.26, 0]),
                           GOLD, 6.0, 0.95)
        t2_animal = thread(anchor, l1[1].get_center() + np.array([0, -0.26, 0]),
                           COOL, 1.8, 0.45)
        ans2 = txt("the street", 28, GOLD, w=4.4)
        ans2.move_to(np.array([0, -0.45, 0]))
        self.play(Transform(t_animal, t2_animal), Transform(t_street, t2_street),
                  Transform(ans, ans2), run_time=self.T(2))
        self.say("and the link jumps", 2, GOLD)
        self.pad_to(END_THREAD)

    # ------------------------------------------------------------------
    def takeaway(self, a, b):
        self.clear_stage(1)
        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 26, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(END_TAKE)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.title),
                  FadeOut(self.marker), run_time=self.T(1))

    def signature(self):
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1))
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))
