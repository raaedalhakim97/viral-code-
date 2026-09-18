# EVERY MANAGER GETS THIS WRONG

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## Built to the hook rules, not to a lesson plan

This is the third cut. The first two were correct and *slow* — a title
card, then a build-up, then the payoff at the end. That ordering is
backwards for short-form. What the research says, and what this cut does:

| Finding | What changed |
| --- | --- |
| Viewers decide in **under 1.7s**; 63% of top-CTR videos hook inside 3s | There is **no** opening card. Frame 1 is the finished mistake. |
| Show the **mistake visually in the first frame** while you state it | `38,000` is on screen at t=0, struck through, with a cross on it |
| **Loss framing beats gain framing** — "*you're* losing money", second person | *"this costs you 95.24 / every single invoice"* — in frame 1 |
| **Identity callout** self-selects the audience, highest-converting for growth | The banner *is* the callout: **EVERY MANAGER GETS THIS WRONG** |
| **Outcome shown in the first 2 seconds** is the top-performing hook type (~2× views) | The real answer lands at **0:05**, before any explanation |
| Hook ≈ 10–14 words, lines short | Captions are 4–7 words, second person, present tense |

The pinned line is no longer a formula. It's **`38,095.24  not  38,000`** —
the answer *and* an open loop, held at the top of the frame the whole way
down.

**One more fix from watching the render:** after the answer pinned at
0:05, the stage sat empty until the bar arrived at 0:14 — nine seconds of
captions over black, which is exactly where people scroll. The wrong sum
now runs live in the centre of the frame during that stretch and gets
crossed out on the beat.

---

## The story

Frame 1 — the mistake, already made:

```
             40,000  −  5%
             ~38,000~      ✗

         this costs you 95.24
          every single invoice
```

Then the real number, immediately: **38,095.24.** *That's what you
actually keep.* It pins to the top and stays.

Then, and only then, why. 40,000 comes in, tax already inside. You take
5% off — 2,000 — and book 38,000. **But 5% of what?** Nobody ever
charged 5% of 40,000. The 5% came off *your* price and was added on top.

**The shape.** Cut your price into 20 equal parts. The tax is one more
part exactly like them, on the end. So what came in is **21 parts**:

```
 [][][][][][][][][][][][][][][][][][][][]  []      =  40,000
  \____________ 20 = yours ____________/    1 = tax
```

```
one part  =  40,000 ÷ 21  =  1,904.76      <- the whole tax
yours     =  20 parts     =  38,095.24
             38,095.24 + 1,904.76  =  40,000.00
```

**The stake, in manager units.** You handed over 2,000 where 1,904.76 was
owed. **95.24 gone per invoice — 9,523.81 across a hundred of them.**

**The rule:** 5% → 21 parts. 10% → 11. 20% → 6. Always one more.

### Verified at import

```
every figure is exact Fraction arithmetic — nothing typed in by hand
one part really is 5% OF THE NET, so the slices agree with ÷ 1.05
38,095.24 + 1,904.76 == 40,000.00, at cent precision, exactly as shown
95.24 per invoice, 9,523.81 per hundred, 2,380.95 on a million
the 5/10/20% -> 21/11/6 rule is checked against 1/s == r/(1+r)
the bar and its labels are asserted to stay inside the frame
```

---

## Why a bar of 21 parts

A proportional before/after can't work: 38,000 and 38,095.24 differ by
under a quarter of a percent, so two bars side by side are two identical
bars and the picture contradicts the caption. The bar doesn't compare the
two answers — it shows how the 40,000 got **built**: twenty parts that
are yours, one more added on the end. Once the 21st part is on screen,
"one in twenty-one, not one in twenty" needs no algebra.

---

## Structure

| Beats | Time | |
| --- | --- | --- |
| 0–5 | 0:00 | **HOOK.** the mistake, struck out, crossed. *this costs you 95.24 / every single invoice* |
| 5–14 | 0:02 | **38,095.24** — *that's what you actually keep* → pins to the top |
| 14–26 | 0:05 | the sum runs in the centre: 40,000 − 2,000 = 38,000 ✗ |
| 26–34 | 0:10 | **5% of WHAT?** *nobody charged 5% of 40,000* |
| 34–62 | 0:13 | the bar: 20 gold parts + 1 rose part. *twenty-one. not twenty.* |
| 62–80 | 0:25 | `÷ 21 = 1,904.76`, the labels become numbers, they add back to 40,000.00 |
| — | 0:30 | *95.24 gone. × 100 invoices = 9,523.81.* |
| 80–88 | 0:32 | *5% tax means 21 parts. 10% means 11. 20% means 6.* |
| 88–92 | 0:35 | *Send this to whoever signs off your invoices* |
| 92–100 | 0:37 | The eye |

---

## Caption

```
Every manager gets this wrong.

40,000 comes in, tax already inside. You take 5% off — 2,000 — and book
38,000.

That costs you 95.24. Every single invoice.

Because 5% of WHAT? Nobody ever charged 5% of 40,000. The 5% came off
YOUR price, and then it was added on top.

So cut your price into 20 equal parts. The tax is one more part, exactly
the same size, on the end.

What came in isn't 20 parts. It's 21.

40,000 ÷ 21 = 1,904.76 — that's the whole tax. The other 20 are yours:
38,095.24. And they add straight back to 40,000.00.

You handed over 2,000. He was owed 1,904.76. Across a hundred invoices
that's 9,523.81 you never owed.

5% means 21 parts. 10% means 11. 20% means 6. Always one more.

#maths #mathtok #tax #vat #smallbusiness #finance #manager #fyp
```

**YouTube title:** `Every manager gets this wrong — 5% tax means 21 parts, not 20`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl net_vs_gross.py NetVsGross -w -r 1080x1920
python3 cinegrade.py videos/NetVsGross.mp4 net_vs_gross.mp4
```

## Changing it

`PAID` and `RATE` are the only inputs. `PARTS_NET` and `SLICES` are
derived (`1/rate`, and one more), so `RATE = 20/100` redraws the bar as 5
parts plus 1 and every number follows. The assertions refuse to build
unless one part really is the tax, the two on-screen amounts still add to
the total at cent precision, and the bar still fits the frame.

**Not tax advice.** One arithmetic fact: when a figure already includes
the tax, the tax is one part in `1/rate + 1` — you divide, you don't
subtract.

---

## Sources for the hook rework

- [TikTok Hook Formulas That Drive 3-Second Holds — OpusClip](https://www.opus.pro/blog/tiktok-hook-formulas)
- [TikTok Hook Formulas Every Founder Should Steal — Conbersa](https://www.conbersa.ai/learn/tiktok-hook-formulas-for-founders)
- [Video Hooks: How to Win the First Two Seconds — RedHub AI](https://blog.redhub.ai/video-hooks)
- [How to Write Viral Hooks for Short-Form Video (2026) — Kineclip](https://kineclip.com/blog/how-to-write-viral-hooks-short-form-2026/)
- [The best TikTok hooks to boost views and engagement — HeyOrca](https://www.heyorca.com/blog/best-tiktok-hooks)
