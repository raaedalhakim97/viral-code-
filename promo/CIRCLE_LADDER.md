# Every Wave Is a Circle — video brief

Companion to `circle_ladder.py`. Six dancing equations, and every one of them is
the same triangle on the same circle.

- **Output:** 1080×1920, 60fps, **28.800000s** — 72 beats = 18 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## One picture, six rungs

A point **P** goes round the unit circle at angle `t`. Drop it to the x-axis and
you have a right triangle whose hypotenuse is the radius:

```
horizontal leg = cos t        vertical leg = sin t        hypotenuse = 1
```

Every rung is that triangle relabelled — nothing is added, only named:

| # | Equation | What the picture is doing |
| --- | --- | --- |
| 1 | a point on a circle | P going round |
| 2 | `sin t` | the vertical leg, in gold |
| 3 | `cos t` | the horizontal leg, in blue |
| 4 | `sin²t + cos²t = 1` | **Pythagoras**, on a hypotenuse of 1 |
| 5 | `eⁱᵗ = cos t + i sin t` | the point *is* the exponential |
| 6 | `eⁱᵖ + 1 = 0` | P standing at (−1, 0) |

**Rung 4 is not a fact to memorise — it is the triangle.** A right triangle with
hypotenuse 1 gives `a² + b² = 1` and the legs are named cos and sin. That is the
entire derivation and it is on screen the whole time.

**Rung 6 is not a mystery — it is a position.** Set `t = π` and the point is at
(−1, 0). The vertical leg collapses to nothing, the horizontal leg becomes the
whole radius pointing left, and the most famous equation in mathematics arrives
as *where the dot is standing* on a circle the viewer has been watching for
twenty seconds.

---

## Verified at import

```
sin²t + cos²t == 1                      across 2000 angles
eⁱᵗ == cos t + i sin t                  across 2000 angles, to 1e-12
eⁱᵖ + 1 == 0                            to floating point (1.2e-16)
```

The scene raises rather than renders if any of those stop holding.

---

## The dance

`P` advances with the beat for the whole video, so the two legs breathe in and
out continuously — the equation at the top pulses on the beat and **the triangle
underneath is what that equation is doing**. That is the difference between this
and a slideshow of formulae.

At rung 6 the spin stops and P is animated onto the *next* half-turn rather than
snapped, so it glides to (−1, 0) instead of jumping backwards:

```python
target = ceil((cur - π) / 2π) * 2π + π
```

---

## Typesetting exponents without LaTeX

There is **no LaTeX in this environment** (`latex` and `dvisvgm` are both absent,
and installing TeX Live timed out), and Unicode has no superscript π — so
`e^(iπ)` would have to be written with a literal caret, which reads as code
rather than mathematics.

`power(base, exp)` builds it by hand: a smaller `Text` raised by 34% of the
base's height. `eqn(...)` then arranges a row of those and plain text. The
result reads as typeset maths with no dependency, and it generalises to any
exponent — including the one Unicode can't express.

Two smaller fixes worth keeping:

- The hypotenuse label `1` is placed along the **outward normal** of the radius,
  `(−sin t, cos t) × 0.32`, rather than at a fixed offset — a fixed offset put it
  inside the triangle for half the rotation.
- The `sin t` label is hidden when `|sin t| < 0.10`. At `t = π` the leg has no
  length and its label would sit on top of the **−1**, which is the whole point
  of the last rung.

---

## Caption

```
Every wave you have ever seen is a point going round a circle.

Watch one point travel round. Drop a line straight down from it to the middle
line, and you've made a right triangle.

The height of that triangle IS sin.
The width of it IS cos.
And the slope is the radius — which is 1.

So sin² + cos² = 1 isn't a formula to memorise. It's Pythagoras on a triangle
whose longest side is 1. It was always just the triangle.

Now the strange part. That same point, written as a complex number, is exactly
e^(it) = cos t + i sin t. The point IS the exponential.

So send the point half a turn round the circle — t = π — and it lands on −1.

e^(iπ) + 1 = 0

The most famous equation in mathematics is a dot standing on the left side of a
circle.

#maths #mathtok #euler #geometry #trigonometry
```

The searchable line is Euler's identity — *"e to the i pi"*, *"euler's
identity explained"* and *"why is sin cos 1"* are all queries people type, and
this video answers all three with the same picture.

**YouTube title:** `e^(iπ) + 1 = 0 — it's just a dot on a circle`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl circle_ladder.py CircleLadder -w -r 1080x1920
python3 cinegrade.py videos/CircleLadder.mp4 circle_ladder.mp4
```
