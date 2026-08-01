# Geometry Ladder — video brief

Companion to `geometry_ladder.py`. The same climb as `equation_ladder`, but every
rung is **drawn instead of typed**.

- **Output:** `videos/GeometryLadder.mp4` — 1440×2560, 60fps
- **Length:** 40 beats = 10 bars. At 150 BPM that is **16.000000s**, exactly.
- **Audio:** none. MONTAGEM ALQUIMIA goes on in the TikTok editor.

---

## Why geometry beats notation here

A typed equation asserts. A construction shows *why*. The difference matters
most at rung 4: **squared error, drawn as actual squares** whose sides are the
residuals. Once you have seen it you cannot unsee what "least squares" means —
it is the picture where the total white area is smallest.

Rung 5 then earns the whole video: the line moves and the squares visibly shrink.
That is gradient descent, with no symbol required.

The symbol still appears — small and grey at the top of frame — so the picture
and the notation stay tied together. But the picture carries it.

| Rung | Symbol | Drawn as |
| --- | --- | --- |
| 1 | `1 + 1 = 2` | two unit segments laid end to end |
| 2 | `y = mx + b` | a line, with the rise-over-run triangle that defines it |
| 3 | `ŷ = w · x + b` | data appears; a drop from one point to the line |
| 4 | `J = ½ Σ (ŷ − y)²` | **the residuals become literal squares** |
| 5 | `w ← w − α ∂J/∂w` | the line moves, the squares shrink |
| 6 | `σ(z) = exp(z)/Σexp(z)` | three bars rescale until they add to one |
| 7 | `Attention(Q,K,V)` | keys lean toward a query; the lean is the weight |

**Gold is spent once**, on the attention output vector at rung 7.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl geometry_ladder.py GeometryLadder -w
python3 cinegrade.py videos/GeometryLadder.mp4 geometry_ladder_graded.mp4
```

Tempo is an environment variable, not a flag. Verify the lock with
`python3 geometry_ladder.py --click 150 click.wav`.

---

## Three bugs this scene cost, all worth knowing

### 1. Float error silently breaks the beat lock

`self.T(beats)` exists because raw multiples of `B` do not land on frames.
`1.5 * (60/150)` is `0.6000000000000001`, and manim builds its frame list with
`arange(0, run_time, 1/fps)` — that trailing bit buys an extra step, **37 frames
where the beat wants 36**. Three such calls put this scene at 963 frames instead
of 960: a sixteenth of a second of drift against the track, from nothing but
float representation.

```python
def T(self, beats):
    return round(beats * self.B * FPS) / FPS
```

**Never pass a raw `n * B` as `run_time`.** `beat_dance` escapes this only
because 120 BPM gives `B = 0.5`, which is exact in binary; change its tempo to
something like 150 and the same drift appears.

### 2. `ShowCreation(make_thing())` leaves an orphan

```python
self.add(self.line)                      # the live always_redraw version
self.play(ShowCreation(make_line()))     # ← builds a SECOND, static line
```

`play()` adds that second object to the scene, and nothing ever removes it. The
`always_redraw` version gets cleaned up on section change; the orphan does not.
In the first cut of this scene the regression line and all seven squares stayed
on screen through softmax, attention **and** the closing eye card.

Draw the static one, then hand over:

```python
drawn = make_line()
self.play(ShowCreation(drawn))
self.remove(drawn)
self.add(self.line)
```

### 3. Data-space geometry can leave the frame

A square whose side is the residual runs off the right edge when the point is
already near `x = 1`. The square now flips inward when it would overflow:

```python
d = 1.0 if x + side_x <= 1.0 else -1.0
```

Anything sized from data rather than from the layout needs this check.

---

## Caption

```
Least squares is called least squares because of the squares.

Every dot is a measurement. Every square is how wrong the line is about it,
times itself. Learning is just moving the line until the white area is as
small as it can get — and six steps later that same idea is attention, the
equation running every model you used today.

#aimath #mathtok #leastsquares #machinelearning #calculus
```

Short alternate:

```
This is what "least squares" actually means. The squares are real.

#aimath #mathtok #machinelearning
```

The first caption is the better bet: "least squares" is a term people have
heard, been examined on, and never had drawn for them. That gap is the hook.
