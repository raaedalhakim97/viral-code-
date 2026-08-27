# 1 : √3 : 2 — the "special" triangle everyone memorises

Companion to `triangle_30_60_90.py`. Continues **"WHY DID WE LEARN
THIS?"** — same shell as `soh_cah_toa.py`, equation pinned at the **top of
the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
1 : √3 : 2
```

A 30-60-90 triangle always has sides in exactly this ratio — not
approximately, exactly, no matter how big or small it's drawn. Every
"special angle" value from every trig class comes straight off this one
triangle.

---

## The exact numbers

```
sin 30° = 1/2          cos 60° = 1/2
sin 60° = √3/2          cos 30° = √3/2
```

sin 30° and cos 60° are the exact same ratio, off the exact same side —
the cofunction fact from `cofunction.py`, two episodes ago, showing up
again for free.

### Verified at import

```
1² + (√3)² == 2²                      it really is a right triangle
sin 30° == cos 60° == 0.5 exactly      cos 30° == sin 60° to 1e-9
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **1 : √3 : 2** — *the "special" triangle* |
| 8–26 | The triangle: 30°, 60°, 90°, sides 1, √3, 2 |
| 26–62 | sin 30° = cos 60° = 1/2 · sin 60° = cos 30° = √3/2 |
| 62–78 | *one triangle, every special-angle value on the sheet* |
| 78–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
1 : √3 : 2. The "special" triangle everyone memorises.

30°, 60°, 90°. Sides 1, √3, 2 — always, exactly, no matter the size.

sin 30°: opposite over hypotenuse = 1/2. cos 60°: adjacent over
hypotenuse — the exact same ratio. sin 60° = cos 30° = √3/2.

One triangle. Every special-angle value on the formula sheet.
Memorise the triangle, not six separate numbers.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #satisfying #school #geometry
```

**YouTube title:** `The one triangle behind every "special angle" you memorised`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl triangle_30_60_90.py Triangle306090 -w -r 1080x1920
python3 cinegrade.py videos/Triangle306090.mp4 triangle_30_60_90.mp4
```

## Changing it

Sides are fixed at the canonical `1, √3, 2` ratio. The assertions confirm
it's a genuine right triangle and that `sin30==cos60` and `sin60==cos30`
hold to floating-point tolerance (the values involve `√3`, so they're
never bit-exact rationals).
