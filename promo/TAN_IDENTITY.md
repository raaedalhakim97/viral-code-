# tan θ = sin θ / cos θ — tan isn't a fourth thing

Companion to `tan_identity.py`. Continues **"WHY DID WE LEARN THIS?"**,
same shell as `soh_cah_toa.py` — same 3-4-5 triangle, equation pinned at
the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
tan θ = sin θ / cos θ
```

sin and cos are already both ratios of the same triangle. Divide one by
the other and the hypotenuse cancels out — what's left is exactly tan.

---

## The exact number

```
sin θ = 3/5     cos θ = 4/5
sin θ / cos θ = (3/5) / (4/5) = 3/4 = tan θ
```

Computed with Python's `Fraction`, never a rounded float — the division
lands on the exact same fraction as `tan θ = opposite/adjacent`, every
time.

### Verified at import

```
sin θ / cos θ == tan θ exactly (Fraction)   no rounding, no coincidence
```

---

## Same triangle, third lens

3-4-5 is the same triangle `soh_cah_toa.py` measured (`sin=0.6, cos=0.8,
tan=0.75`) and `cofunction.py` split into θ and its complement. This is
deliberate — the point isn't a new triangle, it's that **tan was never a
fourth fact to memorise**. It's sin and cos, divided.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **tan θ = sin θ / cos θ** — *tan isn't a fourth thing* |
| 8–26 | The 3-4-5 triangle, marked θ |
| 26–62 | sin θ = 3/5, cos θ = 4/5 → divide → 3/4 = tan θ |
| 62–78 | *"rise over run" was hiding inside sin and cos the whole time* |
| 78–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
tan θ = sin θ / cos θ. Tan isn't a fourth thing — it's the other two,
divided.

The same 3-4-5 triangle. sin θ = 3/5, cos θ = 4/5.

Divide one by the other: (3/5) / (4/5) = 3/4. The hypotenuse cancels — it
was never needed. 3/4 IS tan θ.

Tan was never a separate ratio to memorise. "Rise over run" was hiding
inside sin and cos the whole time.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #satisfying #school #geometry
```

**YouTube title:** `Tan θ isn't a fourth ratio — it's sin divided by cos`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl tan_identity.py TanIdentity -w -r 1080x1920
python3 cinegrade.py videos/TanIdentity.mp4 tan_identity.mp4
```

## Changing it

`OPP, ADJ, HYP` at the top — any Pythagorean triple. The assertion
recomputes `sin/cos` and `tan` as exact `Fraction`s and refuses to build
if they ever stop matching.
