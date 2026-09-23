# lissajous_dance — two sine waves, 1800 dots, thirty seconds

Companion to `times_table_dance.py`. **Same recipe, different machine:**
one line at the start, one at the end, and thirty seconds of
uninterrupted movement in between.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The instruction, never stated on screen

```
x = sin(3t + π/2)        side to side
y = sin(b·t)             up and down
```

One dot per value of `t`, eighteen hundred of them. Both coordinates are
plain sine waves. **The only thing that ever changes is how fast the
vertical one runs.**

## What happens when b lands on a whole number

The ribbon closes, and the figure kisses the frame an exact number of
times:

```
b  touches on the top and bottom
3  touches on the left and right
```

— each divided by whatever factor `b` shares with 3. Which is why the
whole figure **collapses to a perfect circle at b = 3** and to a figure
of eight at b = 6: the shared factor folds the curve onto itself.

---

## Why it reads as dancing

`b` is moved between whole numbers on `smooth(smooth(t))` — flat at both
ends, steep in the middle. The ribbon **holds** closed on the whole
number, then the loop breaks open and the whole thing **whips** through
to the next. One shape every 8 beats — two bars — so every hold lands on
a downbeat.

The path is **2 3 4 5 6 7 6 5 4 3**: it climbs, turns round, comes back,
and rests on the circle. Every step is one unit, so the ribbon always
travels at the same speed.

**Measured on the finished render** (mean frame-to-frame pixel change):

```
whip  3.52      hold  0.00
whip  3.67      hold  0.06
whip  3.18      hold  0.00
whip  3.23      hold  0.03
```

The holds are dead still. Nothing about the rhythm is approximate.

---

## The trap this one avoids

`times_table_dance` could only sweep so far before the outer chords
started spinning fast enough to alias — in that construction a point's
motion scales with its index, so the rim runs away from the middle.

Here a dot at parameter `t` shifts by `t·Δb`, and **`t` never exceeds
2π**, so no part of the ribbon can outrun the rest no matter how far `b`
travels. The figure was sized from the other direction instead: the curve
gets 2.5× longer between b = 2 and b = 7, so at 900 dots it pulled apart
into loose scatter. 1800 keeps it solid at the busiest shape.

### Verified at import

```
tangencies counted from the exact contact parameters, not sampled: for
every b in the path the figure touches top and bottom b/g times and the
sides 3/g times, with g = gcd(3, b)
b = 3 is checked to be a circle to 1e-12
every whole b closes the ribbon exactly at t = 2π
the easing is measured, not assumed: near-zero slope over the first and
last 3% of each move, peak slope above 1.9× the average
every step of the path is exactly one unit
the figure fits the platform safe box
```

---

## Structure

| Beats | Time | |
| --- | --- | --- |
| 0–8 | 0:00 | the 3:2 figure, already there · *"two sine waves drew this."* |
| 8–80 | 0:03 | nine moves, two bars each. nothing to read. |
| 80–92 | 0:32 | *Comment two numbers and I'll draw them* |
| 92–100 | 0:37 | the eye |

---

## Caption

```
Two sine waves drew this.

One goes side to side. One goes up and down. That's the whole machine —
the only thing that changes is how fast the second one runs.

Watch what happens when they line up on whole numbers.

Comment two numbers and I'll draw them.

#satisfying #oddlysatisfying #maths #mathtok #lissajous #visualmath
#physics #fyp
```

**YouTube title:** `Two sine waves, 1800 dots, thirty seconds`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl lissajous_dance.py LissajousDance -w -r 1080x1920
python3 cinegrade.py videos/LissajousDance.mp4 lissajous_dance.mp4
```

Full-res render is under two minutes — the ribbon is a single `DotCloud`,
so all 1800 dots move with one numpy assignment per frame rather than
1800 Python calls.

## Changing it

`A_FREQ` is the horizontal wave, `BPATH` the journey the vertical one
takes, and `BEATS_PER_UNIT` how long each shape holds. `BPATH` is
asserted to move in single units and to fill the dance exactly, so the
holds cannot silently fall off the beat. Any `A_FREQ` works — the
tangency check recomputes itself and will fail the build if the figure
stops matching the count.

The `DotCloud` carries its own updater, so it is `self.add()`ed directly
and never introduced through an `AnimationGroup` — that rebuilds a fresh
group and the updater silently never fires. Same trap that froze the
pendulums in `pendulum_wave.py`.
