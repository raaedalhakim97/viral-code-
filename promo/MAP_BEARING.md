# sin and cos, on a real map

Companion to `map_bearing.py`. **Episode 8**, and the first of the
**"WHERE YOU ACTUALLY USE IT"** companions — episode 5's formula, run on a
problem a person actually has.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **your map is a grid.**
> **the world is not.**
> *sin and cos are the translation*

---

## The spine

```
east   =  r · cos θ
north  =  r · sin θ
```

**Episode 5's spine, with the letters renamed to what they are.** `x` and `y`
were never abstract. On a map they are *east* and *north* — and that renaming is
most of the lesson. The formula did not change. The words did.

| slot | comes from | direction |
| --- | --- | --- |
| **cos θ, sin θ** ← 0.8, 0.6 | **episode 5.** A recall card, into both rows | handed back |
| **r** ← 5 km | the distance your phone gave you | dragged **up** |
| **east, north** → 4 km, 3 km | worked out inside the equation | dropped **down** onto the map |

---

## The real problem

Your phone gives you a **distance and a direction** — *"5 km, that way."* A map
is a **grid**: it only speaks east and north. Those are two different languages
for the same place, and sin and cos are the only thing that translates between
them.

```
distance   5 km
direction  cos θ = 0.8, sin θ = 0.6

east  = 5 · 0.8 = 4 km
north = 5 · 0.6 = 3 km
```

**And then the beat that makes it stick.** Walking 4 km east and then 3 km north
gets you to exactly the same place — but you walked **7 km** to do it, not 5.
That comparison is free, because the picture is already on screen. It is the
difference between distance and displacement, and it is the moment the video
stops being arithmetic and becomes something the viewer has physically done
before, standing at a corner deciding whether to cut across.

### Verified at import

```
cos² + sin² == 1              exactly, as Fractions
5·cos == 4 and 5·sin == 3     whole km, no square roots on screen
4² + 3² == 5²                 the two legs really do reach it, in integers
4 + 3 > 5                     or the closing beat is not true
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *your map is a grid, the world is not* |
| 8–28 | A map. You at the origin, the place 5 km away, and the arrow between |
| 28–56 | The direction recalled from episode 5, then **r ← 5** dragged up |
| 56–82 | **4 km east, 3 km north** drawn onto the map — and the 7 km it costs |
| 82–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

---

## Caption

```
Your map is a grid. The world is not.

Your phone says: "5 km, that way." A map only speaks east and north. Those are
two different languages for the same place — and sin and cos are the
translation. Nothing else does that job.

The direction, in numbers: cos θ = 0.8, sin θ = 0.6.
The distance: 5 km.

east  = 5 × 0.8 = 4 km
north = 5 × 0.6 = 3 km

So: 4 km east, 3 km north. Same place.

But look what that walk costs you. 4 + 3 = 7 km, to get somewhere that was 5 km
away. The straight line was always shorter — you've felt that standing at a
corner, deciding whether to cut across.

This is every sat-nav turning "in 300 m, turn left" into a dot. Every delivery
app. Every game character that walks in a direction. Every drone that gets told
where to go.

An angle and a distance went in. A place on a grid came out.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #sincos #navigation #gcse #studytok
```

**YouTube title:** `sin and cos on a real map — turning a direction into a place`

---

## Subtitle track

`map_bearing.srt` — no gaps, no overlaps, asserted at generation.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl map_bearing.py MapBearing -w -r 1080x1920
python3 cinegrade.py videos/MapBearing.mp4 map_bearing.mp4
```
