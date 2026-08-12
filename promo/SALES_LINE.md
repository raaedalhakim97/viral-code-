# Where m, x and b Come From — video brief

Companion to `sales_line.py`. **Episode 1 of "WHY DID WE LEARN THIS?"** — the
page series about the maths everybody was made to memorise and nobody was told
the use of.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## The idea

The equation is the **spine of the video, not a caption on it**. It sits at the
top from the first second to the last, and it starts *empty*:

```
y  =  m  ·  x  +  b
```

Each letter is a hole. The graph below fills them, one at a time, and every
number is physically **dragged off the picture and into its slot**:

| slot | comes from | on screen |
| --- | --- | --- |
| **x** | the day | the numbers already on the horizontal axis |
| **m** | the step | `+10` from one day to the next, every single time |
| **b** | the start | run the line back past day one — it began at 20 |
| **x** | 5 | ring the 5 that is already on the axis and drop it in |

```
y = m·x + b   →   y = 10·x + b   →   y = 10·x + 20
              →   y = 10·5 + 20  →   = 70
```

A viewer who has only ever seen the letters watches each one get replaced by a
thing they can point at. Nothing is asserted; everything arrives from somewhere
visible.

**The slot being talked about is gold and a size bigger. Slots still waiting are
dim.** So at any moment you can see which letter the video is answering, which
ones are already answered, and which are still open.

---

## What changed, and why

Three attempts got this wrong before it worked:

| cut | problem |
| --- | --- |
| 7 wobbly data points + least squares | too hard, and a dozen numbers on screen at once |
| 4 clean points, numbers cleared per rung | readable, but still too fast |
| 96 beats + camera breath | paced, but **the numbers never connected to the letters** |

The third one is the interesting failure. It was clear, it was slow, and it
still did not teach anything — because the graph and the formula were two
separate things that happened to be on the same screen. Saying *"that step is
m"* is not the same as watching the 10 leave the staircase and land in the m.

**Two things made it work:**

**Ring what is already there, don't add a copy.** The final drag lifts the `5`
that is *already printed on the day axis*. An earlier version drew a fresh `5`
next to it, which quietly broke the whole idea — the number being dragged has
to be a thing the viewer can already see.

**The multiplication dot is load-bearing.** School writes `mx`. Written that
way, the last substitution reads `105 + 20`. The explicit `·` costs one glyph
and makes `10 · 5 + 20` say exactly what it means.

---

## The data

```
day     1    2    3    4          (and 5, which is the whole point)
sales  30   40   50   60
```

The dots sit **exactly** on the line, so least squares never has to be
explained. The shop's sales go up by ten a day because that is the setup, not a
claim about shops. Messier data is a fine follow-up episode — *"what if the dots
don't line up?"* — and it is where the least-squares idea I cut actually
belongs, with a whole video to itself.

### Verified at import

```
every point is exactly on the line     s == 10d + 20, in integers
every step is exactly +10              the claim the staircase makes
STEP == M                              the visible step IS the slope
least squares returns (10, 20)         the fit is computed, not stated
the prediction at day 5 is 70          exactly
```

`least_squares()` is the real calculation, kept even though the data is clean,
so swapping in messier numbers would give a real answer rather than a broken
one.

---

## Pace and camera

**100 beats**, no animation shorter than 1.5 beats, and the hook holds 5 beats
before it shrinks into place at the top — the hook literally *becomes* the tool.

The camera moves the whole way, in two layers:

- **A 32-beat breath**, frame height easing between 100% and 95% on a slow
  cosine — one push-in and pull-out every 12.8 seconds. At 5% it is felt rather
  than noticed.
- **Deliberate pushes**: in to 95% for the staircase, out for the line, in to
  93% for the substitution, out again for the closing lines.

`camera.frame` already lives in `scene.mobjects` — that is why the updater runs,
and why `takeaway()` has to keep it out of the mobjects it clears and fades.

---

## Caption

```
y = mx + b. You wondered what m, x and b actually WERE. Nobody ever showed you.

Watch them arrive.

A small shop. Four days: 30, 40, 50, 60 sales. Four dots on a graph.

x is the day. That's it. That's all x ever was — the number along the bottom.

m? Look at the step from one day to the next. +10. +10. +10. Same jump every
time. Drag that 10 into m.
→ y = 10 · x + b

b? Join the dots into one straight line, then run it BACKWARDS, past day one, to
where it started. 20. Drag that into b.
→ y = 10 · x + 20

The equation is full. Now put tomorrow in. Day 5 — drag the 5 into x.
→ y = 10 · 5 + 20 = 70

Tomorrow you sell 70. You just predicted the future with year-9 maths.

(This is the first model in every AI course on earth. It's called linear
regression.)

We learned this at school. Nobody ever said what for.

#maths #mathtok #algebra #gcse #studytok #ai #linearregression
```

**YouTube title:** `Where m, x and b actually come from`

---

## The series

The name sits in the header for the whole video, so every episode reads as part
of one thing:

> **WHY DID WE LEARN THIS?**

| | |
| --- | --- |
| **Hook** | the formula, and the question everyone had |
| **Middle** | one picture, and the formula fills itself from it |
| **Close** | *We learned this at school. Nobody ever said what for.* |

Shipped so far, all inside the page's scope — **AI, angles, sin and cos.** See
the scope section in `MARKETING.md`; a general-maths formula, however well made,
does not belong here.

| # | formula | the viewer measures | the formula hands them |
| --- | --- | --- | --- |
| 1 | `y = m·x + b` | four days of sales | tomorrow — `sales_line.py` |
| 2 | `cos θ = (a·b)/(\|a\|\|b\|)` | two arrows on a grid | the **angle** — how AI decides two things mean the same — `cosine_similarity.py` |
| 3 | `z = w·x + b`, `y = max(0,z)` | one neuron's wires | why a neuron fires, or does not — `neuron.py` |
| 4 | `new = old − step·slope` | a ball on a valley | which way is downhill — how AI learns — `gradient_descent.py` |

Episodes 3 and 4 are deliberately built on episode 1: **a neuron *is* that same
line with a switch on the end**, and the *slope* that trains it is the same `m`.
The audience has already watched that equation get filled in, so each new
episode has exactly one new idea in it.

Still open, same shape, something to drag:

| formula | the viewer measures | the formula hands them |
| --- | --- | --- |
| softmax | three raw scores | the percentages a model answers with |
| `y = Wx + b` | a whole layer | what changes when one number becomes a grid of them |

---

## Subtitle track

`sales_line.srt` — 13 cues, no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the data

`DAYS`, `SALES` and `AHEAD` at the top are the only things to edit. The
assertions pin the current answers, so new data means updating them too — which
is deliberate, because it forces whoever changes the numbers to look at what the
fit became. Keep the values on the line and the steps equal, or the staircase's
claim stops being true and the assertion will say so.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl sales_line.py SalesLine -w -r 1080x1920
python3 cinegrade.py videos/SalesLine.mp4 sales_line.mp4
```
