# three.js videos

Real 3D, rendered headlessly in Chromium frame by frame, encoded with ffmpeg.
Everything here is free: three.js, Playwright's Chromium, ffmpeg, abc2midi,
FluidSynth and the FluidR3 GM soundfont.

| Scene | Output | Length |
| --- | --- | --- |
| `scene_smart_lookup.js` | Smart Lookup, 3D rebuild of `promo/smart_lookup/smart_lookup.py` | 95.0s, 2850 frames |
| `scene_butterfly.js` | The Butterfly Effect: Lorenz attractor in deep space | 40.0s, 1200 frames |
| `scene_collatz.js` | The Collatz Conjecture: 1..10,000 grown as one coral | 40.0s, 1200 frames |
| `scene_euler.js` | 8s test: 2,144 points fly into the Euler curve | 8.0s |

All are 1080x1920 at 30fps, laid out for the TikTok / Reels / Shorts safe box.

## Render

```bash
cd promo/three
npm install                          # three@0.160.0, playwright-core
node render.mjs scene_butterfly.js out.mp4 1080 1920            # whole film
node render.mjs scene_butterfly.js part.mp4 1080 1920 0 400     # frames 0-399
STILLS="0.5,12.8,30" node render.mjs scene_butterfly.js stills 540 960   # PNG stills
```

A scene exports `FPS`, `DURATION` and `build(THREE, W, H)`, which returns
`{scene, camera, hud, hudCam, update(t)}`. It owns no clock: the renderer calls
`update(t)` once per frame, so frame N is always the same image. That is what
lets a film be split into frame ranges and rendered in parallel, then joined
with `ffmpeg -f concat -c copy`.

The HUD is an orthographic scene in fixed 1080x1920 units, drawn after the
bloom pass so text stays sharp. `hudItem()` throws if anything is placed
outside the platform safe box.

## The Butterfly Effect: what is checked before a frame renders

- `lorenz_check.mjs` confirms the headline numbers standalone first. 1e-9
  apart grows past 1 at sim time 21.97, an implied rate of 0.943 against the
  known Lorenz Lyapunov exponent of ~0.906.
- The on-screen distance counter is the real separation of the pair, frame
  by frame. The fast-forward is labelled on screen while it runs.
- `wings.mjs` showed the pair never stays on opposite wings for long
  (0.7-2 sim units at a time), so no caption claims it does. The caption is
  "SAME RULES. DIFFERENT PATHS." and the build asserts the pair never comes
  back within 1 unit while it is on screen.
- The cloud's "NOW: EVERYWHERE" is timed off its measured spread, and the
  build asserts it ends with 25-75% of the points on each wing.

## The Collatz Conjecture: what is checked

`collatz_check.mjs` and the scene's own import-time checks: 27 takes 111
steps and peaks at 9,232 (step 77); the longest path under 10,000 is 6,171
at 261 steps; 1..10,000 visit 21,664 distinct numbers, and every one of them
reaches 1. "Checked by computer up to 2^68" is the published verification,
quoted, not recomputed.

Drawing, after Edmund Harriss's Collatz coral: each number hangs off
next(number), bent +0.135 rad if even and -0.255 rad if odd, with a 0.11 rad
twist about the direction of travel so the tree lives in 3D. Brightness
rises with depth, because thousands of branches overlap near the root and
additive glow sums them to white.

## Music

Original scores, so no licensing and no copyright claims.

- `music/butterfly_score.py` writes `butterfly_v2.abc` and three stems
  (orchestra, clarinet, drums). Top note E5. The clarinet fades in and out
  and the low drum rush swells into each downbeat as smooth volume curves
  applied at mix time.
- `music/collatz_score.py` sonifies 27's walk: one marimba sixteenth
  per step, pitch from log2 of the number on an E minor pentatonic scale,
  so the tune climbs to 9,232 and falls back to 1. The step tempo is
  derived from the video (111 steps in 12.5s), with a one-sixteenth pickup
  so the arrival at 1 is a downbeat.
- `music/smart_lookup_score.py` gives each of the nine sections its own
  tempo so it holds a whole number of bars. Every scene change lands on a
  downbeat, within 0.16s measured. `smart_lookup_mix.py` applies the
  envelopes.

```bash
python3 butterfly_score.py && for s in orch clar drums; do
  abc2midi $s.abc -o $s.mid
  fluidsynth -ni -q -F $s.wav -r 48000 -g 0.7 /usr/share/sounds/sf2/FluidR3_GM.sf2 $s.mid
done
```

Normalise to -14 LUFS with a -1.5 dBFS true peak (two-pass `loudnorm`), then mux
with `-c:v copy -movflags +faststart`.
