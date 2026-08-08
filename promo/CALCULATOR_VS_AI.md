# Calculator vs AI — video brief

Companion to `calculator_vs_ai.py`. Why the cheapest calculator in the world
beats a frontier model at multiplication.

- **Output:** 1080×1920, 60fps, **35.200000s** — 88 beats = 22 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## The spine

Both halves are a statement about **which digit you are allowed to produce
first**, and they point in opposite directions.

**A calculator must start at the smallest digit.** It adds with a ripple-carry
chain of full adders:

```
S    = A xor B xor Cin
Cout = (A and B) or (Cin and (A xor B))
```

Eight rows of a truth table. Bit 0 decides the carry into bit 1, which decides
the carry into bit 2 — so low-to-high is not a convention, it is **forced by the
arithmetic.** The video runs the real ripple on 1101 + 1011, one column per
beat, right to left, and lands on 11000 = 24.

**A language model writes left to right**, so the first token it emits for a
product is the **highest** place value — the one that depends on everything it
has not worked out yet.

That is not a nitpick, and the video proves it with two lines:

```
317 × 315 =  99,855      leading digit 9,  five digits
317 × 316 = 100,172      leading digit 1,  SIX digits
```

**Change the last digit of the input and the first digit of the answer flips**,
and the answer grows a place. You cannot know the first digit without having
already done the last one. The model has to commit before the work that decides
the answer exists.

Then the measured consequence — GPT-4 on n-digit multiplication:

| digits | accuracy |
| --- | --- |
| 3 | **59%** |
| 4 | **4%** |
| 5 | **0%** |

And the close: the calculator is right **by construction**, the model is right
**by resemblance** — which is why modern systems stopped trying and just call a
calculator.

---

## What is computed and what is quoted

Everything on screen is checked at import, so a bad edit fails the render
instead of shipping:

- the full adder is verified **exhaustively** — all 8 rows satisfy
  `S + 2·Cout == A + B + Cin`
- `317 × 315 == 99855` (5 digits, leads with 9) and
  `317 × 316 == 100172` (6 digits, leads with 1)
- the ripple animation calls the same `full_adder()` the assertions check, so
  the bits on screen are what the gates actually produced

**One figure is quoted rather than computed:** the GPT-4 accuracies, from
*Goat: Fine-tuned LLaMA Outperforms GPT-4 on Arithmetic Tasks*,
[arXiv:2305.14201](https://arxiv.org/abs/2305.14201). It is attributed on screen
because it is the only number in the video I did not derive here.

Worth knowing that the mechanism is documented too, not just the outcome:
benchmark work finds models predict the highest-order digit before the
lower-order ones, which is backwards from how carrying works — the same point
this video makes geometrically.

---

## Three signposted stages

The first cut ran the calculator, the AI and the comparison together as one
stream. Every fact in it was true and **nobody could tell which part they were
in.** That is a structure problem, not a content problem, and no amount of
better writing inside the sections fixes it.

This cut is three stages, each announced by a **full-screen card**, with a live
`1 / 3` marker in the header that stays up for the whole section:

| Beats | |
| --- | --- |
| 0–4 | Title |
| 4–8 | **CARD — 1 · THE CALCULATOR** |
| 8–28 | 13 + 11 in binary. The real carry rippling right to left. = 24. **Nothing about AI.** |
| 28–32 | **CARD — 2 · THE AI** |
| 32–54 | Writes left to right → 317 × 315 vs 317 × 316 → 59% / 4% / 0%. **Nothing about gates.** |
| 54–58 | **CARD — 3 · SIDE BY SIDE** |
| 58–72 | The two in a table, one row at a time |
| 72–78 | "One computes the answer. The other predicts it." |
| 78–88 | The eye |

The comparison is a real two-column table rather than a paragraph, built one row
at a time so each contrast lands on its own beat:

| CALCULATOR | AI |
| --- | --- |
| smallest digit first | biggest digit first |
| logic gates | prediction |
| always exact | 0% at 5 digits |
| by construction | by resemblance |

**Every section pads to a fixed beat.** `END_CALC`, `END_AI`, `END_CMP` and the
rest are constants, and each part ends with `pad_to()`, so slack is absorbed at
the section boundary instead of being hand-counted across a dozen animations.
That is what makes the stage timings stay put when a line gets rewritten.

Chapter 2's equations are built as **five separate mobjects per row** so the two
digits that matter can turn gold on cue. The first cut used a single marker line
at a fixed x, and it landed on the equals sign pointing at nothing.

---

## Caption

```
Why can a $2 calculator multiply better than GPT-4?

A calculator adds with logic gates — XOR for the sum, AND for the carry. Eight
rows of a truth table, no opinion. And it MUST start at the smallest digit,
because every carry moves left. Bit 0 decides the carry into bit 1. It has no
choice about the order.

A language model writes left to right. So the first digit it says is the biggest
one — the one that depends on everything it hasn't worked out yet.

Watch what that costs:
317 × 315 = 99,855
317 × 316 = 100,172

Change the LAST digit of the input and the FIRST digit of the answer flips from
9 to 1, and the answer grows a whole extra place. You cannot know that first
digit without doing the last one first.

Measured: GPT-4 gets 59% of 3-digit multiplications right. 4-digit: 4%.
5-digit: 0%. (Goat, arXiv:2305.14201)

The calculator is right by construction. The model is right by resemblance.
Which is why it now just calls a calculator.

#ai #maths #calculator #gpt #computerscience
```

The searchable phrase is the **first line** — "why can a calculator multiply
better than GPT" is a question people actually type, and this video is silent so
the caption carries all the search weight.

**YouTube title:** `Why a $2 calculator beats GPT-4 at multiplication`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl calculator_vs_ai.py CalculatorVsAI -w -r 1080x1920
python3 cinegrade.py videos/CalculatorVsAI.mp4 calculator_vs_ai.mp4
```
