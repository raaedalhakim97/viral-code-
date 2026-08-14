# How AI knows what "it" means

Companion to `what_does_it_mean.py`.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **how does AI know**
> **what "it" means?**
> *one dot product. that is the whole trick.*

---

## Why this one, now

Both red ball videos end by **naming** attention — *"that limit is called
attention, it is the one idea inside every AI"* — and neither shows what it is.
That is an open loop sitting in the two most-watched things on the page.

Closing it costs almost nothing, because **attention is the dot product from the
cos episode** doing exactly one job: choosing what to look at. The audience
already has the tool. This just points it at a sentence.

---

## The picture

```
the cat sat on the mat because IT was warm
```

What is "it"? Every word is an arrow — episode 2 established that. To resolve
"it", the model takes its arrow and dot-products it against every other word.

```
it   = (3, 4)
mat  = (0, 5)   ->  3(0) + 4(5)  =  20      <- winner
cat  = (5, 0)   ->  3(5) + 4(0)  =  15
sat  = (1, 1)   ->  3(1) + 4(1)  =  7
```

**The cat scoring second is the point.** "The cat" is what most people answer,
and it loses by five. A winner that narrowly beats the obvious wrong answer is a
far better watch than one that wins by a mile — and it is the honest shape of
what a model computes: **not a certainty, a ranking.**

**No softmax here, on purpose.** Turning those scores into percentages needs
`e^x`, which would put the first rounded number in the whole series on screen.
The ranking *is* the idea. The percentages are a detail, and they deserve their
own episode where the rounding is the subject rather than a smudge.

### Verified at import

```
every score is an integer     countable straight off the grid
mat wins                      or the sentence's answer is wrong
cat is second                 the near-miss the video depends on
the gap is 3..8               not a tie, not a rout
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *how does AI know what "it" means?* |
| 8–24 | The sentence. "it" is ringed. *The cat? The mat? You know. The machine does not.* |
| 24–44 | Every word becomes an arrow on a grid |
| 44–72 | Three dot products — **20**, **15**, **7** — each scored and parked |
| 72–82 | mat wins. *That is attention. A dot product, choosing.* |
| 82–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

---

## Caption

```
How does an AI know what "it" means?

"The cat sat on the mat because IT was warm."

You know instantly. The machine doesn't. So it measures.

Every word is an arrow — same as the cos video. To work out what "it" points at,
the model takes the arrow for "it" and dot-products it against every other word.
Multiply the matching numbers, add. That's it.

it  = (3, 4)

mat = (0, 5)  →  3(0) + 4(5) = 20
cat = (5, 0)  →  3(5) + 4(0) = 15
sat = (1, 1)  →  3(1) + 4(1) = 7

Highest score wins. "It" is the mat.

And look at the cat — 15. Second place. That's what most people guess, and it
lost by five. The model isn't certain. It never is. It just ranks.

That is attention. Not a metaphor for attention — literally the thing. A dot
product, choosing what to look at. Run it a few billion times and you get
ChatGPT.

Two videos ago you couldn't follow nine bouncing balls. This is how a machine
decides which one to watch.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #attention #transformers #howaiworks #dotproduct
```

**YouTube title:** `How AI knows what "it" means — attention, in one dot product`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl what_does_it_mean.py WhatDoesItMean -w -r 1080x1920
python3 cinegrade.py videos/WhatDoesItMean.mp4 what_does_it_mean.mp4
```

## Changing the sentence

`IT` and `WORDS` at the top. The assertions pin the current answer — change a
vector and the render fails until the winner still matches the sentence's real
meaning, and until the near-miss is still the word people would guess. Both of
those are what makes the video work, so neither is left to chance.
