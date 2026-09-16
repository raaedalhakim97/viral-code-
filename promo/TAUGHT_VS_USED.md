# maths they taught you vs maths you actually use

Episode of **"WHY DID WE LEARN THIS?"** — split screen, top half against
bottom half.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## Top half — what they taught you

The quadratic formula, on `x² − 5x + 6 = 0`. Discriminant 1, so
`x = (5 ± 1) / 2` → **x = 2 or 3**. Years of drilling.

> times you've used it since school: 0

## Bottom half — what you actually use

Is the 3-pack cheaper? It looks like it has to be. It isn't.

```
one pack    400 g   £1.60   ->  40p per 100 g
3-pack     1200 g   £5.28   ->  44p per 100 g
```

Three singles cost £4.80. The 3-pack costs £5.28. The "bulk" option costs
**48p more** for the same 1200 g. Bigger is not automatically cheaper, and
the only thing that tells you is the division nobody sat you down and
taught.

### Verified at import

```
discriminant is 1, and both roots satisfy the equation exactly
40p and 44p per 100 g are exact, via Fraction — not rounded for effect
the 3-pack really is the dearer option, by exactly 48p
```

---

## What this video does and doesn't claim

It does **not** claim the quadratic formula is useless, or that multipacks
are always a con — neither would be true, and neither is on screen. The
claim is narrower and fully checkable: *for these numbers* the bigger box
is worse value, and per-unit price is the thing that tells you which is
which. The joke is about what got drilled and what got skipped, not about
one kind of maths being fake.

---

## Structure

| Beats | |
| --- | --- |
| 0–10 | **maths they taught you / vs / maths you actually use** — the split appears |
| 10–36 | Top: the formula, the working, `x = 2 or 3`, and the tally |
| 36–62 | Bottom: 400 g for £1.60 against a 3-pack for £5.28 — *which is cheaper?* |
| 62–100 | 40p per 100 g against 44p. The big box is dearer. *Three singles save you 48p.* |
| 100–120 | *One of these you were drilled on for years. The other, nobody mentioned.* |
| 120–132 | *They drilled you on the hard one. The shop is counting on the easy one.* |
| 132–138 | *Send this to someone who buys the big box* |
| 138–150 | The eye |

---

## Caption

```
Maths they taught you vs maths you actually use.

Top: the quadratic formula. x² − 5x + 6 = 0, so x = 2 or 3. Years of
drilling. Times you've used it since school: be honest.

Bottom: one pack is 400g for £1.60. The 3-pack is £5.28. Which is cheaper?

The single works out at 40p per 100g. The 3-pack works out at 44p.

The big box is the expensive one. Buying three singles saves you 48p for
exactly the same 1200 grams.

Bigger isn't automatically cheaper. The only thing that tells you is one
division — and that's the bit nobody ever taught.

They drilled you on the hard one. The shop is counting on the easy one.

#maths #mathtok #moneysaving #supermarket #school #fyp
```

**YouTube title:** `They taught you the quadratic formula. They skipped the one that saves you money.`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl taught_vs_used.py TaughtVsUsed -w -r 1080x1920
python3 cinegrade.py videos/TaughtVsUsed.mp4 taught_vs_used.mp4
```

## Changing it

`SINGLE_G/SINGLE_P` and `PACK_G/PACK_P` are grams and pence. The
assertions recompute both per-100g figures as exact `Fraction`s and refuse
to build unless the multipack is genuinely the dearer one — so the twist
can't quietly invert while the caption still says it holds. `A, B, C` set
the quadratic; its roots are checked back through the equation.
