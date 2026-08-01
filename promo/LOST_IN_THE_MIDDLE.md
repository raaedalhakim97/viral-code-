# Lost in the Middle — video brief

Companion to `lost_in_the_middle.py`. Sources, script, caption, and the reasoning
behind the topic choice.

---

## Why this topic

The page converts views into likes far better than into follows. Reach is not
the bottleneck — the view→follow step is. What converts a stranger into a
follower is a video that changes what they *do*, not one that impresses them.

This one does: **put important context at the start or the end of a prompt,
never the middle.** That is a habit change a viewer can apply five minutes
later, and it comes with a reason they can repeat to someone else.

It is also durable. A video pegged to a model launch decays the week the next
model ships. Quadratic attention scaling does not — the same video keeps earning
views a year out, which matters more for a page whose back catalogue is small.

---

## Sources

Every number on screen is traceable. Do not change one without changing this table.

| Claim on screen | Source |
| --- | --- |
| Attention compares every word to every other word — O(n²) | Definitional (Vaswani et al., *Attention Is All You Need*, 2017) |
| 10 → 100, 1,000 → 1,000,000, 1,000,000 → 1,000,000,000,000 | Arithmetic: n² |
| Every frontier model in 2026 advertises ≥1M tokens | 2026 context-window roundups |
| Real usable context ≈ 50–65% of advertised | RULER benchmark |
| RULER tested 17 long-context models; all 17 degraded | RULER |
| Needles at 30–70% depth: 5–15 point retrieval drop | Liu et al., *Lost in the Middle*, TACL 2024 ([arXiv:2307.03172](https://arxiv.org/abs/2307.03172)) |

**Framing caveat worth keeping honest:** models do not literally compute n²
attention at 1M tokens — that is the point of the video, not an error in it. The
"nobody computes a trillion" beat is what sets up sparse attention, sliding
windows, and state-space compression as the workaround. Do not let a re-edit
collapse those two beats, or the video ends up claiming something false.

---

## Structure

| Beat | Time | What it does |
| --- | --- | --- |
| Hook | 0:00–0:03 | "1,000,000" struck through in gold. The claim, then the denial. |
| The n² wall | 0:03–0:11 | 6 tokens fully connected, then the escalation to a trillion |
| Nobody pays | 0:11–0:14 | Grid darkens to a sparse band — the workaround, shown |
| RULER | 0:14–0:19 | 17 bars drop against ghost outlines of the advertised height |
| The middle | 0:19–0:24 | The U-curve. The whole video in one shape. |
| Payoff + CTA | 0:24–0:32 | What to do about it, then the follow ask |

**Cut discipline:** no shot holds longer than ~2s without a change. The previous
promo had a 3.6s continuous fill where nothing happened — that is the format's
one unforgivable sin.

---

## Narration

Alan (piper `en-gb-alan-low`), seven lines, sparse. See `narrate_scene.py`.

Sparse is deliberate. TikTok transcribes audio and indexes the transcript, so a
silent video forfeits the platform's strongest text signal — but wall-to-wall
narration does not fit a fast-cut scene. The escalation rows sit ~1.2s apart and
a spoken line needs 2–3s. The on-screen text carries the numbers, Alan carries
the meaning, and the searchable phrases — *context window*, *attention*,
*long context*, *RULER* — are the ones spoken aloud.

Run `python3 narrate_scene.py --check` before rendering to see the timing table.

---

## Caption

```
Your AI has a blind spot and it's the middle.

RULER tested 17 long-context models. All 17 degraded before their advertised
limit. Put what matters at the start or the end of your prompt.

#aimath #mathtok #machinelearning #promptengineering #llm
```

Alternates:

**Curiosity-first**
```
Every AI in 2026 says it reads a million words. The math says it stops
paying attention long before that.
```

**Practical-first — best for saves**
```
Stop putting your important context in the middle of the prompt. Here's the
benchmark that explains why.
```

---

## Build

```bash
cd promo

# 1. render
xvfb-run -a -s "-screen 0 1600x1200x24" manimgl lost_in_the_middle.py LostInTheMiddle -w

# 2. grade — bloom, vignette, grain, the house look
python3 cinegrade.py videos/LostInTheMiddle.mp4 graded.mp4

# 3. voice — Alan, muxed without re-encoding the video
python3 narrate_scene.py graded.mp4 final.mp4 --stem alan.wav
```

`--stem` writes Alan alone, full length and already in sync, for laying under
music in CapCut instead of taking the baked mix.

**Still missing: the score.** The video ships silent apart from Alan. The
account's aesthetic depends on atmospheric music and this has none yet —
`cineengine/audio/` in OIS is where that comes from.
