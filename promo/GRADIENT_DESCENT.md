# How AI Learns — video brief

Companion to `gradient_descent.py`. **Episode 4 of "WHY DID WE LEARN THIS?"**

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The hook

> **how does AI learn?**
> **it rolls downhill**
> *one line of maths, a few billion times*

---

## The spine

```
new  =  old  −  step · slope
```

One curve: **how wrong the model is**, for every setting it could have. The
bottom of the valley is the right answer. All of training is that one rule,
applied over and over — look at the slope where you are, and step the other way.

| slot | is | where it comes from |
| --- | --- | --- |
| **old ← 4** | where the ball is now | dragged off the ball |
| **slope ← 2** | which way is downhill | read off the tangent: *along 1, up 2* |
| **step ← 1** | how far to move | **not measured — chosen** |

```
new = 4 − 1·2 = 2      the ball moves
then  2 − 1·1 = 1      it moves again
then it settles at the bottom
```

**The step is the one number that is not dragged off the picture.** `old` and
`slope` are measurements; `step` fades in with the line that says it is yours to
pick. Being straight about that is the honest version — it is the learning rate,
and choosing it is most of the job.

---

## Why the curve is y = x²/4

So that **every number on screen is whole**. Its slope at `x` is `x/2`, so at
x = 4 the slope is 2 and at x = 2 it is 1 — both drawable as *"along 1, up 2"*
on a grid where the x and y scales are equal, **which is why they are equal**.
With step = 1 the update halves the position every time:

```
4  →  2  →  1  →  the bottom
```

so the arithmetic stays in integers and the convergence is something you watch
rather than something you are told.

### Verified at import

```
slope(x) == x/2               checked against a numerical derivative, not assumed
the sequence is 4 → 2 → 1     in integers
every slope shown is whole    so nothing on screen is rounded
each step lowers the height   which is what "downhill" means
```

---

## Caption

```
How does an AI actually learn? It rolls downhill.

Picture a valley. The height is how WRONG the model is. The bottom is the right
answer — and the model can't see where the bottom is. It only knows the ground
under its own feet.

So it does one thing, over and over:

new = old − step × slope

Where is it now? 4.
Which way is downhill? Look at the slope where it stands: along 1, up 2. So the
slope is 2.
How big a step? That one's your choice. Call it 1.

new = 4 − 1×2 = 2

It moved downhill. Now the new one becomes the old one, and go again:
2 − 1×1 = 1

Smaller slope, smaller step. It slows down as it gets close, and stops where the
ground is flat — because a flat slope means nothing left to change.

That's it. That's training. A few billion times.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #machinelearning #howaiworks #calculus #gradientdescent
```

**YouTube title:** `How AI learns — new = old − step × slope`

---

## Subtitle track

`gradient_descent.srt` — 13 cues, no gaps, no overlaps, asserted at generation.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl gradient_descent.py GradientDescent -w -r 1080x1920
python3 cinegrade.py videos/GradientDescent.mp4 gradient_descent.mp4
```
