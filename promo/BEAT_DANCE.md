# Beat Dance — video brief

Companion to `beat_dance.py`. One line, moving on the beat: Lissajous curves
morphing ratio to ratio, then a Fourier square wave built one harmonic at a time.

- **Output:** `videos/BeatDance.mp4` — 1440×2560, 60fps
- **Length:** exactly **64 beats = 16 bars**. At 120 BPM that is 32.000s.
- **Audio:** **none, deliberately.** See below.

---

## The song does not go in the file

Add the trending sound in the TikTok editor, not here. This is not a limitation
to work around — it is the correct workflow, for three reasons:

1. **Attribution.** Audio baked into an upload cannot be attributed to the
   sound's page. The sound page is where a trending audio's reach actually
   comes from; bake it in and you forfeit that entirely.
2. **Timing.** Trending sounds peak in 5–14 days, and posting inside the first
   24 hours of a sound's rise is worth roughly 3× the views of posting after
   peak. A sound picked on render day is often dead by posting day.
3. **Licensing.** TikTok's in-app library is licensed for use on TikTok. A song
   file dropped into a render is not.

So: render silent, pick the sound the day you post, set the BPM to match.

---

## Matching a track

Find the track's BPM (any BPM-detection tool, or tap it out), then:

```bash
manimgl beat_dance.py BeatDance -w --bpm 128
```

Every animation in the scene is a whole or half multiple of `B = 60/BPM`, so
changing BPM rescales the entire piece and it stays locked. Length follows:

| BPM | Length |
| --- | --- |
| 100 | 38.4s |
| 120 | 32.0s |
| 128 | 30.0s |
| 140 | 27.4s |
| 150 | 25.6s |

**Verify before you trust it.** The scene writes a click track at the same tempo:

```bash
python3 beat_dance.py --click 128 click.wav
ffmpeg -i videos/BeatDance.mp4 -i click.wav -c:v copy -shortest check.mp4
```

Watch `check.mp4`. The line's stroke punches on every beat and a gold ring snaps
out on every bar line. If those drift against the click, the BPM is wrong — the
scene itself cannot drift, because nothing in it is off-grid.

---

## The beat budget

64 beats, so the piece ends **on** a bar line and loops clean. The first cut of
this came out at 59.5 beats and ended mid-bar, which shows immediately when you
lay it against a track.

| Section | Beats | What happens |
| --- | --- | --- |
| Wake | 8 (2 bars) | A point becomes a circle, breathing on the beat |
| Dance | 24 (6 bars) | 12 Lissajous ratios, one morph every 2 beats |
| Build | 16 (4 bars) | Sine → square wave, one harmonic per beat |
| Close | 16 (4 bars) | Eye, PAUSE / OBSERVE / LEARN, follow CTA |

**If you change a section length, rebalance another to keep the total at 64.**
Otherwise the last frame lands mid-bar.

---

## Why these visuals

Lissajous figures are the honest answer to "math that dances" — they are
literally two perpendicular oscillations, which is what dancing is. The ratio
label (`3 : 4`) tells the viewer the shape *is* the number, so the visual is not
decoration on top of a caption, it is the caption.

The Fourier section earns the payoff: watching a square wave assemble out of
sine waves is one of the few genuinely surprising things in undergraduate math,
and the Gibbs ringing at the corners — the overshoot that never goes away no
matter how many harmonics you add — is visible in the render. That is real.

---

## Build

```bash
cd promo
xvfb-run -a -s "-screen 0 1600x1200x24" manimgl beat_dance.py BeatDance -w --bpm 128
python3 cinegrade.py videos/BeatDance.mp4 beat_dance_graded.mp4
```

Grade it. This piece is pure line-on-black, which is exactly what bloom is for —
ungraded it reads as a plot, graded it reads as light.

No narration on this one. It is a sound-led piece; Alan would fight the track.
