# EVERY PAY CUT GETS THIS WRONG

Sequel to `net_vs_gross.py` — same build, same spine (*percent of
what?*), different trick.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** ships silent. Voiceover script and `percent_back.srt` are
  below — the cut is beat-locked to **150 BPM**, so a 150 BPM track lands
  on every move without nudging.

---

## The trick

Your pay is cut 20%. A year later they put 20% back. Everyone expects to
be at 1,000 again.

```
1,000  − 20%  =  800
  800  + 20%  =  960        ← 40 short, every time
```

**20% of what?** It came *off* 1,000 and went back *onto* 800. The second
percentage is a percentage of a smaller pile.

## The shape

Cut the 1,000 into **ten blocks of a hundred**.

```
20% off     takes two WHOLE blocks       →  8 blocks
20% back    is 20% of 800 = 160          →  1.6 blocks
```

**Two blocks out. One point six back.** The missing four tenths of a
block is the 40, and it sits on screen in rose to be counted.

## The stake

To undo a cut you always need a *bigger* rise than the cut:

```
down 10%  →  up 11.11%        down 20%  →  up 25%
down 25%  →  up 33.33%        down 50%  →  up 100%
```

### Verified at import

```
every figure is exact Fraction arithmetic — nothing typed in by hand
the shortfall is exactly 40, which is exactly 4% of 1,000
the order doesn't matter: +20% then −20% lands on 960 too
the recovery rise is p/(1−p), checked at 10/20/25/50/90%
+25% on 800 is checked to land back on exactly 1,000
the gap is always exactly r² — 20% → 0.04 → 4%
two blocks out minus 1.6 back is checked to equal the 40 on screen
the blocks are asserted to fit the platform safe box
```

---

## Structure

| Beats | Time | |
| --- | --- | --- |
| 0–5 | 0:00 | **HOOK.** `1,000 − 20% + 20%` → `~1,000~` ✗. *this costs you 40 / every single time* |
| 5–14 | 0:02 | **960** — *that's what you actually get back* → pins to the top |
| 14–26 | 0:05 | the sum runs in the centre: −20% → 800, +20% → 960 ✗ |
| 26–34 | 0:10 | **20% of WHAT?** *it came off 1,000. it went back onto 800.* |
| 34–62 | 0:13 | ten blocks → two whole blocks leave → only 1.6 come back |
| 62–80 | 0:25 | the gap lights up. *200 out, 160 back.* *you need +25%, not 20* |
| 80–88 | 0:32 | *Down 20% needs up 25%. Down 50% needs up 100%.* |
| 88–92 | 0:35 | *Send this to anyone who took a pay cut* |
| 92–100 | 0:37 | The eye |

---

## Caption

```
Every pay cut gets this wrong.

They cut your pay 20%. A year later they put 20% back. You are not back
where you started — you're on 960.

Because 20% of WHAT? It came off 1,000 and it went back onto 800.

Cut the 1,000 into ten blocks of a hundred. The cut takes two whole
blocks. The rise gives you 20% of 800 — one point six blocks.

Two out, one point six back. That missing bit is your 40.

To actually get back to 1,000 you need +25%, not +20%.

Down 20% needs up 25%. Down 50% needs up 100%.

#maths #mathtok #percentages #pay #salary #money #finance #fyp
```

**YouTube title:** `Down 20% then up 20% doesn't get you back — here's the gap`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl percent_back.py PercentBack -w -r 1080x1920
python3 cinegrade.py videos/PercentBack.mp4 percent_back.mp4
```

## Changing it

`PAY` and `RATE` are the only inputs; the block count, the two block
figures and every amount are derived. Set `RATE = 50/100` and the shape
redraws as five blocks out and 2.5 back. The assertions refuse to build
unless the blocks still account for the shortfall exactly and the row
still fits the safe box.

**Note on the first render:** the blocks were 0.62 tall and the missing
0.4 of a block — the whole point of the video — came out as a sliver
about 25px wide and barely readable. They're 1.40 tall now, and the
returned blocks moved from green to blue so they separate from the gold
at a glance.


---

## Audio pack

The video ships silent because the animation is beat-locked, not because
it has to stay silent. Two things make adding audio a paste job.

### Music

Everything in the cut lands on a beat at **150 BPM** — 1 beat = 0.4s,
1 bar = 1.6s, and the whole thing is exactly 25 bars. Drop any 150 BPM
track on it and the hits land with no nudging. Half time (75) and double
(300) work too.

### Voiceover

`percent_back.srt` sits next to the mp4, timed to the stage boundaries,
every line checked to be speakable under 3.2 words/second:

| In | Out | Line |
| --- | --- | --- |
| 0:00.0 | 0:02.0 | Every pay cut gets this wrong. |
| 0:02.0 | 0:05.6 | Take twenty off, put twenty back. You get nine sixty. |
| 0:05.6 | 0:10.4 | They cut your pay twenty percent. A year later, they restore it. |
| 0:10.4 | 0:13.6 | But twenty percent of what? |
| 0:13.6 | 0:19.2 | It came off a thousand. It went back onto eight hundred. |
| 0:19.2 | 0:24.8 | Cut the thousand into ten blocks. The cut takes two whole blocks. |
| 0:24.8 | 0:28.4 | The rise only gives back one point six. |
| 0:28.4 | 0:32.0 | That gap is your forty. You need twenty-five percent. |
| 0:32.0 | 0:36.8 | Down twenty needs up twenty-five. Down fifty needs up a hundred. |

The voice stops at 36.8s so the eye and the handle play clean.

**Note on OpusClip:** its MCP surface has no voiceover and no music
generation — the ops are captions, emoji, keyword highlight, trims, text
overlays, style, social copy and scheduling. Its captions are also built
from a transcript, and this video has no speech to transcribe, so the
`.srt` above is what feeds them. Generate the voice in the OpusClip web
app or any TTS, lay it against these timings, and the captions come from
the same file.
