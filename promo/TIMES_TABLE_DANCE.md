# MATH THAT DANCES — the times tables, drawn on a circle

Third in the dancing lane, after `dancing_equation.py` (a 2×2 matrix) and
`dancing_fourier.py` (epicycles). Different mechanism: no arrows, no
matrix — 200 dots and one multiplication.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The instruction, and it is the whole instruction

```
put 200 dots round a circle, numbered 0 to 199
join every dot n to dot k·n
```

That's it. Nobody draws a curve. For `k = 2` a **cardioid** turns up. For
`k = 3`, a **nephroid**. And the pattern is absurd:

```
the k times table   →   k − 1 lobes
```

`×2` → 1 lobe. `×3` → 2. `×7` → 6. `×12` → 11.

### Verified at import

Not taken on trust from a picture. The envelope of the chord family is
solved numerically (`F = ∂F/∂θ = 0`), and its **cusps are counted** by
finding where the envelope is traced at zero speed:

```
for every k the video shows, the cusp count is exactly k − 1
the envelope's inner radius matches (k−1)/(k+1) to 5e-3
the cusps sit on the unit circle, r = 1
the ring is asserted to fit the platform safe box
```

A render fails rather than showing a shape whose lobe count doesn't match
the rule on screen.

---

## Why this one is beat-locked, and why that matters

`k` is driven by a `ValueTracker`, and **every step lands on a downbeat**.
Between integers the figure smears — hundreds of chords sweeping at once
— then it **snaps into a clean shape exactly on the count.** That's the
dance, and it's the reason the video is silent by design: whatever track
gets dropped on it, the shapes land on the beat.

The march is 8 steps of 2.5 beats, `×5` through `×12`, and the code
asserts the step divides into quarter-beats — if a caption edit ever
pushed it off the grid, the snap would drift out of time and the build
would fail instead.

---

## Hook

Per the retention rules used on `net_vs_gross`: **the outcome is frame 1.**
No title card, no build-up — the finished cardioid is already on screen at
t=0 under one line:

> **the 2 times table drew this.**

Six words, an image that shouldn't come from a times table, and the
curiosity gap does the rest. The pinned line at the top is the answer the
video is walking toward — `the k times table → k − 1 lobes` — which reads
as nonsense for the first ten seconds and then doesn't.

---

## Structure

| Beats | Time | |
| --- | --- | --- |
| 0–5 | 0:00 | **the finished cardioid.** *the 2 times table drew this.* |
| 5–24 | 0:02 | chords clear to 200 bare dots → *join every dot n to dot 2n* → it redraws itself |
| 24–40 | 0:09 | `×3` — the nephroid. *two lobes.* |
| 40–56 | 0:16 | `×4` → three, `×5` → four. *always one less than the times table.* |
| 56–80 | 0:22 | **the dance** — `×5` to `×12`, one integer per 2.5 beats, snapping on the count |
| 80–88 | 0:32 | *One circle. One times table. That's the whole instruction.* |
| 88–92 | 0:35 | *Comment a times table and I'll run it* |
| 92–100 | 0:37 | The eye |

---

## Caption

```
The 2 times table drew this.

200 dots round a circle, numbered 0 to 199. Join every dot n to dot 2n.
That's the entire instruction — nobody draws the curve, it just turns up.

Now the 3 times table. Two lobes.
The 4? Three. The 5? Four.

The k times table gives you k − 1 lobes. Every time.

One circle. One times table. That's the whole thing.

Comment a times table and I'll run it.

#satisfying #oddlysatisfying #maths #mathtok #timestables #cardioid #fyp
```

**YouTube title:** `The 2 times table draws a cardioid — and the pattern never breaks`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl times_table_dance.py TimesTableDance -w -r 1080x1920
python3 cinegrade.py videos/TimesTableDance.mp4 times_table_dance.mp4
```

## Changing it

`N` is the dot count and `DANCE` is the march. Raising `K_LAST` widens the
verified range — the import check recomputes the envelope for every k in
it, so adding multipliers costs about a second of build time and buys a
guarantee. `wheel()` sets the gold → rose → sky colour sweep round the
ring.

The chord group carries its own updater, so it is `self.add()`ed directly
and never introduced through an `AnimationGroup` — that rebuilds a fresh
`VGroup` of the children and the updater silently never fires. This is the
same trap that froze the pendulums in `pendulum_wave.py`.
