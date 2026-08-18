# Your first Wordle guess is probably wrong — the smart one doesn't feel smart

Companion to `wordle_bits.py`. First of the five "trendy" AI-math videos.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## Why this topic

From the trend-research doc: information gain / Wordle is the single strongest
idea in it. It's a real surprise ("the best guess can share zero letters with
the answer"), it's genuinely an AI concept (entropy is what a model is scored on
when choosing what to predict next), and every number in the video is checkable
by a viewer with a phone calculator.

---

## A closed world, on purpose

Real Wordle has 2,315 possible answers — too many numbers for a phone screen.
This video uses **16 real five-letter words**, small enough that every count is
checkable by eye, and `log2(16) = 4.000` is a clean ceiling. The video doesn't
pretend to be the real game — it says "16 possible answers" on screen, not
"here's how Wordle works."

The feedback rule is the **real** Wordle rule, duplicate letters and all: green
if the letter is in that exact spot, yellow if it's elsewhere in the secret
word (correctly handling repeats via a shrinking counter), grey otherwise.
Verified against two known hard cases before anything else was built:

```
SPEED vs ERASE -> YBYYB   (two E's on each side, neither lands in place)
ALLOY vs LOYAL -> YYYYY   (a perfect anagram — every letter present, none placed)
```

---

## Two guesses, same sixteen words

**AUDIO** — four vowels, feels thorough. It splits the 16 words into only **5
groups**. The worst group has **6 words that look completely identical** on
screen: CRANE, GRAPE, PLANT, FLAME, SNAKE, WATER all show the same single gold
tile in position 1 and grey everywhere else. Score: **2.108 bits**.

**CRANE** — no vowel-counting logic to it at all. It splits the same 16 words
into **16 groups** — every single word produces a different five-tile pattern.
That's not a good result, it's **the best possible result**: `log2(16) = 4.000`,
the theoretical ceiling for sixteen options, hit exactly.

### Verified at import

```
the feedback rule handles duplicate letters       tested against known cases
AUDIO's worst group has the size the caption uses  6 of 16, computed
CRANE reaches the theoretical ceiling exactly       log2(16) = 4.000
AUDIO's entropy is lower than CRANE's by >1.5 bits  or the contrast is too small to see
```

Nothing about which guess wins is typed by hand — `analyze()` computes the
buckets and the entropy from the real feedback rule, and the assertions would
fail the render if AUDIO ever came out ahead.

---

## The number is information gain

`H = -Σ p·log2(p)` over the resulting groups is Shannon entropy, and it answers
one question: **how much did this guess actually narrow things down, on
average, before you know the answer?** You never need to know the secret word
to know which guess is smarter — that's the whole trick, and it's also exactly
what a decision tree or a language model is scored on when it picks what to ask
or predict next.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **YOUR FIRST GUESS IS PROBABLY WRONG** — not a bad word, a guess that barely tells you anything |
| 8–20 | 16 words, one secret. *we don't know which* |
| 20–44 | **AUDIO.** Six identical rows. **2.108 bits** |
| 44–68 | **CRANE.** Sixteen distinct rows. **4.000 bits — the ceiling, hit exactly** |
| 68–80 | *you never had to know the secret word... that's called information gain* |
| 80–86 | **INFORMATION GAIN — follow, the math behind AI** |
| 86–100 | The eye |

---

## Caption

```
Your first Wordle guess is probably wrong. Not "bad word" wrong — wrong as in
it barely teaches you anything.

16 possible answers. One is the secret. We don't know which.

Guess AUDIO — four vowels, feels thorough. Watch the sixteen words react: SIX of
them look completely identical. Only the A registers. Everywhere else, grey.
That guess just told you almost nothing: 2.108 bits.

Now guess CRANE. Same sixteen words. Every single one reacts differently. Not
"pretty good" different — EVERY one. That's log2(16) = 4.000 bits, the absolute
maximum possible for sixteen options. CRANE doesn't just do well. It's
mathematically perfect.

Here's the part that should bother you: you never had to know the secret word to
know CRANE was the smarter guess. You just had to count how differently the
board could react.

That number — bits of information gain — is the exact thing a language model is
scored on every time it has to guess what comes next.

#wordle #maths #mathtok #informationtheory #ai #probability #wordlestrategy
```

**YouTube title:** `Why your first Wordle guess is (probably) the wrong one — information gain, explained`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl wordle_bits.py WordleBits -w -r 1080x1920
python3 cinegrade.py videos/WordleBits.mp4 wordle_bits.mp4
```

## Changing it

`WORDS`, `GUESS_FEEL`, `GUESS_SMART` at the top — any 16 distinct real five-letter
words and two guesses. The assertions recompute the bucket counts and entropy
from the real feedback rule and refuse to build if AUDIO's bucket count, worst
group size, or the entropy gap ever drift from what the caption claims.
