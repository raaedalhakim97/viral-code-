# tax = paid ÷ 21

Episode of **"WHERE MATH ACTUALLY GETS USED"**. The answer is pinned at
the **top of the frame** for the whole video — and it's deliberately
strange. *Twenty-one?* The video is the audience finding out why.

- **Output:** 1080×1920, 60fps, **60.000000s** — 150 beats = 37.5 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The story

Someone hands you **40,000**. The price already had 5% tax in it. How
much of it is the taxman's?

**The obvious move.** 5% of 40,000 = 2,000. That's what almost everyone
writes down.

**The doubt.** Five percent… of *what*? Nobody ever charged 5% of 40,000.
The 5% was worked out from **your price** — a number you haven't found
yet — and then added on top.

**The shape.** Cut your price into 20 equal parts. The tax is one more
part, exactly the same size, stuck on the end. So what they handed you is
not 20 parts.

```
 [][][][][][][][][][][][][][][][][][][][]  []      =  40,000
  \____________ 20 = yours ____________/    1 = tax

              twenty-one parts
```

**The answer falls out.**

```
one part   =  40,000 ÷ 21  =  1,904.76      <- the tax, all of it
yours      =  20 parts     =  38,095.24

              38,095.24 + 1,904.76  =  40,000.00
```

**The cost of the mistake.** Taking 5% off the whole thing cuts a 21-part
bar into 20. You hand over 2,000 where 1,904.76 was owed — **95.24 that
was never his.** On a million: 2,380.95.

**The rule worth keeping:** 5% → 21 parts. 10% → 11. 20% → 6. Always one
part more than you'd think.

### Verified at import

```
every figure is exact Fraction arithmetic — nothing typed in by hand
one part really is 5% OF THE NET, so the slice story and ÷ 1.05 agree
38,095.24 + 1,904.76 == 40,000.00, at cent precision, exactly as shown
the overpayment is exactly 2000/21 -> 95.24, and 2,380.95 on a million
the 5/10/20% -> 21/11/6 rule is checked against 1/s == r/(1+r)
the bar and its labels are asserted to stay inside the frame
```

---

## Why a bar of 21 parts, and not two bars

The first cut of this video was a chain of boxes doing `÷1.05` and
`×1.05`. It was correct and it was cold — arithmetic where a picture
should have been.

A proportional comparison doesn't work either: 38,000 and 38,095.24
differ by less than a quarter of a percent, so two bars side by side are
two identical bars, and the video would be arguing against its own
picture.

What *is* visible is the **construction**. The bar doesn't compare two
answers — it shows how the 40,000 got built in the first place: twenty
parts that are yours, and one more added on the end. Once the 21st part
is on screen, "one in twenty-one, not one in twenty" needs no algebra,
and the strange `÷ 21` at the top of the frame explains itself.

---

## Structure

| Beats | |
| --- | --- |
| 0–10 | **they hand you 40,000. the price had 5% tax in it. how much is the taxman's?** |
| 10–26 | the obvious move: `40,000 × 5% = 2,000`. *that's what almost everyone writes down* |
| 26–38 | **five percent… of what?** *nobody ever charged 5% of 40,000* |
| 38–68 | the bar builds: 20 gold parts = YOUR PRICE, then one rose part lands on the end. the whole thing is the 40,000 |
| 68–86 | the rose part steps out. *20 yours + 1 taxman = 21 parts.* **twenty-one. not twenty.** |
| 86–110 | `40,000 ÷ 21 = 1,904.76` → the labels turn into numbers → `38,095.24 + 1,904.76 = 40,000.00` |
| 110–122 | *you'd have handed over 2,000 — 95.24 was never his.* 10% → 11 parts, 20% → 6 |
| 122–132 | *The tax was never 5% of what they paid. It's one part in twenty-one.* |
| 132–138 | share ask |
| 138–150 | The eye |

---

## Caption

```
They hand you 40,000. The price already had 5% tax in it. How much of it
is the taxman's?

Easy — 5% of 40,000 is 2,000. That's what almost everyone writes down.

But five percent of WHAT? Nobody ever charged 5% of 40,000. The 5% came
off YOUR price, and then it was added on top.

So start with your price and cut it into 20 equal parts. The tax is one
more part, exactly the same size, on the end.

Now count what they handed you. Not 20 parts. Twenty-one.

One part = 40,000 ÷ 21 = 1,904.76. That's the tax, all of it.
The other 20 are yours: 38,095.24.

38,095.24 + 1,904.76 = 40,000.00. Nothing left over.

Take 5% off the whole thing and you hand over 2,000 — 95.24 that was
never his. On a million, 2,380.95.

5% means 21 parts. 10% means 11. 20% means 6. Always one more than you'd
think.

#maths #mathtok #tax #vat #smallbusiness #invoice #fyp
```

**YouTube title:** `The bar has 21 parts, not 20 — the tax trick nobody teaches`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl net_vs_gross.py NetVsGross -w -r 1080x1920
python3 cinegrade.py videos/NetVsGross.mp4 net_vs_gross.mp4
```

## Changing it

`PAID` and `RATE` are the only inputs. `PARTS_NET` and `SLICES` are
derived (`1/rate`, and one more), so setting `RATE = 20/100` redraws the
bar as 5 gold parts plus 1 and every number follows. The assertions
refuse to build unless one part really is the tax, the two on-screen
amounts still add to the total at cent precision, and the bar still fits
the frame.

**Not tax advice.** It's one arithmetic fact: when a figure already
includes the tax, the tax is one part in `1/rate + 1` — you divide, you
don't subtract.
