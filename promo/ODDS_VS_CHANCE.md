# 4 to 1 = 1 in 5 = 20%

Episode of **"WHY DID WE LEARN THIS?"**, probability lane. The answer sits
pinned at the **top of the frame** for the whole video.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The idea

Odds and chances are two different numbers and almost everyone reads one
as the other. **"Four to one against"** counts the ways to *lose* against
the ways to *win*. Four to one. So there are **five** outcomes in total,
and the winning one is one of five.

```
a to b against   ->   b / (a + b)

4 to 1   ->   1 / 5   =   20%        (not 1 in 4 = 25%)
```

Read it as 1 in 4 and you've overrated your own bet by a quarter.

## The payoff — the board doesn't add up

Convert a whole bookmaker's board that way:

```
1 to 1   ->   50%
3 to 1   ->   25%
4 to 1   ->   20%
9 to 1   ->   10%
             -----
             105%
```

Exactly one runner can win, so the real chances have to sum to 100. The
extra **five points** is the margin — the same 5 that makes a book a
business. It isn't hidden anywhere; it's printed on the board in a unit
nobody converts.

### Verified at import

```
4 to 1 converts to Fraction(1, 5) exactly — not rounded for effect
the four board prices sum to Fraction(21, 20), i.e. exactly 105%
the edge is exactly Fraction(1, 21) = 4.76% of everything staked
a genuinely fair book (1/1, 2/1, 5/1) is checked to sum to exactly 1
```

---

## What this video does and doesn't claim

It does **not** claim bookmakers are cheating — an overround is openly how
the business is priced, and a book that summed to exactly 100% would make
nothing. The claim is narrower and fully checkable: odds are not chances,
the conversion is `b/(a+b)`, and running it across a board makes the
margin visible. Nothing here is a betting tip.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **"4 to 1 — so that's a 1 in 4 shot, right?"** → answer pins to the top |
| 8–30 | four LOSE boxes, then one WIN box. *five outcomes, not four* |
| 30–42 | *1 in 5 = 20%, not 1 in 4 = 25%* — the rule is `b / (a + b)` |
| 42–63 | a whole board converted: 1/1→50%, 3/1→25%, 4/1→20%, 9/1→10% |
| 63–80 | the bar overshoots the 100% mark. *50 + 25 + 20 + 10 = 105%* — the 5% they keep |
| 80–88 | *Odds count the ways to lose. Chances count everything.* |
| 88–92 | share ask |
| 92–100 | The eye |

---

## Caption

```
"4 to 1" — so that's a 1 in 4 shot, right?

No. Odds count the ways to LOSE against the ways to WIN. Four ways to
lose, one way to win — that's five outcomes, not four.

1 in 5 = 20%. Not 25%. The rule is b / (a + b).

Now run it across a whole board. 1/1 is 50%. 3/1 is 25%. 4/1 is 20%.
9/1 is 10%.

Add them up: 105%.

Only one of them can win, so the real chances have to total 100. Those
extra 5 points are the margin — printed on the board, in a unit nobody
converts.

#maths #mathtok #probability #odds #fyp
```

**YouTube title:** `"4 to 1" is not 1 in 4 — and the board adds up to 105%`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl odds_vs_chance.py OddsVsChance -w -r 1080x1920
python3 cinegrade.py videos/OddsVsChance.mp4 odds_vs_chance.mp4
```

## Changing it

`BOOK` holds the four prices. Every percentage on screen is recomputed
from it with `Fraction`, and the assertions refuse to build unless the
four shares still total exactly 105% — so the payoff line can't drift
out of step with the bars while the caption still says 105.
