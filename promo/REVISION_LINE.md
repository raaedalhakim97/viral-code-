# The best line, run on your own revision

Companion to `revision_line.py`. **Episode 9**, and the second
**"WHERE YOU ACTUALLY USE IT"** companion — episode 6's measurement, run on a
problem this page's audience literally has.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **how many hours is enough?**
> *the line will tell you*

---

## The spine

```
mark  =  m · hours  +  b
```

**Episode 1's spine, with the letters renamed to what they are** — the same move
episode 8 makes. `x` was never abstract; here it is hours of revision.

| slot | comes from | direction |
| --- | --- | --- |
| **m** ← 8 | the step: one more hour is worth 8 marks | dragged **up** |
| **b** ← 38 | where the line starts, at zero hours | dragged **up** |
| **hours** ← 5 | the number the viewer actually wants to try | dragged **up** |
| **mark** → 78 | worked out inside the equation | dropped **down** onto the graph |

---

## Episode 6 found the best line. It never used one.

This does. Four students, hours revised against the mark they got, dots that do
not line up, the line that misses least, and then the only question anybody
actually asks: **what do I get if I do five?**

```
hours   1    2    3    4
mark   48   52   60   72        the dots do NOT line up

best line   mark = 8 · hours + 38
it gives    46   54   62   70    total miss  2² + 2² + 2² + 2²  =  16
at 5 hours  8 · 5 + 38  =  78
```

**Why this data.** Every residual is exactly ±2, so the total is a clean 16 and
no single point looks like the odd one out — the line reads as a *compromise*
rather than a near-miss on one outlier, which is the whole idea episode 6 built.
And 8 marks per hour is optimistic enough to be motivating without being a silly
claim.

---

## The last beat is the honest one, and it is the point

```
the line knows four people.
it does not know you.
```

The line describes those four students. It is **not** a promise about the
viewer, and saying so is worth more than the prediction is.

It is also the single most important thing about every model ever built, and
almost nobody says it out loud: **a model finds the pattern in the data it was
shown, and then gets asked about somebody who was not in it.** That is not a
disclaimer bolted on the end — it is the closing idea, in the same colour as the
warnings, and it is the reason this episode belongs on an AI page rather than a
revision one.

### Verified at import

```
the line is the real least-squares fit    computed, not asserted — returns (8, 38)
every predicted mark is a whole number
every miss is exactly ±2, total 16        in integers
the dots do NOT lie on the line           or there is nothing to fit
the answer at 5 hours is exactly 78
every mark stays inside 0..100            it is a percentage
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *how many hours is enough?* |
| 8–26 | Four students. Hours revised, and what they got. No line fits |
| 26–52 | The line that misses least (total **16**), then **m ← 8** and **b ← 38** |
| 52–82 | **hours ← 5 → 78** — and then *the line knows four people, not you* |
| 82–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

---

## Caption

```
How many hours of revision is enough? There's a formula, and you already know
it.

Four students. Hours revised, and the mark they got:
1 hour → 48
2 hours → 52
3 hours → 60
4 hours → 72

No straight line goes through all four. So you take the line that misses least —
every miss is 2, total 16, and nothing beats it.

That line is:  mark = 8 × hours + 38

Read it. One more hour is worth 8 marks — that's m. With zero hours it starts at
38 — that's b.

So what happens if you do five?

8 × 5 + 38 = 78

And now the part nobody says out loud.

That line knows four people. It does not know you.

Every AI on earth has exactly this problem: it learns a pattern from the data it
was shown, then gets asked about someone who wasn't in it. It will always give
you an answer. That's not the same as being right about you.

Use the line. Don't believe it.

We learned this at school. Nobody ever said what for.

#maths #mathtok #studytok #revision #gcse #ai #machinelearning
```

**YouTube title:** `How many hours of revision is enough? — what the line says`

The searchable line is *"how many hours should I revise"*, which brings the
school audience, and the closing idea is what makes it an AI video.

---

## Subtitle track

`revision_line.srt` — no gaps, no overlaps, asserted at generation.

---

## Changing the data

`MARKS`, `M` and `B` at the top are the only things to edit, and the assertion
recomputes the least-squares fit and checks the line *is* it — the video claims
this is the best line, so the code keeps that true. The 0..100 assertion is
there because a mark is a percentage and a careless edit would quietly put 112
on screen.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl revision_line.py RevisionLine -w -r 1080x1920
python3 cinegrade.py videos/RevisionLine.mp4 revision_line.mp4
```
