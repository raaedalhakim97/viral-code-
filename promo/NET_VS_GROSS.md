# net = gross ÷ 1.05

Episode of **"WHERE MATH ACTUALLY GETS USED"**. The answer sits pinned at
the **top of the frame** for the whole video.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The idea

You're handed **40,000, tax included at 5%.** What's the net?

Almost everyone takes 5% off the 40,000:

```
40,000 × 5%   =  2,000
40,000 − 2,000  =  38,000          <- wrong
```

**The test that settles it costs nothing: put the tax back on.**

```
38,000 × 1.05  =  39,900           100 short
```

You started at 40,000. The round trip doesn't close, so 38,000 was never
the net. The 5% was never 5% *of the 40,000* — it is 5% **of the net**,
and the gross is already 105% of the net. So you divide:

```
40,000 ÷ 1.05  =  38,095.238…   ->  38,095.24
tax            =   1,904.76         not 2,000
```

And the trip closes exactly:

```
38,095.24 × 1.05  =  40,000.00     ✓
```

## The part worth putting on screen

The tax is **1/21 of the gross, not 1/20.** Subtracting 5% overstates it
by 95.24 on this one invoice — and it scales:

```
gross      1,000   ->   net       952.38    overpaid      2.38
gross     40,000   ->   net    38,095.24    overpaid     95.24
gross  1,000,000   ->   net   952,380.95    overpaid  2,380.95
```

### Verified at import

```
every figure is exact Fraction arithmetic — nothing typed in by hand
the wrong net really does come back exactly 100 short
the right net really does round-trip to exactly 40,000
38,095.24 and 1,904.76 are the true cent-roundings of 800000/21 and 40000/21
the round trip still closes at cent precision: 38,095.24 × 1.05 = 40,000.00
tax / gross == Fraction(1, 21)
```

---

## Why the picture is a chain of boxes

The argument *is* a round trip, so the video draws one: 40,000 goes down
an arrow, gets a value, then goes down another arrow labelled `× 1.05`
and has to land back where it started. The wrong path lands on 39,900
with a cross beside it; the right path lands on 40,000.00 with a tick.
Nothing else needs explaining — you can see which chain closes.

The two amounts differ by less than a quarter of a percent, so a
proportional bar chart would have shown two identical-looking bars. The
chain shows the *test* instead of the size, which is the actual lesson.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **40,000, tax included at 5%. what's the net?** → formula pins to the top |
| 8–26 | `40,000 × 5% = 2,000`, `− 5%` → **38,000**. *looks finished. it isn't.* |
| 26–46 | `× 1.05` → **39,900** ✗. *100 short — so 38,000 was never the net* |
| 46–64 | `÷ 1.05` → **38,095.24**. tax 1,904.76, not 2,000. *the gross is already 105% of the net* |
| 64–78 | `× 1.05` → **40,000.00** ✓. *the tax is 1/21 of the gross. not 1/20.* |
| 78–88 | *Subtracting takes 5% of the gross. The tax was 5% of the net.* |
| 88–92 | share ask |
| 92–100 | The eye |

---

## Caption

```
40,000, tax included at 5%. What's the net?

Almost everyone takes 5% off: 40,000 − 2,000 = 38,000.

Test it for free — put the tax back on. 38,000 × 1.05 = 39,900.

You started at 40,000. It's 100 short. The round trip didn't close, so
38,000 was never the net.

The 5% was never 5% of the 40,000. It's 5% OF THE NET — and the gross is
already 105% of the net. So you divide.

40,000 ÷ 1.05 = 38,095.24. Tax 1,904.76, not 2,000.

38,095.24 × 1.05 = 40,000.00. Straight back. That's how you know.

The tax is 1/21 of the gross, not 1/20. On a million, subtracting hands
over 2,380.95 too much.

#maths #mathtok #tax #vat #smallbusiness #accounting #fyp
```

**YouTube title:** `You can't take 5% off a 105% number — net vs gross, settled in one test`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl net_vs_gross.py NetVsGross -w -r 1080x1920
python3 cinegrade.py videos/NetVsGross.mp4 net_vs_gross.mp4
```

## Changing it

`GROSS` and `RATE` are the only inputs; every amount on screen is derived
from them with `Fraction`. Change the rate to 20% (VAT) and the whole
chain follows. The assertions refuse to build unless the wrong path still
falls short and the right path still round-trips exactly — so the video
can't end up showing a tick beside a number that doesn't close.

**Not tax advice.** It's one arithmetic identity: when a figure is
tax-inclusive, you divide by `1 + rate`, you don't subtract `rate`.
