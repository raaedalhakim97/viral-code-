# wtfengine

Turn raw Dota 2 gameplay into beat-synced WTF-moment edits — automatic clip
selection, a camera that zooms in on whatever just happened, and cuts locked
to the music.

Runs entirely offline. No API keys, no GPU, no cloud service. Python +
ffmpeg.

```bash
python -m wtfengine make gameplay.mp4 --music song.mp3 -o out.mp4
```

That single command scans the footage for moments worth showing, detects the
tempo of your track, lays the clips out so each impact lands on a strong
beat, punches the camera in on the action, and renders a vertical mp4.

---

## Install

```bash
pip install -r requirements.txt
```

You also need `ffmpeg` on your PATH:

```bash
sudo apt install ffmpeg      # Debian/Ubuntu
brew install ffmpeg          # macOS
```

## Try it without any footage

The repo ships a generator that fakes a gameplay clip with events at known
timestamps, so you can see the whole thing work before pointing it at a real
VOD:

```bash
python tools/make_sample.py --outdir sample
python -m wtfengine make sample/gameplay.mp4 --music sample/music.wav \
    --start-at-drop -o sample/out.mp4
```

---

## How it works

```
gameplay.mp4 ──> detect ──> moments ──┐
                                      ├──> plan ──> EDL ──> render ──> out.mp4
music.mp3    ──> audio  ──> beats  ───┘
```

**detect** — Samples the video at 10 fps and builds a *hype curve* from two
signals: how many pixels are changing (a teamfight moves a lot of screen; a
lane does not) and how loud the gameplay audio is. Both contribute a
*novelty* term as well — the positive derivative — because what makes a
moment read as "wtf" is the jump, not the level. Peaks in that curve are your
moments.

Alongside the peak it tracks an **action point**: the centroid of where the
change actually happened, weighted so that only the strongest few percent of
changing pixels get a vote. That is what the camera aims at.

**audio** — Beat-tracks the music on its percussive component, infers where
the bar starts by finding the beat phase carrying the most onset energy, and
looks for the biggest sustained energy lift in the track (`--start-at-drop`
uses this to start your edit on the drop).

**plan** — This is where most of the taste lives. The naive approach is to
snap the *start* of every clip to a beat, and it sounds wrong, because what
the ear wants is the **impact** on the beat, not the cut. So the planner keeps
clips butted together and flexes the pre-roll instead: it holds a little more
or a little less run-up so the hit itself lands on a strong beat. Slow-mo
ramps make source seconds and output seconds different lengths, so all of
this happens in a converted time base.

**render** — Reads each clip frame by frame in OpenCV, applies the crop path,
and pipes raw frames to ffmpeg. Doing the camera in Python rather than as an
ffmpeg filter graph costs some speed but buys exact per-frame control, which
is the whole point of a focus camera.

---

## Commands

| Command | What it does |
| --- | --- |
| `analyze` | Find moments and print them. No rendering. |
| `plan` | Build the EDL and print/save it. No rendering. |
| `make` | Detect, plan and render in one go. |
| `render` | Render a previously saved EDL. |

The EDL is plain JSON and fully describes the output, so the intended
workflow for anything you care about is:

```bash
# 1. see what it found
python -m wtfengine analyze raw.mp4

# 2. build a plan you can inspect and hand-edit
python -m wtfengine plan raw.mp4 --music song.mp3 --edl plan.json

# 3. tweak plan.json, then render it
python -m wtfengine render plan.json -o out.mp4
```

Nothing is re-derived at render time — edit a timestamp in `plan.json` and
that is exactly what you get.

## Presets

```bash
python -m wtfengine make raw.mp4 --music song.mp3 --preset hype
```

| Preset | For |
| --- | --- |
| `meme` (default) | Hard punches, heavy slow-mo, shake. TikTok-brained. |
| `hype` | More moments, shorter dwell. 60-second "every fight" reels. |
| `cinematic` | Slow pushes, no shake. Actually-good-play montages. |
| `flat` | Cuts only, no camera work. Useful as an A/B baseline. |

## Useful flags

```
--start-at-drop      find the drop and start the music there
--align downbeat     land impacts on bar starts instead of any strong beat
--zoom 2.4           peak punch-in factor
--slowmo 0.3         speed at impact (1.0 disables the ramp)
--shake 0.02         impact shake amplitude
--max-moments 8      how many clips to keep
--min-gap 6          minimum seconds between moments
--prominence 0.08    lower finds more, weaker moments
--duration 60        cap the output length
--landscape          1920x1080 instead of 1080x1920
--size 1080x1350     any explicit size
--game-audio 0.35    mix the original gameplay audio under the music
--no-quantize        do not snap cuts to the beat
```

`--game-audio` time-stretches the gameplay audio to follow the speed ramps,
so ability sounds stay in sync through slow motion.

---

## Using replay data instead of detection

Motion and loudness are heuristics. Dota 2 replays are ground truth: the
`.dem` combat log records exactly when `Charge of Darkness` was cast, when it
landed, and when the kill registered. If you have the replay, use it — no
heuristic will beat it, and it is the difference between the drop landing on
the impact frame and landing 200 ms off.

Parse the replay with [clarity](https://github.com/skadistats/clarity) (Java)
or [manta](https://github.com/dotabuff/manta) (Go), convert game time to
video time with a single offset, and hand the result over:

```json
[
  {"t": 412.7, "label": "Charge of Darkness", "score": 1.0},
  {"t": 418.2, "label": "kill", "score": 0.9}
]
```

```bash
python -m wtfengine make raw.mp4 --music song.mp3 --markers events.json
```

Detection is skipped entirely; the action-point tracking still runs, so the
camera knows where to look. Labels matter: anything that reads as travel
(`charge`, `blink`, `leap`, `dash`, `chase`) gets a whip camera move instead
of a straight punch.

> The replay parser itself is not included — it is a separate JVM/Go
> toolchain, and which events you care about is a taste decision. The marker
> format above is the whole contract.

---

## Tuning notes

**It found too many boring moments.** Raise `--prominence` and `--min-gap`.

**It missed the good bit.** Lower `--prominence`. If the moment is visually
quiet but loud (a shutdown announcement, a teammate screaming), raise the
audio weight in a config file (`w_audio`).

**The camera feels drunk.** Raise `focus_smooth` in a config file, or use
`--preset cinematic`. If it lags behind the action instead, raise
`focus_lead`.

**Cuts feel late.** Try `--align downbeat` — landing on bar starts is more
forgiving than any strong beat.

Any flag can go in a JSON config instead:

```bash
python -m wtfengine make raw.mp4 --music song.mp3 --config mine.json
```

---

## Limitations

- Detection is motion and loudness, not game understanding. It finds
  teamfights reliably; it will not tell a clutch escape from a lost fight.
  That is what the marker path is for.
- The renderer decodes each clip's source range, so very long VODs spend most
  of their time in the analysis pass (roughly 30× realtime at default
  settings on a laptop CPU).
- Speed ramps use frame duplication, not optical-flow interpolation. Heavy
  slow-mo (below ~0.3) starts to judder.

## Tests

```bash
python -m pytest tests/ -q
```

The unit tests cover the timing maths, camera envelopes and planner. The
integration tests generate a synthetic clip with events at known timestamps
and assert that detection finds them, that the framing lands within 5% of the
planted screen position, and that impacts sit on the beat grid.
