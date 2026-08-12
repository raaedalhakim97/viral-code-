# One Neuron — video brief

Companion to `neuron.py`. **Episode 3 of "WHY DID WE LEARN THIS?"**

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice.**

---

## The hook

> **one neuron**
> **is y = mx + b**
> *with one switch on the end*

That is the whole video in three lines, and it is the reason this episode
exists: the audience already watched `y = m·x + b` get filled in, slot by slot,
in episode 1. This is the **same equation with the letters renamed** — so the
only genuinely new idea in forty seconds is the switch.

```
z  =  w · x  +  b          the line from episode 1
y  =  max( 0, z )          and one switch on the end
```

---

## The picture

```
   x ──w──▶ ( b ) ──▶ y
```

One input, one wire, one body, one output. Each part lights up as its slot in
the equation does, so the letter and the thing it names are never on screen
apart.

| slot | is | on the picture |
| --- | --- | --- |
| **x ← 3** | what comes in | on the input dot |
| **w ← 2** | how much it matters | on the wire |
| **b ← −4** | how hard it is to set off | under the body |

```
z = 2 · 3 + (−4) = 2      positive → y = max(0, 2) = 2      it FIRES
```

Then the payoff, which is the **same neuron and one different input**:

```
z = 2 · 1 + (−4) = −2     negative → y = max(0, −2) = 0     it goes SILENT
```

The output wire goes dark and the body dims. Same weights, same bias, nothing
touched but the input — and nothing comes out.

---

## Number discipline

Every number on screen is a small integer, one arrives per stage, and both
results are exact: **2** and **0**.

**The bias is negative on purpose.** It is what makes the second case shut off,
and *"b = −4 means the input has to beat 4"* is a sentence a fourteen-year-old
can hold. It also forced a typographic fix: the spine's `+` piece is fixed, so a
bare `-4` rendered as `+ -4`. The slot shows `(−4)` and the wire shows `−4`,
both with a real U+2212 minus rather than a hyphen.

### Verified at import

```
z1 == 2 and y1 == 2         the firing case, in integers
z2 == -2 and y2 == 0        the silent case — the switch really does shut
every number shown is whole
relu(-7) == 0, relu(7) == 7 both branches, not just the one used
```

---

## Caption

```
One neuron is y = mx + b with a switch on the end. That's it. That's the whole
thing your phone runs a few billion of.

x is what comes in. w is how much it matters. b is how hard it is to set off.

z = w·x + b

Put numbers on it. Weight 2, input 3, bias −4:
z = 2·3 + (−4) = 2

Positive, so it goes through. The neuron fires. Output 2.

Now change ONE thing — the input becomes 1:
z = 2·1 + (−4) = −2

Negative. And the switch is: y = max(0, z). Negative gets nothing.

y = 0. Same neuron. Silent.

That switch is the only new idea here. Everything else is the straight line you
drew in year 9.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #neuralnetwork #howaiworks #algebra #gcse
```

**YouTube title:** `One neuron is just y = mx + b`

---

## Subtitle track

`neuron.srt` — 14 cues, no gaps, no overlaps, asserted at generation.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl neuron.py Neuron -w -r 1080x1920
python3 cinegrade.py videos/Neuron.mp4 neuron.mp4
```
