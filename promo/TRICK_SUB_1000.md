# 9, 9, 10 — subtract any 3-digit number from 1000, instantly

Episode 5 of **"MENTAL MATH TRICKS"**. Same shell: the rule is pinned at
the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The trick

1000 minus a 3-digit number, with zero borrowing: subtract the first two
digits from 9, and the last digit from 10.

```
1000 - 457:  9-4=5,  9-5=4,  10-7=3  ->  543
1000 - 457 = 543. Matches.
```

A second example, to show it isn't a one-off:

```
1000 - 138:  9-1=8,  9-3=6,  10-8=2  ->  862
1000 - 138 = 862. Matches.
```

### Verified at import

```
1000 - 457 == 543 exactly     1000 - 138 == 862 exactly
both trick results match real subtraction exactly
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **9, 9, 10 — minus each digit** — *subtract from 1000 instantly* |
| 12–44 | 1000−457: 9−4=5, 9−5=4, 10−7=3 → 543. Checked |
| 44–96 | 1000−138: 9−1=8, 9−3=6, 10−8=2 → 862. Checked |
| 96–117 | *why: 999 minus anything never needs to borrow; the +1 lands on the last digit* |
| 117–132 | *No borrowing. No carrying. Instant subtraction from a thousand.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
Subtract any 3-digit number from 1000, instantly. Zero borrowing.

1000 − 457: subtract the first two digits from 9, the last from 10.
9−4=5, 9−5=4, 10−7=3. Put them together: 543.
Check it — 1000 − 457 = 543. Matches.

Try another. 1000 − 138: 9−1=8, 9−3=6, 10−8=2 → 862.
Check it — 1000 − 138 = 862. Still matches. No regrouping, ever.

Why? 999 minus anything never needs to borrow. 1000 = 999 + 1 — that +1
just lands on the last digit.

No borrowing. No carrying. Instant subtraction from a thousand.

#maths #mathtok #mentalmath #lifehacks #mathtricks #satisfying
```

**YouTube title:** `Subtract from 1000 with zero borrowing — the trick nobody taught you`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl trick_sub_1000.py TrickSub1000 -w -r 1080x1920
python3 cinegrade.py videos/TrickSub1000.mp4 trick_sub_1000.mp4
```

## Changing it

`N1` and `N2` at the top — any 3-digit numbers whose last digit isn't 0
(the trick's simplest form assumes no trailing zero). `sub1000_trick()`
is asserted to match real subtraction for both.
