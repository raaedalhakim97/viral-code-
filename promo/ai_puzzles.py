"""
ai_puzzles — 7 shorts: a puzzle, and the algorithm an AI actually uses on it.

    PART=1 BPM=150 manimgl ai_puzzles.py AIPuzzles -w -r 1080x1920

72 beats = 18 bars = 28.800s at 150 BPM.

    1  maze          breadth-first search
    2  river crossing state-space search
    3  tic-tac-toe   minimax
    4  n-queens      backtracking
    5  sudoku        constraint propagation
    6  salesman      combinatorial explosion / heuristics
    7  sliding tile  A* — a heuristic beats raw search

LENGTH, TWICE REVISED. The first cut was 48s and held a frozen frame for a
third of it. The second was 12.8s, which fixed the hold and broke the teaching:
you cannot show someone what breadth-first search IS in nine seconds of
animation. 28.8s is the version that has room for the step the short cut
dropped — WHY THE OBVIOUS APPROACH FAILS — which is the beat that makes an
algorithm feel necessary rather than arbitrary.

Every part now runs: state the puzzle -> show the naive way failing -> walk the
algorithm in labelled steps -> the result -> the takeaway -> the eye.

EVERY NUMBER ON SCREEN WAS COMPUTED, NOT QUOTED.
    255,168             complete legal tic-tac-toe games
    7                   minimum river crossings (BFS over legal states)
    10 steps / 11 rings the maze, from the BFS in this file
    25                  queens backtracks, counted from the real trace
    12 / 181,440        TSP routes for 5 / 10 cities, (n-1)!/2
    4.42e30             ... for 30 cities. At a billion routes a second that
                        is 1.4e14 years, ~10,000x the age of the universe.
                        (20 cities is only ~2 years — an earlier cut claimed
                        it "outlasts the universe", which was simply false.)
    10,461,394,944,000  reachable 15-puzzle states, 16!/2

The maze search and the queens backtracking are the REAL algorithms run at
build time — the frontier order and every backtrack on screen are what the
code actually did, not a hand-drawn impression of it.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    ShowCreation(make_thing()) leaves an orphan copy in the scene
"""
import math
import os
from collections import deque

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
PART = int(os.environ.get("PART", 1))
FPS = 60
TOTAL = 72
BODY_END = 56          # puzzle + why + algorithm + result
TAKE_END = 62          # the two takeaway lines

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
TOP_Y   = 3.30
CAP_Y   = 1.78         # clears the shrunk title (2.62) and subtitle (2.18)
NOTE_Y  = -1.62        # the running commentary under each diagram

TITLES = {
    1: ("THE MAZE",         "breadth-first search"),
    2: ("THE RIVER",        "state-space search"),
    3: ("TIC-TAC-TOE",      "minimax"),
    4: ("SIX QUEENS",       "backtracking"),
    5: ("SUDOKU",           "constraint propagation"),
    6: ("THE SALESMAN",     "why brute force dies"),
    7: ("THE SLIDING TILE", "A*"),
}


def txt(s, size=27, color=WHITE_, bold=True, w=4.3):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def seg(a, b, color=WHITE_, w=3.0, op=1.0):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners([a, b])
    m.set_stroke(opacity=op)
    return m


def cell(x, y, s, fill, op, stroke=0.0):
    r = Rectangle(width=s, height=s, stroke_width=stroke)
    r.set_fill(fill, opacity=op)
    if stroke:
        r.set_stroke(FAINT, opacity=0.8)
    return r.move_to(np.array([x, y, 0]))


def queen(o, s, color=GOLD):
    w = s * 0.30
    pts = [(-w, -w * 0.55), (w, -w * 0.55), (w * 0.92, w * 0.55),
           (w * 0.45, w * 0.05), (0, w * 0.75), (-w * 0.45, w * 0.05),
           (-w * 0.92, w * 0.55)]
    m = VMobject(stroke_color=color, stroke_width=2.4)
    m.set_points_as_corners([o + np.array([a, b, 0]) for a, b in pts] +
                            [o + np.array([pts[0][0], pts[0][1], 0])])
    m.set_fill(color, opacity=0.30)
    return m


def cross(o, color=GREY, s=0.20):
    return VGroup(seg(o + np.array([-s, -s, 0]), o + np.array([s, s, 0]), color, 3.0),
                  seg(o + np.array([-s, s, 0]), o + np.array([s, -s, 0]), color, 3.0))


