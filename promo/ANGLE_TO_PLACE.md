# sin and cos — turning an angle into a place

Companion to `angle_to_place.py`. **Episode 5 of "WHY DID WE LEARN THIS?"**

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **sin and cos**
> what are they FOR?
> *they turn an angle into a place*

---

## The spine

```
x  =  r · cos θ
y  =  r · sin θ
```

Same shell as every episode: it sits at the top for the whole video, it starts
**empty**, and every number is dragged into its slot off the picture.

| slot | comes from | direction |
| --- | --- | --- |
| **cos θ** ← 0.8 | how far ACROSS the point on a radius-1 circle is | dragged **up** |
| **sin θ** ← 0.6 | how far UP it is | dragged **up** |
| **r** ← 5 | the length of the real arrow | dragged **up** |
| **x, y** → 4, 3 | worked out inside the equation | dropped **down** onto the grid |

---

## What the video actually teaches

**Draw a circle of radius one. Put a point on it. Its width is cos θ and its
height is sin θ.** That is not a fact about cos and sin — that *is* them, the
entire definition, and it is the thing school somehow never says out loud. So
both numbers are read straight off the grid rather than pressed on a
calculator.

Then there is exactly one more idea in the whole video: a circle of radius 5 is
the same circle, five times bigger, so the point sits in the same direction and
five times further out.

```
x = 5 · 0.8 = 4
y = 5 · 0.6 = 3
```

An angle went in. A place came out. That is the entire job.

**The angle never gets a number.** θ here is 36.87°, which is ugly, and its
value is irrelevant — the video is about turning *an* angle into a place, not
about which angle. Leaving it as `θ` keeps the only rounded number in the series
off the screen.

### Verified at import

```
cos² + sin² == 1                exactly, as Fractions
5·cos == 4 and 5·sin == 3       whole numbers, no square roots on screen
the fractions match real trig   against np.cos/np.sin at the true angle
25° < θ < 65°                   so the arc is actually visible
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *sin and cos: what are they FOR?* |
| 8–34 | A circle of radius 1, one point, the angle θ, and its width and height |
| 34–54 | 0.8 and 0.6 dragged up into `cos θ` and `sin θ` |
| 54–80 | The real arrow is **5** long. `r` dragged up, and **(4, 3)** dropped down |
| 80–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

**Two grids, cross-faded, not one grid that rescales.** The unit-circle stage
needs gridlines every 0.1 to make 0.8 countable; the payoff stage needs to reach
5. A single scale cannot do both. The angle arc is drawn identically in each so
the viewer can see it is the same turn.

---

## Caption

```
sin and cos. You spent a year on them and nobody said what they were FOR.

They turn an angle into a place. That's it. That's the job.

Draw a circle of radius 1. Put a point on it.

How far ACROSS did it go? 0.8. That's cos θ.
How far UP did it go? 0.6. That's sin θ.

That's not a fact about cos and sin. That IS cos and sin. The whole definition.
Width and height of one turn.

Now the only other idea in this video: a circle of radius 5 is the same circle,
five times bigger. Same direction, five times further out.

x = 5 × 0.8 = 4
y = 5 × 0.6 = 3

Your point is at (4, 3).

An angle went in. A place came out.

Every game character that walks in a direction, every robot arm, every phone
screen that rotates — this line, running a few thousand times a second.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #sincos #gcse #studytok #ai
```

**YouTube title:** `sin and cos — how an angle becomes a place`

The searchable lines are *"what are sin and cos actually used for"* and *"what
is cos actually"*. Both are among the most-typed trig queries there are, and
they land on the same picture.

---

## Subtitle track

`angle_to_place.srt` — no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the angle

`COS` and `SIN` at the top are the only things to edit, and they must be a
Pythagorean pair over the same denominator or the point is not on the circle —
the `cos² + sin² == 1` assertion will say so immediately. `R` then has to be
chosen so `R·COS` and `R·SIN` are both whole, which is what keeps square roots
and rounding off the screen.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl angle_to_place.py AngleToPlace -w -r 1080x1920
python3 cinegrade.py videos/AngleToPlace.mp4 angle_to_place.mp4
```
