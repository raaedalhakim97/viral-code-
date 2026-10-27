# three.js videos

Real 3D, rendered headlessly in Chromium frame by frame, encoded with ffmpeg.
Everything here is free: three.js, Playwright's Chromium, ffmpeg, abc2midi,
FluidSynth, and for the v3 scores the VSCO 2 Community Edition orchestral
samples (CC0, real recordings).

| Scene | Output | Length |
| --- | --- | --- |
| `scene_smart_lookup.js` | Smart Lookup, 3D rebuild of `promo/smart_lookup/smart_lookup.py` | 95.0s, 2850 frames |
| `scene_butterfly.js` | The Butterfly Effect: Lorenz attractor in deep space | 40.0s, 1200 frames |
| `scene_collatz.js` | The Collatz Conjecture: 1..10,000 grown as one coral | 40.0s, 1200 frames |
| `scene_euler.js` | 8s test: 2,144 points fly into the Euler curve | 8.0s |
| `scene_weighted_wave.js` | Smart Lookup Part II: The Weighted Wave | 95.0s, 5700 frames |
| `scene_elise.js` | The Shape of Für Elise: every note drawn as a spinning vector | 62.0s, 3720 frames |

All are 1080x1920 at 30fps, laid out for the TikTok / Reels / Shorts safe box,
except Part II: 1920x1080 at 60fps, with a portrait mode (pass 1080 1920) for
the vertical teaser.

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

## Smart Lookup Part II: The Weighted Wave

Each of 67 words has 32 weights θ, and each weight drives one wave:
ψ(x) = Σ θ_k sin(2π f_k x + φ_k), with x the position round the closed Euler
curve and f_k = k (whole numbers, so ψ is periodic on the loop). A word sits at
the argmax of |ψ|. Training is real gradient descent on L = -ψ(x_target)² on
the unit sphere, 8 steps, one per on-screen pulse. 67 x 32 = 2,144, Part I's
point count.

`weighted_wave_math.mjs` holds all of it and is imported by both the scene and
`weighted_wave_check.mjs`, so what is checked is exactly what is drawn:

- 30/67 words in their slot before training, 67/67 after (words per step:
  30 36 42 55 61 64 65 67 67). The slot is the word's own 32 points, ±16; a
  32-wave peak cannot be placed finer than that, and the worst trained peak
  lands 5.2 points off.
- WATER: 27/32 of its waves push the same way at its peak before, 32/32 after,
  and the peak grows 1.51x. Every step lowers the loss for every word.
- The interference beat is two real sinusoids (6 and 7 cycles): the envelope
  reaches 1.99 where they add and 0.02 where they cancel.

The bloom is |ψ| at WATER's peak. It is never on a linear ramp, never covers the
frame, and is gone within 3 s. `tex/make_tex.py` typesets the equations
(latex + dvisvgm). The scene's HUD throws if any item would fall off the frame.

```bash
node weighted_wave_check.mjs                     # every claim, before rendering
./run_ww.sh                                      # 1920x1080 60fps master, 3 parallel chunks
./run_teaser.sh                                  # 64-79 s in portrait for the 15 s teaser
cd music/part2 && python3 vo.py && python3 sound_ww.py <vsco path>
python3 master.py ww_mix.wav ww_mix_m.wav && python3 master.py ww_music.wav ww_music_m.wav && cd ../..
A=music/part2 MASTER=ww_master_video.mp4 ./finish_ww.sh   # master, no-VO, 30 s loop, 15 s teaser
```

Sound (`music/part2/sound_ww.py`): voiceover by Piper (offline, en-us-ryan-high);
a 45 Hz bed that matches at both ends for the loop; 32 ticks at 440 + 35k Hz
as the bars rise; two glides that start a fifth apart (260/390 Hz), pass
through a minor third and meet in unison at 0:44; 8 bass pulses on the 8
gradient steps; two seconds of near-silence, then one piano C6 on the bloom;
C major at the reveal. `check_sync.py` measures the level jump at every cue.
Instruments are VSCO 2 CE (CC0); the upright piano is by Simon Dalzell, via
Versilian Studios. Its files are named by sample index: MIDI key = 21 + 2 x NNN.

