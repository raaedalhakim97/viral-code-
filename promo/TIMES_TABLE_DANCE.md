# times_table_dance — 400 dots, one multiplication, thirty seconds

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## Almost no words

No banner, no series title, no pinned rule, no running commentary. **One
line at the start, one at the end**, and between them thirty seconds of
uninterrupted movement. The figure is the content; anything written over
it is competing with it.

```
0:00–0:03   the cardioid, already there  ·  "the 2 times table drew this."
0:03–0:32   the dance. nothing to read.
0:32–0:37   "Comment a times table and I'll run it"
0:37–0:40   the eye
```

The only thing on screen during the dance is a small dim number at the
top — the current multiplier. It isn't an explanation, it's an
anticipation device: you start wondering what the next one will look like.

---

## The instruction, never stated on screen

```
400 dots round a circle, numbered 0 to 399
join every dot n to dot k·n
```

`k = 2` gives a cardioid. Push `k` upward and the figure never settles,
because the k times table draws **k − 1 lobes** and k is always climbing.

---

## Why it reads as dancing and not sliding

`k` is **not** swept at a constant rate. It runs on

```
k(s) = 2 + s − (A/2π)·sin(2πs)        A = 0.9
dk/ds = 1 − A·cos(2πs)
```

Near an integer the speed drops to **0.1** and the shape *holds*. Between
integers it climbs to **1.9** and the whole thing *whips* through. One
clean figure every 6 beats — hold, whip, hold — and because `k(s)` hits an
exact integer at every integer `s`, **every hold lands on a downbeat.**

It is one continuous move from start to finish. Nothing cuts, nothing
restarts, there is a single `play()` call covering the whole 30 seconds.
A quarter-turn of drift is layered on top so the figure travels rather
than pulsing in place.

**Measured on the finished render** (mean frame-to-frame pixel change):

```
hold  k=3   1.36      whip  k≈3.5   4.45
hold  k=4   1.22      whip  k≈4.5   4.08
hold  k=5   1.07      whip  k≈5.5   3.77
hold  k=6   0.94      whip  k≈6.5   4.01
```

Roughly 4× the motion mid-whip as at the hold. The rhythm is real, not
intended.

---

## What 400 points changed, and where it stops

Doubling from 200 makes the low-k figures noticeably silkier — the
cardioid becomes a solid sweep of lines instead of a visible fan. But
density cuts both ways: **past about k = 14, four hundred chords stop
being a figure and become grey mush.** The first cut ran to k = 21 and the
back half was unwatchable.

Two fixes, both in the code:
- the sweep **stops at k = 14**, asserted at import
- stroke opacity **falls as k climbs** (`0.52 · 6/(k+4)`, clamped) so the
  perceived brightness stays flat instead of saturating into a flat disc

The 400 dots themselves were dropped — the chord endpoints already draw
the rim, so the dots were 400 redundant `move_to` calls per frame.

### Verified at import

```
the envelope of the chord family is solved numerically (F = ∂F/∂θ = 0)
and its cusps counted, for every k the sweep passes through: always k − 1
the envelope's inner radius matches (k−1)/(k+1)
k(s) is strictly increasing, and lands on an integer at every integer s —
    so the holds cannot drift off the beat
the sweep is asserted to stop at or below k = 14
the ring is asserted to fit the platform safe box
```

---

## Caption

```
The 2 times table drew this.

400 dots round a circle. Join every dot n to dot k·n. That's it — nobody
draws the curve.

Then let k climb.

Comment a times table and I'll run it.

#satisfying #oddlysatisfying #maths #mathtok #timestables #cardioid
#visualmath #fyp
```

**YouTube title:** `400 dots, one times table, thirty seconds`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl times_table_dance.py TimesTableDance -w -r 1080x1920
python3 cinegrade.py videos/TimesTableDance.mp4 times_table_dance.mp4
```

Full-res render is ~5 minutes — 400 chords are rebuilt every frame.

## Changing it

`N` is the dot count, `UNITS` how far k climbs, `BEATS_PER_UNIT` how long
each shape holds, and `EASE_A` how hard it holds (0 = constant speed, →1 =
long stillness and a violent whip). `UNITS × BEATS_PER_UNIT` must equal
the dance length in beats, and the code asserts it — so the holds cannot
silently fall off the beat.

The chord group carries its own updater, so it is `self.add()`ed directly
and never introduced through an `AnimationGroup` — that rebuilds a fresh
`VGroup` of the children and the updater silently never fires. Same trap
that froze the pendulums in `pendulum_wave.py`.
