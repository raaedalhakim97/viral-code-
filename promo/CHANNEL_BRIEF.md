# Observer Collapse — channel brief

The standing brief for the page. Everything below is either a decision already
made in the work, or a rule the renders now enforce in code. Where something is
unverified, it says so.

---

## 1. Positioning

**The mathematics behind AI, one cinematic animation at a time.**

The niche is not "AI news" and not "math tutorials". It is the *mechanism* —
the equation under the thing everyone is already talking about. AI news decays
in a week; the math does not. A video about attention scaling still earns views
a year after the model it referenced was retired.

**What separates this page from every other AI account:** production value. The
animations are better than the category average by a wide margin, and that is
the moat. Protect it before anything else.

---

## 2. The actual problem to solve

The page converts views into **likes** far better than into **follows**.
High view-to-follower ratios on top videos mean reach is not the bottleneck —
the view→follow step is.

That single fact should drive most decisions:

- **Every video ends with a follow ask.** Not a brand sign-off. The eye and
  PAUSE / OBSERVE / LEARN are the signature, not the CTA — the CTA goes under them.
- **Teach something a viewer can use.** A habit they can apply the same day
  converts to follow; a video that only impresses converts to a like.
- **Series over one-offs.** A numbered series gives a reason to follow rather
  than like. This is the highest-leverage unbuilt thing on the list.

---

## 3. Content pillars

| Pillar | What it is | Role |
| --- | --- | --- |
| **Mechanism** | The math under a thing people already use — attention, embeddings, gradient descent | Core. Most videos. Durable. |
| **Foundations** | Linear algebra, calculus, Fourier, geometry — the prerequisites, made visual | Evergreen, feeds search |
| **Beat pieces** | Sound-led, no narration, pure visual math on a trending audio | Reach plays. Cheap to re-render. |

Pure brand content is not a pillar. A video that teaches a cold viewer nothing
underperforms on reach — post those to the profile, not at the feed.

---

## 4. Visual system

Locked, and mostly enforced in the scene files.

- **Black background.** `#000000`, never grey.
- **White line work.** `#F7FAFC` primary, `#8A94A6` secondary, `#2A2F3A` faint.
- **ONE gold accent per piece.** `#EBCB8B`. Exactly one. The scarcity is the
  whole reason it reads as an accent — a second gold element costs more than it
  gains. CTAs stay white.
- **Empty space is the style.** Do not fill the frame because it is empty.
- **Cut discipline: no shot holds longer than ~2s without a change.** A cut, a
  scale change, a reveal, a sound hit. The original promo had a 3.6s continuous
  fill where nothing happened — that is the format's one unforgivable sin.

### TikTok safe zone — enforced in code

The UI covers the frame. Anything that must be *read* lives inside these bounds:

| Edge | Covered by | Bound (frame height 9) |
| --- | --- | --- |
| Bottom ~22% | caption, handle, music ticker | `SAFE_BOT = -2.52` |
| Top ~12% | search / following bar | `SAFE_TOP = +3.42` |
| Right ~15% | like / comment / share rail | keep text centred |

The first promo put captions at y = -2.9 — under the caption block *and* in the
vignette falloff. Legible in the render, gone on the phone. `--safe` draws the
guides; use it.

---

## 5. Voice

**Alan** — piper `en-gb-alan-low`, `length_scale` 1.18, processed as the
Observer: rumble trimmed under 90 Hz, reverb at a watcher's distance, never a
cathedral. The chain lives in `narrate_scene.py` and mirrors OIS `tools/narrate.py`.

**Narration is sparse, not wall-to-wall.** A fast-cut scene has no room for a
documentary track — cuts land ~1.2s apart, a spoken line needs 2–3s. The
on-screen text carries the numbers; Alan carries the meaning; the silence
between them is the pacing.

**Why narrate at all:** TikTok transcribes audio and indexes the transcript. A
silent video forfeits the platform's strongest text signal. So the *searchable*
phrases are the ones spoken aloud — say "context window", "attention",
"long context" out loud even when they are already on screen.

Beat pieces are the exception: they carry a track, and Alan would fight it.

---

## 6. Captions

TikTok indexes caption text, on-screen text, and the audio transcript.

**A video with no narration has no transcript, so its caption carries nearly all
the search weight.** Those captions must work harder and name everything the
video shows but never says.

Rules:
- Front-load the searchable term — first line, not buried
- Name what is on screen but unnamed (the video shows harmonics; the caption
  must say *Fourier series*)
- 4–6 hashtags, mixing niche with one broad. Never `#fyp` or `#viral` — no
  measurable lift, and they read as low-effort against a premium aesthetic
- Look for the crossover audience. A Fourier video is math content, but it is
  also *music production* content, and that audience is much larger

---

## 7. Sound

Trending audio is added **in the TikTok editor**, never baked into the file:

1. Baked audio cannot be attributed to the sound's page, and the sound page is
   where the reach comes from
2. Sounds peak in 5–14 days; posting inside the first 24h of a rise is worth
   roughly 3× posting after peak, so the track is a posting-day decision
3. TikTok's library is licensed for TikTok; a song file dropped into a render
   is not

Beat pieces render silent and beat-locked, so any track can go under them.
`--bpm` rescales the whole piece.

**Open gap:** narrated pieces still ship with no score. The atmospheric music is
part of why the aesthetic works and none of these videos have it yet.

---

## 8. Pipeline

```bash
manimgl <scene>.py <Scene> -w              # render, 1440x2560 @ 60fps
python3 cinegrade.py in.mp4 graded.mp4     # house look: bloom, vignette, grain
python3 narrate_scene.py graded.mp4 out.mp4 --stem alan.wav
```

Grade every piece. Manim writes pure vector frames — hard-edged strokes on flat
black, no falloff. That is a plot. Bloom, vignette and grain are what make
white-on-black read as *light on film*, and it is the difference between the
manim scenes and the hand-built episodes.

Vignette is **0.22**, not the 0.42 the trailers use — that value was tuned on
16:9 with content centred, and at 9:16 the falloff lands on the caption line.

---

## 9. Known unknowns

Listed so they are not mistaken for settled:

- **Follower and engagement figures are unverified.** They come from an uploaded
  report, not from the TikTok API. The "engagement rate" row in that report is
  mislabelled — it is likes-per-follower, not engagement rate.
- ~~The live handle is unconfirmed.~~ **Resolved: `@observercollaps`.** The
  uploaded report said `@observer.collapse`; the account owner says
  `@observercollaps`. All three scenes were corrected and re-rendered. Treat
  figures and details in that report with matching suspicion — it already had
  one mislabelled metric and now one wrong handle.
- **Repo split is unresolved.** Scenes and pipeline are in `viral-code-`;
  `cineengine` and the score are in OIS. Until this is settled, no piece can
  have music.
