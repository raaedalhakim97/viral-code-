# a² + b² = c² — The Number On The Box

Companion to `screen_diagonal.py`. **Episode 2 of "WHY DID WE LEARN THIS?"**

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** AI voiceover — see below. `screen_diagonal_vo.mp4` carries it;
  `screen_diagonal.mp4` is still silent if you would rather use a trending sound.

---

## The hook

> **a² + b² = c²**
> they teach you this at school
> *you're about to realise what for*

Same shell as episode 1: the equation is the spine, it sits at the top from the
first second to the last, it starts empty, and every number is dragged into its
slot off a picture.

---

## What makes this one different: **c goes the other way**

In episode 1 every number travelled the same direction — off the graph, up into
the formula. Here:

| | | |
| --- | --- | --- |
| **a ← 8** | across the screen | dragged **up** into the equation |
| **b ← 6** | up the screen | dragged **up** into the equation |
| **c → 10** | *worked out inside the equation* | dropped back **down** onto the diagonal |

Nobody ever measures a diagonal. You can put a ruler across a screen and up a
screen, and then the formula hands you the one length you could not reach. **That
is what an equation is for**, stated as a movement rather than as a sentence —
and it is the only number in the video that travels downward.

---

## The payoff is a thing everyone has bought

```
8 across    6 up    →    8² + 6² = 64 + 36 = 100 = 10²
```

**Screens are sold by their diagonal.** A "10-inch tablet" is 8 inches across
and 6 inches up, and the 10 on the box is `c`. Almost everybody has bought a
phone, a laptop or a TV by a number in inches without ever asking what that
number measures.

The convention goes back to round CRT tubes, where the diagonal was the only
single number that described a circular screen, and it survived because it is
the one measurement that stays comparable across aspect ratios — 4:3, 16:9,
21:9 all get one honest number.

