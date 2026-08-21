# sin² θ + cos² θ = 1 — the identity that looks scary

Companion to `pythagorean_identity.py`. Continues **"WHY DID WE LEARN
THIS?"**, paired with `soh_cah_toa.py` — same shell, equation pinned at the
**top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
sin² θ + cos² θ = 1
```

One line, gold, pinned at the top from the moment it lands. Everything below
it is proof, not derivation — the identity is stated first, then earned twice.

---

## Two triangles, not one

A single worked example can always be a coincidence. This proves the identity
on two triangles that share nothing except being right triangles:

```
3-4-5:     sin θ = 3/5,  cos θ = 4/5    ->  9/25   + 16/25  = 25/25  = 1
5-12-13:   sin θ = 5/13, cos θ = 12/13  ->  25/169 + 144/169 = 169/169 = 1
```

Every fraction is computed with Python's `Fraction`, never a rounded float —
`= 1` on screen means exactly one, not `0.9999999`.

### Verified at import

```
3-4-5 and 5-12-13 are both genuine Pythagorean triples
both triangles' sin² + cos² equal exactly Fraction(1, 1)
the two triangles do not share a ratio     or the "different triangle" claim is false
```

---

## Why it is always one

Divide the Pythagorean theorem itself, `a² + b² = c²`, by `c²` on both sides:

```
(a/c)² + (b/c)² = 1
```

But `a/c` and `b/c` **are** `sin θ` and `cos θ` — `soh_cah_toa.py` said so two
videos ago. The identity is not a new fact to memorise. **It is Pythagoras,
wearing sin and cos as initials.**

---

## A real bug caught during layout

The first cut used a fixed screen scale for every triangle. 3-4-5 fit fine;
5-12-13 ran clean off the right edge of the 9:16 frame, because a triangle
with a side of 12 at the same scale as one with a side of 4 is three times
wider. Fixed by scaling each triangle to a **constant on-screen span**
(`TARGET_SPAN / max(opp, adj)`) regardless of its real side lengths — both
triangles now read at the same visual size, and the actual numbers are still
the real 3, 4, 5 and 5, 12, 13, just drawn to fit.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **sin² θ + cos² θ = 1** — *the identity that looks scary* |
| 8–38 | Triangle one: 3, 4, 5. `(3/5)² + (4/5)² = 9/25 + 16/25 = 1` |
| 38–68 | A totally different triangle: 5, 12, 13. Same result, exactly |
| 68–80 | *that is not a coincidence... this identity IS Pythagoras, divided* |
| 80–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
sin²θ + cos²θ = 1. The identity that looks like a nightmare.

Triangle one: 3, 4, 5. sin θ = 3/5, cos θ = 4/5.

(3/5)² + (4/5)² = 9/25 + 16/25 = 1. Exactly one. Not almost.

Could be a coincidence of that one triangle. So try a completely different
one: 5, 12, 13.

(5/13)² + (12/13)² = 25/169 + 144/169 = 1. Again. Exactly.

Here's why it's ALWAYS one. Take Pythagoras — a² + b² = c² — and divide both
sides by c². You get (a/c)² + (b/c)² = 1. And a/c, b/c are just cos θ and
sin θ.

This identity isn't a new fact. It's Pythagoras, wearing sin and cos as
initials.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #pythagoras #geometry #school #satisfying
```

**YouTube title:** `sin²θ + cos²θ = 1 isn't scary — it's just Pythagoras, divided`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl pythagorean_identity.py PythagoreanIdentity -w -r 1080x1920
python3 cinegrade.py videos/PythagoreanIdentity.mp4 pythagorean_identity.mp4
```

## Changing it

The two triples are set by the two `tri(opp, adj, hyp)` calls at the top —
any Pythagorean triples. The assertions recompute both triangles' `sin² + cos²`
as exact `Fraction`s and refuse to build if either isn't exactly `1`, or if the
two triangles happen to share a ratio (which would quietly break the "totally
different triangle" claim).
