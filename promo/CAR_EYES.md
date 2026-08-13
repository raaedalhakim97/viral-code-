# Rotation, run on a self-driving car

Companion to `car_eyes.py`. **Episode 10**, and the third
**"WHERE YOU ACTUALLY USE IT"** companion — episode 7's formula, doing the job
it is genuinely doing right now, in traffic.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **a self-driving car**
> **cannot see the world.**
> *it only sees its own view*

---

## The real problem

A car's camera does not report where things *are*. It reports where things are
**relative to the car**: *"3 metres to my right, 4 metres in front of me."*

*Right* and *ahead* are the **car's** words, and they change the instant the car
turns. A map does not have an *ahead*. It has north and east, and it never
turns.

So every single thing the car sees has to be **turned** before it means
anything — and turning is the one job sin and cos do.

```
camera says   3 right, 4 ahead        in the CAR's frame
car is turned by θ                    cos θ = 0.8, sin θ = 0.6

new x = 3(0.8) − 4(0.6) = 0
new y = 3(0.6) + 4(0.8) = 5

on the map    (0, 5)                  5 m due north
```

**And what happens if you skip it:** the car brakes for somebody who is not
there. That is one line, it is true, and it is what makes the maths feel like it
matters — because it does.

---

## The spine

```
new x  =  x · cos θ  −  y · sin θ
new y  =  x · sin θ  +  y · cos θ
```

Identical to episode 7, deliberately — so it is recognisably the same tool, and
the *picture* carries all of the new meaning.

| slot | comes from | direction |
| --- | --- | --- |
| **cos θ, sin θ** ← 0.8, 0.6 | how far the car is turned. A recall card, into all four slots | handed back |
| **x** ← 3 | what the camera said: 3 m right | dragged **up** |
| **y** ← 4 | what the camera said: 4 m ahead | dragged **up** |
| **new x, new y** → 0, 5 | worked out inside the equation | dropped **down**: the arrow swings, and the car straightens with it |

**The car wedge turns too.** When the sighting rotates onto the map frame, the
little wedge swings from θ to straight up. That is the whole idea in one motion:
nothing in the world moved — the *words* changed.

### Verified at import

```
cos² + sin² == 1                   exactly, as Fractions
the sighting lands on (0, 5)       in Fractions, not floats
distance in == distance out == 25  turning cannot move the pedestrian
it matches a real rotation matrix  against np.cos/np.sin at the true angle
it lands at exactly 90°            so "due north" is literally true
the slot map matches the spine     every S_X index really does hold an "x"
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *a self-driving car cannot see the world* |
| 8–24 | The camera's report: a person, 3 m right and 4 m ahead |
| 24–40 | *Right and ahead of WHAT?* The car's turn, recalled into four slots |
| 40–68 | 3 and 4 dragged up, and the sighting swings to **5 m due north** |
| 68–82 | Skip it and the car brakes for somebody who isn't there |
| 82–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

---

## Caption

```
A self-driving car cannot see the world. It only ever sees its own view.

Its camera says: "person — 3 metres to my right, 4 metres in front of me."

Right and ahead of WHAT? Of the car. Turn the car and both of those words change
meaning, while the person hasn't moved an inch.

A map has no "ahead". It has north. So every single thing the car sees has to be
turned before it means anything — and turning is the one job sin and cos do.

How far the car is turned: cos θ = 0.8, sin θ = 0.6

new x = 3(0.8) − 4(0.6) = 2.4 − 2.4 = 0
new y = 3(0.6) + 4(0.8) = 1.8 + 3.2 = 5

On the map: the person is 5 metres due north. Same person, still 5 metres away —
new words.

Skip that step and the car brakes for somebody who isn't there.

Robot vacuums, AR filters, drones landing, a phone that knows which way up it
is. All of them. Thousands of times a second.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #selfdriving #trigonometry #robotics #howaiworks
```

**YouTube title:** `Why a self-driving car needs trigonometry`

---

## Subtitle track

`car_eyes.srt` — no gaps, no overlaps, asserted at generation.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl car_eyes.py CarEyes -w -r 1080x1920
python3 cinegrade.py videos/CarEyes.mp4 car_eyes.mp4
```
