# THE MATH BEHIND AI — seven-part series

One scene file, seven videos. `PART` selects which.

```bash
PART=3 BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl series.py Series -w
python3 cinegrade.py videos/Series.mp4 series_3_graded.mp4
```

- **Each part:** 32 beats = 8 bars = **12.800s** at 150 BPM, 1440×2560, silent
- **Total:** ~90 seconds of content from one file

---

## Why a series at all

The page has 2,645 likes against 101 followers. Reach is not the problem — a
video already hit 15.6K on a 101-follower base. **The problem is that nothing on
the page promises a next episode.**

A like costs nothing. A follow is a bet that you will make more of what they
just watched. `PART 3 / 7` on the end card makes that bet for them, and
`part 4 next` tells them what they're buying.

That is the entire mechanism. Everything else here is production.

## Why 12.8 seconds

Completion rate. A short video watched to the end — often twice — is a far
stronger signal than a long one abandoned at 40%. Every part is under 13
seconds, which also puts all of them inside an 18-second sound.

---

## The seven

| # | Title | Hook | What it draws |
| --- | --- | --- | --- |
| 1 | THE LINE | "Two numbers make every line there is." | `m` tilts it, `b` slides it |
| 2 | THE PREDICTION | "A line stops being a shape and starts being a guess." | what happened vs what it guessed, then every gap at once |
| 3 | THE ERROR | "It's called least squares because of the squares." | each gap becomes a square; the error **is** the white area |
| 4 | LEARNING | "Learning is just rolling downhill." | three visible steps, the squares shrinking |
| 5 | THE CHOICE | "How does a model choose?" | scores → exp stretches the gaps → divide by the total |
| 6 | ATTENTION | "This is the one running your AI." | keys lean toward a question; the lean is the weight |
| 7 | THE CLIMB | "Six steps from a straight line to a language model." | the whole ladder, fast |

Hooks are claims or questions, never topic labels. "Why is it called least
squares?" earns a second of attention; "Least squares" does not.

---

## Posting

**Order matters — post 1 through 7.** The numbering is the point; shuffling it
throws away the reason to follow.

Suggested rhythm: one part every 2–3 days, so the series stays live for about
three weeks. Post **part 7 last** and pin it, since it works standalone and is
the best single entry point for someone landing cold on your profile.

**Sound:** all seven render silent and beat-locked at 150 BPM. Attach the same
sound to all of them if you want the series to feel like one object, or pick
whatever is trending on the day for each. Both work; the first is more
recognisable, the second gets more reach.

If the sound isn't 150 BPM, re-render at its tempo — `pad_to()` keeps every part
exactly 8 bars whatever the BPM.

---

## Captions

Each names the searchable term the video shows but never says. These videos have
no narration, so the caption carries nearly all the search weight.

**Part 1**
```
Every line you have ever seen is two numbers. One tilts it, one slides it.
That is all a linear model is — and it is where every AI starts.

PART 1 of 7 · the math behind AI

#aimath #mathtok #linearalgebra #machinelearning
```

**Part 2**
```
The moment a line stops being a shape and starts being a guess.

It now has an opinion about every x — including ones it has never seen. The
distance between what happened and what it guessed is the whole game.

PART 2 of 7 · the math behind AI

#aimath #mathtok #regression #machinelearning
```

**Part 3**
```
Least squares is called least squares because of the squares.

Every gap becomes a square with that gap as its side. Add up the white area and
that number IS the error. Least squares is just the line where the area is
smallest.

PART 3 of 7 · the math behind AI

#aimath #mathtok #leastsquares #statistics #machinelearning
```

**Part 4**
```
Training a model is one move repeated: nudge the line, watch the area shrink.

α is how big a nudge. Too small and it takes forever. Too big and it overshoots
the bottom. That is gradient descent, and that is all training is.

PART 4 of 7 · the math behind AI

#aimath #mathtok #gradientdescent #machinelearning #calculus
```

**Part 5**
```
How a model turns three numbers into a decision.

exp() stretches the gaps between the scores, then you divide by the total so
they add to one. Now they are probabilities. That function is softmax, and it
runs at the end of nearly every model you have used.

PART 5 of 7 · the math behind AI

#aimath #mathtok #softmax #neuralnetworks
```

**Part 6**
```
Attention is the model asking: of everything I could look at, what matters here?

Each thing it could look at leans toward or away from the question. How much it
leans is its weight. The answer is the blend. That is the equation behind every
model you used this week.

PART 6 of 7 · the math behind AI

#aimath #mathtok #attention #transformers #machinelearning
```

**Part 7**
```
Six steps from a straight line to a language model.

A line. A guess. How wrong the guess is. Nudging it. Turning scores into a
choice. Asking what matters. That's the whole climb — none of it is magic.

PART 7 of 7 · the math behind AI

#aimath #mathtok #machinelearning #neuralnetworks #transformers
```

---

## What the file enforces

`pad_to()` holds each part until it has used exactly 24 beats of build, so the
close lands on beat 32 every time. The first cut came out at 28, 29, 30, 33 and
35 beats — **four of seven ended mid-bar**, which shows immediately against a
track. If a part ever overruns, `pad_to` raises rather than silently drifting:
that means trim the part, not stretch the target.

Elapsed time is counted inside `T()`, which is also what snaps `run_time` to
whole frames. Every timed call in the file goes through it. **If one doesn't,
the padding silently lies** — so don't add a bare `self.wait(0.5)`.
