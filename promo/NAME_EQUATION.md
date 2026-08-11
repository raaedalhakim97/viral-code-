# Your Name Is An Equation — video brief

Companion to `name_equation.py`. The announcement video for follower #1000: the
four stages a name goes through — **tokenize → vectors → space x y → equation** —
ending on a closed curve that belongs to that name and no other.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Name in this cut:** `MIRANDA` → `[13, 9, 18, 1, 14, 4, 1]` — 7 letters, 7-fold
- **Audio:** none. Add a track in the TikTok editor on posting day.

---

## The four stages, in the order they were asked for

| Beats | | |
| --- | --- | --- |
| 0–4 | | Hook: *your name is an equation — follower #1000 gets theirs* |
| 4–8 | **CARD** | **1 · TOKENIZE** |
| 8–20 | | `MIRANDA` comes apart into `M I R A N D A`. A model never sees the word. |
| 20–24 | **CARD** | **2 · VECTORS** |
| 24–38 | | `a = 1 … z = 26` → `[ 13, 9, 18, 1, 14, 4, 1 ]` |
| 38–42 | **CARD** | **3 · SPACE X Y** |
| 42–56 | | Each number becomes a wheel in the plane. The number is its **speed**. |
| 56–60 | **CARD** | **4 · EQUATION** |
| 60–75.5 | | The equation, one full lap, the curve, and a hold on it named |
| 75.5–84 | | **HERO** — labels go, the shape takes the screen and turns |
| 84–90 | | **FOLLOWER #1000 — comment your name** |
| 90–100 | | The eye |

A live `n / 4` marker sits in the header for the whole of each stage, so a
viewer who arrives mid-scroll knows which part they are in.

---

## The rule

Letter *k* gets a wheel. Chain the wheels tip to tail and follow the last tip:

```
x(t) = Σ rₖ · cos(vₖ t)
y(t) = Σ rₖ · sin(vₖ t)        vₖ = m·aₖ + 1        rₖ = 0.72ᵏ
```

`aₖ` is the letter (a = 1 … z = 26) and **m is how many letters the name has**.
For `MIRANDA`: `a = 13, 9, 18, 1, 14, 4, 1`, m = 7, so
`v = 92, 64, 127, 8, 99, 29, 8`.

### Why `m·aₖ + 1` and not just the letter

The first cut used the bare letter as the speed. It was honest, it closed, it
was unique to the name — and it looked like a scribble. The speeds shared no
structure, so nothing lined up with anything.

With `vₖ = m·aₖ + 1`, every speed leaves **the same remainder when divided by
m**. Advance `t` by 1/m of a lap and every term picks up the same factor:

```
z(t + 2π/m) = Σ rₖ e^(i vₖ t) · e^(i(m aₖ + 1)2π/m)
            = Σ rₖ e^(i vₖ t) · e^(2πi aₖ) · e^(2πi/m)
            = e^(2πi/m) · z(t)                      because every aₖ is a whole number
```

The curve comes back to itself, **rotated by exactly one m-th of a turn**. An
m-letter name draws an m-fold flower. `MIRANDA` has seven letters, so it draws a
seven-fold rosette; a four-letter name draws a four-fold one. That is the line
the video says out loud, and it is the reason the shape is worth looking at.

Three things fall out of the rule, and all three are asserted:

- **Every curve closes.** Every `vₖ` is a whole number, so both sums have period
  2π exactly. The point always comes home — there is no fudging the last frame.
- **The m-fold symmetry is exact**, not approximate — checked to 1e-12.
- **Different names give different curves,** including anagrams: reordering the
  letters changes which radius each speed gets, so `MAYA` and `AMYA` are not the
  same drawing.

**The montage is empty by default.** An earlier cut morphed through a second
name to prove the shapes differ, which is a good argument and the wrong video
when the clip is a reply to one person — no other name should share her screen.
`MONTAGE` still works if a comparison is ever wanted; whatever it does not use
goes to the labelled hold, and `pad_to` raises rather than drifts, so adding
names back without widening stage 4 fails the render instead of quietly eating
the hero beat.

