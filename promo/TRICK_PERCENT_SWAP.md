# x% of y = y% of x — percentages you can flip

Episode 4 of **"MENTAL MATH TRICKS"**. Same shell: the rule is pinned at
the **top of the frame for the whole video**.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The trick

"8% of 50" sounds annoying. Flip it: "50% of 8" is instant — that's just
half of 8. They give the exact same answer, always.

```
8% of 50  ==  50% of 8  ==  4
```

A harder pair, same flip:

```
4% of 75  ==  75% of 4  ==  3
```

### Verified at import

```
8% of 50 == 50% of 8 == 4 exactly
4% of 75 == 75% of 4 == 3 exactly
```

---

## Structure

| Beats | |
| --- | --- |
| 0–12 | **x% of y = y% of x** — *percentages you can flip* |
| 12–44 | 8% of 50 → flip → 50% of 8 = 4. Checked both ways |
| 44–96 | 4% of 75 → flip → 75% of 4 = 3. Checked both ways |
| 96–117 | *why: both are just x/100 × y — order never matters* |
| 117–132 | *Flip it to whichever number is easier. The answer never changes.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
Percentages you can flip. x% of y always equals y% of x.

8% of 50 sounds annoying. Flip it: 50% of 8. 50% is just half — half of 8
is 4. Check it — 8% of 50 = 4 too. Exact same answer.

Try harder numbers. 4% of 75 → flip → 75% of 4. Three quarters of 4 is 3.
Check it — 4% of 75 = 3 too. Still exact.

Why? Both are just x/100 times y. Multiplication doesn't care which side
is the percent.

Flip it to whichever number is easier. The answer never changes.

#maths #mathtok #mentalmath #lifehacks #mathtricks #percentages #satisfying
```

**YouTube title:** `The percentage trick that makes hard math instant`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl trick_percent_swap.py TrickPercentSwap -w -r 1080x1920
python3 cinegrade.py videos/TrickPercentSwap.mp4 trick_percent_swap.mp4
```

## Changing it

`X1, Y1` and `X2, Y2` at the top — any numbers. `pct_of()` uses exact
`Fraction` arithmetic and is asserted symmetric (`pct_of(x,y) == pct_of(y,x)`)
for both pairs.
