# SOH CAH TOA — what does it actually mean?

Companion to `soh_cah_toa.py`. Continues **"WHY DID WE LEARN THIS?"** — same
shell as `angle_to_place.py`: the equation is the spine, it stays pinned at
the **top of the frame for the whole video**, and every number is dragged into
its slot off the picture rather than typed on top of it.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
sin θ = opp / hyp
cos θ = adj / hyp
tan θ = opp / adj
```

All three rows sit at the top together, for the entire video — nothing about
this mnemonic is hidden behind a single line that scrolls away. The viewer can
see all three ratios fill in side by side and compare them directly.

---

## One triangle, three ratios

A 3-4-5 right triangle — the smallest whole-number right triangle there is.
Its sides are counted straight off a grid:

```
opposite = 3      adjacent = 4      hypotenuse = 5
```

**Three drags fill six slots.** "3" fills sin's numerator *and* tan's
numerator at once. "5" fills sin's *and* cos's denominator at once. "4" fills
cos's *and* tan's remaining slot. All three "scary" ratios are full before the
video is half over:

```
sin θ = 3/5 = 0.6      cos θ = 4/5 = 0.8      tan θ = 3/4 = 0.75
```

Each row **collapses** from the fraction into its decimal on screen — the
fraction is shown first so the arithmetic is visible, then it resolves into
the number, still pinned at the top.

---

## Same numbers as episode 5, different lens

3-4-5 is the exact triangle `angle_to_place.py` measured on the unit circle
(`cos = 0.8`, `sin = 0.6`). That is deliberate, not recycled laziness: there it
was a point on a circle, here it is a ratio of triangle sides. **SOH CAH TOA
and the circle definition are the same fact**, and putting the same numbers in
front of the viewer twice, from two angles, is how that lands without saying
it outright.

### Verified at import

```
3² + 4² == 5²                         it really is a right triangle
the three ratios are exact fractions   0.6, 0.8, 0.75 — no rounding
tan == sin / cos                       the three are not independent facts
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **SOH · CAH · TOA** — *what does it actually mean?* |
| 8–34 | One right triangle. Sides counted: 3, 4, 5. Check: 9+16=25 |
| 34–70 | Three drags, three collapses: sin θ = 0.6, cos θ = 0.8, tan θ = 0.75 |
| 70–77 | *it's three divisions, done on one triangle* |
| 77–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
SOH CAH TOA. What does it actually mean?

One right triangle. Sides: 3, 4, 5 — the smallest whole-number right triangle
there is. Count them straight off the grid. Check: 9 + 16 = 25. It really is a
right triangle.

Now watch. Three drags fill six slots at once:

sin θ = 3/5 = 0.6
cos θ = 4/5 = 0.8
tan θ = 3/4 = 0.75

That's it. That's the whole spell. Three divisions, done on one triangle —
opposite over hypotenuse, adjacent over hypotenuse, opposite over adjacent.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #sohcahtoa #geometry #school #satisfying
```

**YouTube title:** `SOH CAH TOA finally makes sense — one triangle, three divisions`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl soh_cah_toa.py SohCahToa -w -r 1080x1920
python3 cinegrade.py videos/SohCahToa.mp4 soh_cah_toa.mp4
```

## Changing it

`OPP, ADJ, HYP` at the top — any Pythagorean triple. The assertions recompute
all three ratios as exact `Fraction`s and refuse to build if the triple isn't a
genuine right triangle or if `tan` ever stops matching `sin/cos`.
