# Part 2 — the answer, and then the real trick

Companion to `red_ball_2.py`. The sequel to `red_ball.py`.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## It imports part 1 rather than repeating it

The paths, the freeze frame, the numbers on the balls, the answer itself **and
the physics engine** all come from `red_ball.py`. Nothing is retyped.

That matters more than it sounds. Getting the answer wrong between two videos is
the one mistake that destroys both at once — and it is exactly the mistake a
viewer who screenshots part 1 and pauses part 2 will catch. Importing makes it
impossible rather than unlikely.

`red_ball.py` was refactored to expose `simulate(seed, frames, n, speed)` and
`label_order(path)` so round 2 can use the same bounce code. **Part 1's output
is byte-identical after that change** — verified by hashing `PATH` before and
after.

---

## Structure

| Beats | |
| --- | --- |
| 0–5 | **A hard cut onto part 1's exact final frame.** Same trails, same nine balls, same numbers |
| 5–10 | *You picked a number. No changing it now.* |
| 10–20 | **NUMBER 5.** The reveal, decoys dimmed — *"or thought you were"* |
| 20–27 | **ROUND 2.** New run, new red ball, *lock on* |
| 27–58 | The colour goes — and the **taunts start appearing at the top** |
| 58–68 | Freeze, number them, **NUMBER 3** |
| 68–80 | *You read all that, didn't you. That is exactly when you lost it.* |
| 80–88 | Attention, named — then the series line |
| 88–93 | **Send this to whoever said the wrong number** |
| 93–100 | The eye |

**The opening is a cut, not a fade.** Landing instantly on part 1's last frame
is the continuity gag, and it also sidesteps a real manim trap: fading a mobject
whose updater rewrites its point count every frame breaks the interpolation
(`could not broadcast (105,3) into (3,3)`). Part 1 got away with `FadeIn` on its
trails only because they started empty.

---

## The trick, which is the actual video

While the viewer is holding on to the round 2 ball, text starts appearing at the
**top of the screen**, well outside the circle:

```
        I'm telling you —
        you can't
        you're reading this
        aren't you
        that's the trick
```

Reading those words costs you the ball. Keeping the ball costs you the words.
**There is no way to have both** — and that is not a gimmick, it is the
definition of attention, performed on the viewer instead of described at them.

Part 1 said *"you could not watch nine."* This one proves you could not even
watch **two**.

> **the ball, or the words. you were never going to get both.**

Every taunt is asserted to land inside the tracking stretch. One that arrived
after the freeze would cost nothing, and the video would be lying about what it
just did to you.

---

## Two rounds, two seeds

| | seed | red index | answer | crowded | roams |
| --- | --- | --- | --- | --- | --- |
| round 1 | 142 | 0 | **5** | 82% | 0.71 |
| round 2 | 50 | 4 | **3** | 84% | 0.48 |

**Round 2's answer is deliberately not 5.** Repeating the number would make the
whole thing look rigged, and the assertion refuses to build if it does. Both
answers are also asserted to be neither 1 nor 9, so the left-to-right reading
order gives nothing away in either round.

### Verified at import

```
part 1's constants are unchanged      seed, speed, ball count
round 2's physics is exact            speed drift, containment, reflection
round 2's ball roams and stays crowded
round 2's answer != part 1's, and is not on the edge
both label sets are permutations of 1..9
every taunt lands inside the tracking stretch
```

---

## Caption

```
PART 2. The answer is NUMBER 5.

Screenshot part 1 and check — same frame, same trails, same numbers. Nothing
moved.

Now round 2. Same game, new ball. And this time watch what happens.

…

You read the words at the top, didn't you.

That's the trick. That IS the video. Reading them cost you the ball. Keeping the
ball would have cost you the words. There was never a version where you got
both.

Round 2's answer was NUMBER 3.

Part 1 showed you that you can't watch nine things. This one shows you that you
can't watch two.

Choosing what to drop has a name. It's called attention — and it is the one idea
inside every AI you've ever used. A model can't look at everything either. The
entire trick of a transformer is deciding, every single word, what to hold on to
and what to let go.

You didn't fail it. You demonstrated it.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #attention #illusion #physics #howaiworks
```

**YouTube title:** `Part 2 — the answer, and the trick you fell for`

---

## Posting

Post this **after** part 1's comments have filled up, not the same day. Reply to
the wrong guesses on part 1 with *"part 2 is up"* rather than the answer — the
answer is what part 2 is for.

The share line changed from part 1's. *"Send this to whoever said the wrong
number"* only works once there is somebody who said a wrong number, which is
exactly the state part 1 leaves the comment section in.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl red_ball_2.py RedBall2 -w -r 1080x1920
python3 cinegrade.py videos/RedBall2.mp4 red_ball_2.mp4
```

Part 1 must be rendered from the same `red_ball.py` this imports. Change `SEED`,
`SPEED` or the beat layout there and **both videos need re-rendering**, or the
freeze frames stop matching and the continuity gag breaks.
