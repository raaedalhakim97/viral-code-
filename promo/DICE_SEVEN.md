# P(7) = 6/36 = 1/6 — why seven is the number

Episode of **"WHY DID WE LEARN THIS?"**, probability lane. The answer sits
pinned at the **top of the frame** for the whole video.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The idea

Two dice give eleven possible totals — 2 through 12 — so it *feels* like
eleven options with a roughly equal shout. It isn't, because the dice
don't roll totals. They roll **pairs**, and there are 36 of them, every
one equally likely.

```
          1    2    3    4    5    6
    1     2    3    4    5    6    7
    2     3    4    5    6    7    8
    3     4    5    6    7    8    9
    4     5    6    7    8    9   10
    5     6    7    8    9   10   11
    6     7    8    9   10   11   12
```

Seven fills a whole diagonal. Twelve gets one corner.

```
 7  ->  1+6  2+5  3+4  4+3  5+2  6+1     6 of 36  =  1/6  =  16.7%
12  ->  6+6                              1 of 36         =   2.8%
```

**Seven turns up six times as often as twelve.** Stack all 36 pairs by
total and you get a hill with 7 at the peak: 1, 2, 3, 4, 5, **6**, 5, 4,
3, 2, 1.

### Verified at import

```
all 36 ordered pairs enumerated from the rules, not typed in
the eleven counts are 1,2,3,4,5,6,5,4,3,2,1 and sum to 36
P(7) == Fraction(1, 6) exactly
7 has strictly more ways than every other total
the 7:12 ratio is exactly 6
```

---

## Why the picture is a 6×6 grid

The grid *is* the argument. Once you see 36 cells instead of 11 totals,
the answer stops needing a formula — you can count the gold diagonal.
The histogram afterwards is just the same 36 cells restacked, so nothing
new is being asserted, only re-shown.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | two dice. **which total should you bet on?** → answer pins to the top |
| 8–28 | the 6×6 grid builds. *the dice don't roll sums, they roll pairs* |
| 28–52 | the six 7s light up: 1+6 2+5 3+4 4+3 5+2 6+1 — *6 out of 36 = 1/6 = 16.7%* |
| 52–63 | 6+6 lights up alone. *one pair out of 36 = 2.8%* — 7 is six times as common |
| 63–78 | the 36 pairs restack into a hill: 1 2 3 4 5 **6** 5 4 3 2 1 |
| 78–88 | *Eleven sums. Thirty-six rolls. That's the whole trick.* |
| 88–92 | share ask |
| 92–100 | The eye |

---

## Caption

```
Roll two dice. Which total should you bet on?

The totals run 2 to 12 — eleven of them. But the dice don't roll totals,
they roll pairs, and there are 36 pairs.

Six of them make 7: 1+6, 2+5, 3+4, 4+3, 5+2, 6+1. That's 6 out of 36 =
1/6 = 16.7%.

Twelve needs 6+6. One pair out of 36 = 2.8%.

Seven comes up SIX TIMES as often as twelve.

Stack all 36 by total and you get a hill: 1, 2, 3, 4, 5, 6, 5, 4, 3, 2, 1.
Seven is the top of it. Every board game already knew.

#maths #mathtok #probability #dice #boardgames #fyp
```

**YouTube title:** `Why 7 is the most likely roll — the 36-square grid that explains it`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl dice_seven.py DiceSeven -w -r 1080x1920
python3 cinegrade.py videos/DiceSeven.mp4 dice_seven.mp4
```

## Changing it

Nothing about the dice is hard-coded — `ROLLS` is `product(range(1,7),
repeat=2)` and every count comes off it. Change the die size and the
counts, the grid, the highlighted diagonal and the histogram all follow,
but the assertions will refuse to build if 7 stops being the unique peak
or the 7:12 ratio stops being exactly 6, because the video says both out
loud.
