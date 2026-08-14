# The Car Wash Puzzle — video brief

Companion to `carwash_puzzle.py`. Second video in the **puzzle** format after
`rope_puzzle` — pose it, make the viewer commit, show why the wrong answer is
tempting, pay it off at the end.

- **Output:** 1080×1920, 60fps, **48.000000s** — 120 beats = 30 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## The puzzle

> I need to wash my car. The car wash is five minutes away.
> Should I walk or drive?

The answer is **drive**, and the reason has nothing to do with distance. The car
is not how you get there — it is *what you are bringing*. Walk, and the car is
still on the driveway, so the goal is unmet at any distance. Five minutes, five
hours, five metres: it does not matter.

---

## What this video claims, and what it deliberately does not

It does **not** claim that AI models get this wrong.

That was not verifiable at build time — the web search hit a session limit — and
frontier models most likely answer it correctly. Asserting a failure I had not
observed would repeat the exact mistake that sinks this genre: a video built on
"AI says 1+1=3" whose top comment is a screenshot of the model getting it right.
That comment costs more than the video earns.

What it *does* claim is true of any pattern matcher, silicon or otherwise: **a
question whose surface matches a familiar template invites the template's
answer.** "X is five minutes away, walk or drive?" has the shape of a
travel-optimisation problem, and that shape answers "walk, it's close." The
actual goal — *the car has to be there* — sits outside the template entirely.

That is this channel's standing thesis restated in twelve words: answering the
*form* of a question instead of the question. It is the same idea as
`illusion_of_logic`, but as a puzzle the viewer plays rather than a claim they
are asked to accept.

**If you want the "AI fails this" version, run it past a few models and send me
the screenshots.** With evidence I would build it that way happily — it is the
stronger hook. Without evidence it is a liability.

---

## Structure

| Ch | Beats | What it does |
| --- | --- | --- |
| 1 | 24 | The question. HOME → CAR WASH, 5 min, **the car parked on the drive** |
| 2 | 24 | A · walk / B · drive. "Pick before you scroll", with a draining timer |
| 3 | 24 | The sentence's *shape* — three slots, the stock answer, then the flash |
| 4 | 24 | Both end states. A: car never arrived ✗. B: the car drives across ✓ |
| 5 | 24 | Distance was never the question, then the signature |

---

## Two build notes worth keeping

**The car has to be on screen from chapter 1.** The first cut of this scene never
drew it — the whole answer turns on where the car *is*, and it existed only as
the words "+ car" inside a box in chapter 4. It is now a glyph: parked under HOME
in ch1, and in ch4 it physically drives the corridor between HOME and WASH. The
payoff is a thing moving, not a label changing.

**Chapter 2 was 20 beats of frozen frame.** The commit window is the most
important beat in the puzzle format and it was also the deadest — eight seconds
of a still image, on a silent video, at the exact point where a viewer decides
whether to stay. It now carries a gold bar that drains over 8 beats. Same
function, and the eye has somewhere to go.

The general version, since it caught me twice now: `pad_to` makes a chapter land
on its bar line, but it does not make the chapter *worth* its length. Check the
scripted-versus-held ratio per chapter, not just the total duration. Anything
under about half scripted needs more content, not more patience.

---

## Caption

```
I need to wash my car. The car wash is 5 minutes away. Should I walk or drive?

A) walk — it's close    B) drive

Almost everyone's first instinct is A, and A is wrong. Not because 5 minutes is
far. Because if you walk, the car is still sitting on your driveway.

The car isn't how you get there. It's what you're bringing.

The question is shaped like a travel problem — "X is N minutes away, walk or
drive?" — and that shape has a stock answer. The actual goal sits outside the
pattern, so the pattern never checks it. That's the trap, and it's the same one
a language model falls into when it answers the form of a question instead of
the question.

Did you say walk?

#puzzle #brainteaser #riddle #aithinking #logic
```

**YouTube title:** `The car wash puzzle — how AI would actually solve it`

**"Did you say walk?"** is the comment driver. Keep it last — it is the same
role "Did you get it right?" plays on the rope puzzle, and admitting a wrong
answer to something this simple is easy, which is exactly why people do it.

Hashtags fish the puzzle/riddle pools first and AI second. `#puzzle` and
`#brainteaser` are an order of magnitude larger than `#aimath`, and the AI angle
is in the caption body where TikTok can still index it — this video is silent,
so the caption carries all of the search weight.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl carwash_puzzle.py CarWashPuzzle -w -r 1080x1920
python3 cinegrade.py videos/CarWashPuzzle.mp4 carwash_graded.mp4
```
