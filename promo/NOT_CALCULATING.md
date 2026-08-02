# It Isn't Calculating — video brief

Companion to `not_calculating.py`. Built from a submitted script titled
*"1+1=3: How AI Reimagines Reality"*, with the thesis kept and the mechanism
corrected.

- **Output:** 1440×2560, 60fps, **~37.4s**, narrated by Alan
- **Thesis (unchanged from the submission):** an LLM predicts, it does not calculate

---

## What changed from the submitted script, and why

### The mechanism was wrong

The original said an AI might answer `1 + 1 = 3` because it saw enough jokes,
stories and typos in training where `1 + 1 =` was followed by `3`. That is a
plausible-sounding account and it is not what happens.

- **No frontier model gets `1+1` wrong.** Building a video on a failure that
  doesn't occur means the top comment is a correction. On a channel whose only
  real asset is credibility, that is the most expensive possible mistake.
- **The real causes are architectural, not anecdotal.** Tokenizers split numbers
  by *language* frequency rather than digit structure, so the model often never
  sees `4827` as a quantity. And a transformer is fixed-depth — it cannot run an
  unbounded carry loop, so it pattern-matches the shape of an answer instead of
  computing one.

### The hook survives, as a subversion

`1 + 1 = 3` still opens the video — struck through, followed by *"No AI says
this."* A viewer who expected the cliché and doesn't get it is more hooked than
one who gets it. Then the video pivots to a failure that is real, sourced, and
**reproducible on the viewer's own phone**, which is what drives comments.

### 5 minutes became 37 seconds

The submission was scripted at 5:00. Completion rate is the signal that moves a
101-follower account, and a five-minute video from that base is abandoned inside
the first thirty seconds. Every beat of the original argument survives —
tokenization, training, latent space, attention, probabilistic output — just at
the density the format rewards.

---

## Sources

| On screen | Source |
| --- | --- |
| GPT-4: **59%** on 3-digit multiplication, **4%** on 4-digit | Cross-digit interactions scale O(n²) |
| Tokenizers split numbers by language frequency, not place value | Identified as a primary architectural cause of arithmetic failure |
| A transformer runs the same fixed stack every time | Definitional — fixed-depth architecture, no unbounded loop |

**Do not change a number without changing this table.** The `48 | 27` split on
screen is illustrative of *how* tokenizers chunk numbers, not a claim about one
specific model's vocabulary — the on-screen label says "what the model gets"
rather than naming a tokenizer.

---

## Structure

| Beat | Time | What it does |
| --- | --- | --- |
| The subversion | 0:00–0:04 | `1+1=3`, struck. "No AI says this." |
| The cliff | 0:04–0:13 | 59% → 4%. Nothing about the maths got harder. |
| It never sees the number | 0:13–0:21 | `4827` → `48` `27` |
| It can't carry | 0:21–0:27 | your loop vs a fixed stack of layers |
| The payoff | 0:27–0:33 | "It predicts what an answer would look like." |
| Close | 0:33–0:37 | signature + follow ask |

---

## Build

```bash
cd promo
xvfb-run -a -s "-screen 0 1600x1200x24" manimgl not_calculating.py NotCalculating -w
python3 cinegrade.py videos/NotCalculating.mp4 nc_graded.mp4
SCRIPT=not_calculating python3 narrate_scene.py nc_graded.mp4 final.mp4 --stem alan.wav
```

`SCRIPT` selects the read from `SCRIPTS` in `narrate_scene.py`. Run
`SCRIPT=not_calculating python3 narrate_scene.py --check` for the timing table
before committing to a render.

---

## Caption

```
Your AI cannot multiply, and the reason is stranger than you think.

Ask GPT-4 for 3-digit multiplication and it is right about 59% of the time.
Add one digit and it drops to 4%. Nothing about the arithmetic got harder.

It never sees the number — the tokenizer splits it where language is common,
not where place value is. And it cannot carry, because it runs the same fixed
stack of layers whether the sum is easy or hard.

It is not computing the answer. It is predicting what an answer looks like.

Try it. Four digits. Watch it fold.

#aimath #mathtok #llm #tokenization #machinelearning
```

**"Try it. Four digits."** is the most valuable line in the caption. A claim a
viewer can test in ten seconds is a claim they comment about, and comments are
a ranking signal.

Short alternate:

```
Ask any AI to multiply two four-digit numbers. It gets it right about 4% of
the time — and not for the reason you would guess.

#aimath #mathtok #llm
```
