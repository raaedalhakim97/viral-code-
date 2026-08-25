# split. add. insert. — multiply by 11 in your head

Episode 1 of **"MENTAL MATH TRICKS"** — a new sub-series built for plain
language and quick payoff: the trick, a live example, a harder example
that proves it isn't a fluke, then the one-line reason it works. Same
shell: the rule is pinned at the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The trick

For any 2-digit number, split the digits, add them, and drop the sum in
the middle.

```
52 -> 5 | 2 -> 5+2=7 -> 572
52 × 11 = 572. Matches.
```

## The part everyone forgets

If the two digits add to 10 or more, that sum doesn't fit in one slot —
carry the 1 into the left digit.

```
87 -> 8 | 7 -> 8+7=15 -> carry: (8+1) 5 7 -> 957
87 × 11 = 957. Matches.
```

### Verified at import

```
52 * 11 == 572 (no-carry case)     87 * 11 == 957 (carry case)
both trick results match real multiplication exactly
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **split. add. insert.** — *multiply by 11 in your head* |
| 12–44 | 52 → 5\|2 → 7 → 572. Checked against 52×11 |
| 44–96 | 87 → 8\|7 → 15, carry the 1 → 957. Checked against 87×11 |
| 96–117 | *why: 11×n = 10n + n — shift and add* |
| 117–132 | *Try it on any two-digit number. It works every single time.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
Multiply anything by 11 in your head. Split it. Add it. Insert it.

52 → split into 5 and 2. Add them: 5+2=7. Drop it in the middle: 572.
Check it — 52 × 11 = 572. Matches.

Now the part everyone forgets. 87 → 8 and 7. 8+7=15 — too big to fit.
Carry the 1 into the left digit: 9, 5, 7 → 957.
Check it — 87 × 11 = 957. Still matches.

Why? 11 × n is just 10n + n — shift it over, then add. That IS the trick.

Try it on any two-digit number. It works every single time.

#maths #mathtok #mentalmath #lifehacks #mathtricks #satisfying
```

**YouTube title:** `Multiply by 11 in your head — the trick everyone forgets the carry on`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl trick_times_11.py TrickTimes11 -w -r 1080x1920
python3 cinegrade.py videos/TrickTimes11.mp4 trick_times_11.mp4
```

## Changing it

`N1` (no-carry example) and `N2` (carry example) at the top — any 2-digit
numbers. `x11_trick()` is asserted to match real multiplication for both.