**The sample count follows the name.** The fastest wheel turns `m × biggest
letter + 1` times per lap — 91 for RANIA, **127 for MIRANDA**. A fixed
`NPTS` meant longer names traced as visible polygons, so it is now derived
from the name: 55 samples per cycle of the fastest wheel.

**The key line shows the letters, not the derived speeds.** With seven of each,
`a = … → v = …` shrank to fit the frame and became unreadable. The rule
`vₖ = 7·aₖ + 1` is on screen directly above it, so `v` is never a mystery.

### What is claimed and what is not

Stages 1 and 2 are **true of every language model** — text is split into tokens
and the tokens become numbers before anything else happens. Stage 3 onward is
**our rule**, and the video says so: nothing here claims a model draws curves
from names. The stage cards keep the two halves visibly separate.

### Verified at import

```
vals("maya") == [13, 1, 25, 1]        a = 1, z = 26
every curve closes                    |p(0) − p(2π)| < 1e-9, every name
m-fold symmetry is exact              |z(t + 2π/m) − e^(2πi/m)·z(t)| < 1e-12
distinct names → distinct curves      no collisions
MAYA ≠ AMYA                           max separation 0.99 units
```

The name list is deduped before the collision check — `MONTAGE` may legitimately
end back on `NAME`, and without the dedupe the check flags a name against
itself.

The scene raises rather than renders if any of those stop holding.

---

## Two things worth keeping

**An updater that hard-codes opacity fights `.animate.set_opacity()`.** The
wheels and the trail are rebuilt every frame from `self.tt`, so any opacity set
by an animation is overwritten on the next frame. Both read a second tracker,
`self.dim`, instead — which is what lets the stage-4 card dim the drawing
underneath it. The first cut dimmed only the wheels and the card number landed
on a full-brightness gold arc.

**A morph is not a beat of screen time.** The closing montage first gave ALEX
and SARA three beats each, spent entirely on the `Transform` — so each name was
only fully drawn on the single frame the transform ended, and was immediately
morphed away. Each now gets 1.5 beats of morph and 1.5 beats of hold.

**A curve with ninety loops fills in solid at normal stroke width.** At 3.4 the
flower rendered as a gold disc — every crossing merged. The trace and the final
curve are drawn at 1.8, which is thin enough that the loops stay separate at
working size and much thinner than it sounds once the hero beat scales it up.

**The wheels have to recede while the curve builds.** The fastest wheel turns
about ninety times in one lap, so at full brightness it strobes over the thing
it is drawing. `self.dim` is animated from 1.0 down to 0.30 across the trace.
For the same reason the stage-3 preview sweep only runs `t` to 0.13 of a lap —
at 0.55 the fast wheel was already a blur and the point of that beat, that the
wheels turn at *different* speeds, was invisible.

**The shape needs a beat with nothing else in it.** At working size, with a
name, a tagline, a stage marker and a title around it, a rosette this dense
reads as a smudge — and it is the entire reason to watch to the end. The last
**8.5 beats** drop every label, scale the curve from 1.22 to 1.98 units and turn
it slowly through 0.9 radians. That beat is the payoff, not the equation.

**The hook holds for 3 beats, not 2.** Every other video in the library gives
the opening card 2 beats (0.8s) before shrinking it to a header. That is the one
frame that has to stop the scroll, so here it gets 1.2s and the slack comes out
of the section pad.

---

## Caption

