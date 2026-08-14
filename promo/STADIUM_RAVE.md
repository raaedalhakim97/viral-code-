# Stadium Rave — promo brief

Companion to `stadium_rave.py`. A 3D Lissajous curve dances liquid, then
collapses into the page's mark.

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

## The equation is the dance — not a metaphor

```
x = A·sin(a·u + δ)      y = B·sin(b·u)      z = C·sin(c·u + ε)
```

This is the same `sin(at), sin(bt)` from the Lissajous video already on the page.
The reason it is the right tool here is that **liquid dancing's documented move
vocabulary and this equation's parameters are the same two knobs.**

The rave form in the Jellyfish Jam scene is **liquid dancing** — the glowstick
dance out of the late-80s/90s underground, whose practitioners get called
"octopuses" because the motion never stops. Its core moves are *figure eights
handed from one hand to the other at the crossover*, *a wave that passes between
the arms*, and *wrist rolls layered on top*
([Rave Harmony](https://raveharmony.com/how-to-dance-at-a-rave-the-ultimate-guide/),
[City Dance](https://citydance.org/rave-dance-moves-for-beginners/)).

| The move | What it *is* in the equation |
| --- | --- |
| arm circles | **1:1** — a 1:1 ratio is an ellipse, a circle when A=B and δ=π/2, a straight line at δ=0 |
| **the figure eight** | **1:2** — a 1:2 ratio *is* a figure eight |
| hand-to-hand hand-off | **δ**, the phase offset — two tracers half a cycle apart, one leading, one following |
| wrist rolls / digits | higher ratios, **3:4** and **5:4** — `a` sets horizontal lobes, `b` vertical, so more lobes is finer detail |

Reference for the ratio→shape mapping:
[Wikibooks](https://en.wikibooks.org/wiki/Trigonometry/For_Enthusiasts/Lissajous_Figures),
[mathcurve](https://mathcurve.com/courbes2d.gb/lissajous/lissajous.shtml).

So **walking the ratio walks the move list**, and the phase term is the hand-off.
The equation on screen shows `a : b` updating live, so the viewer watches `1 : 2`
appear at the exact moment the figure eight forms.

**The trail is a glowing head with a fading tail because liquid dance is
performed with glowsticks.** That is historically what the motion looks like, not
a styling decision.

### The phase has to be anchored per move

Letting δ run from absolute zero meant the closing 1:2 arrived at δ = 16.8 rad
and read as two stacked ellipses rather than an eight. δ is now measured from the
beat the current move started on, so **every move opens on its canonical shape** —
1:1 begins as a straight line and opens into a circle, 1:2 begins as a clean
figure eight — and then morphs through the family, which is the liquid motion.

### What is not verified

**No frame-by-frame description of the SpongeBob animation exists in text, and
this build cannot watch video.** The vocabulary above comes from liquid/rave
dance sources generally — the style that scene depicts — not from that
animation. citydance.org is also blocked by this environment's egress proxy, so
it is cited from search results rather than the page.

---

## What happens

| Beats | Ratio | Move |
| --- | --- | --- |
| 0–8 | 1:1 | arm circles — opens from a line into a circle |
| 8–16 | **1:2** | **the figure eight** |
| 16–24 | 2:3 | the hand-off |
| 24–32 | 3:4 | wrist rolls |
| 32–40 | 5:4 | full liquid |
| 40–48 | 1:2 | back to the eight |
| 48–52 | — | the curve becomes the eye |
| 52–60 | — | PAUSE / OBSERVE / LEARN, the follow ask, the handle |

The ratio switches **on the bar line**, which is where a dancer changes move.
Amplitude pulses **on every beat** — that is the bounce. δ advances continuously
so the shape breathes. Two tracers, white and gold, sit half a cycle apart.

The whole thing is a **3D** Lissajous knot, projected here rather than with
manimgl's 3D camera: rotation about the vertical axis, a pitch, a perspective
divide, and depth-driven stroke width. **The pitch sign matters** — with
`− z·sin φ` the near side projects *higher* than the far side, which is the view
from underneath and turns the figure inside out. It must be `+ z·sin φ`.

At the end the curve does not fade and get replaced: the ghost stroke
**Transforms into the eye's outline**, because both are a single closed path. It
is the same line the whole way through.

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
This is one equation dancing: x = sin(au+δ), y = sin(bu), z = sin(cu).

Liquid dancing — the glowstick style from 90s raves — is built on three moves:
arm circles, figure eights handed from one hand to the other, and wrist rolls.
Every one of them is a setting of that equation.

a:b = 1:1 is a circle. a:b = 1:2 is a figure eight — literally, that's what a
1:2 Lissajous ratio draws. Push the ratio to 3:4 and 5:4 and you get the wrist
rolls. The phase δ is the hand-off: two glowsticks half a cycle apart, one
leading, one following.

So the curve isn't imitating the dance. The dance and the curve have the same
two knobs. Then it collapses into the logo.

One month ago this page didn't exist. Since then: linear algebra, embeddings,
attention, the maths behind how AI actually thinks — all of it drawn.

#mathtok #animation #manim #spongebob #stadiumrave
```

**YouTube title:** `A 3D Lissajous curve, and the two numbers behind it`

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
