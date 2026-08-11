# y = mx + b Predicts Tomorrow — video brief

Companion to `sales_line.py`. Fourth in the ladder family after
`circle_ladder.py`, `square_ladder.py` and `sine_unroll.py`, on the same shell:
**one picture, six rungs, nothing ever added — only named.**

- **Output:** 1080×1920, 60fps, **28.800000s** — 72 beats = 18 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## The angle

Everyone was made to memorise `y = mx + b`, and almost nobody was told what it
was *for*. This video gives it one job — **guess tomorrow's sales** — and does
it on a single set of axes with seven dots.

It is also the honest bridge to the rest of the page: this is linear
regression, the first model in every machine-learning course, and the affine
part of a neural network layer is the same expression with matrices in it.

---

## One picture, six rungs

```
day     1   2   3   4   5   6   7
sales  12  15  14  19  21  20  25
```

| | | |
| --- | --- | --- |
| **1** | the axes | `y = mx + b` — x is the day, y is the sales |
| **2** | seven dots | one per day, and that is all the data there is |
| **3** | **b** | where the line starts — day zero, `b = 10` |
| **4** | **m** | one day along, two sales up — `m = rise ÷ run = 2` |
| **5** | the line | `y = 2x + 10`, the one that misses by the least |
| **6** | **the prediction** | run it one day further: day 8 → `2(8) + 10` = **26** |

---

## The fit is real, and it comes out exact

The seven points are not decoration. The least-squares line through them is
`y = 2x + 10` with **no rounding anywhere**, so every number said on screen is
the true answer rather than a convenient one:

```
mean day 4      mean sales 18
Sxy = 56        Sxx = 28        m = 56/28 = 2        b = 18 − 2·4 = 10
residuals:  0, +1, −2, +1, +1, −2, +1      →  they sum to exactly 0
```

Residuals summing to zero is not a coincidence — it is what "best fit" *means*,
and it is why the line can be called the best one without hedging.

### Verified at import

```
m == 2 and b == 10                    exactly, and cross-checked against np.polyfit
residuals sum to 0                    exactly
no nearby (m, b) fits better          40,401-point grid around the answer
the prediction at day 8 is 26         exactly
```

The scene raises rather than renders if any of those stop holding, so the data
cannot be edited into saying something the arithmetic does not.

### The one claim not derived on screen

The closing line — *a neural net layer is still `y = Wx + b`* — is a statement
about how those models are built, not something the video proves. It is true of
the affine part of a standard layer, and it is the only sentence in the video
that isn't computed in front of you.

---

## Three things worth keeping

**A label that lands on an axis tick reads as a duplicate.** The `b` marker sat
at the same height as the grey `10` on the y-axis and half a unit to its left,
so the frame showed "10  10". It now sits *inside* the plot, up and right of the
gold dot.

**Residuals two sales tall are invisible in the page's blue.** The whole of rung
5 turns on seeing that no line touches every dot. At `#5E81AC` and 2.6 wide the
sticks vanished against black; they are drawn at `#88C0D0` and 4.4 now.

**The closing line needs beats of its own.** *A neural net layer is still
y = Wx + b* is the reason the video exists, and in the first cut it arrived on
the very last beat of the takeaway and faded 0.4s later. Rung 6 gives up two
beats so the line holds for two clear ones. The payoff equation `= 26 sales`
is never cleared at all — the takeaway keeps it and fades everything else, so
it sits above the closing lines for nearly four seconds.

**The prediction needs the plot to have room to its right.** The axes run to day
9 with data only to day 7, so the dashed extension and the landing dot at day 8
have somewhere to go. If the axes stopped at the data, the payoff would happen
in the margin.

---

## Caption

```
y = mx + b. They made you memorise it. Nobody said what it was for.

Here's what it's for.

A small shop. Seven days of sales: 12, 15, 14, 19, 21, 20, 25.
Put them on a graph — x is the day, y is the sales. Seven dots.

b is where the line STARTS. Before day one you were already selling 10. So
b = 10.

m is how fast it CLIMBS. Go one day along, the line goes 2 sales up.
m = rise ÷ run = 2.

So the line is y = 2x + 10.

No straight line touches all seven dots. This is the one that misses by the
least — that's the whole idea of a "line of best fit". Nothing more mysterious
than that.

Now the part school skipped. Run the same line ONE DAY FURTHER.

Day 8 → 2(8) + 10 = 26

That's tomorrow's sales. That's a prediction, and you just made it with year-9
maths.

This is called linear regression. It's the first model in every AI course on
earth — and inside a neural network, every layer is still y = Wx + b.

You already learned it. Nobody told you it was AI.

#maths #mathtok #algebra #ai #machinelearning #linearregression #gcse #studytok
```

The first line is the searchable one — *"what is y = mx + b used for"* and
*"what is a line of best fit"* are both typed queries with a school audience
behind them, and *"linear regression explained"* brings the AI audience to the
same video.

**YouTube title:** `y = mx + b — the school formula that predicts tomorrow`

---

## Subtitle track

`sales_line.srt` — 9 cues, no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the data

`DAYS`, `SALES` and `AHEAD` at the top are the only things to edit — m, b, the
prediction, every label and every assertion follow from them. The assertions
pin the *current* answers (`m == 2`, `b == 10`, `PRED == 26`), so new data means
updating those three lines too; that is deliberate, because it forces whoever
changes the numbers to look at what the fit actually became.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl sales_line.py SalesLine -w -r 1080x1920
python3 cinegrade.py videos/SalesLine.mp4 sales_line.mp4
```
