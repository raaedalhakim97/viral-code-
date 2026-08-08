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

## No figure — 18 lines in a ring

The subject is **18 straight lines standing in a circle in 3D**. Nothing is a
body. The dance is applied to the lines directly:

| | |
| --- | --- |
| `bounce = \|sin(πb)\|` | one hard hit per beat, on **Y** |
| `sway = sin(πb)` | reverses every beat, so the rock spans **two** beats |
| `lean` | radial, driven by sway — moves **X and Z together** |
| `stretch` | each line grows on the beat and settles between |
| phase `2i/N` | the same motion delayed around the ring, so a **wave travels** through the formation instead of all 18 moving as one block |

The two rhythms are the point. One alone is a metronome; bouncing on the beat
while rocking across two is what makes it read as dancing rather than blinking.

### What the motion is and is not based on

The source is the **Jellyfish Jam** rave — SpongeBob S1E7b, 1999 — where the
track is "Stadium Rave" by Mark Govener, APM stock techno from *Clubmix*, in the
same lane as 2 Unlimited's "Get Ready For This".

**No frame-by-frame choreography for that scene exists in text, and this build
could not watch the footage.** So what is reproduced is the motion *character*
of four-on-the-floor rave — the hard downbeat, the two-beat rock, a crowd of
uprights leaning in waves — not a transcription of specific moves. Worth being
straight about, because "studied the dance" would overstate it.

### Depth is computed, not faked

The projection is done in the file rather than with manimgl's 3D camera: a
rotation about the vertical axis, a pitch, a perspective divide, then per-line
stroke width and opacity taken from the resulting depth. Near lines are thick
and bright, far lines thin and dim, and the ring orbits about one turn across
the video.

**The pitch sign matters and I got it wrong first.** With `yr = y·cos φ − z·sin φ`
the near side of the ring projects *higher* than the far side, which is what you
see looking up from underneath — the formation reads inside-out. It has to be
`+ z·sin φ` to look down on the ring.

---

## What happens

| Beats | |
| --- | --- |
| 0–14 | **The ring dances.** Nothing else on screen. This is the whole hook. |
| 14–20 | "every video here is one line" |
| 20–28 | The 18 lines flatten into a **sine wave** |
| 28–36 | They snap to a **square wave** — *7 harmonics* |
| 36–44 | Back to the ring. "math you can watch move" |
| 44–52 | They re-form as the **observer eye** |
| 52–60 | PAUSE / OBSERVE / LEARN, the follow ask, the handle |

Every target shape is also **18 parts** — the sine and square split into 18
arcs, the eye into 5 + 5 lids, 5 pupil-ring, 1 pupil, 2 chips. So the same
eighteen lines fly into every shape. Nothing is added or removed, which is the
claim the promo is making.

**The square wave is real.** An odd-harmonic partial sum to 7 terms, so the
overshoot at each edge is genuine Gibbs ringing rather than a drawn squiggle —
and it is the exact figure from the Fourier video already on the page. The promo
quotes the catalogue instead of describing it.

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
Eighteen lines, dancing in three dimensions.

Then they flatten into a sine wave. Then they snap into a square wave — seven
harmonics, real ones, which is why the corners ring like that. Then they become
the logo.

Same eighteen lines the whole time. Nothing added, nothing removed.

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
