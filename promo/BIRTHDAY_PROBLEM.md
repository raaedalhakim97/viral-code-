# 23 people → 50.7%

Episode of **"WHY DID WE LEARN THIS?"**, probability lane. The answer sits
pinned at the **top of the frame** for the whole video.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The idea

How many people in a room before two of them share a birthday? Most
people guess somewhere near 180 — half of 365. The answer is **23**, and
the reason the guess is so far out is that it answers a different
question.

**The mistake is putting yourself in the middle.** Asked about the room,
almost everyone quietly solves *how many before someone matches ME*:

```
you against the other 22   ->   1 - (364/365)^22   =   5.9%
```

That really is tiny. But nobody said it had to be you. **Any** two will
do, and a room of 23 holds

```
23 × 22 / 2  =  253 pairs
```

253 separate chances to collide. Which is why 23 is already past a coin
flip:

```
22 people  ->  47.6%
23 people  ->  50.7%      <- the crossing
50 people  ->  97.0%
70 people  ->  99.9%
```

### Verified at import

```
p(n) computed exactly with Fractions, not from a remembered table
22 is genuinely below 50% and 23 genuinely above — the crossing IS the claim
50.7 / 47.6 / 97.0 / 99.9 all reproduced to one decimal place
253 pairs from comb(23, 2), and the 5.9% "someone matches me" figure
the drawn web is asserted to contain exactly 253 lines
```

---

## Reading the picture

23 dots on a ring. First one dot lights up and sends 22 spokes — that's
the sum you did in your head, and it looks as thin as it is. Then the
spokes clear and all 253 pair-lines draw in. The hairball *is* the
answer: you were counting one dot's lines, the room was counting
everyone's.

The curve at the end is `p(n)` for n = 1…70, with the 50% line marked so
the crossing at 23 is something you can see rather than take on trust.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **how many people before two share a birthday?** → answer pins to the top |
| 8–28 | 23 dots appear. *most people guess a hundred and eighty* |
| 28–42 | one dot, 22 spokes. *you against the other 22: 5.9%* — *but nobody said it had to be YOU* |
| 42–59 | all 253 pair-lines draw. *23 × 22 / 2 = 253 pairs* |
| 59–78 | the curve, 50% line, the marked crossing at 23 → 50.7%. *50 people: 97%. 70: 99.9%* |
| 78–88 | *You counted yourself. The room was counting pairs.* |
| 88–92 | share ask |
| 92–100 | The eye |

---

## Caption

```
How many people in a room before two of them share a birthday?

Most people guess about 180. It's 23.

Here's why the guess is so far off: you solved a different problem. You
asked how many before someone matches YOU — and with 22 other people
that really is tiny, 5.9%.

But nobody said it had to be you. Any two will do.

A room of 23 holds 23 × 22 / 2 = 253 different pairs. Every one of them
is its own chance to collide.

22 people: 47.6%. 23 people: 50.7% — past the coin flip.
50 people: 97%. 70 people: 99.9%.

You counted yourself. The room was counting pairs.

#maths #mathtok #probability #birthdayparadox #fyp
```

**YouTube title:** `23 people is already a coin flip — the birthday problem, drawn`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl birthday_problem.py BirthdayProblem -w -r 1080x1920
python3 cinegrade.py videos/BirthdayProblem.mp4 birthday_problem.mp4
```

## Changing it

`N` is the room size and `N_MAX` the right edge of the curve; the ring,
the web, the pair count and the plotted curve all follow from them.
`p_share()` is exact `Fraction` arithmetic, and the assertions refuse to
build unless N−1 is still below 50% and N still above — so the headline
number on screen can never quietly stop being the crossing point.
