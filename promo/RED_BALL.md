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
for **sixteen seconds** you try to keep hold of it.

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

Seed **142**, out of 150 searched, picked on two measurable properties of the
red ball across the all-white stretch:

| property | value | why it matters |
| --- | --- | --- |
| **it roams** | mean distance from its own average position = **0.71** of the radius | you cannot find it by staring at one spot |
| **it is crowded** | another ball within three ball-radii in **78%** of frames | this is the thing that actually makes the eye jump to the wrong ball |
| **its bounce count is unremarkable** | 7, against a median of 7 | so counting bounces cannot cheat it |

Both are re-asserted at import, so the difficulty is a property of the file
rather than a hope.

**All nine balls have identical speed and identical radius.** Once the colour is
gone there is no tell — asserted, because a video that cheats here is worthless.

### Verified at import

```
every ball's speed is constant     drift 7.8e-16 across all frames, all nine
every ball stays inside            max radius exactly R − r, never over
angle in == angle out              2.8e-16, every bounce
every ball actually bounces
the red ball roams and stays crowded   the two difficulty properties above
```

---

## Structure

| Beats | |
| --- | --- |
| 0–7 | *Can you follow the RED ball?* It is ringed. **Lock on.** |
| 7–13 | It moves, still red — six beats to get your eye on it |
| 13–53 | **The colour goes.** Sixteen seconds, nine identical balls, trails |
| 53–62 | Freeze. The balls are **numbered 1–9**. *Which one? Say it out loud.* |
| 62–74 | The reveal, and the decoys dim |
| 74–82 | *You could watch one. You could not watch nine. That limit is attention.* |
| 82–88 | *Every bounce was: angle in = angle out.* Then the series line |
| 88–92 | **Send this to your school friend — see if THEY can hold it** |
| 92–100 | The eye |

**The numbers at the freeze are the comment engine.** Without them, "did you get
it?" has no answer anybody can type. With them, every viewer has a number they
committed to before the reveal — and the caption asks for it. On a page where
comments are the growth channel, that is the single highest-value four beats in
the video.

**Sixteen seconds is deliberate.** Long enough that nearly everyone loses it,
short enough that the payoff still lands inside a scroll.

---

## Caption

```
Can you follow the RED ball?

Nine balls. One is red — for six seconds. Then the colour goes and they're all
identical: same size, same speed, no tells. That's not a figure of speech, it's
in the code.

Sixteen seconds. Then they freeze, they get numbered, and you have to commit.

Comment your number BEFORE you watch the end. No editing it after 👀

—

Two things nobody tells you about this game:

Every single bounce is one line of school maths. Angle in = angle out. The ball
hits the wall, the part of its motion going INTO the wall flips, the part
sliding ALONG the wall doesn't. That's it. That's the whole physics engine.

And the reason you lost the ball? You could watch one. You could not watch nine.

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
