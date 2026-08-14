# Wait for it — fifteen dots that always come back

Companion to `the_sync.py`. A **spectacle** video, not a lesson.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## What it is for

Its job is to be **watched twice and followed** — not to teach. The library
teaches; this brings people to the library.

Fifteen dots start in a perfect vertical line, break into travelling waves,
twist into something that looks completely random — and then snap back into a
straight line at an exact instant. Then do it again.

---

## Nothing is faked, and that is why it works

Dot *k* swings at

```
ω(k) = 2π (K0 + k) / T
```

so the slowest makes **10** swings per cycle and the fastest makes **24** — each
one exactly *one more* than the dot above it. Every frequency is a whole number
of cycles per `T`, so at `t = 0, T, 2T` every sine is zero at the same moment.

**The alignment is arithmetic, not animation.** Measured `max |sin|` at the
realignment instants is **2e-14** — float noise, not a fudge.

| | |
| --- | --- |
| sync period `T` | 12.8 s = 32 beats |
| motion window | beat 6 → 70 = 25.6 s = **exactly two cycles** |
| aligned at | beats 6, 38, 70 |

### Verified at import

```
every dot is dead centre at t = 0, T and 2T      to 1e-12
the swing counts are consecutive integers        10, 11, 12 ... 24
the motion window is a whole number of cycles    or it ends mid-chaos
no two dots share a frequency                    or they never separate
```

---

## The reveal is the numbers themselves

At the end the dots freeze in line and each is labelled with its swing count:
**10, 11, 12 … 24**. The reason becomes visible without a word of explanation —
*they were never random, they were counting.*

That is the whole payoff, and it is why this earns a follow rather than just a
like: the viewer gets the trick **and** the reason inside forty seconds.

---

## Structure

| Beats | |
| --- | --- |
| 0–6 | **WAIT FOR IT.** Fifteen dots, one straight line, still |
| 6–38 | Cycle one — apart, chaos, back together |
| 38–70 | Cycle two |
| 70–84 | Frozen in line. The swing counts appear: *each swings once more than the one above* |
| 84–92 | **FOLLOW — and the next one is better** |
| 92–100 | The eye |

**The dots hold at the aligned position after beat 70**, not wherever the clock
happened to stop. `t_motion()` clamps to the run length, so the freeze frame is
always the perfect line.

---

## Caption

```
Wait for it.

Fifteen dots. One straight line. Watch them fall apart — and then come back.

Nothing here is edited or timed by hand. Each dot swings exactly ONE more time
than the dot above it: 10, 11, 12, all the way to 24.

That's it. That's the whole trick.

Because every one of them is a whole number of swings, there is exactly one
moment where all fifteen are back in the middle at once — and it arrives, every
time, like clockwork. They were never random. They were counting.

Watch it twice. The second time, follow one dot.

#satisfying #maths #mathtok #physics #oddlysatisfying #waitforit #sync
```

**YouTube title:** `Wait for it — 15 dots that always come back`

---

## Posting

**This is a top-of-funnel video.** No formula on screen, nothing to understand,
no prior episode needed. It exists to be shared by people who will never watch a
maths video — and to hand them a reason to follow at the exact moment they are
most impressed.

Pin a comment saying **"follow one dot on the second watch"**. It doubles watch
time on the same forty seconds, and rewatch is the metric Shorts actually rewards.

---

## Changing it

`N`, `K0` and the beat layout at the top. The assertions will refuse to build
anything that does not realign exactly — a non-integer frequency ratio, a motion
window that is not a whole number of cycles, or two dots sharing a frequency.
Those three mistakes are the only ways this video can be quietly wrong.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl the_sync.py TheSync -w -r 1080x1920
python3 cinegrade.py videos/TheSync.mp4 the_sync.mp4
```
