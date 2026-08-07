# How AI Solves It — 7 shorts

Companion to `ai_puzzles.py`. Seven classic puzzles, and the actual algorithm a
machine uses on each one.

- **Output:** 1080×1920, 60fps, **12.800000s** each — 32 beats = 8 bars at 150 BPM
- **Audio:** none. Add a track in the TikTok editor.

---

## What changed from every earlier video on this page

Three things, all driven by the analytics review rather than taste.

**Length: 12.8s, down from 48s.** The account sits in a 100–200 view band and
average watch time is still unknown. Until that number exists, short is the
safer bet — a 13-second video that gets finished and looped beats a 48-second
one that gets abandoned at five.

**Frame one is the loudest frame.** The earlier videos opened on near-black with
a small grey `1 / 6  put it down` progress bar. On a phone at scroll speed that
is a black rectangle, and it was spending the one second TikTok's test batch
gives you. These open full-screen on the puzzle name, and the chapter mark only
appears at beat 2.

**The hold moved to the end.** The first cut of these ran 48 beats and every
part finished animating around beat 15–22, then froze until beat 36 — five to
nine seconds of still image mid-video. The close now begins the instant the
animation ends, so the only long hold is on the takeaway card, which is where
the follow ask lives and the one place a hold does work.

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
