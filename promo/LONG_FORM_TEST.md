# The long-form test

`illusion_of_logic.py` exists to answer one question: **does this audience watch
long-form at all?** Everything else on the page is 13–38 seconds. This is 89.6.

**It is silent.** The first cut carried a TTS read and sounded like one. Every
Piper tier reachable from the render container is flat, and the good British
voice lives on HuggingFace, which the egress policy blocks. So the argument is
carried by construction instead — line geometry, and equations that pulse on
the beat. Add a track in the TikTok editor; the piece is beat-locked at 150 BPM
(224 beats, 56 bars) so any tempo fits after a re-render.

**What silence costs:** TikTok indexes the audio transcript, and there now
isn't one. Two things compensate, and both are done — every searchable term
appears on screen as text (*tokenizer*, *place value*, *transformer*,
*probability*), and the caption below carries the rest. It does mean the
caption is doing more work here than on a narrated video.

The video is the instrument. This file is the experiment.

---

## Why 89 seconds and not five minutes

The submitted script was written at 5:00. The honest reason it is not:

**If people leave at 0:45, a five-minute cut tells you exactly what an 89-second
cut tells you — for four times the render.** The question is whether they stay
past a minute. Answer that first, then extend.

If the retention curve is still healthy at 0:60, a five-minute version is worth
building and I will build it. If it collapses at 0:30, no amount of length was
ever going to work and you have saved yourself the effort.

---

## What to measure

Open TikTok Studio → the video → Analytics. Record these, and record the same
numbers for two or three of your **short** videos so there is something to
compare against.

| Metric | Where | Why it matters |
| --- | --- | --- |
| **Average watch time** (seconds) | Analytics | The single most important number. Not a percentage — actual seconds. |
| **% watched full** | Analytics | Completion. Expect this to be lower than a 13s video. That is fine — see below. |
| **Retention curve** | Analytics | *Where* they leave. The shape tells you what to fix. |
| **Follows from this video** | Analytics | The actual goal. |
| **Comments** | Obvious | This video asks viewers to test a claim. That should show up here. |

---

## The counter-intuitive part

**A lower completion rate can still be a win.** The algorithm rewards total
watch time, not the percentage.

| | Length | Completion | Average watch |
| --- | --- | --- | --- |
| A series part | 12.8s | 90% | **11.5s** |
| This video | 89.6s | 40% | **35.8s** |

The long video loses badly on completion and wins by 3× on watch time. If that
is what the numbers say, long-form works for this audience regardless of how
the completion figure looks.

So the decision rule is:

- **Average watch time higher than your shorts** → long-form works. Extend to
  the five-minute cut.
- **Follows-per-view higher** → long-form works, and it converts. Do more.
- **Average watch time lower, and they drop before 0:30** → the hook or the
  pacing is the problem, not the length. Do not extend.
- **They drop right at a chapter boundary** → that chapter is the weak one.
  The HUD makes this diagnosable — chapters are visible on screen, so a drop at
  0:43 points at chapter 4.

---

## What is built in to fight abandonment

Ninety seconds of white line art on black is where boredom lives. Five
devices, all deliberate:

1. **The equations dance.** One clock drives a scale pulse on every equation and
   a breath on the geometry, so the frame is never static even while someone is
   reading it. That is the difference between cinematic and a slideshow, and it
   matters more without a voice to carry the time.
2. **A segmented progress bar and chapter number, always on screen.** A viewer
   who can see how much is left stays longer than one who is guessing. It also
   makes the retention curve diagnosable after the fact.
3. **An open loop at 0:15** — *"it fails 96% of the time. Why?"* — not closed
   until the last chapter.
4. **The strongest visual placed early.** The 59% → 4% cliff is at 0:20, not
   saved for the end. Nothing is gained by holding your best card until after
   people have left.
5. **The same cut discipline as the shorts.** Nothing holds past ~2s.

---

## One control to keep the test clean

Post it **on its own**, not on the same day as a series part. Two posts in a day
split their own reach and you will not be able to tell which effect you are
looking at.

Everything else stays constant: same handle, same aesthetic, same CTA, same kind
of caption. The only variable being tested is length.

---

## Caption

```
Your AI cannot multiply, and the reason is stranger than you think.

3-digit multiplication: right about 59% of the time. Add one digit: 4%. Nothing
about the arithmetic got harder.

It never sees the number — the tokenizer splits it where language is common,
not where place value is. It cannot carry, because it runs the same fixed stack
of layers whether the sum is easy or hard. So it does not compute an answer, it
ranks what an answer would look like and picks the top one.

Our intelligence looks for truth by following rules. Its intelligence looks for
what usually comes next.

Try it. Four digits. Watch it fold.

#aimath #mathtok #llm #tokenization #machinelearning
```
