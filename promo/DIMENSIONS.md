# Why 1,536 Dimensions — video brief

Companion to `dimensions.py`. Why an embedding needs a space that big, and the
genuinely strange thing that happens once you are in one.

- **Output:** 1080×1920, 60fps, **51.200000s** — 128 beats = 32 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## Why this topic

Embeddings are the live subject in AI right now — the comparisons between
closed models (Voyage, Gemini, OpenAI, Cohere) and open ones (Qwen3, BGE-M3,
EmbeddingGemma) are everywhere, and the whole conversation assumes a fact
nobody explains: *why is the vector 1,536 numbers long?*

That gap is the video. It is also durable — the number on the box changes with
each model release, the geometry does not.

---

## Every number was measured

Not asserted, not quoted. `cos_samples()` in the scene draws real random unit
vectors with a fixed seed, and the histograms on screen are those samples.

| dims | theory std (1/√d) | measured | pairs within ±0.05 of perpendicular |
| --- | --- | --- | --- |
| 2 | 0.7071 | 0.7052 | 3.3% |
| 10 | 0.3162 | 0.3155 | 11.4% |
| 100 | 0.1000 | 0.1003 | 37.6% |
| 768 | 0.0361 | 0.0359 | 83.6% |
| **1,536** | **0.0255** | **0.0254** | **95.2%** |
| 3,072 | 0.0180 | 0.0181 | 99.4% |

Theory and measurement agree to four decimals, which is the point — this is not
a metaphor, it is what the space does.

**Volume inside radius 0.99, in 1,536 dimensions: 1.975 × 10⁻⁷.** So 99.99998%
of a high-dimensional ball sits in its outer 1%.

**~1.1 × 10¹⁰ directions** fit pairwise within ten degrees of perpendicular in
1,536 dimensions, from the standard concentration bound `exp(d·ε²/2)` at
ε = 0.1736. It is a *lower* bound on the packing, which is the honest direction
for the claim being made.

---

## Structure

| Ch | Time | What it does |
| --- | --- | --- |
| 1 | 0:00–0:13 | **The problem.** In a plane you get two perpendicular directions. A third word has to overlap — and overlapping directions mean confused meanings. |
| 2 | 0:13–0:26 | **The measurement.** Real histograms of the angle between two random words, at 2 → 10 → 100 → 1,536 dimensions. The spread collapses to a needle. |
| 3 | 0:26–0:38 | **The count.** 2 dimensions: 2 directions. 1,536: eleven billion. |
| 4 | 0:38–0:51 | **The strange part.** Where the volume actually lives, plus the close. |

---

## One visual I had to rebuild

Chapter 4 originally drew the "outer 1% shell" as two concentric circles at
radius 1.5 and 1.485 — **which is a gap of 0.015 and completely invisible.** The
idea never landed because the picture could not carry it at that scale.

It now plots `r^d` against `r` instead: in 2 dimensions a gentle parabola, in
1,536 a line that lies flat on the floor and then slams into the wall at the
edge. That is the actual mathematics rather than an illustration of it, and it
reads in about a second.

Anything drawn to scale from a real ratio needs this check — if the ratio is
extreme, the honest picture is a graph, not a diagram.

---

## Caption

```
Every word an AI knows lives in 1,536 dimensions. Here is why it needs that many.

In a flat plane you get two perpendicular directions. Two. A third word has to
overlap one of them, and overlapping directions mean confused meanings.

So pick two random directions in 1,536 dimensions and measure the angle between
them: 95% of the time they land within 0.05 of a right angle. Not designed that
way — that is just what the space does. It leaves room for about eleven billion
directions that barely touch each other, which is why every word can have its
own without stepping on another.

And the strange part: 99.99998% of a 1,536-dimensional ball sits in its outer
1%. High dimensions are almost entirely empty space, and that emptiness is
exactly the point.

#aimath #mathtok #embeddings #machinelearning #linearalgebra
```

Short alternate:

```
Two random directions in 1,536 dimensions are perpendicular 95% of the time.
That is not a design choice — it is just what high-dimensional space does, and
it is the reason embeddings work at all.

#aimath #mathtok #embeddings
```

The long one is the better bet. This video is silent, so there is no transcript
for TikTok to index and the caption carries all of the search weight — the terms
that matter are *embeddings*, *dimensions*, *perpendicular*, *vector*.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl dimensions.py Dimensions -w -r 1080x1920
python3 cinegrade.py videos/Dimensions.mp4 dimensions_graded.mp4
```
