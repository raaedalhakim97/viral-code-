# x(t) = Σ c·e^(ikt) — spinning arrows that draw the eye

**"SATISFYING MATH"** episode. The sequel to `dancing_equation.py`: that
one danced a 2×2 matrix, this one dances a Fourier series.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The idea

Take a chain of arrows, joined tip to tail. Spin each at its own constant
speed. Follow the tip of the last one. That path can be **any** closed
shape — you only have to pick the right lengths and speeds.

```
x(t)  =  sum of  c · e^(i k t)
```

Each arrow is one term: its length is `|c|`, its speed is `k`.

## What it draws

The channel's own eye mark, as a closed outline — out along the top curve,
back along the bottom. The coefficients aren't hand-tuned; they're the
discrete Fourier transform of that outline, largest arrow first.

```
 1 arrow   -> a circle        max error 0.50  = 16% of the shape width
 4 arrows  -> the shape       max error 0.16  =  5%
24 arrows  -> sharp corners   max error 0.027 =  0.8%
```

---

## The payoff is the lopsidedness

The arrows are nothing like equal:

```
1st / 2nd   =   5.5x
1st / 10th  =   137x

first  4 arrows  =  91.6% of the total arrow length
other 20 arrows  =   8.4%
```

Four arrows out of twenty-four carry almost all of it. The other twenty do
nothing but sharpen the two corners — bin them and you'd barely see the
difference.

**Which is exactly how image compression works.** Keep the few large
coefficients, throw the many small ones away, and the picture survives.
That's what a JPEG does — in two dimensions, with cosines.

### Verified at import

```
the outline is closed                     first point meets last
error falls as terms are added            1 -> 4 -> 24
24 terms land within 0.03 of the outline
the first four arrows really are >90% of the total arrow length
the first arrow really is >5x the second
the arrow chain can never leave the frame  sum of all |c| is checked
every frequency used is odd                the symmetry claim is real
```

---

## A note on what this video does *not* do

The classic epicycle animation shows a long visible chain of comparable
arms. This one can't, and doesn't pretend to: for any simple closed curve
the fundamental dominates, so after three or four arrows the rest are
specks. The first cut fought that and the caption said "twenty-four" over
a picture showing one arm and a speck — a mismatch between the claim and
the frame.

Rather than pick a jagged shape just to make the chain look busy, the
video now says the true thing out loud and makes the lopsidedness the
point. The weakness *is* the lesson.

---

## Structure

| Beats | |
| --- | --- |
| 0–10 | **every arrow is a number** — spin them and watch |
| 10–32 | One arrow. One arrow only ever draws a circle. |
| 32–58 | Four arrows — already the shape |
| 58–106 | Twenty-four. Nothing steers the tip. The last twenty only sharpen the corners |
| 106–120 | *the first four are 92% of the total length · the other twenty are 8% · bin them and you'd barely see it* |
| 120–132 | *That is what a JPEG does. Keep the big ones. Bin the rest.* |
| 132–138 | share ask |
| 138–150 | The eye — the same mark the arrows just drew |

---

## Caption

```
Every arrow is a number. Spin them all at once and watch what they draw.

One arrow only ever draws a circle. That's all one arrow can do.

Four arrows, and it's already the shape.

Twenty-four. Nothing is steering the tip — each arrow just turns at its
own speed, forever. The last twenty only sharpen the corners.

Now look at the sizes. They're nothing like equal. The first four arrows
are 92% of the total length. The other twenty are 8%.

Bin those twenty and you'd barely see the difference.

That is what a JPEG does to a photo. Keep the big ones. Bin the rest.

#satisfying #oddlysatisfying #fourier #maths #compression #fyp
```

**YouTube title:** `Spinning arrows draw a shape — and show you how JPEG works`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl dancing_fourier.py DancingFourier -w -r 1080x1920
python3 cinegrade.py videos/DancingFourier.mp4 dancing_fourier.mp4
```

## Changing it

`STAGE_TERMS` sets the three stages, `SCALE` the drawing size. Swap
`eye_outline()` for any closed complex-valued path and everything else
follows — but the assertions will refuse to build if the new shape breaks
a claim the video makes out loud: the 92/8 split, the >5× first-to-second
ratio, the falling error, or the chain staying inside the frame.
