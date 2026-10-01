# EVERY SHOPPER FALLS FOR THIS

Third in the run with `net_vs_gross.py` and `percent_back.py` — same
build, different shape. Two separate items here, rather than one pile
being cut.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio: none.** Ships silent, no voiceover script, no SRT. Still
  beat-locked to 150 BPM if a track ever goes on it.

---

## The trick

The sign says **fifty**. Two things at 20 each:

```
pay 20 + 10  =  30          full price 40
saved 10 of 40              = a quarter, not a half
```

**Half off what?** Half of *one item*, not half of your basket.

## The shape

Cut each item into four. Two items is **eight quarters** on screen. The
deal removes **two** of them — the right half of the second item.

```
item 1            item 2
[][][][]          [][]▓▓          2 of 8  =  25%
```

Two out of eight is countable, which is the whole reason it's drawn that
way rather than asserted in a caption.

## The payoff

Rank the three signs and **the one with the biggest number on it comes
last**:

```
buy 1 get 1 FREE   →   50%
3 for 2            →   33%
buy 1 get 1 half   →   25%     ← the one shouting "50"
```

### Verified at import

```
every figure is exact Fraction arithmetic — nothing typed in by hand
BOGO-half is exactly 1/4 off, 3-for-2 exactly 1/3, BOGOF exactly 1/2
the ranking is asserted, so the payoff cannot silently invert
the saving is price-independent — checked at 3, 7, 19 and 250
two cells of eight is checked to equal the headline fraction
the cells, and the two table columns, are asserted not to collide
```

---

## Structure

| Beats | Time | |
| --- | --- | --- |
| 0–5 | 0:00 | **HOOK.** `BUY ONE GET ONE 50% OFF` → `~50% off~` ✗. *it's twenty-five / and 3-for-2 beats it* |
| 5–14 | 0:02 | **25%** — *that's what you actually save* → pins to the top |
| 14–26 | 0:05 | the sum in the centre: two items 40, pay 20+10 = 30, saved 10 |
| 26–34 | 0:10 | **half off WHAT?** *half of one item. not half of your basket.* |
| 34–62 | 0:13 | eight quarters → the deal takes two → *two out of eight is a quarter* |
| 62–80 | 0:25 | the league table, worst deal boxed in rose |
| 80–88 | 0:32 | *Half off one isn't half off two. The 3-for-2 beats it.* |
| 88–92 | 0:35 | *Send this to whoever does the big shop* |
| 92–100 | 0:37 | The eye |

---

## Caption

```
Every shopper falls for this.

"Buy one get one 50% off" is not 50% off. It's 25%.

Two things at £20. You pay £20 and £10 — thirty for forty quid of stuff.
You saved a tenner out of forty.

Because half off WHAT? Half of one item, not half of your basket.

Cut each item into four. Two items is eight quarters, and the deal takes
two of them. Two out of eight is a quarter.

Now rank the signs. Buy one get one FREE is 50%. Three for two is 33%.
Buy one get one half price is 25%.

The one with the biggest number on it is the worst deal in the shop.

#maths #mathtok #shopping #supermarket #moneysaving #deals #fyp
```

**YouTube title:** `"Buy one get one 50% off" is 25% off — and 3-for-2 beats it`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl bogo_quarter.py BogoQuarter -w -r 1080x1920
python3 cinegrade.py videos/BogoQuarter.mp4 bogo_quarter.mp4
```

## Changing it

`PRICE` and `ITEMS` are the inputs; the paid total, the saving and the
cell counts all derive from them. The three offers live in `TABLE` and
their percentages are computed, not typed — and the ranking is asserted,
so if an edit ever made the loud sign the *best* deal the build would
fail instead of shipping a payoff that isn't true.

**Note on the first render:** the table's labels ran into their
percentages — "buy one get one FREE" overlapped "50%". The labels are
shorter now and the two columns are asserted not to touch.

**Why not the obvious sibling.** "50% off then 20% off is 60%, not 70%"
was the other candidate. It would have been the third video running on
the same *percent of what?* spine as `net_vs_gross` and `percent_back`.
This one has a different shape and a ranking for a payoff, so it doesn't
read as a repeat on the grid.