## The Shape of Für Elise

A note is a spinning vector: y = A e^(-t/τ) sin(2πft) is the shadow of an arrow
of length A e^(-t/τ) turning f times a second. `music/elise/arrange.py` writes
the arrangement (Beethoven's notes, public domain; solo piano, then strings and
cello, full orchestra, solo piano again) as `elise.abc` and as
`elise_score.json`, and that one note list drives both the audio and the
picture, so every arrow appears on the frame its note sounds.

- Real notes spin far too fast to see, so every frequency is divided by 110.
  All pitch ratios stay exact, and the screen says so.
- Chords: each note of the chord is one axis, so the chord is a point moving in
  3D, (sin 2πf₁t, sin 2πf₂t, sin 2πf₃t). Whole-number ratios close into a knot;
  equal temperament almost does, and the drift on screen is the real one.
- Instruments: `harmonics.py` measures the overtone strengths of a recorded A3
  (220 Hz) for piano, violin, cello and horn. Those numbers are the lengths of
  each instrument's 12-vector chain. The violin's fundamental measures at 3%:
  violins radiate poorly that low, and the 660 Hz third harmonic confirms the
  note is A3.
- Every note's entrance flashes and lets off lit smoke in its colour. Both are
  computed from (note, t), so frames stay independent and render in parallel.

```bash
cd music/elise && python3 arrange.py && python3 harmonics.py <vsco> && cp elise_score.json harmonics.json ../..
python3 elise_audio.py <vsco> elise_score.json elise_mix.wav   # real samples, score offset 2.5 s
cd ../.. && (cd tex_elise && python3 make_tex.py) && ./run_elise.sh
```

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

### v3: real orchestral samples (Collatz, Butterfly Effect)

`music/v3/` replaces the 2008 FluidR3 soundfont with VSCO 2 Community Edition
recordings, played by a small sampler in `produce_v3.py`. It picks the nearest
sampled pitch, the velocity layer and the round-robin, and trims leading
silence so attacks land on time. The score is rewritten with colour harmony
(add9, maj7(#11), sus4 -> 3), one developed motif, low horns in unison with
cellos, and a 3+3+2 spiccato ostinato. Production adds sub-bass drops,
reversed cymbals, filtered risers, a low-passed saw pad, sidechain pumping
and convolution reverb.

Get the samples with a sparse clone (about 840 MB of the 3 GB library):

```bash
git clone --filter=blob:none --no-checkout --depth 1 https://github.com/sgossner/VSCO-2-CE.git vsco
# then sparse-checkout the folders listed at the top of produce_v3.py's INST table
```

`score_butterfly_v3.py` / `produce_bf3.py` do the same for The Butterfly
Effect on its original grid (76 BPM, so every hit stays where it was):
clarinet and violas in unison for the two points, then low horns climbing
against falling cellos at the split. The clarinet fade and the soft drum
rush are volume curves applied in the mixer, not velocity steps.

**Check the pitch before trusting the names.** `check_pitch.py` measured
that VSCO names most instruments with middle C = C3, so every one but the harp
sounds an octave above its file name. The first v3 render trusted the names
and played the strings and horns an octave too high.

```bash
python3 butterfly_score.py && for s in orch clar drums; do
  abc2midi $s.abc -o $s.mid
  fluidsynth -ni -q -F $s.wav -r 48000 -g 0.7 /usr/share/sounds/sf2/FluidR3_GM.sf2 $s.mid
done
```

Normalise to -14 LUFS with a -1.5 dBFS true peak (two-pass `loudnorm`), then mux
with `-c:v copy -movflags +faststart`.
