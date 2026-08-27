# tan 45° = 1 — the triangle where tan is exactly one

Companion to `triangle_45_45_90.py`. Continues **"WHY DID WE LEARN
THIS?"** — same shell as `soh_cah_toa.py`, equation pinned at the **top of
the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
tan 45° = 1
```

A right triangle with a 45° angle has to be isosceles — the other acute
angle is forced to be 45° too, so both legs are the same length. Opposite
over adjacent is then just a number divided by itself.

---

## The exact numbers

```
legs: 1 and 1.  hypotenuse: √2.
sin 45° = cos 45° = √2/2      tan 45° = 1/1 = 1
```

Every other tan value on the sheet is some ugly fraction or root. This one
is exactly 1 — the simplest ratio in all of trigonometry, and it happens
because the triangle is *forced* to be symmetric.

### Verified at import

```
1² + 1² == (√2)²                   it really is a right triangle
sin 45° == cos 45° to 1e-9         tan 45° == 1.0 to 1e-9
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **tan 45° = 1** — *the triangle where tan = 1* |
| 8–26 | The triangle: legs 1 and 1, hypotenuse √2, both angles 45° |
| 26–62 | sin 45° = cos 45° = √2/2 · tan 45° = 1/1 = 1 |
| 62–78 | *the symmetry forces it — equal legs, equal ratio* |
| 78–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
tan 45° = 1. The triangle where tan is exactly one.

Both legs equal. Both acute angles have to be 45° — no other option.

sin 45° and cos 45° use the exact same two sides: √2/2. Now opposite over
adjacent: 1 over 1. tan 45° = 1. No rounding. No decimal. Exactly one.

The symmetry forces it. The simplest ratio in all of trigonometry: 1 : 1.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #satisfying #school #geometry
```

**YouTube title:** `The only tan value that's exactly 1 — and why it has to be`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl triangle_45_45_90.py Triangle454590 -w -r 1080x1920
python3 cinegrade.py videos/Triangle454590.mp4 triangle_45_45_90.mp4
```

## Changing it

Legs are fixed at `1, 1` (canonical isosceles right triangle). The
assertions confirm it's a genuine right triangle and that `tan45==1.0`
exactly (the one value in this whole series that's bit-exact despite
involving `√2` internally, since the roots cancel: `1/1`).
