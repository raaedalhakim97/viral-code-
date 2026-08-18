# The dancing equation — four numbers, and everything they do

Companion to `dancing_equation.py`. A **dance video that happens to be the most
important equation in AI.**

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## What it is

A circle of 72 dots and two arrows get multiplied by a 2×2 matrix.

```
x  ->  W x
```

The matrix changes pose on every bar, and the shape does exactly what the four
numbers say. Rotate. Stretch. Shear. Flip. Swap. Sixteen bars of it.

It is a dance video and a linear-algebra lesson at the same time, and neither
half is pretending.

---

## Every pose is an integer matrix

This is the reason it works as a house video. **On every downbeat all four
numbers on screen are exact whole numbers, and so is the determinant.** The
dance is a walk between integer poses, not a smear of decimals.

The display shows a plain integer whenever the live value is one to within
`1e-9`, and one decimal place while it is travelling. So the numbers flow during
a move and snap clean on the beat, which is the visual rhythm of the whole
video.

```
I      [1  0 / 0  1]   det  1
R90    [0 -1 / 1  0]   det  1
WIDE   [2  0 / 0  1]   det  2
TALL   [1  0 / 0  2]   det  2
SHEAR  [1  1 / 0  1]   det  1
FLIP   [1  0 / 0 -1]   det -1
SWAP   [0  1 / 1  0]   det -1
```

---

## The columns are the arrows

This is the payoff, and it is exact rather than a metaphor:

> **column one is where the gold arrow lands.**
> **column two is where the blue one lands.**
> **that is all matrix multiplication is.**

Watch `TALL` — the matrix reads `[1 0 / 0 2]`, and the blue arrow is sitting at
exactly twice its old length while the gold one has not moved. The second column
*is* the blue arrow's new home. Nothing else in the frame needs explaining after
that.

## The determinant is on screen the whole time

`det` is the one number a viewer can watch mean something: **it is how much
bigger the area got.** It reads 1 through the rotations, 2 through the
stretches, and goes **negative at exactly the moment the shape turns inside
out** — which is the beat labelled *"inside out — look at det."*

### Verified at import

```
every pose is integer                      or the downbeats show decimals
the choreography returns to the identity   or the loop has a seam
no pose leaves the frame                   largest singular value x UNIT
the determinants are what is claimed       computed, never typed
a caption names the move being made        the label-to-pose map is asserted
"inside out" lands on a negative det       or the line is a lie
```

That last pair exists because the captions drifted once already — "rotate."
was sitting on the identity bar. Now `NAMED` pins each named move to its matrix
and the render fails if they separate.

---

## Seamless loop

The choreography starts at the identity and its **last pose is the identity**,
so the final frame and the first frame are the same picture. Rewatch is the
metric Shorts actually rewards, and a loop is the cheapest way to buy it.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | `x → W x`, the matrix, the circle. *four numbers.* |
| 8–72 | **Sixteen bars.** One pose per bar, landing at 62% of the bar and holding |
| 72–86 | *column one is where the gold arrow lands… and one layer of an AI is exactly this* |
| 86–92 | **y = W x + b** — *that is the whole machine* |
| 92–100 | The eye |

Each move lands **before** the bar is over and then holds — `hit()` finishes the
interpolation at 62% — which is what makes it read as choreography rather than a
slow morph.

---

## Caption

```
Four numbers. Watch what they can do.

x → W x

That's it. That's the entire operation. A 2x2 grid of numbers, and a shape that
does exactly what the numbers say — rotate, stretch, shear, flip, swap.

Every pose here is whole numbers. Nothing is rounded, nothing is faked. When it
holds on the beat, what you're reading is exact.

Here's the part that makes the whole thing click:

Column one is where the GOLD arrow lands.
Column two is where the BLUE arrow lands.

That's all matrix multiplication is. Look at the tall one — [1 0 / 0 2] — the
blue arrow is exactly twice as long and the gold one hasn't moved. The matrix
isn't describing the shape. It's telling you where the two arrows go, and the
shape just follows.

And det, the number underneath? That's how much bigger the area got. It goes
negative at exactly the moment the shape turns inside out.

Now the reason this matters: one layer of a neural network is this. Not like
this — this. y = Wx + b. Run it a few billion times and you get ChatGPT.

It loops. Watch it again and follow one arrow.

#maths #mathtok #linearalgebra #ai #matrix #howaiworks #satisfying
```

**YouTube title:** `Four numbers, and everything they do — the equation every AI runs on`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl dancing_equation.py DancingEquation -w -r 1080x1920
python3 cinegrade.py videos/DancingEquation.mp4 dancing_equation.mp4
```

## Changing the choreography

`POSES` at the top — any list of integer 2×2 tuples. The assertions will refuse
a non-integer pose, a sequence that does not end on the identity (which would
seam the loop), a pose whose largest singular value pushes the shape out of
frame, and a caption that names a move the matrix is not making.
