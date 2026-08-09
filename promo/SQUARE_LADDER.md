# Where The 2ab Comes From — video brief

Companion to `square_ladder.py`. Sister video to `circle_ladder.py`, and built
the same way: **one picture, five rungs, nothing ever added — only relabelled.**

- **Output:** 1080×1920, 60fps, **28.800000s** — 72 beats = 18 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## Why this one

The comment that arrived on *Every Wave Is A Circle* was:

> *"We did these equations in school but I never took the time to look at them
> this way."*

That is the format, stated by a viewer: **something they were made to memorise,
shown as a picture for the first time.** No AI, no new maths — just the thing
they already half-remember, drawn.

`(a + b)² = a² + 2ab + b²` is the best remaining candidate in school algebra.
Everyone memorised it. Almost nobody was shown the square. And the one thing
that confuses people — *why is there a 2* — is literally two rectangles.

---

## One square, five rungs

A square of side `a + b`, cut once across and once down:

| | | |
| --- | --- | --- |
| **1** | one square, side a + b | its area is `(a+b)²` |
| **2** | cut it — four pieces, nothing else | `a² + ab + ab + b²` |
| **3** | the two rectangles are congruent | `(a+b)² = a² + 2ab + b²` |
| **4** | drop them and the square has a hole | `(a+b)² ≠ a² + b²` |
| **5** | let b shrink — call it h | `(x+h)² = x² + 2xh + h²` → `d(x²)/dx = 2x` |

**Rung 3 proves the 2, it doesn't assert it.** A gold copy of the top-left
rectangle rotates 90° and lands exactly on the bottom-right one. That is the
whole answer to "why is there a 2ab", and it takes two beats.

**Rung 4 is the mistake, shown as a hole.** The two rectangles fade out and
there is a visible gap in the square. `a² + b²` is not wrong by an abstraction —
it is short by that much area.

**Rung 5 is calculus on the same square.** Rename a and b to x and h, shrink h
to a sliver, and the picture becomes: a big square `x²`, two thin strips
`2xh`, and a corner `h²` too small to matter. What the square gains when x grows
by h is `2xh + h²`, so it grows at `2x`. A fourteen-year-old's diagram produces
a derivative with no limits notation anywhere on screen.

### Verified at import

```
the four pieces tile the square exactly      200 split fractions
the two ab pieces have equal area            to 1e-12
(a+b)² == a² + 2ab + b²                      2000 random pairs
(a+b)² != a² + b²                            asserted, because that's rung 4
(x+h)² − x² == 2xh + h²                      exact integers, 39×39 grid
((x+h)² − x²)/h → 2x                         h = 1e-6
```

The growth identity is checked in **integer** arithmetic on purpose. In float64
the subtraction `(x+h)² − x²` loses about 1e-14 to cancellation, so a
floating-point assertion at a tight tolerance proves the rounding, not the
algebra.

---

## Three things worth keeping

**Opacity belongs to a ValueTracker, not to the updater.** Every region is
redrawn each frame from `self.frac_t`, so any fill set by `FadeIn` or
`.animate.set_opacity()` is overwritten on the next frame. Each region reads its
own `ValueTracker`, and reveals and fades are animations *on those trackers* —
which is also what makes rung 4's hole and rung 5's highlight possible at all.

**A position updater must not be attached during `ShowCreation`.** It rewrites
the points every frame and wipes out the partial draw. The split lines are
revealed by fading their stroke opacity instead.

**A payoff needs a hold, not just an arrival.** The derivative lands on the last
beat of rung 5, and in the first cut the takeaway cleared it one beat later —
the climax of the video was on screen for a third of a second. The takeaway now
keeps `self.eq` and fades everything else, so `d(x²)/dx = 2x` sits above the
closing lines for seven beats.

---

## Caption

```
(a + b)² = a² + 2ab + b². Where does the 2ab come from?

Draw a square with side a + b. Cut it once across, once down. Four pieces:

a·a in the corner. b·b in the opposite corner. And two rectangles, both a·b.

Those two rectangles are the same rectangle — rotate one and it lands exactly
on the other. That's your 2ab. It was never a rule, it was two pieces.

Which is also why (a + b)² is NOT a² + b². Take the two rectangles away and
there is a hole in the square that size.

Now the good part. Keep the same square, call the sides x and h, and let h get
small. The square grows by two thin strips — 2xh — plus a corner h² that is
basically nothing.

So x² grows at 2x.

d(x²)/dx = 2x

That's the derivative, and it's the same square you drew in year 9.

#maths #mathtok #algebra #calculus #gcse #studytok #学习
```

**YouTube title:** `Where the 2ab comes from — (a+b)² is just a square`

The searchable lines are *"why is (a+b)² not a²+b²"* and *"why is the derivative
of x² equal to 2x"*. Both are typed queries with a school-age audience behind
them, and this video answers both with one drawing.

---

## Subtitle track

`square_ladder.srt` — 14 cues, no gaps, no overlaps, asserted at generation.
Upload on YouTube under Subtitles → Add language → Upload file → With timing.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl square_ladder.py SquareLadder -w -r 1080x1920
python3 cinegrade.py videos/SquareLadder.mp4 square_ladder.mp4
```

---

## The rest of the queue

Same format, same 72-beat shell, each one a school formula nobody was shown:

| picture | rungs |
| --- | --- |
| squares on a right triangle | Pythagoras, and why `a² + b²` is areas not lengths |
| a rectangle of dots | `1+2+…+n = n(n+1)/2`, in one slide |
| L-shaped shells | `1+3+5+…` is always a perfect square |
| a square with a bite out of it | `a² − b² = (a+b)(a−b)`, by sliding the L |
| a circle cut into wedges | why the area of a circle is `πr²` |
