# Why doesn't AI start with equal numbers?

Companion to `symmetry_break.py`. Third of the five "trendy" AI-math videos —
from the trend-research doc's "randomness prevents gridlock" pick, replaced
with the actual, provable AI reason: symmetry breaking in weight
initialisation.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## Why this angle instead of the pop-sci one

The trend doc's framing — "a little randomness stops a crowd of robots from
freezing" — is a real phenomenon but a fuzzy one to animate honestly in 40
seconds. **Neural network weight initialisation is the same idea, except it is
exactly provable**, with real gradient descent, real numbers, and a genuine
"stuck forever vs. solved" contrast rather than a vague appeal to "a bit of
randomness helps."

---

## Three neurons, one tiny job, real calculus

```
y_hat(x) = sum_i  v_i * relu(w_i * x)
```

trained by actual gradient descent on two examples — `x=1 → y=3` and
`x=-1 → y=-3` — no shortcuts. The gradients are the real calculus, computed
once by hand and then **re-run at import** so the numbers on screen are real,
not typed in.

## Started identical, they move identically — forever

If `w1=w2=w3` and `v1=v2=v3` at step zero, then every gradient every neuron
ever receives is identical too. Gradient descent has no way to break a tie it
was never given. The three bars in that half of the video aren't a good
visual choice — they are **one trajectory, drawn three times**, and the
spread between them is checked to be **exactly `0.0`** at all 200 training
steps, not "very small."

Two opposite-signed training examples can't both be solved by three neurons
that are only ever allowed to move together, so the loss gets stuck at
**exactly 4.500** and stays there for the rest of training.

## Break the tie, and the loss goes to zero

Same two examples, same learning rate, same 200 steps — the only change is the
starting numbers are three *different* small values (`np.random.default_rng(153)`).
One neuron ends up strongly positive, one strongly negative, one near zero:
**they specialise**, and between them they solve both examples. Final loss:
`9.86e-32` — 32-bit float noise, i.e. exactly zero as far as a computer can
tell.

### Verified at import

```
identical init keeps every weight identical, every step   0.0 spread, always
the symmetric run's loss floor is exactly 4.500             not "roughly"
the broken-symmetry run reaches float-noise loss             < 1e-9
both runs train on the same two examples, same rate, same steps
```

---

## A real bug caught along the way

The loss readout ghosted permanently in an early cut — "4.500" and "0.000"
stuck visibly overlapping each other for the rest of the video. The actual
cause: the symmetric stage's on-screen loss text was never explicitly removed
before the random stage began; a **freshly-built, never-added** text object
was being faded out in its place, so the true leftover text sat underneath
every later number for good. Fixed by keeping the reference to what is
actually on screen and fading *that* out. Documented in the source as the
lesson it is: don't rebuild a reference to "the current text" from scratch —
carry the real mobject through.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **WHY DOESN'T AI START WITH EQUAL NUMBERS?** — *it's not superstition, it's provable* |
| 8–20 | The tiny job: see +1 → output +3, see −1 → output −3. Three identical bars |
| 20–46 | Symmetric run. Bars move as one. **Stuck. Exactly 4.500.** |
| 46–72 | Random run. Bars split apart, one goes negative. **Loss zero.** |
| 72–84 | *three identical numbers can only move together. break the tie, and they specialise* |
| 84–92 | **SYMMETRY BREAKING — follow, that's why weights start random** |
| 92–100 | The eye |

---

## Caption

```
Why doesn't AI start with equal numbers? It's not superstition. It's provable.

Three neurons. One tiny job: see +1, output +3. See -1, output -3.

Start all three IDENTICAL and train with real gradient descent. Watch the bars
— they can only ever move as one. Three numbers, but really only one degree of
freedom. The loss gets stuck at exactly 4.500 and NEVER moves again, no matter
how long you train. I ran it 200 steps to be sure. Still 4.500.

Same problem. Same learning rate. Same 200 steps. The only change: three
DIFFERENT tiny random numbers to start.

Watch what happens. The bars split apart — one goes strongly positive, one
strongly negative, one stays near zero. They specialise. Loss: zero.

Three identical starting numbers can only ever move together. That's not bad
luck, it's the math. Break the tie at the start, and they can finally do
different jobs.

That's the actual reason every real neural network initialises with small
random numbers instead of zero or a constant. Not a superstition. A proof.

#maths #mathtok #ai #neuralnetworks #deeplearning #machinelearning #gradientdescent
```

**YouTube title:** `Why AI never starts with equal numbers — symmetry breaking, proven`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl symmetry_break.py SymmetryBreak -w -r 1080x1920
python3 cinegrade.py videos/SymmetryBreak.mp4 symmetry_break.mp4
```

## Changing it

`W_SYM0`/`V_SYM0` and the random seed (153) at the top, plus `LR`/`STEPS`. The
assertions re-run the full 200-step training from scratch at import and refuse
to build if identical init ever produces the slightest weight spread, if the
symmetric loss floor drifts from 4.5, or if the random run fails to reach
float-noise loss.
