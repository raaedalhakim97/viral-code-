# Your Name Is An Equation — video brief

Companion to `name_equation.py`. The announcement video for follower #1000: the
four stages a name goes through — **tokenize → vectors → space x y → equation** —
ending on a closed curve that belongs to that name and no other.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Name in this cut:** `RANIA` → `[18, 1, 14, 9, 1]`
- **Audio:** none. Add a track in the TikTok editor on posting day.

---

## The four stages, in the order they were asked for

| Beats | | |
| --- | --- | --- |
| 0–4 | | Hook: *your name is an equation — follower #1000 gets theirs* |
| 4–8 | **CARD** | **1 · TOKENIZE** |
| 8–20 | | `RANIA` comes apart into `R A N I A`. A model never sees the word. |
| 20–24 | **CARD** | **2 · VECTORS** |
| 24–38 | | `a = 1 … z = 26` → `[ 18, 1, 14, 9, 1 ]` |
| 38–42 | **CARD** | **3 · SPACE X Y** |
| 42–56 | | Each number becomes a wheel in the plane. The number is its **speed**. |
| 56–60 | **CARD** | **4 · EQUATION** |
| 60–78 | | The equation, one full lap, the curve. Then SARA, then back to RANIA. |
| 78–84 | | **HERO** — labels go, the shape takes the screen and turns |
| 84–90 | | **FOLLOWER #1000 — comment your name** |
| 90–100 | | The eye |

A live `n / 4` marker sits in the header for the whole of each stage, so a
viewer who arrives mid-scroll knows which part they are in.

---

## The rule

Letter *k* of the name gets a wheel of radius `1/k` turning at a speed equal to
the letter's value. Chain the wheels tip to tail and follow the last tip:

```
x(t) = Σ (1/k) · cos(vₖ t)
y(t) = Σ (1/k) · sin(vₖ t)          v = the letters, a=1 … z=26
```

For `RANIA` that is `v = 18, 1, 14, 9, 1` and `r = 1, ½, ⅓, ¼, ⅕`.

Two things fall out of it, and both are the reason the video works:

- **Every curve closes.** Every `vₖ` is a whole number, so both sums have period
  2π exactly. The point always comes home — there is no fudging the last frame.
- **Different names give different curves,** including anagrams: reordering the
  letters changes which radius each speed gets, so `MAYA` and `AMYA` are not the
  same drawing.

The montage ends back on `RANIA` rather than on a stranger's name, so the last
shape before the hero beat is hers.

### What is claimed and what is not

Stages 1 and 2 are **true of every language model** — text is split into tokens
and the tokens become numbers before anything else happens. Stage 3 onward is
**our rule**, and the video says so: nothing here claims a model draws curves
from names. The stage cards keep the two halves visibly separate.

### Verified at import

```
vals("maya") == [13, 1, 25, 1]        a = 1, z = 26
every curve closes                    |p(0) − p(2π)| < 1e-9, every name
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

**The shape needs a beat with nothing else in it.** At working size, with a
name, a tagline, a stage marker and a title around it, a rosette this dense
reads as a smudge — and it is the entire reason to watch to the end. The last
six beats drop every label, scale the curve from 1.22 to 1.98 units and turn it
slowly. That beat is the payoff, not the equation.

**The hook holds for 3 beats, not 2.** Every other video in the library gives
the opening card 2 beats (0.8s) before shrinking it to a header. That is the one
frame that has to stop the scroll, so here it gets 1.2s and the slack comes out
of the section pad.

---

## Caption

```
Your name is an equation. Follower #1000 gets theirs.

Here's what happens to a name before any AI touches it.

1 — TOKENIZE. A model never sees the word "RANIA". Text gets cut into tokens
first. Short name, so: R A N I A.

2 — VECTORS. Every token becomes a number. a=1, b=2, all the way to z=26.
RANIA is now [18, 1, 14, 9, 1]. That's all a model ever holds — numbers.

3 — SPACE X Y. Now put those numbers in the plane. Give each one a wheel: wheel
1 is full size, wheel 2 is half, wheel 3 is a third. And the number itself is
the SPEED — how fast that wheel turns. Chain them tip to tail and follow the
last tip.

4 — EQUATION.
x(t) = Σ (1/k)·cos(vₖ t)
y(t) = Σ (1/k)·sin(vₖ t)

Every letter is a whole number, so the curve always closes. One lap and it comes
home. That shape is RANIA — and no other name draws it.

Follower #1000 gets their name turned into this. Comment your name.

#maths #mathtok #ai #howaiworks #tokenization #fourier #generativeart
```

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
NAME = "RANIA"
MONTAGE = ["SARA", "RANIA"]   # contrast, then back to hers
```

One thing that does **not** follow automatically: a line of narration that
counts the letters. `"four numbers, one moving point"` was hard-coded and went
wrong the moment the name stopped being four letters; it is now
`f"{len(vals(NAME))} numbers, one moving point"`. Any new line that states a
count has to be built the same way.

When #1000 lands, swap `NAME` to their name, re-render, and the whole video is
about them.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl name_equation.py NameEquation -w -r 1080x1920
python3 cinegrade.py videos/NameEquation.mp4 name_equation.mp4
```
