# The Rope Puzzle — video brief

Companion to `rope_puzzle.py`. First video on the page built as a **puzzle**
rather than an explainer: pose it, make the viewer commit, show the working,
pay it off at the end.

- **Output:** 1080×1920, 60fps, **48.000000s** — 120 beats = 30 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## Why this format is different from everything else on the page

Every other video hands over an answer. This one asks for one first.

That commitment step is the whole mechanism. Someone who has silently picked
**B** watches to the end to find out whether they were right — and a meaningful
share of them will say so in the comments, because being wrong about something
this simple is worth admitting. Comments are a ranking signal, and this is the
only format that reliably produces them.

Chapter 2 exists purely to force the choice. It could be cut for pacing; don't.

---

## The puzzle

> A rope is tight around the Earth's equator. You add **one metre** of rope.
> How high does it lift off the ground, all the way around?

Almost everyone says a hair's width or less. The intuition is that one metre
against forty million is nothing.

**The answer is 15.9 cm** — your hand slides under it, everywhere on Earth.

---

## The maths, verified

```
lift = ((C + 1) / 2π) − r  =  1 / 2π  =  0.159155 m  =  15.92 cm
```

| sphere | radius | lift from +1 m of rope |
| --- | --- | --- |
| Earth | 6,371 km | **15.92 cm** |
| tennis ball | 3.3 cm | **15.92 cm** |
| a pea | 5 mm | **15.92 cm** |

The radius cancels in the second line of algebra. The size of the sphere never
enters the answer, which is why the tennis ball at the end is the real payoff
rather than a garnish.

---

## Drawing it honestly

A 15.9 cm gap on a 6,371 km radius is one part in forty million — **it cannot be
drawn to scale.** This is the same trap that killed the first version of the
`dimensions` chapter 4 visual, so the rule got applied up front here:

- The Earth diagrams are schematic and carry **"(not to scale)"** on screen.
- The answer is then shown twice at scales where it *can* be truthful — a
  ground line with a hand under it, and a tennis ball where the same absolute
  gap is now larger than the ball.

The tennis ball drawing is both the honest one and the punchline. That is not a
coincidence: when a ratio is too extreme to draw, the fix is usually to change
what you are drawing, not to fake the proportions.

---

## Structure

| Ch | Beats | What it does |
| --- | --- | --- |
| 1 | 24 | The rope, the +1 metre, the question |
| 2 | 24 | Three options. "Pick before you scroll." |
| 3 | 24 | `C = 2πr` → `C + 1 = 2π(r + d)` → **the r cancels** → `d = 1/2π` |
| 4 | 24 | 15.9 cm. Hand under the rope. Then the tennis ball, same gap. |
| 5 | 24 | Why the size never mattered, then the signature |

---

## Caption

```
A rope is pulled tight around the Earth's equator. You add one metre of rope.
How far does it lift off the ground, all the way around?

A) a hair's width   B) a coin   C) your hand fits under

Most people say A. The answer is C — 15.9 cm, everywhere on the planet.

Two lines of algebra and the radius cancels out: C = 2πr, so C + 1 = 2π(r + d),
so d = 1/2π. The size of the sphere never enters the answer. Do it with a tennis
ball and the rope lifts by exactly the same 15.9 cm.

Did you get it right?

#mathtok #maths #puzzle #geometry #brainteaser
```

**"Did you get it right?"** is the line that earns the comments. Keep it last.

Note the hashtags are deliberately *not* the AI set — this one is a pure maths
puzzle and should be fishing in the puzzle and brainteaser pools, which are far
larger than `#aimath`. The account's top performer was geometry, not AI news.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl rope_puzzle.py RopePuzzle -w -r 1080x1920
python3 cinegrade.py videos/RopePuzzle.mp4 rope_graded.mp4
```

---

## If this format works

The puzzle shape is reusable and the page has no others yet. Candidates that
survive the same "wrong intuition + one-line proof + drawable" test:

- **Two envelopes / the birthday problem** — 23 people for a 50% collision
- **The pizza question** — one 18-inch or two 12-inch, and why area betrays you
- **Simpson's paradox** — both groups improve, the total gets worse. This one
  doubles as an AI/data video, which the others do not.

Simpson's paradox is the strongest of the three for this channel, because it is
a puzzle *and* a real trap in machine learning.
