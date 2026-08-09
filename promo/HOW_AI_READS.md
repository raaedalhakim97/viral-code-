# How AI Reads — video brief

Companion to `how_ai_reads.py`. Chunks and threads: why a model can't count the
r's in strawberry, and how one word at the end of a sentence changes what
another word means.

- **Output:** 1080×1920, 60fps, **32.000000s** — 80 beats = 20 bars at 150 BPM
- **Audio:** none. Add the sound in the TikTok editor — see below.

---

## Two stages, not three

The first draft had **tokens → numbers → threads**. The middle stage ("every
token becomes a row of numbers") is true and it is the part nobody needed. It
made the video a lecture. Cutting it left two stages that each have a joke or a
twist in them:

| Beats | |
| --- | --- |
| 0–4 | Title |
| 4–8 | **CARD — 1 · CHUNKS** |
| 8–36 | Watch a real BPE glue letters into `straw` and `berry`. **3 r's. 2 chunks.** |
| 36–40 | **CARD — 2 · THREADS** |
| 40–66 | Which word is "it"? Then change one word and the link jumps. |
| 66–70 | "It never reads a word. It reads the pieces, and the links." |
| 70–80 | The eye |

---

## Stage 1 is a real tokenizer, trained at build time

`tiktoken` installs in this environment but its vocabulary lives behind a host
the egress proxy blocks, so rather than quote GPT's splits from memory this file
**implements byte-pair encoding and trains it** on the corpus in the source.
Every state on screen is one the algorithm actually passed through:

```
s t r a w b e r r y   →   s t r a w b er r y   →   s t r a w ber r y
→   s t r a w berr y  →   s t r a w berry      →   s t ra w berry
→   st ra w berry     →   stra w berry         →   straw berry
```

The merges that build those two pieces, in the order learned:

| # | merge | result |
| --- | --- | --- |
| 2 | `e` + `r` | `er` |
| 7 | `b` + `er` | `ber` |
| 8 | `ber` + `r` | `berr` |
| 12 | `berr` + `y` | `berry` |
| 24 | `s` + `t` | `st` |
| 25 | `st` + `ra` | `stra` |
| 26 | `stra` + `w` | `straw` |

**Nobody told it about "straw" or "berry."** It merged whatever pair was most
frequent, and those fell out of counting. That is the whole idea of the section.

And the payoff, which is a joke and an explanation at the same time:

> **strawberry → [straw][berry]  —  3 r's, 2 chunks**

The model is not looking at letters. It is looking at two pieces. That is the
honest reason letter-counting questions go wrong.

`N_MERGES = 32` is tuned deliberately. At 26 merges the word already splits into
`straw` + `berry`; by 90 the toy corpus is so over-trained that `strawberry`
collapses to a **single** token and the demo dies. The count is load-bearing —
change the corpus and the assertions at the top will catch it.

### What is not claimed

This is **BPE, the algorithm GPT-style tokenizers use**, trained on a toy
corpus. The splits are this tokenizer's, not OpenAI's. The video says "it",
never "GPT splits it this way." An earlier draft of this idea would have failed
honesty on exactly that point: with the original corpus, `strawberry` *shattered*
into nine near-letters, which is the opposite of what makes the joke true — so
the corpus was changed until the demo matched the claim, rather than the claim
being bent to match the demo.

---

## Stage 2: the link that moves

> the animal didn't cross the street because it was too **tired**

Which word is "it"? A thick gold thread runs from **it** up to **animal**, a thin
one to **street**.

Then one word changes:

> the animal didn't cross the street because it was too **wide**

and the thick thread **jumps to street**. Same sentence, one word, different
meaning. That is the clearest thing attention does, and it needs no jargon.

**The 85% is a computed softmax, not a measured attention head.** The scores are
stated as an example; the weights are their exact softmax, asserted at import to
sum to 1 and to round to 85 / 10 / 3 / 2. No model was run and the video does
not imply one was. The sentence pair is the standard Winograd-style example —
that swapping *tired* for *wide* moves the referent is a fact about English.

**The threads had to be straight.** The first cut used a sagging curve, but the
two text lines sit about one unit apart and the sag dipped below both endpoints,
so the threads read as underlines scribbled through the sentence. Straight lines
with a dot at each end read unambiguously as links.

---

## The sound

Render silent and add the track in the TikTok editor on the **day you post** —
audio baked into an upload cannot be attributed to the sound's page, and that
page is where a trending sound's reach comes from.

Trending as of the August 2026 check, per
[SocialBee](https://socialbee.com/blog/trending-tiktok-songs/),
[Buffer](https://buffer.com/resources/trending-songs-tiktok/) and
[tokchart](https://tokchart.com/): **Petal** (Ariana Grande), **Material Lover**
(Sienna Spiro), **Fade Into You** (Mazzy Star), *Cinderella*, *MORNING DEW*.

**Do not treat that list as current.** Trending sounds peak in 5–14 days, so a
sound chosen on render day is often dead by posting day — pick from TikTok's own
trending panel when you upload, then match the tempo:

```bash
BPM=<the real number> xvfb-run -a -s "-screen 0 1600x1200x24" \
    manimgl how_ai_reads.py HowAIReads -w -r 1080x1920
```

Nothing in the file is hard-coded to 150. For a 125 BPM sound, note that a beat
is then 28.8 frames rather than a whole number — `stadium_rave.py` has the
cumulative frame-snapping `T()` that handles that case and should be copied
across if this video moves off 150.

---

## Caption

```
Why can't AI count the r's in "strawberry"?

Because it never sees the letters.

Before a model reads anything, the text gets cut into chunks. And the chunks
aren't words — they're whatever pieces showed up most often in training. Watch
it happen: e+r becomes "er", b+er becomes "ber", then "berr", then "berry".
Separately s+t becomes "st", then "stra", then "straw".

Nobody told it about "straw" or "berry". It just counted.

So "strawberry" arrives as TWO pieces: [straw][berry]. The word has 3 r's. The
model is looking at 2 chunks. That's the whole reason it miscounts.

Then it reads the links. Take this:
"The animal didn't cross the street because it was too tired."
What is "it"? The animal — tired is a thing animals are.

Now change ONE word at the end:
"...because it was too wide."
Suddenly "it" is the street.

Same sentence. One word. The meaning moves. That's what a model is actually
tracking — not the words, the links between them.

#ai #howaiworks #tokenization #chatgpt #machinelearning #strawberry
```

**"Why can't AI count the r's in strawberry"** is the first line on purpose —
it is a question people genuinely type, it is the most-shared AI-failure story
of the last two years, and this video actually answers it instead of just
pointing at it.

**YouTube title:** `Why AI can't count the r's in "strawberry"`

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl how_ai_reads.py HowAIReads -w -r 1080x1920
python3 cinegrade.py videos/HowAIReads.mp4 how_ai_reads.mp4
```
