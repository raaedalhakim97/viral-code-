# c² = a² + b² − 2ab cos C — no right angle. now what?

Companion to `law_of_cosines.py`. Continues **"WHY DID WE LEARN THIS?"**,
same shell as `soh_cah_toa.py` and `pythagorean_identity.py` — equation
pinned at the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
c² = a² + b² − 2ab cos C
```

Every previous episode in this series lived on a *right* triangle. This one
opens by breaking that pattern on purpose: a triangle with **no right angle
at all**. SOH CAH TOA has nothing to say here. That's the hook.

---

## A scalene triangle, deliberately not Pythagorean

```
a = 6      b = 5      c = 7
```

`6² + 5² = 61 ≠ 49 = 7²` — checked at import, not assumed. This is not a
right triangle, so there is no opposite/adjacent/hypotenuse to reach for.

The video rearranges the law of cosines to solve for the angle instead:

```
cos C = (a² + b² − c²) / 2ab = (36 + 25 − 49) / 60 = 12/60 = 1/5
```

Computed as an exact `Fraction`, not a rounded decimal.

### Verified at import

```
6² + 5² != 7²                          it really isn't a right triangle
cos C == Fraction(1, 5) exactly         no rounding anywhere in the algebra
the triangle closes: |P−Q| ≈ c to 1e-9  the drawn triangle matches the numbers
```

---

## Why it collapses back to Pythagoras

Set `C = 90°`. Then `cos C = 0`, and the whole `−2ab cos C` term vanishes:

```
c² = a² + b² − 2ab·0  =  a² + b²
```

**That's Pythagoras.** The law of cosines was never a separate fact to
memorise on top of it — Pythagoras is just the special case where the
triangle happens to have a right angle. The law of cosines is what's
underneath it the rest of the time.

---

## A real bug caught during layout

The first cut placed the `"a=6   b=5   c=7"` caption at `y=-2.55` — close
enough to the triangle's own **"a"** side-length label (which sits at the
midpoint of the base edge, `-0.30` below it) that the two visually collided
on a screenshot check. Fixed by moving the caption down to `y=-2.92`,
clearing it from the triangle entirely. Re-rendered and re-confirmed.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **c² = a² + b² − 2ab cos C** — *no right angle. now what?* |
| 8–30 | Triangle drawn: a=6, b=5, c=7. No right-angle marker — genuinely scalene |
| 30–62 | Rearrange, solve: cos C = (36+25−49)/60 = 12/60 = 1/5 |
| 62–78 | Set C = 90°. cos C → 0. The formula collapses to a² + b² — *that's Pythagoras* |
| 78–88 | *We learned this at school. Nobody ever said what for.* + share ask |
| 88–92 | share ask (cont.) |
| 92–100 | The eye |

---

## Caption

```
c² = a² + b² − 2ab cos C. No right angle. Now what?

A triangle: a=6, b=5, c=7. Not a right triangle — 6² + 5² isn't 7². SOH CAH
TOA has nothing to say here.

Rearrange the law of cosines and solve for the angle instead:

cos C = (36 + 25 − 49) / 60 = 12/60 = 1/5. Exact fraction.

Now set C to 90°. cos C becomes 0. The whole −2ab cos C term disappears.

c² = a² + b². That's Pythagoras. It never left — it's just the special case
where the angle happens to be 90°.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #lawofcosines #pythagoras #geometry #school #satisfying
```

**YouTube title:** `The law of cosines is just Pythagoras with an angle bolted on`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl law_of_cosines.py LawOfCosines -w -r 1080x1920
python3 cinegrade.py videos/LawOfCosines.mp4 law_of_cosines.mp4
```

## Changing it

`A_LEN, B_LEN, C_LEN` at the top — any scalene triple. The assertions refuse
to build if the triple happens to be a right triangle (that's a different
video), and recompute `cos C` as an exact `Fraction` and the drawn triangle's
closing side length to confirm the picture matches the algebra.
