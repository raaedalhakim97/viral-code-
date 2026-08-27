# sin(2θ) = 2 sin θ cos θ — doubling the angle isn't doubling the sine

Companion to `double_angle.py`. Continues **"WHY DID WE LEARN THIS?"** —
same shell as `soh_cah_toa.py` and `tan_identity.py`, same 3-4-5 triangle.
Equation pinned at the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
sin(2θ) = 2 sin θ cos θ
```

sin(2θ) is NOT 2 × sin θ — a mistake almost everyone makes on first sight.
The actual rule needs BOTH sin θ and cos θ, multiplied together, then
doubled.

---

## The exact number

```
sin θ = 3/5     cos θ = 4/5
2 × (3/5) × (4/5) = 24/25
```

And the actual angle, doubled and measured directly, lands on exactly the
same number:

```
sin(2θ) = 24/25 = 0.96 — matches, exactly
```

### Verified at import

```
2 * sinθ * cosθ == Fraction(24, 25) exactly
sin(2θ), measured directly, matches to 1e-9 — not a coincidence
```

---

## Same triangle, fourth use

3-4-5 is the same triangle from `soh_cah_toa.py` and `tan_identity.py`.
This time the point is a genuine trap: the "obvious" guess (double the
sine) is wrong, and the real formula is checked two ways — algebraically,
and by measuring the doubled angle directly — to prove it isn't a trick of
the specific numbers.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **sin(2θ) = 2 sin θ cos θ** — *doubling the angle isn't doubling the sine* |
| 8–26 | The 3-4-5 triangle, marked θ |
| 26–62 | sin θ · cos θ → 2×(3/5)×(4/5)=24/25 → sin(2θ)=24/25, measured directly |
| 62–78 | *2 sin θ alone would be way too big — this is the real rule* |
| 78–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
sin(2θ) = 2 sin θ cos θ. Doubling the angle isn't doubling the sine.

sin θ and cos θ, from the same 3-4-5 triangle: 3/5 and 4/5. Multiply them
together, then double it: 2 × 3/5 × 4/5 = 24/25.

Now measure the ACTUAL doubled angle directly. sin(2θ) = 24/25 = 0.96.
Exactly the same number. Not a coincidence.

2 × sin θ alone would be way too big. Both sin AND cos, multiplied — that's
the whole formula.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #satisfying #school #geometry
```

**YouTube title:** `sin(2θ) is NOT 2sinθ — here's the actual formula, proven`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl double_angle.py DoubleAngle -w -r 1080x1920
python3 cinegrade.py videos/DoubleAngle.mp4 double_angle.mp4
```

## Changing it

`OPP, ADJ, HYP` at the top — any Pythagorean triple. `2*sinθ*cosθ` is
computed as an exact `Fraction` and checked against `sin(2θ)` measured
directly via `math.sin` on the doubled angle, to `1e-9`.