```
Your name is an equation. Follower #1000 gets theirs.

Here's what happens to a name before any AI touches it.

1 — TOKENIZE. A model never sees the word "MIRANDA". Text gets cut into tokens
first. Short name, so: M I R A N D A.

2 — VECTORS. Every token becomes a number. a=1, b=2, all the way to z=26.
MIRANDA is now [13, 9, 18, 1, 14, 4, 1]. That's all a model ever holds — numbers.

3 — SPACE X Y. Put those numbers in the plane and give each one a spinning
wheel. Wheel 1 is full size, each one after is 0.72 of the last. The number
decides how FAST its wheel turns. Chain them tip to tail and follow the last
tip.

4 — EQUATION.
x(t) = Σ rₖ·cos(vₖ t)
y(t) = Σ rₖ·sin(vₖ t)        vₖ = 7·aₖ + 1

Here's the pretty part. Every speed leaves the same remainder when you divide it
by 7 — so if you turn t by a seventh of a lap, the whole shape comes back to
itself, turned by a seventh of a turn.

Seven letters. Seven-fold flower.

Different name, different number of letters, different flower. That one is
MIRANDA's, and no other name draws it.

Follower #1000 gets their name turned into this. Comment your name.

#maths #mathtok #ai #howaiworks #tokenization #fourier #generativeart
```

### Alternate caption — "how it's made"

Same video, process angle. Use this one if the flower is the hook rather than
the AI stages. Build-in-public captions get saved and re-watched, and every line
here is a step someone could actually follow.

```
How to turn a name into a flower 🌸

Step 1 — letters become numbers.
a=1, b=2, all the way to z=26.
MIRANDA → 13, 9, 18, 1, 14, 4, 1

Step 2 — every number gets a wheel.
The first wheel is full size. Each one after it is 0.72 of the one before, so
they shrink as they go.

Step 3 — the number decides the SPEED.
Not the letter itself — 7 times the letter, plus 1. Why 7? Because MIRANDA has 7
letters. Speeds: 92, 64, 127, 8, 99, 29, 8.

Step 4 — chain the wheels tip to tail and follow the very last tip for one
full lap. That path is the drawing.

Two things make it work, and both are just arithmetic:

Every speed is a whole number → after one lap the pen is exactly back where it
started. The shape always closes. Nothing is fudged.

Every speed leaves the same remainder when divided by 7 → turn the lap a seventh
of the way round and the whole picture lands back on itself, rotated a seventh
of a turn. That's the seven petals.

7 letters, 7-fold flower. A 4-letter name draws a 4-fold one.

Your name has a flower too. Comment it 👇

#maths #mathtok #generativeart #creativecoding #fourier #howitsmade #python
```

**YouTube title for this cut:** `How to turn a name into a flower (the maths behind it)`

---

**YouTube title:** `Turning a name into an equation — tokens, vectors, curves`

The searchable lines are *"how does AI turn words into numbers"* and
*"what is tokenization"* — both are typed queries, and stages 1–2 answer them
before the art starts.

---

## Subtitle track

`name_equation.srt` — the on-screen text as **21 timed cues** covering the full
40.0s with no gaps and no overlaps (both asserted when the file is generated).

Upload it on YouTube under Subtitles → Add language → Upload file → With
timing. TikTok has no caption upload, so there the caption above does the work.

---

## Changing the name

`NAME` and `MONTAGE` at the top of the file are the only things to edit — the
speeds, radii, scale, equation key line and every assertion follow from them.
`RAD_STR` carries fractions up to `⅙`, so names past six letters need one more
entry in that list.

```python
NAME = "MIRANDA"
MONTAGE = []      # her name only — no other name shares the screen
```

One thing that does **not** follow automatically: a line of narration that
counts the letters. `"four numbers, one moving point"` was hard-coded and went
wrong the moment the name stopped being four letters; it is now
`f"{M_FOLD} numbers, one moving point"`. Any new line that states a count has to
be built the same way — and so does anything sized for a short name, which is
what `NPTS` and the key line caught when MIRANDA arrived.

When #1000 lands, swap `NAME` to their name, re-render, and the whole video is
about them.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl name_equation.py NameEquation -w -r 1080x1920
python3 cinegrade.py videos/NameEquation.mp4 name_equation.mp4
```
