# 47500 ÷ 234 — video brief

Companion to `no_calculator.py`. A division that looks like calculator work,
done on paper in nineteen seconds.

- **Output:** 1080×1920, 60fps, **48.000000s** — 120 beats = 30 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## The maths, verified

```
475 ÷ 234  →  2  remainder   7      234 × 2 = 468,  475 − 468 =   7
 70 ÷ 234  →  0  remainder  70      234 does not fit in 70
700 ÷ 234  →  2  remainder 232      234 × 2 = 468,  700 − 468 = 232

47500 ÷ 234 = 202 remainder 232
232 / 234   = 0.99145…
47500 / 234 = 202.991452991…
```

Every figure on screen was computed and checked, not estimated.

---

## Why *this* division

A quotient of 202.99 is unremarkable, and "here is long division" is not a
video. What makes this one worth 48 seconds is that the method contains its own
punchline.

At the `700 ÷ 234` step you test **234 × 3 = 702** and reject it — it overshoots
700 by **2**. Later, the check on the answer is **234 × 203 = 47502**, which
overshoots 47500 by **2**. It is the same 2. The near-miss halfway through the
working is *precisely* why the final answer sits a hair under 203.

So the payoff is not a new fact bolted onto the end. It is the viewer being
shown that they already computed the answer four steps ago and did not notice.
That is the only structure that justified picking this division over any other,
and chapters 4 and 5 are built to make the callback land.

---

## Structure

| Ch | Beats | What it does |
| --- | --- | --- |
| 1 | 20 | Calculator, crossed out. `47500 ÷ 234`. Grab a pen. 19 seconds. |
| 2 | 20 | Nobody divides 47500 — the split to `475 \| 0 \| 0`, matched to 234 |
| 3 | 20 | First digit. 234×2=468 ✓, 234×3=702 ✗. Write 2, carry 7 |
| 4 | 20 | Both zeros. 70 → 0. Then 700, and **702 misses by just 2** |
| 5 | 20 | 232/234 = 0.99 → just under 203. The check. **The same 2.** |
| 6 | 20 | ≈ 202.99, no calculator, then the signature |

---

## The stopwatch

The hook promises 19 seconds, so a stopwatch runs in the top-left through
chapters 3–5 and stops when the answer lands. It is a real timer on real screen
time, not a graphic: it starts at 16.0s and the answer appears at 35.2s.

The waits in chapter 5 before "a hair under 203" are load-bearing — they exist
to put that reveal at 19.0s on the clock. Do not trim them without moving the
timer start.

It also holds at `19s` for 1.8s after reaching 19 rather than vanishing on the
instant. The first cut stopped it the moment it ticked over, which gave the
number 12 frames on screen — too brief to read, which defeats the point of
having promised it in the hook.

---

## Caption

```
47500 ÷ 234 without a calculator. Grab a pen — this takes 19 seconds.

You never divide 47500. You divide 475.

How many 234s fit in 475? Two — 234 × 2 = 468, and 234 × 3 = 702 is too big.
468 from 475 leaves 7. Bring down a zero: 70, and 234 doesn't fit, so write 0.
Bring down the last zero: 700. Now 234 × 3 = 702 — over by just 2. So it's 2
again, and 700 − 468 = 232.

202 remainder 232. And 232 out of 234 is 0.99, so the answer is a hair under 203.

Here's the part most people miss. Check it: 234 × 203 = 47502. That's 2 more
than 47500 — the same 2 that made 702 too big halfway through. You'd already
worked out the answer four steps earlier without noticing.

47500 ÷ 234 = 202.99

Try one in the comments and I'll do it.

#mentalmath #maths #mathtrick #longdivision #nocalculator
```

**"Try one in the comments and I'll do it."** is the comment driver, and unlike
the puzzle videos it also generates the next video for free — whatever people
post is a ready-made sequel with a built-in audience already invested in it.

Hashtags fish the mental-maths and study pools rather than the AI ones. This is
the first video on the page with no AI angle at all, which makes it a clean test
of whether the audience is here for the maths or for the AI framing — worth
knowing before committing more of the calendar either way.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl no_calculator.py NoCalculator -w -r 1080x1920
python3 cinegrade.py videos/NoCalculator.mp4 no_calculator.mp4
```