Sources: [SlashGear](https://www.slashgear.com/1333864/tvs-measured-diagonally/),
[BGR](https://www.bgr.com/2202051/why-is-screen-size-measured-diagonally/),
[Yahoo Tech](https://tech.yahoo.com/home-entertainment/tvs/articles/why-screen-size-measured-diagonally-101700668.html).

### Why 8 × 6 and not a "real" TV

8 × 6 is **4:3** — the classic screen ratio, and the numbers are exact:
`64 + 36 = 100 = 10²`, no rounding anywhere.

A 16:9 screen would have been more modern and much worse: a 55-inch TV is
47.94 × 26.96, and `48² + 27² = 3033`, whose square root is 55.07. **A video
whose payoff has to say "approximately" has lost.** The rule for this series is
that the number in the reveal is the true answer, not a convenient one.

### Verified at import

```
A² + B² == C²             exactly, in integers
A : B reduces to 4 : 3    a real aspect ratio, not one invented to fit
C == 10                   a whole number, so the payoff needs no rounding
```

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — the formula, and the promise |
| 8–24 | **a, b, c named on the screen.** Each slot lights gold as its edge lights gold |
| 24–46 | **Measure.** 8 dragged into a², 6 dragged into b² |
| 46–64 | **Solve.** 64 + 36 → 100 → c = 10, inside the equation |
| 64–82 | **Reveal.** The 10 drops onto the diagonal. *The box says 10"* |
| 82–91 | *We learned this at school. Nobody ever said what for.* |
| 91–100 | The eye |

The slot being talked about is gold and a size bigger; slots still waiting are
dim — and **the matching edge of the screen lights up at the same moment**, so
the letter and the thing it names are never on screen apart.

---

## Caption

```
a² + b² = c². They made you learn it. Watch what it was for.

Look at any screen you own. It has three lengths.

a is across. b is up. c is corner to corner.

You can measure a. You can measure b. Nobody has ever measured c — try putting a
ruler diagonally across your laptop.

So measure what you can:
across = 8
up = 6

Drop them in:
8² + 6² = c²
64 + 36 = 100
c = 10

And there it is. The diagonal is 10 — a number you never measured, handed to you
by the formula.

Now the part that will annoy you.

Every screen you have ever bought was sold to you by c. A "10-inch tablet" isn't
10 inches across — it's 8 across and 6 up. The number on the box is the DIAGONAL.
Same for your TV. Same for your laptop. Same for your phone.

They teach you this at school. You just now realise its use.

#maths #mathtok #pythagoras #gcse #studytok #geometry #techtok
```

**YouTube title:** `a² + b² = c² — the number on your TV box`

The searchable lines are *"what is the Pythagorean theorem used for"* and
*"why are TV screens measured diagonally"* — the second is a query people type
out of pure curiosity, and this video answers it with the first.

---

## Voiceover

`screen_diagonal_vo.mp4` is the graded render with an AI voice track over it;
`screen_diagonal_voice.wav` is the voice alone, for CapCut.

```bash
cd promo
SCRIPT=screen_diagonal python3 narrate_scene.py --check          # timing only
SCRIPT=screen_diagonal python3 narrate_scene.py screen_diagonal.mp4 \
       screen_diagonal_vo.mp4 --stem screen_diagonal_voice.wav
```

**Why bother when the video already has on-screen text.** TikTok transcribes
video audio and indexes the transcript. A silent video forfeits the platform's
strongest text signal, so the voice exists to say the two searchable sentences
out loud — *"a squared plus b squared equals c squared"* and *"every screen you
have ever bought was sold to you by its diagonal"*.

**The read is sparse on purpose.** Eleven lines across forty seconds, each
landing just *after* the thing it names, never on top of it. The on-screen text
already says every number; the voice says the meaning. The silence between the
lines is the pacing, not a gap to fill.

| at | line |
| --- | --- |
| 0.5 | a squared plus b squared equals c squared |
| 4.1 | Look at any screen you own |
| 6.0 | a is across. b is up. c is corner to corner |
| 10.9 | Measure across. Eight |
| 14.9 | Measure up. Six |
| 18.4 | Nobody ever measures a diagonal |
| 20.4 | Eight squared, sixty four. Six squared, thirty six |
| 23.8 | A hundred. So c is ten |
| 26.2 | A length you never measured, handed to you by the formula |
| 30.4 | Every screen you have ever bought was sold to you by its diagonal |
| 33.8 | We learned this at school. Nobody ever said what for |

**Two lines had to be shortened, not sped up.** `narrate_scene.py` speeds a line
that will not fit, down to a floor of `length_scale 0.80`, and then reports the
overrun rather than clipping. *"Nobody has ever measured a diagonal"* and
*"Eight squared is sixty four…"* both hit the floor and still bled into the next
line — two lines of speech on top of each other is worse than either being a
beat late. They were rewritten shorter instead, and the last line now clears at
36.5s, a tenth of a second before the eye. Worst overrun is **−0.07s**: nothing
overlaps.

Voice is `en-us-ryan-medium` through the house chain — rumble trimmed, a
watcher's distance of reverb. `VOICE=` and `PACE=` override both.

---

## Subtitle track

`screen_diagonal.srt` — 13 cues, no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## The pattern, now that there are two

The drag-into-the-slot mechanic is the reusable part of this series, and episode
2 adds the second half of it:

- **Drag up** what the viewer can measure.
- **Drop down** what only the formula can give them.

Any formula with that shape fits the shell. Next candidates:

| formula | measure | the formula hands you |
| --- | --- | --- |
| `πr²` | the radius of a pizza | why 16-inch is nearly twice 12-inch |
| `d = √(Δx² + Δy²)` | two points on a map | the straight-line distance your phone shows |
| percentages | 20% off, then 10% off | the price that is *not* 30% off |
| standard deviation | a set of wages | what "average salary" was hiding |

The map one is the natural episode 3: it is the same `a² + b² = c²` with the
triangle drawn between two pins, and it is genuinely what every map app computes
for "as the crow flies".

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl screen_diagonal.py ScreenDiagonal -w -r 1080x1920
python3 cinegrade.py videos/ScreenDiagonal.mp4 screen_diagonal.mp4
```
