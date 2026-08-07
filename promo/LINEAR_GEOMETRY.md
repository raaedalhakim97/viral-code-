# What Is a Matrix? — video brief

Companion to `linear_geometry.py`. Dancing linear equations, drawn as geometry.

- **Output:** 1080×1920, 60fps, **35.200000s** — 88 beats = 22 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## One matrix carries the whole video

```
A = [ 2  1 ]        det A = 3
    [ 1  2 ]
```

| Read it as | And you get |
| --- | --- |
| **rows** | the two equations `2x + y = 0` and `x + 2y = 3`, meeting at **(−1, 2)** |
| **columns** | where the basis lands: `(1,0) → (2,1)`, `(0,1) → (1,2)` |
| **unit square** | `(0,0) (2,1) (3,3) (1,2)` — area exactly **3**, which *is* the determinant |
| **eigenvectors** | `(1,1)` stretched **×3**; `(−1,1)` left alone **×1** |

Those are not four topics. They are the same four numbers seen from four sides,
which is the entire argument of the video: **the equation, the picture and the
matrix are one object.** Nothing on screen is an analogy.

The singular case reuses it by changing one entry:

```
B = [ 2  1 ]        det B = 0
    [ 4  2 ]
```

B's columns `(2,4)` and `(1,2)` both lie on `y = 2x`, so the plane falls flat
onto a line. B's rows are `2x + y = 0` and `4x + 2y = 3` — parallel, never
meeting. **Space collapsing and the system having no solution are the same
fact**, and the video shows them as one event rather than two.

Every value was checked with numpy before the scene was written, and the four
key ones are asserted at import, so a bad edit fails the render instead of
shipping.

---

## Structure

| Beats | What happens |
| --- | --- |
| 0–4 | Title, full screen |
| 4–19 | `y = mx + b` — **m tilts the line, b lifts it.** Two numbers, every line there is |
| 19–32 | A second equation, a second line, and the gold dot where they cross |
| 32–48 | The four numbers become a matrix; the plane deforms; the square's area goes 1 → 3 |
| 48–58 | Change one entry: the plane falls onto a line, area → 0, the lines go parallel |
| 58–68 | The one arrow that does not turn — it only grows, ×3 |
| 68–88 | Takeaway, then the eye |

The dancing equation at the top pulses on every beat for the whole runtime. It
is the only thing on screen that never stops moving, which is what ties the
notation to the picture the rest of the frame is drawing.

---

## The viewport, and why it exists

A stretches by ×3. That means **the transformed plane cannot stay inside a fixed
box** — `(3,3)` is as far out as the honest picture goes, and the grid runs well
past it. The first cut let it, and the grid ended up drawn straight across the
title.

The fix is not to shrink the maths until it fits. The plot is a **viewport**:
opaque bands mask everything above `y = 1.46` and below `y = −1.36`, and the
grid runs off the sides. That is what looking at part of an infinite plane
actually looks like, and it keeps the header and the commentary line on solid
black.

One catch worth remembering: **the bands only mask what was added before them.**
manimgl draws in insertion order, so anything created later sits on top. In
chapter 4 the collapsed square reaches `(3,6)` and punched straight through the
mask. It is now drawn clipped to the plot box — `(0,0)–(1.5,3)` — which is the
part that is genuinely in view.

---

## Caption

```
What is a matrix? Not a table of numbers. A picture of what happens to space.

Start with y = mx + b. Two numbers: m tilts the line, b lifts it. That's every
line there is.

Add a second equation and you get a second line. Solving them just means finding
where the two pictures cross — here, (−1, 2).

Now stack the four numbers into a matrix. Watch what it does to the plane: every
grid line bends, and the unit square becomes a parallelogram of area 3. That
number is the determinant. It was never a formula — it's an area.

Change one entry and the whole plane falls flat onto a line. Area 0. And the two
equations become parallel, so they never meet. Those aren't two facts. A
determinant of zero and a system with no solution are the same thing seen twice.

Last one: almost every arrow turns when the matrix hits it. One direction
doesn't. It only grows — exactly 3×. That's an eigenvector, and it's the reason
the word shows up everywhere in machine learning.

#linearalgebra #maths #matrix #geometry #mathtok
```

Alternate short opener if the long one underperforms:

```
A matrix isn't a table of numbers. It's a picture of what happens to space —
and the determinant is just the area of one square after you apply it.

#linearalgebra #maths #matrix #geometry #mathtok
```

The searchable phrase is the **first line**, since this is silent and there is no
transcript for either platform to index. *What is a matrix*, *determinant*,
*eigenvector* and *linear algebra* all carry real standing search demand — this
is a stronger YouTube candidate than most of the page.

**YouTube title:** `What is a matrix, really? (the picture nobody shows you)`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl linear_geometry.py LinearGeometry -w -r 1080x1920
python3 cinegrade.py videos/LinearGeometry.mp4 linear_geometry.mp4
```
