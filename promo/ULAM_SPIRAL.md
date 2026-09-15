# 49% prime — the lines nobody can explain

**"SATISFYING MATH"** episode — entertainment lane. Built to be watched.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The setup

Write 1, 2, 3, 4, … in a square spiral. Mark every prime.

```
17 16 15 14 13
18  5  4  3 12
19  6  1  2 11
20  7  8  9 10
21 22 23 24 25
```

Primes are supposed to be the unpredictable ones — no formula generates
them, the gaps between them are erratic. So the marks should look like
noise. They don't. They fall onto clear diagonal lines.

Stanisław Ulam noticed this in 1963, doodling through a boring talk.

## The numbers on screen

```
45 × 45 spiral  =  2025 numbers,  306 of them prime   ->  15.1% overall
the diagonal x + y = -2  runs 43 cells, holds 21 primes ->  48.8%
```

That one line is **more than three times** as prime-dense as the grid
average. And it isn't cherry-picked from a handful of candidates — it's
the longest of several diagonals that all run well above the background
rate.

### Verified at import

```
every spiral cell is distinct                 the walk never repeats itself
the 5x5 layout matches the standard Ulam arrangement
306 primes below 2025, 21 of them on the highlighted diagonal
the highlighted diagonal really is >3x the overall prime density
```

---

## One thing I got wrong first

The original plan was to highlight Euler's polynomial `n² + n + 41` —
famously prime for n = 0…39 — as *the* diagonal. Checked it before
building: those 40 values land on **28 different diagonals**, not one.
The quadratics that do run along Ulam diagonals have the form
`4n² + bn + c`; Euler's doesn't, so it scatters. Replaced with the
empirically densest long diagonal, measured directly from the grid.

(The Euler fact is still true and still checked in this repo — 41, 43,
47, … 1601, all prime, breaking at n = 40 where the value is 41². It just
isn't a straight line here.)

---

## Structure

| Beats | |
| --- | --- |
| 0–10 | **"primes aren't random."** — write them in a spiral |
| 10–40 | The 5×5 spiral with real numbers, then the primes light up |
| 40–100 | Scale to 2025 numbers, 306 prime dots bloom in — the diagonals appear |
| 100–120 | One diagonal highlighted: *21 of its 43 numbers are prime* → **49% prime. average: 15%.** |
| 120–132 | *Nobody knows why the lines are there. Sixty years, still open.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
Primes aren't random. Write them in a spiral and the lines show up.

1, 2, 3, 4 — spiralling outward. Now light up every prime.

Do it for two thousand numbers and something strange happens. Primes are
supposed to be the unpredictable ones. No formula makes them. The gaps
between them are a mess.

So why are they sitting on diagonals?

Take one of those lines: 21 of the 43 numbers on it are prime. That's 49%.
The average across the whole grid is 15%.

Stanislaw Ulam spotted this in 1963, doodling through a boring talk.
Sixty years later nobody can explain it.

#satisfying #oddlysatisfying #primes #maths #numbertheory #fyp
```

**YouTube title:** `Primes fall on straight lines and nobody knows why`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl ulam_spiral.py UlamSpiral -w -r 1080x1920
python3 cinegrade.py videos/UlamSpiral.mp4 ulam_spiral.mp4
```

## Changing it

`SIDE` sets the grid (45 → 2025 numbers) and `DIAG_C` picks the
highlighted diagonal. The assertions recount the primes and the diagonal's
hit rate and refuse to build if the on-screen percentages stop matching,
so the numbers in the caption can't drift away from the picture.
