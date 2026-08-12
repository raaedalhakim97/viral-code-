# cos — How AI Decides Two Things Mean The Same

Companion to `cosine_similarity.py`. **Episode 2 of "WHY DID WE LEARN THIS?"**

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **cos**
> is how AI compares
> *you learned it for triangles*

---

## Why this one is in scope

It is the only formula that touches **all three** of the page's subjects in one
picture: it *is* an angle, it is built out of **cos**, and cosine similarity is
the number underneath every search box, every recommendation and every RAG
lookup in production. The `a² + b² = c²` episode was cut for exactly the
opposite reason — see the scope section in `MARKETING.md`.

---

## The spine

```
              a · b
  cos θ  =  ─────────
             |a| · |b|
```

Same shell as episode 1: the equation sits at the top for the whole video, it
starts **empty** — the slots hold `a · b` and `|a| · |b|` in dim grey — and
every number is dragged into its slot off the picture.

| slot | comes from | direction |
| --- | --- | --- |
| **a · b** ← 15 | multiply the matching numbers, add | dragged **up** |
| **\|a\|·\|b\|** ← 25 | five long times five long | dragged **up** |
| **cos θ** → 0.6 | worked out inside the equation | dropped **down** onto the arc |

**The score goes the other way, exactly like the prediction in episode 1.** You
can count both arrows straight off the grid. Nobody can measure the angle
between them. So the two things you *can* get are dragged up, and the one you
cannot is handed back down.

---

## Same number discipline as episode 1

```
a = (5, 0)    |a| = 5
b = (3, 4)    |b| = 5
a · b   = 5×3 + 0×4 = 15
|a||b|  = 5 × 5     = 25
cos θ   = 15 / 25   = 0.6        exact, and θ = 53°
```

Small integers, one new number per stage, each stage's numbers cleared before
the next arrives, and **the payoff exact rather than rounded.**

**`a = (5, 0)` is doing real work.** It puts the first arrow flat along the
axis, so `|a| = 5` is readable off the grid with no square-root side quest — and
it leaves one honest **multiplication by zero** in the dot product, which is the
clearest possible demonstration of "multiply the *matching* numbers".

`b = (3, 4)` is the 3-4-5, the one length everybody already knows, so `|b| = 5`
can be stated as a measurement rather than derived.

And 53° is a big enough angle to actually see. `a = (4,3)` with `b = (3,4)` also
gives clean integers, but the angle is 16° and the arc reads as a smudge.

### Verified at import

```
|a| and |b| are whole numbers      nothing on screen needs a square root
a·b == 15 and |a||b| == 25         in integers
cos == Fraction(3, 5) == 0.6       checked as a fraction, not a float
30° < θ < 75°                      so the arc is actually visible
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *cos is how AI compares* |
| 8–26 | Two arrows on a grid, and the angle θ between them |
| 26–46 | **a · b.** Count the arrows off the grid, multiply matching, add → 15 |
| 46–64 | **\|a\|·\|b\|.** Each arrow is 5 long → 25 |
| 64–82 | **0.6** drops onto the arc, then a 0–1 scale gives the number meaning |
| 82–91 | *We learned this at school. Nobody ever said what for.* |
| 91–100 | The eye |

**The score needs a scale or it means nothing.** `0.6` on its own is a number
with no size. After it lands on the arc, the grid clears and a 0→1 bar appears
with the marker at 0.6 — *nothing in common* at one end, *the same* at the
other. The bar's own labels carry that, so the note line gets the one sentence
that names the thing instead.

**The score had to move further out.** It first dropped at 2.35 grid units along
the bisector, which is where the `θ` label lives — the payoff landed on top of
it. It drops at 3.4 now.

---

## Caption

```
cos. You learned it for triangles. It's how AI decides two things mean the same.

Every thing an AI knows — a word, a photo, a song — becomes an arrow.

Two things, two arrows. And how alike they are IS the angle between them. Small
angle, nearly the same. Right angle, nothing in common.

But nobody can measure that angle. So:

Count the arrows off the grid.
a = (5, 0)
b = (3, 4)

Multiply the matching numbers and add:
5×3 + 0×4 = 15

Each arrow is 5 long, so the bottom is 5 × 5 = 25.

cos θ = 15 / 25 = 0.6

0.6. On a scale where 1 is the same direction and 0 is nothing in common. And
you never measured a single angle.

This is called cosine similarity. It's the number under every search box, every
"you might also like", and every time a chatbot looks something up before it
answers.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #cosine #trigonometry #machinelearning #howaiworks
```

**YouTube title:** `cos — how AI decides two things mean the same`

The searchable lines are *"what is cosine similarity"* and *"what is cos
actually used for"*. The first brings the AI audience, the second brings the
school one, and they land on the same picture.

---

## Subtitle track

`cosine_similarity.srt` — 13 cues, no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the vectors

`AX, AY` and `BX, BY` at the top are the only things to edit. Every number,
label and assertion follows from them — but the assertions pin the *current*
answers, so new vectors mean updating those too. That is deliberate: the
`|a|`/`|b|` assertion will fail the render the moment a vector needs a square
root, which is the thing that would quietly put an ugly number on screen.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl cosine_similarity.py CosineSimilarity -w -r 1080x1920
python3 cinegrade.py videos/CosineSimilarity.mp4 cosine_similarity.mp4
```
