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

## The sound: MONTAGEM ALQUIMIA

Chosen and locked. The render stays silent and the track is attached in the
TikTok editor — audio baked into an upload cannot be attributed to the sound's
page, and that page is where a trending sound's reach comes from.

**It is 0:18 long.** This piece is 16.0s at 150 BPM, so it fits with ~2s spare.
Do not lengthen the scene past 18s or the audio runs out mid-video, which reads
worse than a short video. If the piece ever needs to grow, raise the BPM rather
than adding beats.

### Confirming the tempo

150 BPM is the genre default, not a measurement of this specific track — and if
ALQUIMIA is a slowed edit it will be lower. `bpm_probe.wav` plays 8 seconds of
click at 130, 140, 150 and 160 in sequence; play it against the sound and use
whichever locks. Then:

```bash
BPM=<measured> manimgl equation_ladder.py EquationLadder -w
```

Everything in the scene is a whole or half multiple of `B = 60/BPM`, so the
piece rescales and stays locked. Length at each candidate:

| BPM | Length |
| --- | --- |
| 130 | 18.5s — **too long for an 18s sound** |
| 140 | 17.1s |
| 150 | 16.0s |
| 160 | 15.0s |

At 130 the piece overruns the track. If the measurement comes back at 130, drop
a rung from `LADDER` (4 beats) to bring it to 16.6s.

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
