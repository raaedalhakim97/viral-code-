# even ÷2 · odd ×3+1 — the rule nobody can prove

**"SATISFYING MATH"** episode — entertainment lane. Built to be watched.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The rule, and it is the whole rule

```
even  ->  halve it
odd   ->  triple it and add one
```

Start anywhere. You land on 1.

```
6  ->  3, 10, 5, 16, 8, 4, 2, 1                    8 steps
27 ->  ... climbs to 9,232 ...                   111 steps
```

27 is the one worth watching: it doesn't creep down, it goes *up* to nine
thousand two hundred and thirty-two first, thrashing the whole way, and
still lands on 1.

Every number anyone has ever tried lands on 1. Nobody has proved it always
does — open since 1937. Erdős: *"mathematics is not yet ready for such
problems."*

### Verified at import

```
the two headline paths are recomputed from the rule, not hard-coded
27's step count and peak are exactly 111 and 9232
a brute-force sweep confirms every start from 1 to 100000 reaches 1
every plotted path ends on the value 1
```

---

## Reading the picture

`y` is `log10(value)` — without the log, 27's peak of 9,232 would flatten
every other path into the baseline. `x` is progress along the path, and
every path is drawn spanning the full width so all 99 of them stay
visible and converge on the same point.

The first cut right-aligned the paths on absolute step count instead. It
looked wrong: 27 is nearly 4× longer than a typical path, so the other 98
collapsed into a sliver at the right edge and "ninety-nine starts" read as
about two. Normalising each path to the full width fixed it, and matches
how 27 was already drawn in the stage before.

---

## Structure

| Beats | |
| --- | --- |
| 0–10 | **"pick any number."** — even ÷2, odd ×3+1 |
| 10–34 | 6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1, one number at a time |
| 34–76 | 27's path draws itself: up to 9,232, then down to 1. *111 steps.* |
| 76–120 | 99 starting numbers at once, braiding into a single point |
| 120–132 | *Every number ever tried lands on 1. Nobody has proved it always does.* |
| 132–138 | *Comment a number and I'll run it* |
| 138–150 | The eye |

---

## Caption

```
Pick any number. Even? Halve it. Odd? Triple it and add one. Repeat.

Start with 6: 3, 10, 5, 16, 8, 4, 2, 1. Eight steps, done.

Now try 27. It doesn't go down — it climbs. All the way to nine thousand
two hundred and thirty-two, thrashing the whole way.

111 steps later: 1.

Ninety-nine different starting numbers. Every single one ends in the same
place.

Every number anyone has ever tested lands on 1. Nobody has proved it
always does. It's been open since 1937.

Comment a number and I'll run it.

#satisfying #oddlysatisfying #collatz #maths #unsolved #fyp
```

**YouTube title:** `The simplest unsolved problem in maths — even ÷2, odd ×3+1`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl collatz.py Collatz -w -r 1080x1920
python3 cinegrade.py videos/Collatz.mp4 collatz.mp4
```

## Changing it

`MANY` sets which starting numbers make up the fan. The brute-force sweep
at import is the slow part (~a second); lower its ceiling if iteration
speed matters. The assertions refuse to build if any plotted path fails to
end on 1, or if 27's headline numbers stop being 111 and 9232.
