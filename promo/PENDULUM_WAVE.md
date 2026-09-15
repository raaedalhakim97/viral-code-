# every 22 seconds — ten pendulums that come back

First **"SATISFYING MATH"** episode — the entertainment lane. No lesson, no
formula on screen until the payoff. Built to be watched, not studied: same
house grade and signature, far less talking.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The setup

Ten pendulums, released at the same instant, all pushed the same distance
sideways. Their lengths are picked so that in one 22-second cycle,
pendulum *k* completes exactly **16 + k** full swings — 16, 17, 18, … 25.

A pendulum's frequency depends only on its length (`f ∝ 1/√L`, so
`L ∝ 1/f²`), so choosing those swing counts fixes the ten lengths exactly:

```
swings/cycle:  16    17    18    19    20    21    22    23    24    25
length:       5.20  4.61  4.11  3.69  3.33  3.02  2.75  2.52  2.31  2.13
```

Nothing drives them. Nothing connects them. No one nudges them back. They
drift apart into what looks like pure noise — and then, 22 seconds later,
every one is back in line at the same instant, because every one has
completed a **whole number** of swings.

The video runs the cycle twice: chaos, snap, chaos, snap.

### Verified at import

```
L × f² is the same constant for all ten        real pendulum physics
every swing count per cycle is a whole number  this is what makes them realign
smallest vertical gap between bobs > bob diameter — they never collide
max swing angle 5.93°                          small-angle regime, so the
                                               period really is amplitude-
                                               independent and the snap is exact
motion window is exactly 2 cycles (44.000s = 2 × 22.0s)
```

---

## A real bug caught in QA

The first cut looked right in stills and was completely frozen — the bobs
never moved. Cause: `LaggedStartMap(FadeIn, wave)` builds a **new** `VGroup`
of the children (`AnimationGroup.__init__`), and the scene tracks *that*
copy. The original group — the one carrying the swing updater — was never
in `scene.mobjects`, and `Scene.update_mobjects` only calls `update()` on
things in that list, so the updater never fired.

Caught by measuring bob pixel positions across frames rather than eyeballing
stills: the leftmost bob moved only ~15px when it should have swung 94px,
and that 15px was pure camera-breath zoom. Fixed with
`FadeIn(wave, lag_ratio=0.06)` — `Animation` takes `lag_ratio` directly, so
the staggered reveal survives and `animation.mobject` stays the real group.

Verified after the fix: at a sync point the bob-to-bob gaps are uniform
(≈ pivot spacing); at mid-cycle they alternate between ≈3px and ≈48px —
the signature zigzag of alternating ±amplitude.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **"they come back."** — ten pendulums, one release |
| 8–10 | the rig fades in, all ten aligned |
| 10–65 | released together → drift → *"no pattern. nothing in step."* → *"wait."* |
| 65 | **first realignment**, exactly on the beat — *"every 22 seconds."* pins to the top |
| 65–120 | *"nothing is connecting them" · "the only difference is length"* → **second realignment** |
| 120–132 | *Nothing is coordinating them. Ten lengths. That's the whole trick.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
They come back. Ten pendulums, one release, nothing connecting them.

Watch them come apart. Within a few seconds there's no pattern left —
nothing in step, nothing repeating.

Then, exactly 22 seconds after the release, all ten are back in line at
the same instant.

Nothing is coordinating them. No motor, no timing, no one touching them.
The only difference between them is length.

Each one is cut so it completes a whole number of swings in 22 seconds —
16 swings, 17, 18, all the way to 25. Whole numbers. So they can only
finish together.

Ten lengths. That's the whole trick.

#satisfying #oddlysatisfying #physics #pendulum #maths #asmr #fyp
```

**YouTube title:** `Ten pendulums fall into chaos — then snap back, exactly on time`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl pendulum_wave.py PendulumWave -w -r 1080x1920
python3 cinegrade.py videos/PendulumWave.mp4 pendulum_wave.mp4
```

## Changing it

`N`, `N0` and `CYCLE` at the top. The assertions recompute the lengths and
refuse to build if `L × f²` stops being constant, if any swing count stops
being a whole number, if two bobs could collide, if the swing angle leaves
the small-angle regime, or if the motion window stops being an exact whole
number of cycles — any of which would break the realignment.