def observer_eye(color):
    grp = VGroup()
    for sign in (1, -1):
        m = VMobject(color=color, stroke_width=2.2)
        m.set_points_smoothly(
            [np.array([x, sign * 0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
             for x in np.linspace(-1.6, 1.6, 20)])
        grp.add(m)
    grp.add(Circle(radius=0.42, stroke_color=color, stroke_width=2.2).move_to(ORIGIN))
    grp.add(Dot(ORIGIN, radius=0.12, fill_color=color))
    rng = np.random.default_rng(2)
    for _ in range(5):
        s = rng.uniform(0.05, 0.12)
        sq = Square(side_length=s, color=color, stroke_width=1.5)
        sq.move_to([rng.uniform(1.7, 2.4), rng.uniform(-0.6, 0.6), 0])
        sq.set_fill(color, opacity=0.5)
        grp.add(sq)
    return grp


# --------------------------------------------------------------------------
# (6,1) is a genuine dead end — the corridor a guess walks into. Verified:
# 23 cells all reachable, shortest path 10 steps, 11 BFS rings.
MAZE = [
    "#######",
    "#S....#",
    "#.###.#",
    "#...#.#",
    "#.#.#.#",
    "#.#.#.#",
    "#.#...#",
    "###.#E#",
    "#######",
]
DEAD_END = [(2, 1), (3, 1), (4, 1), (5, 1), (6, 1)]


def maze_bfs(grid):
    h, w = len(grid), len(grid[0])
    start = end = None
    for r in range(h):
        for c in range(w):
            if grid[r][c] == "S":
                start = (r, c)
            elif grid[r][c] == "E":
                end = (r, c)
    dist, prev, q = {start: 0}, {}, deque([start])
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            n = (r + dr, c + dc)
            if 0 <= n[0] < h and 0 <= n[1] < w and grid[n[0]][n[1]] != "#" \
                    and n not in dist:
                dist[n] = dist[(r, c)] + 1
                prev[n] = (r, c)
                q.append(n)
    if end not in dist:
        raise ValueError("maze has no solution — fix MAZE")
    rings = {}
    for k, v in dist.items():
        rings.setdefault(v, []).append(k)
    path, cur = [end], end
    while cur != start:
        cur = prev[cur]
        path.append(cur)
    return [rings[d] for d in sorted(rings)], path[::-1], start, end


def queens_trace(n):
    ev, cols, d1, d2 = [], set(), set(), set()

    def go(r):
        if r == n:
            return True
        for x in range(n):
            if x in cols or r - x in d1 or r + x in d2:
                continue
            cols.add(x); d1.add(r - x); d2.add(r + x)
            ev.append(("put", r, x))
            if go(r + 1):
                return True
            cols.discard(x); d1.discard(r - x); d2.discard(r + x)
            ev.append(("undo", r, x))
        return False

    go(0)
    return ev


class AIPuzzles(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None

        self.clock = ValueTracker(0.0)
        self.clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(self.clock)

        self.open_card()
        [self.p1, self.p2, self.p3, self.p4,
         self.p5, self.p6, self.p7][PART - 1]()

    # ------------------------------------------------------------------
    def T(self, beats):
        self.used += beats
        return round(beats * self.B * FPS) / FPS

    def pad_to(self, target):
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(f"PART {PART} overruns by {-rem:.2f} beats")
        if rem > 0.01:
            self.wait(self.T(rem))

    def kick(self):
        t = self.clock.get_value()
        return float(np.exp(-(((t % self.B) / self.B) / 0.15) ** 2))

    def dance(self, mob, amt=0.055):
        h0 = mob.get_height()
        mob.add_updater(lambda m: m.set_height(h0 * (1 + amt * self.kick())))
        return mob

    def say(self, s, beats=2, color=WHITE_, size=23):
        """Running commentary under the diagram. This is the line the 12.8s
        cut had no room for, and it is what makes the algorithm legible."""
        new = txt(s, size, color, bold=False, w=4.4)
        new.move_to(np.array([0, NOTE_Y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    # ------------------------------------------------------------------
    def open_card(self):
        """Frame one is the loudest frame. No HUD, no progress bar."""
        name, method = TITLES[PART]
        self.title = txt(name, 54, WHITE_, w=4.6)
        self.title.move_to(np.array([0, 1.05, 0]))
        self.sub = txt(method, 24, GOLD, bold=False)
        self.sub.move_to(np.array([0, 0.35, 0]))
        self.add(self.title, self.sub)          # on screen at frame 0
        self.wait(self.T(2))

        self.mark = txt(f"{PART} / 7   HOW AI SOLVES IT", 18, GREY,
                        bold=False, w=3.6)
        self.mark.move_to(np.array([0, TOP_Y, 0]))
        self.play(FadeIn(self.mark), run_time=self.T(1))
        self.play(self.title.animate.set_height(
                      self.title.get_height() * 0.52).move_to(np.array([0, 2.62, 0])),
                  self.sub.animate.set_height(
                      self.sub.get_height() * 0.86).move_to(np.array([0, 2.18, 0])),
                  run_time=self.T(1))

    def close(self, a, b):
        self.pad_to(BODY_END)
        for m in self.stage + ([self.note] if self.note else []):
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.stage +
                    ([self.note] if self.note else [])], run_time=self.T(1))

        l1 = txt(a, 29, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.55, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2), rate_func=rush_from)
        l2 = txt(b, 25, GOLD, w=4.4)
        l2.move_to(np.array([0, -0.25, 0]))
        self.play(FadeIn(l2), run_time=self.T(1))
        self.pad_to(TAKE_END)
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(self.title),
                  FadeOut(self.sub), FadeOut(self.mark), run_time=self.T(1))
        self.signature()

    def signature(self):
        """The logo card. Every video on the page ends here."""
        self.clock.clear_updaters()
        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.25, 0])).scale(0.78)
        self.play(ShowCreation(eye), run_time=self.T(3))
        words = VGroup(txt("PAUSE", 20), txt("OBSERVE", 20), txt("LEARN", 20)) \
            .arrange(RIGHT, buff=0.42).move_to(np.array([0, -0.55, 0]))
        self.play(FadeIn(words, shift=0.08 * UP), run_time=self.T(1))
        cta = txt("Follow for the math behind AI", 27)
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.18)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=self.T(1))
        self.pad_to(TOTAL - 2)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=self.T(2))

    # ==================================================================
    def p1(self):
        rings, path, start, end = maze_bfs(MAZE)
        h, w = len(MAZE), len(MAZE[0])
        s = 0.42
        ox, oy = -(w - 1) * s / 2, 0.10 + (h - 1) * s / 2

        cells, walls = {}, VGroup()
        for r in range(h):
            for c in range(w):
                x, y = ox + c * s, oy - r * s
                if MAZE[r][c] == "#":
                    walls.add(cell(x, y, s, FAINT, 1.0))
                else:
                    cells[(r, c)] = cell(x, y, s, COOL, 0.0, stroke=1.0)
        board = VGroup(walls, *cells.values())
        self.play(FadeIn(board), run_time=self.T(2))
        for tag, pos, col in (("start", start, WHITE_), ("exit", end, GOLD)):
            t = txt(tag, 15, col, bold=False, w=0.8)
            t.move_to(np.array([ox + pos[1] * s, oy - pos[0] * s, 0]))
            board.add(t)
        self.play(FadeIn(board[-2]), FadeIn(board[-1]), run_time=self.T(1))
        self.stage = [board]
        self.say("find the shortest way out", 2)

        # why guessing fails — a real dead-end corridor
        self.say("guess a direction and commit", 2)
        self.play(*[cells[p].animate.set_fill(GREY, 0.45) for p in DEAD_END],
                  run_time=self.T(2))
        de = cross(np.array([ox + s, oy - 6 * s, 0]), WHITE_, 0.14)
        self.play(ShowCreation(de), run_time=self.T(1))
        self.stage.append(de)
        self.say("dead end. start again.", 3)
        self.play(FadeOut(de), *[cells[p].animate.set_fill(COOL, 0.0)
                                 for p in DEAD_END], run_time=self.T(1))
        self.stage.remove(de)

        self.say("so it never picks one", 2)
        self.say("it spreads into all of them at once", 3)
        for i, ring in enumerate(rings):
            grp = [cells[p] for p in ring if p in cells]
            if grp:
                self.play(*[c.animate.set_fill(COOL, 0.60) for c in grp],
                          run_time=self.T(1.5), rate_func=linear)
        self.say("every square now knows its distance", 3)
        self.play(*[cells[p].animate.set_fill(GOLD, 0.85) for p in path],
                  run_time=self.T(3))
        self.say(f"first touch of the exit — {len(path) - 1} steps", 3, GOLD)
        self.close("The first path it finds is the shortest one.",
                   "That is breadth-first search.")

    # ==================================================================
    def p2(self):
        NEAR_Y, FAR_Y = 1.15, -0.75
        COLS = {"wolf": -1.35, "goat": 0.0, "cabbage": 1.35}
        moves = [("goat", 1), (None, -1), ("wolf", 1), ("goat", -1),
                 ("cabbage", 1), (None, -1), ("goat", 1)]

        river = VGroup(seg(np.array([-2.3, 0.55, 0]), np.array([2.3, 0.55, 0]), FAINT, 3),
                       seg(np.array([-2.3, -0.18, 0]), np.array([2.3, -0.18, 0]), FAINT, 3))
        items = {}
        for name, x in COLS.items():
            box = Rectangle(width=1.15, height=0.40, stroke_width=2.0)
            box.set_stroke(GOLD if name == "goat" else GREY, opacity=0.9)
            lab = txt(name, 18, GOLD if name == "goat" else WHITE_, bold=False, w=1.0)
            items[name] = VGroup(box, lab).move_to(np.array([x, NEAR_Y, 0]))
        self.play(FadeIn(river), run_time=self.T(1))
        self.play(*[FadeIn(g, shift=0.08 * DOWN) for g in items.values()],
                  run_time=self.T(2))
        self.stage = [river] + list(items.values())
        self.say("get all three across", 2)
        self.say("the boat holds one", 2)

        # the two constraints, drawn
        bad = VGroup()
        w1 = seg(np.array([-1.35, NEAR_Y - 0.28, 0]),
                 np.array([0.0, NEAR_Y - 0.28, 0]), GREY, 2.4)
        w2 = seg(np.array([0.0, NEAR_Y - 0.44, 0]),
                 np.array([1.35, NEAR_Y - 0.44, 0]), GREY, 2.4)
        bad.add(w1, w2)
        self.play(ShowCreation(w1), run_time=self.T(1))
        self.say("alone, the wolf eats the goat", 2)
        self.play(ShowCreation(w2), run_time=self.T(1))
        self.say("alone, the goat eats the cabbage", 2)
        self.stage.append(bad)
        self.play(FadeOut(bad), run_time=self.T(1))
        self.stage.remove(bad)

        self.say("every arrangement is a state", 2)
        self.say("it searches them for a legal path", 3)
        boat = Rectangle(width=0.60, height=0.24, stroke_width=2.2)
        boat.set_stroke(WHITE_, opacity=0.9).move_to(np.array([0, 0.38, 0]))
        self.play(FadeIn(boat), run_time=self.T(1))
        self.stage.append(boat)

        for i, (what, direction) in enumerate(moves):
            by = -0.02 if direction > 0 else 0.38
            anims = [boat.animate.move_to(np.array([0, by, 0]))]
            if what:
                anims.append(items[what].animate.move_to(
                    np.array([COLS[what], FAR_Y if direction > 0 else NEAR_Y, 0])))
            lab = f"{i + 1}.  " + (f"{what} across" if what and direction > 0
                                   else f"{what} back" if what else "row back empty")
            self.say(lab, 1, GOLD if what == "goat" else GREY, 21)
            self.play(*anims, run_time=self.T(1.5), rate_func=smooth)

        self.say("7 crossings — proven minimum", 2, GOLD)
        self.close("The goat crosses three times.",
                   "AI turns a story into a map of states.")

    # ==================================================================
    def p3(self):
        root = np.array([0, 1.05, 0])
        kids = [np.array([x, 0.05, 0]) for x in (-1.5, 0, 1.5)]
        gk = [np.array([x, -0.95, 0]) for x in (-1.95, -1.05, -0.45,
                                                0.45, 1.05, 1.95)]
        edges = VGroup(*[seg(root, k, FAINT, 2.0) for k in kids],
                       *[seg(kids[i // 2], g, FAINT, 2.0) for i, g in enumerate(gk)])
        dots = VGroup(*[Dot(p, radius=0.10, fill_color=WHITE_)
                        for p in [root] + kids + gk])
        n = txt("255,168 possible games", 24, GREY, bold=False)
        n.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(n), run_time=self.T(1))
        self.stage = [n]
        self.say("you have never beaten a computer at this", 3)
        self.play(ShowCreation(edges), FadeIn(dots), run_time=self.T(3))
        self.stage += [edges, dots]
        self.say("it maps every move you could make", 3)

        vals = [-1, 0, 1, 0, 1, -1]
        leaves = VGroup()
        for p, v in zip(gk, vals):
            t = txt(f"{v:+d}", 20, GOLD if v > 0 else GREY, bold=False, w=0.5)
            t.move_to(p + np.array([0, -0.40, 0]))
            leaves.add(t)
        self.play(FadeIn(leaves, shift=0.08 * UP), run_time=self.T(2))
        self.stage.append(leaves)
        self.say("+1 it wins,  0 draw,  −1 you win", 3)

        mins = [min(vals[0:2]), min(vals[2:4]), min(vals[4:6])]
        mid = VGroup()
        for p, v in zip(kids, mins):
            t = txt(f"{v:+d}", 22, GOLD if v > 0 else GREY, w=0.5)
            t.move_to(p + np.array([0.34, 0.10, 0]))
            mid.add(t)
        self.say("your turn: it assumes you play your best", 3)
        self.play(FadeIn(mid), run_time=self.T(2))
        self.stage.append(mid)
        self.say("so each branch keeps your best, not its own", 3)

        top = txt(f"{max(mins):+d}", 26, GOLD, w=0.6)
        top.move_to(root + np.array([0.40, 0.14, 0]))
        self.say("its turn: it takes the best of those", 3)
        self.play(FadeIn(top, scale=1.2), run_time=self.T(2))
        self.stage.append(top)
        self.say("a draw, against your perfect play", 3, GOLD)
        self.close("It plays every game to the end first.",
                   "Then picks the branch you cannot win.")

    # ==================================================================
    def p4(self):
        n, s = 6, 0.55
        ox, oy = -(n - 1) * s / 2, 0.35 + (n - 1) * s / 2
        squares = VGroup()
        for r in range(n):
            for c in range(n):
                squares.add(cell(ox + c * s, oy - r * s, s,
                                 GREY if (r + c) % 2 else FAINT,
                                 0.22 if (r + c) % 2 else 0.65))
        self.play(FadeIn(squares), run_time=self.T(2))
        self.stage = [squares]
        self.say("six queens, none attacking", 2)

        # show what "attacking" means
        demo = queen(np.array([ox + 2 * s, oy - 2 * s, 0]), s)
        self.play(FadeIn(demo), run_time=self.T(1))
        lines = VGroup()
        o = np.array([ox + 2 * s, oy - 2 * s, 0])
        for d in ((1, 0), (0, 1), (1, 1), (1, -1)):
            lines.add(seg(o - np.array([d[0], d[1], 0]) * 2.4,
                          o + np.array([d[0], d[1], 0]) * 2.4, GREY, 1.8, 0.55))
        self.play(ShowCreation(lines), run_time=self.T(2))
        self.say("a queen owns its row, column and diagonals", 3)
        self.play(FadeOut(demo), FadeOut(lines), run_time=self.T(1))

        self.say("so it places one, then tries the next row", 3)
        live, undos = {}, 0
        for kind, r, c in queens_trace(n):
            o = np.array([ox + c * s, oy - r * s, 0])
            if kind == "put":
                q = queen(o, s)
                live[(r, c)] = q
                self.add(q)
            else:
                undos += 1
                q = live.pop((r, c), None)
                if q is not None:
                    self.remove(q)
            self.wait(self.T(0.25))
            if undos == 1 and kind == "undo":
                self.say("stuck — take the last one back", 2)

        for q in live.values():
            self.stage.append(q)
        self.say(f"solved, after {undos} backtracks", 3, GOLD)
        self.close(f"It was wrong {undos} times on the way.",
                   "Backtracking: be wrong, cheaply.")

    # ==================================================================
    def p5(self):
        s = 0.60
        grid, marks = VGroup(), {}
        for r in range(3):
            for c in range(3):
                o = np.array([(c - 1) * s, 1.05 - r * s, 0])
                grid.add(cell(o[0], o[1], s, FAINT, 0.55, stroke=1.0))
                d = txt(str(r * 3 + c + 1), 24, GREY, bold=False, w=0.4)
                d.move_to(o)
                marks[r * 3 + c + 1] = d
                grid.add(d)
        self.play(FadeIn(grid), run_time=self.T(2))
        self.stage = [grid]
        self.say("one empty square in a sudoku", 3)
        self.say("nine numbers could go in it", 3)
        self.say("a person tries them. it doesn't.", 3)

        for reason, gone, beats in (
                ("its row already contains 2, 4 and 9", [2, 4, 9], 3),
                ("its column already contains 1, 6 and 8", [1, 6, 8], 3),
                ("its box already contains 3 and 5", [3, 5], 3)):
            self.say(reason, beats)
            self.play(*[marks[g].animate.set_opacity(0.08) for g in gone],
                      run_time=self.T(2))

        self.say("eight are impossible", 3)
        left = self.dance(txt("7", 46, GOLD).move_to(np.array([0, -0.75, 0])), 0.06)
        self.play(FadeIn(left, scale=1.3), run_time=self.T(2))
        self.stage.append(left)
        self.say("one is left, and it was never a guess", 3, GOLD)
        self.close("It never tried a number.",
                   "It removed the eight that couldn't fit.")

    # ==================================================================
    def p6(self):
        pts = [np.array([0.95 * np.cos(a), 0.95 * np.sin(a) + 0.75, 0])
               for a in np.linspace(0, 2 * np.pi, 6)[:5]]
        dots = VGroup(*[Dot(p, radius=0.10, fill_color=WHITE_) for p in pts])
        self.play(FadeIn(dots), run_time=self.T(2))
        self.stage = [dots]
        self.say("visit all five, come home, go the shortest way", 3)

        shown = None
        for k in range(3):
            order = [0] + list(np.roll([1, 2, 3, 4], k)) + [0]
            t = VGroup(*[seg(pts[order[i]], pts[order[i + 1]], GOLD, 2.0, 0.75)
                         for i in range(5)])
            self.play(ShowCreation(t), run_time=self.T(1.5))
            if k == 0:
                self.say("check a route, measure it, try the next", 3)
            if k < 2:
                self.play(FadeOut(t), run_time=self.T(0.5))
            else:
                shown = t
                self.stage.append(t)
        self.say("with five cities there are only 12 to check", 3)

        rows = VGroup()
        for i, n in enumerate((5, 10, 30)):
            v = math.factorial(n - 1) // 2
            val = f"{v:,}" if v < 10 ** 9 else "4.4 × 10³⁰"
            row = VGroup(txt(f"{n} cities", 22, GREY, bold=False, w=1.5),
                         txt(val, 24, GOLD if i == 2 else WHITE_, w=2.6))
            row.arrange(RIGHT, buff=0.25)
            if row.get_width() > 4.4:
                row.set_width(4.4)
            row.move_to(np.array([0, -0.40 - i * 0.42, 0]))
            self.play(FadeIn(row, shift=0.1 * RIGHT), run_time=self.T(2),
                      rate_func=rush_from)
            rows.add(row)
            if i == 1:
                self.say("ten cities and it is already 181,440", 3)
        self.stage.append(rows)
        self.say("thirty and no computer will ever finish", 3, GOLD)
        self.close("A billion routes every second.",
                   "30 cities still outlasts the universe.")

    # ==================================================================
    def p7(self):
        cap = txt("10,461,394,944,000 states", 24, GREY, bold=False)
        cap.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(cap), run_time=self.T(1))
        self.stage = [cap]
        self.say("slide the tiles into order", 3)
        self.say("searching all of it is hopeless", 3)

        goal = np.array([0, -0.85, 0])
        rng = np.random.default_rng(7)
        blobs = VGroup()
        for side, lab, aimed, note in (
                (-1.15, "blind search", False, "blind, it spreads everywhere"),
                (1.15, "with a hunch", True,
                 "add one guess: how far is the goal still?")):
            o = np.array([side, 0.55, 0])
            t = txt(lab, 20, GOLD if aimed else GREY, bold=False, w=1.9)
            t.move_to(np.array([side, 1.45, 0]))
            self.play(FadeIn(t), run_time=self.T(1))
            self.say(note, 3)
            g = VGroup()
            for _ in range(120 if not aimed else 26):
                if aimed:
                    u = rng.uniform(0, 1)
                    p = o + (goal - o) * u + np.array(
                        [rng.normal(0, 0.11), rng.normal(0, 0.09), 0])
                else:
                    a, r = rng.uniform(0, 2 * np.pi), rng.uniform(0, 0.72)
                    p = o + np.array([r * np.cos(a), r * np.sin(a), 0])
                g.add(Dot(p, radius=0.036, fill_color=GOLD if aimed else COOL))
            self.play(FadeIn(g, lag_ratio=0.02), run_time=self.T(4))
            blobs.add(t, g)
        self.stage.append(blobs)
        self.say("it walks almost straight there", 3)

        star = Dot(goal, radius=0.13, fill_color=WHITE_)
        lab = txt("solved", 20, WHITE_, bold=False)
        lab.move_to(goal + np.array([0, -0.40, 0]))
        self.play(FadeIn(star), FadeIn(lab), run_time=self.T(2))
        self.stage += [star, lab]
        self.close("Both find it. One barely looks.",
                   "A good guess about distance is the whole trick.")
