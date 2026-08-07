# How AI Solves It — 7 shorts

Companion to `ai_puzzles.py`. Seven classic puzzles, and the actual algorithm a
machine uses on each one.

- **Output:** 1080×1920, 60fps, **28.800000s** each — 72 beats = 18 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## Length, revised twice

**48s → 12.8s → 28.8s.** Worth recording why, because both wrong answers were
wrong for different reasons.

The 48-second cut held a frozen frame for a third of its length: every part
finished animating around beat 15–22 and then sat there until beat 36.

Cutting to 12.8s fixed that and broke something more important. **You cannot
show someone what breadth-first search *is* in nine seconds of animation.** The
casualty was the step that makes an algorithm feel necessary rather than
arbitrary: *why the obvious approach fails*. Without it the video shows a
technique nobody asked for the point of.

28.8s is the version with room for the full shape, which every part now follows:

> state the puzzle → **show the naive way failing** → walk the algorithm in
> labelled steps → the result → the takeaway → the eye

The maze is the clearest case. At 12.8s it flooded a grid and announced an
answer. It now walks you into a dead-end corridor first, crosses it out, and
*then* floods — so the flood reads as a solution to a problem you just watched
happen.

**Frame one is still the loudest frame**, and that stays. The earlier videos
opened on near-black with a small grey `1 / 6  put it down` progress bar, which
at scroll speed is a black rectangle, spending the one second TikTok's test
batch gives you. These open full-screen on the puzzle name; the `1 / 7` mark
appears at beat 2.

**The logo card is back.** The 12.8s cut dropped the observer eye and shipped
only a grey handle line — the one piece of the page's identity that appears in
every other video. All seven now close on the eye, PAUSE / OBSERVE / LEARN, and
the follow ask, with 10 beats to read it.

## A running commentary line

Every part now carries a line of narration under the diagram, swapped as the
algorithm proceeds — `guess a direction and commit` → `dead end. start again.`
→ `so it never picks one` → `it spreads into all of them at once`.

This is the single biggest difference from the short cut, and it is what makes
the videos teachable rather than decorative. It also gives TikTok and YouTube
on-screen text to OCR, which matters more than usual here because these are
silent and there is no transcript to index.

---

## The seven

| # | Puzzle | Algorithm | Takeaway |
| --- | --- | --- | --- |
| 1 | The maze | breadth-first search | It never guessed a direction — it flooded every one |
| 2 | Wolf, goat, cabbage | state-space search | A story becomes a map of states |
| 3 | Tic-tac-toe | minimax | It plays every game to the end, then picks |
| 4 | Six queens | backtracking | Be wrong, cheaply |
| 5 | Sudoku | constraint propagation | It never tried a number — it removed eight |
| 6 | The salesman | combinatorial explosion | Stop trying to be perfect |
| 7 | Sliding tile | A* | A good guess about distance is the whole trick |

Seven puzzles, seven *different* algorithms. That's deliberate — the series
teaches the shape of the field, not seven versions of "computers are fast."

---

## Every number was computed

| Claim | Value | Source |
| --- | --- | --- |
| Tic-tac-toe games | **255,168** | full game-tree enumeration, stopping at a win |
| River crossings | **7** | BFS over the legal states |
| Maze shortest path | **10 steps** | the BFS in the scene |
| Queens backtracks | **25** | the real trace, counted |
| TSP routes, 5 / 10 / 30 | **12 / 181,440 / 4.4 × 10³⁰** | (n−1)!/2 |
| 15-puzzle states | **10,461,394,944,000** | 16!/2 |

**The maze flood and the queens backtracking are the real algorithms**, run at
build time. The order the frontier expands and every single undo on screen are
what the code actually did — not a hand-drawn impression of it. `maze_bfs()`
raises if the maze has no solution, and part 4's "it was wrong 25 times" is
`len([e for e in trace if e[0] == 'undo'])`, not a number I liked the sound of.

### One claim I had to throw out

