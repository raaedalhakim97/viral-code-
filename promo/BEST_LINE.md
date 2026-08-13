# What if the dots DON'T line up?

Companion to `best_line.py`. **Episode 6 of "WHY DID WE LEARN THIS?"** — and
the direct sequel to episode 1.

- **Output:** 1080×1920, 60fps, **40.000000s** — 100 beats = 25 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor. **No AI voice** — see the
  scope section in `MARKETING.md`.

---

## The hook

> **miss = real − guess**
> but what if the dots
> *DON'T line up?*

---

## Episode 1 cheated, on purpose

Its four dots sat exactly on the line, so the line could just be drawn through
them and `m` and `b` read straight off. Real sales never do that — and the
moment they don't, *"draw the line"* stops being something you can do by eye and
becomes something you have to **measure**.

That measurement is the whole of this video, and it is the same measurement
every AI on earth is trained by.

---

## The spine

```
miss  =  real  −  guess
```

| slot | comes from | direction |
| --- | --- | --- |
| **real** ← 45 | the dot: what the shop actually sold on day 2 | dragged **up** |
| **guess** ← 40 | the line: what the line said it would sell | dragged **up** |
| **miss** → 5 | the gap between them | dropped **down** onto the bar |

Two measurements up, the thing they make dropped back down — the same two-way
pattern as every episode.

---

## The data

```
day     1    2    3    4
sales  30   45   50   65        the dots do NOT line up

line A   y = 10x + 20  ->  30  40  50  60     nails two, misses two by 5
line B   y = 11x + 20  ->  31  42  53  64     misses all four, a little

total    A:  0² + 5² + 0² + 5²  =  50
         B:  1² + 3² + 3² + 1²  =  20
```

**The lesson is in that comparison.** The line that goes exactly through two of
the points is the **worse** line. The good line misses everything slightly
rather than some things badly — which is not obvious, is genuinely useful, and
happens to be a sentence about maths that is also a sentence about life.

**Line A is episode 1's line**, which is why it is the one that gets tried
first: the audience has already watched it get built.

**Why square.** A dot 3 below is exactly as wrong as a dot 3 above, so the signs
have to stop cancelling. Squaring is the cheapest way to do that, and it is
where *least squares* gets its name.

### Verified at import

```
line B is the real least-squares fit    computed, not asserted — returns (11, 20)
every prediction is a whole number      both lines, all four days
the two totals are 50 and 20            in integers
line A nails exactly two of them        the claim the picture makes
B beats A                               so the payoff is a fact, not a hope
the dots do NOT lie on line A           or this is episode 1 again
```

---

## It closes the loop on episode 4

Gradient descent said *"the height of the valley is how wrong the model is"* and
never said where that height came from. **This is where it comes from.** The
total miss *is* the height. Episode 4 rolls down the hill this episode builds.

---

## Structure

| Beats | |
| --- | --- |
| 0–8 | Hook — *what if the dots don't line up?* |
| 8–26 | Four dots. They don't line up. So which line is right? |
| 26–50 | Line A. One dot, one gap: **real 45, guess 40, miss 5** |
| 50–68 | All four gaps, squared, added: **total miss = 50** |
| 68–82 | Tilt it. The bars shrink, the total falls to **20**. That is training |
| 82–88 | *We learned this at school. Nobody ever said what for.* |
| 88–92 | **Send this to your school friend — tell them THIS is how it's solved** |
| 92–100 | The eye |

**The y-axis is cropped to 25–72, not 0–72.** At full range a miss of 5 is 6% of
the plot and the bars are invisible. Cropped, it is 11% and they read. Nothing
is lost — `b` is not what this episode is about.

**Line A's two zero-length bars are a feature.** "It nails two of them and blows
two" is exactly the shape of the wrong answer, and you can see it at a glance.

---

## Caption

```
Last time the dots sat perfectly on a line. Real sales never do that.

Four days: 30, 45, 50, 65. Now no straight line goes through all four. So which
line is RIGHT?

You need a way to score a line. Here it is:

miss = real − guess

Day 2. The line says 40. The shop sold 45. The miss is 5.

Do that for every day. A dot below counts the same as a dot above, so square
them so the signs stop cancelling:

Line A (y = 10x + 20): 0² + 5² + 0² + 5² = 50
Line B (y = 11x + 20): 1² + 3² + 3² + 1² = 20

50 down to 20. Line B is better — and look WHY. Line A goes exactly through two
of the points. Line B goes exactly through none of them.

The good line misses everything a little, instead of nailing two and blowing
two.

That number — the total miss — is the ONLY thing training an AI ever does. Nudge
the line, check the number, keep whatever made it smaller. A few billion times.

We learned this at school. Nobody ever said what for.

#maths #mathtok #ai #machinelearning #leastsquares #statistics #gcse
```

**YouTube title:** `What if the dots don't line up? — the line that misses least`

---

## Subtitle track

`best_line.srt` — no gaps, no overlaps, asserted at generation.
YouTube → Subtitles → Add language → Upload file → With timing.

---

## Changing the data

`SALES`, and the two candidate lines `MA/BA` and `MB/BB`, are the only things to
edit. The assertions pin the current answers — including the one that recomputes
the least-squares fit and checks line B *is* it. Change the data and that
assertion fails until B is set to the real best line, which is deliberate: the
video claims B is the best line there is, so the code has to keep that true.

---

## Build

```bash
cd promo
BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" manimgl best_line.py BestLine -w -r 1080x1920
python3 cinegrade.py videos/BestLine.mp4 best_line.mp4
```
