# a/sinA = b/sinB = c/sinC — the same triangle, again

Companion to `law_of_sines.py`. Continues **"WHY DID WE LEARN THIS?"** —
same shell as `soh_cah_toa.py`, same 30-60-90 triangle as
`triangle_30_60_90.py` two episodes ago. Equation pinned at the **top of
the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The spine

```
a/sin A = b/sin B = c/sin C
```

Divide any side of a triangle by the sine of the angle across from it. Do
it for all three sides. Every triangle gives the same answer, all three
times.

---

## The exact number

On the familiar 1 : √3 : 2 triangle, that number is exactly 2:

```
a/sin A = 1/sin 30° = 2
b/sin B = 2/sin 90° = 2
c/sin C = √3/sin 60° = 2
```

Three different sides, three different angles — the exact same constant.

### Verified at import

```
a/sinA == b/sinB == c/sinC == 2.0, all to 1e-9
```

---

## Same triangle, third use

The 1 : √3 : 2 triangle already gave up its special-angle values in
`triangle_30_60_90.py`. Here it proves something bigger: the ratio "side
over sine of opposite angle" isn't a fact about *this* triangle — it's a
fact about *any* triangle. This one's just clean enough to check by hand.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **a/sinA = b/sinB = c/sinC** — *the same triangle, again* |
| 8–26 | The 30-60-90 triangle, sides labeled a=1, b=2, c=√3 |
| 26–62 | a/sinA=2 · b/sinB=2 · c/sinC=2 — three sides, one number |
| 62–78 | *this isn't special to this triangle — it's every triangle* |
| 78–92 | *We learned this at school. Nobody ever said what for.* + share ask |
| 92–100 | The eye |

---

## Caption

```
a/sinA = b/sinB = c/sinC. The same triangle, again.

Side a, divided by sin of its own angle A: 1/sin30° = 2.

The right angle's side, b: 2/sin90° = 2.

The third side, c: √3/sin60° = 2.

Three different sides. The exact same number, every time.

This isn't special to this triangle. a/sinA is the same constant for ANY
triangle, always.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #satisfying #school #geometry
```

**YouTube title:** `Every side of a triangle hides the exact same number`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl law_of_sines.py LawOfSines -w -r 1080x1920
python3 cinegrade.py videos/LawOfSines.mp4 law_of_sines.mp4
```

## Changing it

`SIDE_A/ANG_A`, `SIDE_B/ANG_B`, `SIDE_C/ANG_C` at the top define the
triangle. The assertions confirm it's a genuine right triangle and that
all three `side/sin(angle)` ratios agree to `1e-9`.