An earlier cut of part 6 ended on *"20 cities outlasts the universe."* It does
not. At a billion routes a second, 20 cities is 6.08 × 10¹⁶ routes — about
**1.9 years**. Nowhere near.

30 cities is 4.42 × 10³⁰ routes, which at the same rate is 1.4 × 10¹⁴ years, or
roughly **10,000× the age of the universe**. So the table now ends at 30 and the
card states the rate it assumes, because the claim only means anything with the
rate attached.

Part 7 had the same disease in smaller form: it closed on *"one looks at 5×
less,"* which was me reading a ratio off my own dot counts and presenting it as
a property of A*. It now says "one barely looks."

---

## Captions

Each is written so the searchable phrase is in the **first line**, since these
are silent and there's no transcript for TikTok or YouTube to index.

**1 — maze**
```
How does AI find its way out of a maze? It doesn't guess a direction. It floods
every direction at once — breadth-first search — and the first time the flood
touches the exit, that path is guaranteed shortest. 10 steps here.

#ai #algorithms #computerscience #maze #coding
```

**2 — river**
```
The wolf, goat and cabbage puzzle — and how a computer solves it. The trick a
machine finds instantly: the goat has to cross three times. AI turns the story
into a map of states and walks it. 7 crossings is provably the minimum.

#puzzle #riddle #ai #logic #brainteaser
```

**3 — tic-tac-toe**
```
Why you can never beat the computer at tic-tac-toe. There are 255,168 possible
games. It plays all of them to the end, scores each one, then picks the branch
where your best play still loses. That's minimax.

#ai #tictactoe #gametheory #algorithms #minimax
```

**4 — six queens**
```
Six queens, six rows, none attacking. Watch the computer get it wrong 25 times
on the way to right. That's backtracking — place, fail, undo, try the next one.
Being wrong cheaply is the whole strategy.

#chess #puzzle #algorithms #ai #coding
```

**5 — sudoku**
```
How AI solves sudoku — and it's not by trying numbers. It looks at what the row
already has, what the column has, what the box has, and deletes those options.
Eight disappear. One is left. That's constraint propagation.

#sudoku #ai #logic #puzzle #algorithms
```

**6 — salesman**
```
Why brute force dies. 5 cities is 12 possible routes. 10 cities is 181,440.
30 cities is 4.4 × 10³⁰ — and at a billion routes every second, checking them
all takes 10,000 times longer than the universe has existed. So AI stops trying
to be perfect and starts guessing well.

#ai #algorithms #maths #computerscience #tsp
```

**7 — sliding tile**
```
The sliding tile puzzle has 10,461,394,944,000 possible states. Blind search
looks everywhere. A* uses one extra piece of information — a rough guess at how
far the goal still is — and walks almost straight to it. Same answer, a fraction
of the looking.

#ai #algorithms #astar #pathfinding #computerscience
```

---

## Posting

These are a series, so post **one a day in order** and reply to every comment on
the previous one before the next goes up. The numbered `1 / 7` mark is doing the
same job as the earlier series — giving someone who liked part 3 a reason to
check the profile for parts 1 and 2, which is the exact leak in the funnel.

Also upload all seven to YouTube Shorts on the same schedule. Titles as the
question, not the label:

- `How does AI escape a maze?`
- `The wolf, goat and cabbage puzzle — how a computer solves it`
- `Why you can't beat the computer at tic-tac-toe`
- `Watch an algorithm fail 25 times before it succeeds`
- `How AI solves sudoku without guessing`
- `Why brute force takes longer than the universe`
- `The trick that makes pathfinding fast`

---

## Build

```bash
cd promo
for p in 1 2 3 4 5 6 7; do
  PART=$p BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" \
    manimgl ai_puzzles.py AIPuzzles -w -r 1080x1920
  mv videos/AIPuzzles.mp4 videos/AIPuzzles_$p.mp4
  python3 cinegrade.py videos/AIPuzzles_$p.mp4 ai_puzzle_$p.mp4
done
```
