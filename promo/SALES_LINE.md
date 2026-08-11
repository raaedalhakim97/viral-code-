# y = mx + b — What Is It For? — video brief

Companion to `sales_line.py`. **Episode 1 of "WHY DID WE LEARN THIS?"** — the
page series about the maths everybody was made to memorise and nobody was told
the use of.

- **Output:** 1080×1920, 60fps, **28.800000s** — 72 beats = 18 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## The series

The series name sits in the header for the whole video, so every episode reads
as part of one thing:

> **WHY DID WE LEARN THIS?**

The shape of every episode is the same and it is the shape the audience asked
for in the comments: *"we did these equations in school but I never took the
time to look at them this way."*

| | |
| --- | --- |
| **Hook** | the formula, and the question everyone had — *what is it FOR?* |
| **Middle** | one picture, one new number per rung |
| **Close** | *We learned this at school. Nobody ever said what for.* |

Candidates for the next episodes, all with the same three-part shape:

| formula | what it was for |
| --- | --- |
| `a² + b² = c²` | how your phone knows how far away something is |
| percentages | what "20% off, then 10% off" actually costs |
| `πr²` | why a 16-inch pizza is nearly twice a 12-inch |
| standard deviation | why "average" hides everything that matters |
| `(a+b)²` | already shipped as `square_ladder.py` |

---

## One picture, five rungs

```
day     1    2    3    4          (and 5, which is the whole point)
sales  30   40   50   60
```

| | | |
| --- | --- | --- |
| **1** | four dots | a shop, four days. That is all the data. |
| **2** | the step | ten more, every day, always ten → **m = 10** |
| **3** | run it back | join the dots, follow the line back past day one → **b = 20** |
| **4** | together | `y = 10x + 20` — the step and the start |
| **5** | one day further | day 5 → `10×5 + 20` = **70** |

---

## What changed from the first cut, and why

The first version used **seven** days of realistic, wobbly sales
(12, 15, 14, 19, 21, 20, 25) and spent a whole rung on least squares —
residuals, *"the line that misses by the least"*, all of it. Every word was
true. It was also **hard**, and it put a dozen numbers on screen at once: seven
data values, three axis labels, m, b and the prediction, all competing.

This cut fixes that with three rules:

1. **Four data points, not seven.**
2. **One new number per rung**, and each rung's numbers are cleared before the
   next arrives — the four sales values fade the moment the step arrows appear,
   the arrows fade before the line is drawn, the `b` marker fades before the
   prediction.
3. **No y-axis numbers at all.** The dots carry their own values while they need
   them. The only permanent numbers are the day ticks 1–5.

**The dots sit exactly on the line**, so least squares never has to be
explained. The shop's sales go up by ten a day because that is the setup, not a
claim about how shops behave. Real data is messier and the idea is identical —
that is a fine follow-up episode, not this one.

### Verified at import

```
every point is exactly on the line     s == 10d + 20, in integers
every step is exactly +10              which is the claim rung 2 makes
STEP == M                              the visible step IS the slope
least squares returns (10, 20)         the fit is computed, not asserted
the prediction at day 5 is 70          exactly
```

`least_squares()` is the real calculation, kept even though the data is clean —
so the file still contains the honest machinery, and swapping in messier data
would produce a real answer rather than a broken one.

---

## Three things worth keeping

**Numbers on screen are a budget, not a detail.** The single biggest fix here
was not wording, it was *deleting numbers*. If a viewer has to work out which
number is which, the maths never gets a chance.

**A staircase explains slope better than a formula does.** Three L-shaped steps
between the dots, each labelled `+10`, say "rise over run" without either word.
Rung 2 never uses the term.

**The closing line needs beats of its own.** *Nobody ever said what for* is the
whole point of the series, and it gets two clear beats before anything fades.
The payoff equation `= 70` is never cleared — the takeaway keeps it and fades
everything else, so it sits above the closing lines.

---

## Caption

```
y = mx + b. You wondered what it was for. Nobody ever told you.

Here it is.

A small shop. Four days: 30, 40, 50, 60 sales. Four dots on a graph — x is the
day, y is the sales.

Look at the step from one day to the next. +10. +10. +10. It never changes.

THAT is m. m = 10.

Now join the dots — one straight line — and run it backwards, past day one, to
where it started. 20.

THAT is b. b = 20.

So the line is y = 10x + 20.

Now the bit school skipped. Run it ONE MORE DAY.

Day 5 → 10×5 + 20 = 70

That's tomorrow. You just predicted the future with year-9 maths.

(And this is the first model in every AI course on earth. It's called linear
regression.)

We learned this at school. Nobody ever said what for.

#maths #mathtok #algebra #gcse #studytok #ai #linearregression
```

The AI line is in brackets on purpose — it is a bonus for the people who care,
not the point of the video. The point is the last line.

**YouTube title:** `y = mx + b — what was it actually for?`

---

## Subtitle track

`sales_line.srt` — 8 cues, no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the data

`DAYS`, `SALES` and `AHEAD` at the top are the only things to edit. The
assertions pin the current answers, so new data means updating them too — which
is deliberate, because it forces whoever changes the numbers to look at what the
fit became. Keep the values on the line and the steps equal, or rung 2's claim
stops being true and the assertion will say so.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl sales_line.py SalesLine -w -r 1080x1920
python3 cinegrade.py videos/SalesLine.mp4 sales_line.mp4
```
