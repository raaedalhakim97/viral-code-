# Why Is It Called A Sine Wave — video brief

Companion to `sine_unroll.py`. Third in the ladder family after
`circle_ladder.py` and `square_ladder.py`, on the same shell: **one picture, six
rungs, nothing ever added — only relabelled.**

- **Output:** 1080×1920, 60fps, **28.800000s** — 72 beats = 18 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## Why this one, right after the circle video

`circle_ladder.py` showed the circle and the triangle on it — height is sin,
width is cos, Pythagoras, Euler. It never showed the **wave**. So the most
obvious question a viewer is left with is the one the title asks, and it is a
question people genuinely type: *why is it called a sine wave.*

---

## The picture

A point goes round a circle on the left. To its right is a window on the last
wavelength or so of its **height** — the newest sample sits hard against the
circle and older ones slide right, so the wave never runs off the frame:

```
wave(x, t) = A·R·sin( t − k·f·(x − X0) )        wave(X0, t) = the dot's height
```

| | | |
| --- | --- | --- |
| **1** | one point, going round | the circle |
| **2** | its HEIGHT, drawn over time | `y = sin t` |
| **3** | a second point, a quarter turn ahead | `y = cos t` |
| **4** | slide the gold wave a quarter wavelength | `cos t = sin(t + 90°)` |
| **5** | spin faster / draw it bigger | `y = A·sin(f t)` |
| **6** | look at the circle **edge-on** | `y = sin t` |

**Rung 3 is why there is a second dot.** cos t gets plotted as a *height*, but
on the circle it is a *width* — so a horizontal connector from the first dot to
the cosine pen would be a lie about what is being measured. `sin(t + 90°)` is
exactly `cos t`, so a second dot a quarter turn ahead has cos t as its **height**
and the same honest horizontal connector works. It also means rung 4 is
something the viewer has already watched happen rather than a new claim.

**Rung 4 proves the shift.** A ghost of the gold wave slides right by exactly a
quarter wavelength — `π/(2k)` screen units — and lands on the blue one. It then
thins to 30% opacity so the blue shows *through* it; at full opacity the thick
gold simply hid the thing it had just matched.

**Rung 6 is the payoff, and it is literally true.** The circle squashes to a
vertical line — that is what circular motion looks like from the side — and the
dot is left going up and down, still driving the same wave. Simple harmonic
motion *is* the side view of uniform circular motion. Nothing is exaggerated to
get the ending.

### Verified at import

```
cos t == sin(t + π/2)                       2000 angles, 1e-12
sin has period 2π                           2000 angles, 1e-12
the pen at X0 equals the dot's height       exactly, all t
the quarter-wavelength slide lands on cos   286 phases × the whole window
```

---

## One thing worth keeping

**A ghost that has to land on a moving target cannot be a frozen copy.** The
first version snapshotted the sine and `.shift()`ed it right. Over the three
beats of the slide the live wave moved on, so the ghost landed on nothing. The
ghost is now driven by a *shift tracker* read inside its updater, so it stays
live for the whole slide and coincides with the cosine exactly at the end —
which is what makes the assertion above worth having.

---

## Caption

```
Why is it called a sine WAVE?

Take one point going round a circle. That's the whole ingredient list.

Now draw its HEIGHT over time — how high it is, moment by moment. That's it.
That's the sine wave. Nothing was added.

Now add a second point a quarter turn ahead. Its height is cos t. Same circle,
same speed — it just left earlier.

So cos t = sin(t + 90°). Slide the gold wave a quarter wavelength to the right
and it lands exactly on the blue one. Same wave, different starting point.

Spin the point faster and the wave tightens. Draw the circle bigger and the wave
gets taller. Frequency and amplitude — both are just facts about the circle.

Then the good part. Look at the circle edge-on. It collapses to a line, and the
point is left going straight up and down — still drawing the same wave.

A sine wave is a circle, seen from the side.

#maths #mathtok #trigonometry #sine #physics #gcse #studytok
```

**YouTube title:** `Why it's called a sine WAVE — a circle, seen from the side`

The searchable lines are *"why is it called a sine wave"*, *"where does the sine
wave come from"* and *"difference between sin and cos"* — the third one is
answered in rung 4 in six seconds, and it is one of the most-typed trig queries
there is.

---

## Subtitle track

`sine_unroll.srt` — 14 cues, no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl sine_unroll.py SineUnroll -w -r 1080x1920
python3 cinegrade.py videos/SineUnroll.mp4 sine_unroll.mp4
```
