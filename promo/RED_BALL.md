# Can you follow the RED ball?

Companion to `red_ball.py`. A tracking game — and then the reason it is hard.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **Can you follow**
> **the RED ball?**

Nine balls bounce inside a circle. One is red. It turns white with the rest, and
for **fourteen seconds** you try to keep hold of it.

**There is no reveal.** The balls freeze, they get numbered, and the video asks
for a number instead of giving one. The answer is **number 5** — pinned in the
comments, and the whole of part 2.

---

## Why this belongs on this page, and is not just a repost

Two reasons, and both are honest.

### 1. The bounce is an angle problem

Every bounce in this video is one line:

```
v'  =  v  −  2 (v · n) n
```

where `n` is the direction straight out from the centre. That is **the dot
product from the cos episode**, doing the only job it does here: splitting the
velocity into the part running along the wall and the part running into it, and
flipping the second one.

Angle in equals angle out — and it is **asserted, every bounce**, to 1e-12,
rather than assumed. The measured reflection error across the whole run is
**2.8e-16**.

### 2. Losing the ball is what *attention* means

You could watch one. You could not watch nine. That limit is exactly the problem
the attention mechanism exists to solve, and **feeling it for sixteen seconds
explains it better than a diagram does.** That is the closing beat, and it is
what makes this an AI video rather than a party trick.

---

## The seed is chosen, not random

Seed **142**, from a 200-seed search **at this exact speed and beat layout**,
picked on measurable properties of the red ball across the all-white stretch.
Re-run `red_ball_seed_search.py` if `SPEED`, `N` or the beats change — a seed
that is hard at one speed is not hard at another.

| property | value | why it matters |
| --- | --- | --- |
| **it roams** | mean distance from its own average position = **0.71** of the radius | you cannot find it by staring at one spot |
| **it is crowded** | another ball within three ball-radii in **82%** of frames | this is the thing that actually makes the eye jump to the wrong ball |
| **its bounce count is unremarkable** | 9, against a median of 9 | so counting bounces cannot cheat it |
| **its number is 5** | neither 1 nor 9 | the reading order gives nothing away |

Both are re-asserted at import, so the difficulty is a property of the file
rather than a hope.

**All nine balls have identical speed and identical radius.** Once the colour is
gone there is no tell — asserted, because a video that cheats here is worthless.

### Verified at import

```
every ball's speed is constant     drift 7.8e-16 across all frames, all nine
every ball stays inside            max radius exactly R − r, never over
angle in == angle out              5.6e-16, every bounce
every ball actually bounces
the red ball roams and stays crowded   the two difficulty properties above
the answer is not 1 and not 9      or the numbering leaks it
the labels are a permutation of 1..9   no two balls share a number
```

---

## Structure

| Beats | |
| --- | --- |
| 0–6 | *Can you follow the RED ball?* It is ringed. **Lock on.** |
| 6–11 | It moves, still red — five beats to get your eye on it |
| 11–45 | **The colour goes.** Fourteen seconds, nine identical balls, trails |
| 45–56 | Freeze. The balls are **numbered 1–9**. *Pick a number. Out loud. Now.* |
| 56–70 | **PART 2 has the answer. Comment your number below.** No reveal |
| 70–78 | *You could watch one. You could not watch nine. That limit is attention.* |
| 78–86 | *Every bounce was: angle in = angle out.* Then the series line |
| 86–92 | **Send this to your school friend — see if THEY can hold it** |
| 92–100 | The eye |

**The numbers at the freeze are the comment engine.** Without them, "did you get
it?" has no answer anybody can type. With them, every viewer has a number they
committed to before the reveal — and the caption asks for it. On a page where
comments are the growth channel, that is the single highest-value four beats in
the video.

**Fourteen seconds at speed 0.82 is deliberate.** Fast enough that nearly
everyone loses it inside five, short enough that the ask still lands inside a
scroll.

**Withholding the reveal is the whole point of this cut.** A reveal ends the
video. A withheld reveal sends the viewer to the comments — which on a page this
size is the only place growth actually comes from. `ANSWER` is derived from the
simulation rather than typed, so part 2 cannot contradict part 1.

---

## Caption

```
Can you follow the RED ball?

Nine balls. One is red — for six seconds. Then the colour goes and they're all
identical: same size, same speed, no tells. That's not a figure of speech, it's
in the code.

Fourteen seconds. Then they freeze, they get numbered, and you have to commit.

COMMENT YOUR NUMBER 👇 No editing it after.

The answer is pinned in the comments — and the full reveal is PART 2.

—

Two things nobody tells you about this game:

Every single bounce is one line of school maths. Angle in = angle out. The ball
hits the wall, the part of its motion going INTO the wall flips, the part
sliding ALONG the wall doesn't. That's it. That's the whole physics engine.

And the reason you lost it? You could watch one. You could not watch nine.

That limit has a name. It's called attention — and it is the one idea inside
every AI you have ever used. The whole reason ChatGPT works is a mechanism for
deciding what to watch and what to let go of, because it has the same problem
you just had.

You didn't fail the test. You demonstrated it.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #attention #physics #illusion #howaiworks
```

**YouTube title:** `Can you follow the red ball? (and why you can't)`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl red_ball.py RedBall -w -r 1080x1920
python3 cinegrade.py videos/RedBall.mp4 red_ball.mp4
```

## Changing the difficulty

`SEED`, `N` and `SPEED` at the top. Change any of them and the two difficulty
assertions re-run — a seed where the red ball loiters in one corner, or drifts
around on its own, **fails the render**. Re-run the search in
`red_ball_seed_search.py` to find a new one rather than guessing.

## Part 2

The answer is **number 5**, and `red_ball.py` exposes it as `ANSWER` so
part 2 can import it rather than repeat it. Part 2 needs the same `SEED`,
`SPEED` and beat layout, or the freeze frame — and therefore the numbering —
will not match what part 1 showed.
