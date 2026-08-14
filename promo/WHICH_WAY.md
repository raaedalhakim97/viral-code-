# Which way is it spinning?

Companion to `which_way.py`. A **spectacle** video, not a lesson — and the one
built to start arguments.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## What it is for

`the_sync.py` earns a follow by being satisfying. **This one earns comments by
being unresolvable.** A globe of dots turns on a vertical axis with every depth
cue removed. Half the room sees it going left, half sees it going right, and
both are right.

That is the whole engine: people do not argue with the page, they argue with
**each other**. Comments-per-view is the highest of any format, because every
reply is somebody insisting the other person is blind.

---

## It is genuinely ambiguous, and that is proven, not asserted

The dots sit on rings, an **even** number to a ring, equally spaced in angle
around it. Rotating the whole set by `+a` and by `−a` gives two point sets whose
**flat projections are identical** — because each ring is symmetric under
`z → −z`, and an orthographic projection throws `z` away.

```
measured difference between the two pictures:  2e-15
                    over 132 dots and 96 angles
```

Float noise. Not a visible quantity. **There is nothing on screen that could
tell them apart** — so a viewer who is certain it goes left is not making a
mistake, and neither is the one who is certain it goes right. Their brain is
supplying a sign the picture never contained.

### Verified at import

```
+a and -a project to identical pictures    to 2e-15, over 96 angles
every ring has an even dot count           which is why the above holds
the poles sit on the axis                  they must not drift
the rotation rate is constant              any wobble leaks the direction
```

The comparison sorts both pictures into a canonical order before subtracting,
so it tests that the two are the same **set of points** — not that dot *k*
happens to land where dot *k* landed.

---

## The payoff, which is the honest bit

Fade in **one** depth cue — near dots brighter and larger — and the direction
snaps into place. Then flip the same cue, and it snaps the other way, with the
motion itself completely unchanged.

```
cue =  0     every dot identical. ambiguous.
cue = +1     near dots bright and large.  it "obviously" goes one way
cue = -1     far dots bright and large.   it "obviously" goes the other
```

The viewer watches their own perception reverse while nothing about the
animation does. That is what turns a gimmick into something worth following:

> **a flat picture has no depth. your brain guessed — and never told you.**

---

## Why the dots must be identical with the cue off

Any variation at all — a colour gradient, a connecting line, a size difference,
a trail — collapses the ambiguity and the video quietly stops being true. With
`cue = 0` every dot is the same size, colour and opacity. That is a constraint,
not a style choice.

**The dots visibly pair up twice per turn, and that is unavoidable.** For the two
directions to project identically, the point set must be mirror-symmetric about
some plane through the axis — and at the moment the picture faces that plane,
every mirrored pair lands on the same spot. It reads as a pulse. It is the price
of exactness, and it is cheap.

---

## The globe

Rings are spaced evenly in **height**, not in latitude, so they land evenly on
screen instead of bunching at the equator. Dots per ring scale with the ring's
circumference, so density is even and it reads as a solid turning body. Alternate
rings are offset by **half a step**, which kills the vertical striping — and a
half-step offset is exactly the one phase shift that leaves a ring symmetric
under `z → −z`, so the proof survives it.

| | |
| --- | --- |
| rings | 9, at heights ±0.92 ±0.69 ±0.46 ±0.23 and 0 |
| dots per ring | 8, 14, 16, 18, **18**, 18, 16, 14, 8 — plus 2 poles |
| total | 132 |
| turn | 4.0 s = 10 beats, constant |

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | **WHICH WAY IS IT SPINNING?** *left, or right?* |
| 8–40 | Let them look. Let them commit. *pick one. out loud.* |
| 40–56 | *half of you said left. half said right. **you are both correct.*** |
| 56–78 | The cue fades in, then flips. *the dots never changed direction. not once.* |
| 78–86 | *a flat picture has no depth. your brain guessed — and never told you.* |
| 86–92 | **COMMENT WHICH WAY** you saw it first |
| 92–100 | The eye |

The long 32-beat stretch at 8–40 is deliberate and is the most important part of
the video. People need time to **commit** to an answer before being told the
other half disagrees — a viewer who has not yet decided has nothing to defend,
and nothing to defend means no comment.

---

## Caption

```
Which way is this spinning?

Say it out loud before you scroll. Left, or right.

Now go read the comments. Half the people there are certain it's the opposite of
what you just said — and they are watching the exact same video.

Here's the part nobody tells you: they're right too.

The dots sit on rings, an even number to each ring. Spin that set one way or the
other and the flat picture that reaches your screen is IDENTICAL — I measured it,
the difference is 0.000000000000002. There is no depth on a screen. There never
was. The direction you're so sure about is not in the video. Your brain put it
there and didn't mention it.

Watch the last part again. I change ONE thing — which dots are brighter — and the
whole thing reverses. The dots never change direction. Not once.

Comment which way you saw it FIRST. Then check the replies.

#opticalillusion #illusion #maths #mathtok #satisfying #whichway #brain
```

**YouTube title:** `Which way is it spinning? Half of you are wrong — and so is the other half`

---

## Posting

Top-of-funnel. No formula on screen, nothing to understand, no prior episode
needed.

**Pin a comment with your own answer** — "I see it going right" — and reply to
the first few people who disagree. Comment threads where the account argues back
run several times longer than threads where it does not, and length is what the
ranker reads.

---

## Changing it

`HEIGHTS`, `EQUATOR_DOTS` and the beat layout at the top. The assertions refuse
to build anything where the two directions are distinguishable, so an odd ring
count, a phase offset that is not a half step, or a pole that drifts off the axis
all fail the render rather than shipping a video whose central claim is false.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl which_way.py WhichWay -w -r 1080x1920
python3 cinegrade.py videos/WhichWay.mp4 which_way.mp4
```
