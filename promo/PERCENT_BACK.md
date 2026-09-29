# EVERY PAY CUT GETS THIS WRONG

Sequel to `net_vs_gross.py` — same build, same spine (*percent of
what?*), different trick.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The trick

Your pay is cut 20%. A year later they put 20% back. Everyone expects to
be at 1,000 again.

```
1,000  − 20%  =  800
  800  + 20%  =  960        ← 40 short, every time
```

**20% of what?** It came *off* 1,000 and went back *onto* 800. The second
percentage is a percentage of a smaller pile.

## The shape

Cut the 1,000 into **ten blocks of a hundred**.

```
20% off     takes two WHOLE blocks       →  8 blocks
20% back    is 20% of 800 = 160          →  1.6 blocks
```

**Two blocks out. One point six back.** The missing four tenths of a
block is the 40, and it sits on screen in rose to be counted.

## The stake

To undo a cut you always need a *bigger* rise than the cut:

```
down 10%  →  up 11.11%        down 20%  →  up 25%
down 25%  →  up 33.33%        down 50%  →  up 100%
```

### Verified at import

```
every figure is exact Fraction arithmetic — nothing typed in by hand
the shortfall is exactly 40, which is exactly 4% of 1,000
the order doesn't matter: +20% then −20% lands on 960 too
the recovery rise is p/(1−p), checked at 10/20/25/50/90%
+25% on 800 is checked to land back on exactly 1,000
the gap is always exactly r² — 20% → 0.04 → 4%
two blocks out minus 1.6 back is checked to equal the 40 on screen
the blocks are asserted to fit the platform safe box
```

---

## Structure

| Beats | Time | |
| --- | --- | --- |
| 0–5 | 0:00 | **HOOK.** `1,000 − 20% + 20%` → `~1,000~` ✗. *this costs you 40 / every single time* |
| 5–14 | 0:02 | **960** — *that's what you actually get back* → pins to the top |
| 14–26 | 0:05 | the sum runs in the centre: −20% → 800, +20% → 960 ✗ |
| 26–34 | 0:10 | **20% of WHAT?** *it came off 1,000. it went back onto 800.* |
| 34–62 | 0:13 | ten blocks → two whole blocks leave → only 1.6 come back |
| 62–80 | 0:25 | the gap lights up. *200 out, 160 back.* *you need +25%, not 20* |
| 80–88 | 0:32 | *Down 20% needs up 25%. Down 50% needs up 100%.* |
| 88–92 | 0:35 | *Send this to anyone who took a pay cut* |
| 92–100 | 0:37 | The eye |

---

## Caption

```
Every pay cut gets this wrong.

They cut your pay 20%. A year later they put 20% back. You are not back
where you started — you're on 960.

Because 20% of WHAT? It came off 1,000 and it went back onto 800.

Cut the 1,000 into ten blocks of a hundred. The cut takes two whole
blocks. The rise gives you 20% of 800 — one point six blocks.

Two out, one point six back. That missing bit is your 40.

To actually get back to 1,000 you need +25%, not +20%.

Down 20% needs up 25%. Down 50% needs up 100%.

#maths #mathtok #percentages #pay #salary #money #finance #fyp
```

**YouTube title:** `Down 20% then up 20% doesn't get you back — here's the gap`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl percent_back.py PercentBack -w -r 1080x1920
python3 cinegrade.py videos/PercentBack.mp4 percent_back.mp4
```

## Changing it

`PAY` and `RATE` are the only inputs; the block count, the two block
figures and every amount are derived. Set `RATE = 50/100` and the shape
redraws as five blocks out and 2.5 back. The assertions refuse to build
unless the blocks still account for the shortfall exactly and the row
still fits the safe box.

**Note on the first render:** the blocks were 0.62 tall and the missing
0.4 of a block — the whole point of the video — came out as a sliver
about 25px wide and barely readable. They're 1.40 tall now, and the
returned blocks moved from green to blue so they separate from the gold
at a glance.
