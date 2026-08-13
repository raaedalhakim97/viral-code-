# How you turn anything — with sin and cos

Companion to `rotate_it.py`. **Episode 7 of "WHY DID WE LEARN THIS?"** — and
the direct sequel to episode 5.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **how do you TURN something?**
> *sin and cos do the whole job*

---

## The spine

```
new x  =  x · cos θ  −  y · sin θ
new y  =  x · sin θ  +  y · cos θ
```

Same shell as every episode, and the same naming as episode 4's
`new = old − step · slope` — *new* means "after one move" across the series.

| slot | comes from | direction |
| --- | --- | --- |
| **cos θ, sin θ** ← 0.8, 0.6 | **episode 5.** A recall card, straight into all four slots | handed back |
| **x** ← 3 | counted across on the grid | dragged **up** |
| **y** ← 4 | counted up on the grid | dragged **up** |
| **new x, new y** → 0, 5 | worked out inside the equation | dropped **down**: the arrow swings there |

**Episode 5 built the ingredients, so this one does not have to earn them
again.** That is what makes a nine-piece formula fit in forty seconds: the only
things the viewer has to find on the picture are the two numbers of the point
itself.

---

## The numbers

```
point   (3, 4)                 counted off the grid
turn    cos θ = 0.8, sin θ = 0.6

new x = 3(0.8) − 4(0.6) = 2.4 − 2.4 = 0
new y = 3(0.6) + 4(0.8) = 1.8 + 3.2 = 5
```

**The arrow lands on (0, 5).** Dead straight up, exactly 5 tall. That is the
whole reason these numbers were chosen: the payoff is a place the eye can check
in half a second, and the `0` arrives as a visible **2.4 − 2.4** rather than as
a claim.

**Turning never changes length.** 5 in, 5 out — and the picture says so, because
`(3,4)` and `(0,5)` are both obviously the 3-4-5 hypotenuse.

**Why there is a minus.** It is the question every student has about this
formula and nobody ever answers. Turning up-and-left means the height starts
eating into the width, so the `y` term comes *off* the new x. The video says it
in one line, at the exact moment the 2.4 cancels the 2.4 — which is the only
moment it can be felt rather than asserted.

### Verified at import

```
cos² + sin² == 1                  exactly, as Fractions
the rotation lands on (0, 5)      in Fractions, not floats
length in == length out == 25     turning cannot change length
it matches a real rotation matrix against np.cos/np.sin at the true angle
it lands at exactly 90°           or the payoff does not read
every number shown is exact       0.8 0.6 2.4 1.8 3.2 — one decimal each
the slot map matches the spine    every S_X index really does hold an "x"
```

That last one is worth keeping. With eighteen flat slots across two rows, an
off-by-one in the slot map would silently drop `3` into a `·` and nothing would
crash — it would just be wrong on screen.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *how do you TURN something?* |
| 8–24 | One arrow on a grid: across 3, up 4 |
| 24–37 | **From last time:** cos θ = 0.8, sin θ = 0.6 → four slots filled for free |
| 37–52 | 3 and 4 dragged up. The equation is full |
| 52–82 | 2.4 − 2.4 = **0**, 1.8 + 3.2 = **5**, and the arrow swings to (0, 5) |
| 82–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

---

## Caption

```
How do you TURN something? Sin and cos do the whole job.

Your arrow: across 3, up 4. That's all an arrow is — two numbers.

Now turn it. Here's the formula school gave you and never explained:

new x = x cos θ − y sin θ
new y = x sin θ + y cos θ

You already know cos θ and sin θ from last time: 0.8 and 0.6. Four slots filled
for free.

new x = 3(0.8) − 4(0.6) = 2.4 − 2.4 = 0
new y = 3(0.6) + 4(0.8) = 1.8 + 3.2 = 5

The arrow is now at (0, 5). Dead straight up.

And THAT is what the minus is for. As you turn up and to the left, the height
starts eating into the width — so the y term comes OFF the new x. Watch the 2.4
cancel the 2.4. That's the minus doing its job.

One more thing: 5 long before, 5 long after. Turning never stretches anything.

Every screen that rotates, every game camera, every 3D model, every arrow spun
in an AI's meaning-space — this, a few million times a second.

We learned this at school. Nobody ever said what for.

#maths #mathtok #trigonometry #sincos #rotation #gcse #ai
```

**YouTube title:** `How to turn anything — the rotation formula, explained`

---

## Subtitle track

`rotate_it.srt` — no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the point or the angle

`X`, `Y`, `COS` and `SIN` at the top are the only things to edit, and every
assertion pins the current answers — deliberately. The 90° assertion is the
important one: it fails the moment a change stops the arrow landing somewhere
the eye can check, which is the whole reason this particular pair was picked.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl rotate_it.py RotateIt -w -r 1080x1920
python3 cinegrade.py videos/RotateIt.mp4 rotate_it.mp4
```
