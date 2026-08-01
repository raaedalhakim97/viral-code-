# Equation Ladder — video brief

Companion to `equation_ladder.py`. The climb from `1 + 1 = 2` to attention, one
equation per bar, beat-locked to a funk montagem.

- **Output:** `videos/EquationLadder.mp4` — 1440×2560, 60fps
- **Length:** 40 beats = 10 bars. At 150 BPM that is **16.000s**.
- **Audio:** none. The montagem goes on in the TikTok editor.

---

## Why 150 BPM

Funk montagem sits on the modern Brazilian funk **150 BPM** wave. Brazilian
phonk generally runs 135–150, and montagem specifically is the 150 strand.

Tempo comes from an environment variable, **not a flag**:

```bash
BPM=150 manimgl equation_ladder.py EquationLadder -w
```

`manimgl` parses `sys.argv` itself and hard-errors on any argument it doesn't
recognise, so a scene file cannot add a `--bpm` flag. An env var sidesteps argv.

Verify the lock before trusting it:

```bash
python3 equation_ladder.py --click 150 click.wav
ffmpeg -i videos/EquationLadder.mp4 -i click.wav -c:v copy -shortest check.mp4
```

---

## Picking the sound

From the reference sound list, the montagem options were:

| Sound | Posts | Length |
| --- | --- | --- |
| YOSHO HAI MONTAGEM | 327.9K | 1:00 |
| MONTAGEM PEGADORA | 194.3K | 3:25 |
| MONTAGEM ALQUIMIA | 334 | 0:18 |

**Post count is not the same as opportunity.** A sound with 327K posts is
saturated — its sound page is a firehose and a 101-follower account lands
nowhere near the top of it. A sound with a few hundred posts is either rising,
which is the best possible position, or dead. The way to tell them apart is to
check the count again a day later: climbing fast means rising.

The reach research is consistent on this — trending sounds peak in 5–14 days,
and posting inside the first 24 hours of a rise is worth roughly 3× posting
after peak. Big numbers mean you already missed it.

**Length constrains the edit.** At 16.0s this piece fits every sound above,
including the 18s one. Do not lengthen it past the shortest sound you might
want to use — audio running out mid-video is worse than a short video.

---

## The ladder

Seven rungs, one per bar. The order is the order you'd learn them, and that's
the argument: the last line isn't magic, it's the fifth thing after a straight
line.

| Rung | Equation | Gloss |
| --- | --- | --- |
| 1 | `1 + 1 = 2` | arithmetic |
| 2 | `y = mx + b` | a straight line |
| 3 | `ŷ = w · x + b` | a prediction |
| 4 | `J = ½ Σ (ŷ − y)²` | how wrong it is |
| 5 | `w ← w − α ∂J/∂w` | learning |
| 6 | `σ(z) = exp(z) / Σ exp(z)` | turning it into a choice |
| 7 | `Attention(Q,K,V) = softmax(QKᵀ/√d)V` | and this runs your AI |

Each lands centre-stage, then gets pushed up the stack by the next one. Four
stack slots — five lines on screen is the readable limit on a phone.

**Gold is spent once, on rung 7.** The whole ladder is white; the equation that
actually runs a model is the only thing that glows.

---

## Two manimgl traps this scene documents

Both fail **silently** — the render succeeds and looks wrong.

**1. `Text(color=...)` does nothing.** `StringMobject`, which `Text` inherits
from, hardcodes `fill_color=WHITE` and `base_color=WHITE` in its signature, and
both beat a caller's `color=`. Verified directly:

```
Text("X", color=GOLD)       -> #FFFFFF
Text("X", base_color=GOLD)  -> #FFFFFF
Text("X", fill_color=GOLD)  -> #EBCB8B   <- the only one that works
```

This had collapsed the entire white/grey hierarchy to flat white across every
scene, and swallowed every intended gold text accent. Use `fill_color=`.

**2. No LaTeX in the container.** The equations are Unicode text, not `Tex`.
Every glyph is checked against DejaVu Sans Bold before use — a missing one
renders as a blank box and nobody notices until it's posted.

---

## Caption

```
Everything your AI does is five steps up from a straight line.

y = mx + b becomes a prediction, the prediction gets a loss, the loss gets a
gradient, the gradient becomes learning — and the last line is attention, the
equation running every model you've used this week.

None of it is magic. It's just the step after the step after the step.

#aimath #mathtok #machinelearning #neuralnetworks #calculus
```

Short alternate, for a fast montagem where nobody reads:

```
From 1 + 1 = 2 to the equation that runs ChatGPT. Seven steps.

#aimath #mathtok #machinelearning
```

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl equation_ladder.py EquationLadder -w
python3 cinegrade.py videos/EquationLadder.mp4 equation_ladder_graded.mp4
```

No narration. It's a sound-led piece and Alan would fight the track.
