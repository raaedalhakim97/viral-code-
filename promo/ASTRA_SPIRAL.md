# 137.5077901...° — the real math behind the Astra headline

Standalone news-hook episode. Not part of a regular shell series, but
reuses the same house pattern: the number is pinned at the **top of the
frame for the whole video**, silent, beat-locked.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The real news (sourced, not invented)

OpenAI's next model family, **Astra**, produced Lean-verified solutions to
**ten open problems** in mathematics and theoretical computer science —
several unsolved for a decade or more. One of the ten: the general upper
bound on high-dimensional sphere-packing density, unmoved since the
**Kabatiansky-Levenshtein bound of 1978** (~2⁻⁰·⁵⁹⁹ᵈ). Astra's result,
via the Cohn-Elkies linear-programming method, pushes that bound to
roughly **2⁻⁰·⁶¹ᵈ**.

Checked against multiple independent sources before building this video:

- [OpenAI's New Model, Astra, Has Solved Ten Open Math Problems — DataCamp](https://www.datacamp.com/blog/open-ai-model-astra-solved-ten-open-math-problems)
- [OpenAI announces "next major model" Astra — The Decoder](https://the-decoder.com/openai-announces-its-next-major-model-astra-by-dropping-ten-previously-unsolved-math-solutions/)
- [Hacker News discussion (item 49143688)](https://news.ycombinator.com/item?id=49143688)
- [OpenAI's Astra Solved Decades-Old Math Problems For $2,000 — Forbes](https://www.forbes.com/sites/jonmarkman/2026/08/03/openais-astra-solved-10-decades-old-math-problems-for-just-2000/)
- [OpenAI's Astra solves 10 long-open math problems — SiliconANGLE](https://siliconangle.com/2026/08/02/openais-astra-solves-10-long-open-math-problems-publishes-proofs/)
- [Sphere Packing and Non-Sofic Groups: What AI Actually Solved — MindStudio](https://www.mindstudio.ai/blog/ai-sphere-packing-nonsofic-groups-explained)

**No source describes Astra using a "spiral."** That's not how the actual
proof works (Cohn-Elkies LP bound, not a spiral construction), and this
video says so on screen — see below.

---

## What this video actually shows

Not Astra's proof — nobody could animate a Cohn-Elkies linear-programming
bound in hundreds of dimensions honestly in 60 seconds. Instead: an
honest, self-contained 2D packing puzzle, solved by a real spiral — the
**golden-angle spiral** used in phyllotaxis (sunflower seed heads,
pinecones) — as a small, correct taste of *why packing problems are hard*
and *how a spiral can do real work on one*. The video states this
explicitly: *"this is the 2D toy version — not Astra's real proof."*

## The puzzle

Place 120 points outward along a spiral (radius ∝ √index), turning by a
fixed angle at every step. Draw the largest non-overlapping circle at
every point. Same rule, same N, two different angles:

```
a "reasonable" angle, 90°:              packing ≈ 0.8%
the golden angle, 137.5077901...°:      packing ≈ 55.2%
```

Same 120 circles. **67× denser**, from one angle choice.

### Verified at import

```
both spirals: zero circle overlaps, by construction (checked pairwise)
golden-angle density > 50%, 90° density < 2%
density ratio > 50x — both computed from the identical N and scale
```

The 90° spiral clumps because 90° is a simple fraction of a full turn
(1/4) — points 4 steps apart land on the same ray, and since consecutive
radii grow like √i, those same-ray points get arbitrarily close together
as the spiral grows, forcing tiny circles. The golden angle is the
"most irrational" real number (worst possible rational approximations, by
its continued-fraction expansion) — no small integer k makes k × angle
land back near a multiple of 360°, so points never clump on a ray.

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **137.5077901...°** — *"48 years. broken this week."* (the real headline) |
| 12–44 | The 90° spiral: 120 circles, clumped into a cross, packing ≈ 0.8% |
| 44–88 | The golden-angle spiral: same 120 circles, packing ≈ 55.2%, 67× denser |
| 88–107 | *why: the golden angle never repeats as a simple fraction of a turn* — and the honesty line: *"this is the 2D toy version — not Astra's real proof"* |
| 107–122 | *Real math didn't stop moving. It just moved somewhere you didn't hear about.* |
| 122–132 | share ask |
| 132–150 | The eye |

---

## Caption

```
48 years. Broken this week. OpenAI's Astra just solved it — a sphere-
packing record from 1978.

Same puzzle, tiny version: pack circles as densely as you can. Step
outward along a spiral, turning the same angle every time.

Turn 90° every step — a "reasonable" angle. Packing: 0.8%. Look how much
is wasted.

Turn 137.5077901...° instead — the golden angle. Same 120 circles.
Packing: 55.2%. Sixty-seven times denser. No gaps, no overlaps — checked,
not eyeballed.

Why? The golden angle never repeats as a simple fraction of a turn, so no
two points ever line up and clump.

This is the 2D toy version — not Astra's real proof. The real one runs in
hundreds of dimensions and just moved a bound nobody touched since 1978.

Real math didn't stop moving. It just moved somewhere you didn't hear
about.

#maths #mathtok #AI #openai #astra #spherepacking #satisfying
```

**YouTube title:** `OpenAI's Astra just broke a 48-year math record — here's the 2D version of why it's hard`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl astra_spiral.py AstraSpiral -w -r 1080x1920
python3 cinegrade.py videos/AstraSpiral.mp4 astra_spiral.mp4
```

## Changing it

`N` (circle count) and `BAD_ANGLE` at the top. The assertions recompute
both packings' densities and their overlap-free-ness at import and refuse
to build if the golden angle ever stops beating the comparison angle by at
least 50×, or if any pair of circles in either packing overlaps.
