# Stadium Rave — promo brief

Companion to `stadium_rave.py`. The line gets up and dances, then collapses into
the page's mark.

- **Output:** 1080×1920, 60fps, **28.800000s** — 60 beats = 15 bars at **125 BPM**
- **Sound:** **Stadium Rave** (SpongeBob). Added in the TikTok editor, not baked in.

---

## The tempo is 125, and that broke an assumption

Every other scene in this repo runs at 150 BPM, where one beat is 0.4s —
**exactly 24 frames** at 60fps. Convenient, and I had quietly relied on it.

"Stadium Rave" is **125 BPM**: one beat is 0.48s = **28.8 frames**, which is not
a whole frame. Rounding each `run_time` independently, the way every earlier
scene does, drifts by a frame here and there and the loop stops closing.

`T()` now snaps the **cumulative** position to the frame grid and returns the
difference, so error cannot accumulate:

```python
f0 = round(used_before * B * FPS)
f1 = round(used_after  * B * FPS)
run_time = (f1 - f0) / FPS
```

At 125 BPM, a whole number of frames needs a multiple of **5** beats and a whole
number of bars needs a multiple of **4**, so the total must be a multiple of 20.
60 beats satisfies both: 15 bars, 1728 frames, 28.800000s exactly.

**This `T()` is the better one and should be back-ported** to the other scenes if
any of them ever move off 150.

### Verify the tempo before you post

125 BPM is what the trackers report for the original. **TikTok sounds are
frequently sped-up edits**, and a sped-up Stadium Rave will not be 125:

```bash
python3 stadium_rave.py --click 125 click.wav
ffmpeg -i videos/StadiumRave.mp4 -i click.wav -c:v copy -shortest check.mp4
```

If the clicks drift against the bounce, re-render with the real number —
`BPM=` is an environment variable and nothing is hard-coded.

Sources for 125: [SongBPM](https://songbpm.com/@spongebob-squarepants/stadium-rave),
[GetSongBPM](https://getsongbpm.com/song/stadium-rave/YvZDjp),
[Musicstax](https://musicstax.com/track/stadium-rave/70OkogQFdbKotGlMKEMGXB).

---

## What happens

| Beats | |
| --- | --- |
| 0–12 | **The dance.** Nothing else on screen. This is the whole hook. |
| 12–20 | "every video here is one line" |
| 20–28 | The figure unfolds into a **sine wave** |
| 28–36 | It snaps to a **square wave** — *7 harmonics* |
| 36–44 | Back to dancing. "math you can watch move" |
| 44–52 | It collapses into the **observer eye** |
| 52–60 | PAUSE / OBSERVE / LEARN, the follow ask, the handle |

The figure is **six strokes** — head, torso, two arms, two legs — and every
target shape is also six strokes, so the same six lines fly into the sine wave,
into the square wave, into the eye. Nothing is added or removed; it is one line
the whole way through, which is the claim the promo is making.

**The square wave is real.** It is an odd-harmonic partial sum to 7 terms, so the
overshoot at each edge is genuine Gibbs ringing rather than a drawn squiggle —
and it is the exact figure from the Fourier video already on the page. The promo
quotes the catalogue instead of describing it.

---

## Getting the dance to read

The first pass used small amplitudes and folded the forearms back across the
head. It read as a stick figure fidgeting, not dancing. Three things fixed it:

- **Exaggerate past what feels right.** Bounce 0.17 → 0.30, sway 0.10 → 0.20,
  lean 0.20 → 0.26. On a phone, at speed, subtle is invisible.
- **Arms up and OUT.** Upper arms at 144° / 36° so the elbows clear the head,
  with the forearms punching toward vertical on every beat. That is the
  jellyfish-rave read, and it is why both arms move together rather than
  alternating like a walk.
- **Two rhythms, not one.** `bounce = |sin(πb)|` lands once per beat;
  `sway = sin(πb)` reverses every beat. The figure bounces on the beat while
  rocking across two — which is what stops it looking like a metronome.

---

## One trap worth writing down

**Never name a Scene method `run()`.** `Scene.run()` is manimlib's own entry
point; overriding it replaced the render loop, and the sequence fired before
`construct` had set any state. The error surfaced as
`AttributeError: 'StadiumRave' object has no attribute 'used'`, which points
nowhere near the actual cause.

---

## Caption

```
Every video on this page is one line. Here it is dancing.

Then it unfolds into a sine wave. Then it snaps into a square wave — seven
harmonics, real ones, which is why the corners ring like that. Then it becomes
the logo.

Same line the whole time. Nothing added, nothing removed.

One month ago this page didn't exist. Since then: linear algebra, embeddings,
attention, the maths behind how AI actually thinks — all of it drawn.

#mathtok #animation #manim #spongebob #stadiumrave
```

`#spongebob` and `#stadiumrave` are the reason this one can travel. They are
enormous pools that the maths hashtags are not, and the sound page is where a
trending audio's reach comes from — which is exactly why the render is silent
and the track goes on in the editor.

---

## Build

```bash
cd promo
BPM=125 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl stadium_rave.py StadiumRave -w -r 1080x1920
python3 cinegrade.py videos/StadiumRave.mp4 stadium_rave.mp4
```
