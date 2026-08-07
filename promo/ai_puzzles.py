"""
ai_puzzles — 7 shorts: a puzzle, and the algorithm an AI actually uses on it.

    PART=1 BPM=150 manimgl ai_puzzles.py AIPuzzles -w -r 1080x1920

32 beats = 8 bars = 12.800s at 150 BPM. About a quarter the length of the
earlier videos: the 100-200 view band and the unknown watch time both argue for
short, and the opening frame is now the loudest frame instead of a chapter HUD.

The close starts the moment a part's animation ends rather than padding to a
fixed bar, so the only long hold in the video is on the takeaway card.

    1  maze          breadth-first search
    2  river crossing state-space search
    3  tic-tac-toe   minimax
    4  n-queens      backtracking
    5  sudoku        constraint propagation
    6  salesman      combinatorial explosion / heuristics
    7  sliding tile  A* — a heuristic beats raw search

EVERY NUMBER ON SCREEN WAS COMPUTED, NOT QUOTED.
    255,168             complete legal tic-tac-toe games
    7                   minimum river crossings (BFS over legal states)
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
import os
from collections import deque

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
PART = int(os.environ.get("PART", 1))
FPS = 60
TOTAL = 32

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
LINE_Y  = -2.05
TOP_Y   = 3.30
# The shrunk title sits at 2.62 and the subtitle at 2.18, so a scene's own
# caption has to clear 2.05. Everything below the header uses this line.
CAP_Y   = 1.78

TITLES = {
    1: ("THE MAZE",        "breadth-first search"),
    2: ("THE RIVER",       "state-space search"),
    3: ("TIC-TAC-TOE",     "minimax"),
    4: ("SIX QUEENS",      "backtracking"),
    5: ("SUDOKU",          "constraint propagation"),
    6: ("THE SALESMAN",    "why brute force dies"),
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
    """A crown, not a chess glyph — reads at thumbnail size."""
    w = s * 0.30
    pts = [(-w, -w * 0.55), (w, -w * 0.55), (w * 0.92, w * 0.55),
           (w * 0.45, w * 0.05), (0, w * 0.75), (-w * 0.45, w * 0.05),
           (-w * 0.92, w * 0.55)]
    m = VMobject(stroke_color=color, stroke_width=2.4)
    m.set_points_as_corners([o + np.array([a, b, 0]) for a, b in pts] +
                            [o + np.array([pts[0][0], pts[0][1], 0])])
    m.set_fill(color, opacity=0.30)
    return m


# --------------------------------------------------------------------------
MAZE = [
    "#######",
    "#S....#",
    "#.###.#",
    "#...#.#",
    "###.#.#",
    "#...#.#",
    "#.#...#",
    "#...#E#",
    "#######",
]


def maze_bfs(grid):
    """Real BFS. Returns rings (cells by distance) and the shortest path."""
    h, w = len(grid), len(grid[0])
    start = end = None
    for r in range(h):
        for c in range(w):
            if grid[r][c] == "S":
                start = (r, c)
            elif grid[r][c] == "E":
                end = (r, c)
    dist = {start: 0}
    prev = {}
    q = deque([start])
    while q:
        r, c = q.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < h and 0 <= nc < w and grid[nr][nc] != "#" \
                    and (nr, nc) not in dist:
                dist[(nr, nc)] = dist[(r, c)] + 1
                prev[(nr, nc)] = (r, c)
                q.append((nr, nc))
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
    """Real backtracking. Returns ('put'|'undo', row, col) in the order run."""
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
                      self.title.get_height() * 0.52).move_to(
                      np.array([0, 2.62, 0])),
                  self.sub.animate.set_height(
                      self.sub.get_height() * 0.86).move_to(
                      np.array([0, 2.18, 0])),
                  run_time=self.T(1))

    def close(self, a, b):
        """Starts as soon as the method ends. The slack lands here."""
        for m in self.stage:
            m.clear_updaters()
        self.play(*[FadeOut(m) for m in self.stage], run_time=self.T(1))

        l1 = txt(a, 30, WHITE_, w=4.4)
        l1.move_to(np.array([0, 0.75, 0]))
        self.play(FadeIn(l1, shift=0.12 * UP), run_time=self.T(2),
                  rate_func=rush_from)
        l2 = self.dance(txt(b, 26, GOLD, w=4.4)
                        .move_to(np.array([0, -0.10, 0])), 0.05)
        self.play(FadeIn(l2), run_time=self.T(1))
        self.wait(self.T(1))

        h = txt("@observer.collapse", 22, GREY, bold=False)
        h.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(h), run_time=self.T(1))
        self.pad_to(TOTAL - 2)
        self.clock.clear_updaters()
        self.play(FadeOut(l1), FadeOut(l2), FadeOut(h),
                  FadeOut(self.title), FadeOut(self.sub), FadeOut(self.mark),
                  run_time=self.T(2))

    # ==================================================================
    def p1(self):
        """Maze — the real BFS frontier, ring by ring."""
        rings, path, start, end = maze_bfs(MAZE)
        h, w = len(MAZE), len(MAZE[0])
        # 9 rows at 0.52 is 4.68 tall and does not fit between the header and
        # the safe zone. 0.46 does, centred on -0.25.
        s = 0.46
        ox, oy = -(w - 1) * s / 2, -0.25 + (h - 1) * s / 2

        cells, walls = {}, VGroup()
        for r in range(h):
            for c in range(w):
                x, y = ox + c * s, oy - r * s
                if MAZE[r][c] == "#":
                    walls.add(cell(x, y, s, FAINT, 1.0))
                else:
                    cells[(r, c)] = cell(x, y, s, COOL, 0.0, stroke=1.0)
        board = VGroup(walls, *cells.values())
        self.play(FadeIn(board), run_time=self.T(1))

        for tag, pos, col in (("start", start, WHITE_), ("exit", end, GOLD)):
            t = txt(tag, 17, col, bold=False, w=0.9)
            t.move_to(np.array([ox + pos[1] * s, oy - pos[0] * s, 0]))
            board.add(t)
        self.play(FadeIn(board[-2]), FadeIn(board[-1]), run_time=self.T(1))
        self.stage = [board]
        self.wait(self.T(1))

        # every ring is one half-beat: the frontier expanding at tempo
        for ring in rings:
            grp = [cells[p] for p in ring if p in cells]
            if not grp:
                continue
            self.play(*[c.animate.set_fill(COOL, 0.55) for c in grp],
                      run_time=self.T(0.75), rate_func=linear)

        self.play(*[cells[p].animate.set_fill(GOLD, 0.85)
                    for p in path if p in cells],
                  run_time=self.T(2))
        self.close("It never guessed a direction.",
                   f"It flooded every one. {len(path) - 1} steps.")

    # ==================================================================
    def p2(self):
        """River crossing. The bank the item is standing on is the whole state,
        so the items have to be visible objects that move — a changing cargo
        label never showed the viewer what the puzzle was."""
        NEAR_Y, FAR_Y = 1.28, -1.62
        COLS = {"wolf": -1.35, "goat": 0.0, "cabbage": 1.35}
        # +1 = crossing to the far bank. Verified by BFS: 7 is the minimum.
        moves = [("goat", 1), (None, -1), ("wolf", 1), ("goat", -1),
                 ("cabbage", 1), (None, -1), ("goat", 1)]

        river = VGroup(seg(np.array([-2.3, 0.62, 0]), np.array([2.3, 0.62, 0]), FAINT, 3),
                       seg(np.array([-2.3, -0.98, 0]), np.array([2.3, -0.98, 0]), FAINT, 3))
        cap = txt("the boat holds one", 22, GREY, bold=False)
        cap.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(river), FadeIn(cap), run_time=self.T(1))

        items = {}
        for name, x in COLS.items():
            box = Rectangle(width=1.15, height=0.42, stroke_width=2.0)
            box.set_stroke(GOLD if name == "goat" else GREY, opacity=0.9)
            lab = txt(name, 19, GOLD if name == "goat" else WHITE_,
                      bold=False, w=1.0)
            g = VGroup(box, lab).move_to(np.array([x, NEAR_Y, 0]))
            items[name] = g
        self.play(*[FadeIn(g, shift=0.08 * DOWN) for g in items.values()],
                  run_time=self.T(1))

        boat = Rectangle(width=0.62, height=0.26, stroke_width=2.2)
        boat.set_stroke(WHITE_, opacity=0.9).move_to(np.array([0, 0.42, 0]))
        self.play(FadeIn(boat), run_time=self.T(1))
        self.stage = [river, cap, boat] + list(items.values())
        self.wait(self.T(1))

        for what, direction in moves:
            by = -0.78 if direction > 0 else 0.42
            anims = [boat.animate.move_to(np.array([0, by, 0]))]
            if what:
                anims.append(items[what].animate.move_to(
                    np.array([COLS[what], FAR_Y if direction > 0 else NEAR_Y, 0])))
            self.play(*anims, run_time=self.T(2), rate_func=smooth)

        self.close("The goat crosses three times.",
                   "AI turns a story into a map of states.")

    # ==================================================================
    def p3(self):
        """Minimax — scores climbing back up the tree."""
        root = np.array([0, 1.16, 0])
        kids = [np.array([x, 0.06, 0]) for x in (-1.5, 0, 1.5)]
        gk = [np.array([x, -1.14, 0]) for x in (-1.95, -1.05, -0.45,
                                                0.45, 1.05, 1.95)]
        edges = VGroup(*[seg(root, k, FAINT, 2.0) for k in kids],
                       *[seg(kids[i // 2], g, FAINT, 2.0)
                         for i, g in enumerate(gk)])
        dots = VGroup(*[Dot(p, radius=0.10, fill_color=WHITE_)
                        for p in [root] + kids + gk])
        self.play(ShowCreation(edges), FadeIn(dots), run_time=self.T(2))
        self.stage = [edges, dots]

        n = txt("255,168 possible games", 24, GREY, bold=False)
        n.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(n), run_time=self.T(1))
        self.stage.append(n)
        self.wait(self.T(1))

        vals = [-1, 0, 1, 0, 1, -1]
        leaves = VGroup()
        for p, v in zip(gk, vals):
            t = txt(f"{v:+d}", 20, GOLD if v > 0 else GREY, bold=False, w=0.5)
            t.move_to(p + np.array([0, -0.42, 0]))
            leaves.add(t)
        self.play(FadeIn(leaves, shift=0.08 * UP), run_time=self.T(2))
        self.stage.append(leaves)
        self.wait(self.T(1))

        mins = [min(vals[0:2]), min(vals[2:4]), min(vals[4:6])]
        mid = VGroup()
        for p, v in zip(kids, mins):
            t = txt(f"{v:+d}", 22, GOLD if v > 0 else GREY, w=0.5)
            t.move_to(p + np.array([0.34, 0.10, 0]))
            mid.add(t)
        self.play(FadeIn(mid), run_time=self.T(2))
        top = txt(f"{max(mins):+d}", 26, GOLD, w=0.6)
        top.move_to(root + np.array([0.40, 0.14, 0]))
        self.play(FadeIn(top, scale=1.2), run_time=self.T(2))
        self.stage += [mid, top]

        self.close("It plays every game to the end.",
                   "Then picks the branch you can't win.")

    # ==================================================================
    def p4(self):
        """Six queens — the real backtracking trace, every undo included."""
        n, s = 6, 0.60
        ox, oy = -(n - 1) * s / 2, (n - 1) * s / 2 - 0.35
        squares = VGroup()
        for r in range(n):
            for c in range(n):
                squares.add(cell(ox + c * s, oy - r * s, s,
                                 GREY if (r + c) % 2 else FAINT,
                                 0.22 if (r + c) % 2 else 0.65))
        self.play(FadeIn(squares), run_time=self.T(1))
        rule = txt("no two on a line", 22, GREY, bold=False)
        rule.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(rule), run_time=self.T(1))
        self.stage = [squares, rule]
        self.wait(self.T(1))

        live, undos = {}, 0
        ev = queens_trace(n)
        for kind, r, c in ev:
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

        for q in live.values():
            self.stage.append(q)
        self.close(f"It was wrong {undos} times.",
                   "Backtracking: be wrong, cheaply.")

    # ==================================================================
    def p5(self):
        """Constraint propagation — candidates removed, not guessed."""
        s = 0.62
        grid = VGroup()
        marks = {}
        for r in range(3):
            for c in range(3):
                o = np.array([(c - 1) * s, 1.15 - r * s, 0])
                grid.add(cell(o[0], o[1], s, FAINT, 0.55, stroke=1.0))
                d = txt(str(r * 3 + c + 1), 24, GREY, bold=False, w=0.4)
                d.move_to(o)
                marks[r * 3 + c + 1] = d
                grid.add(d)
        self.play(FadeIn(grid), run_time=self.T(2))
        cap = txt("one empty square, nine options", 22, GREY, bold=False)
        cap.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(cap), run_time=self.T(1))
        self.stage = [grid, cap]
        self.wait(self.T(1))

        for reason, gone in (("its row already has these", [2, 4, 9]),
                             ("its column has these", [1, 6, 8]),
                             ("its box has these", [3, 5])):
            t = txt(reason, 22, WHITE_, bold=False, w=4.3)
            t.move_to(np.array([0, -0.95, 0]))
            self.play(FadeIn(t), run_time=self.T(1))
            self.play(*[marks[g].animate.set_opacity(0.10) for g in gone],
                      run_time=self.T(1))
            self.play(FadeOut(t), run_time=self.T(0.5))
            self.wait(self.T(0.5))

        left = self.dance(txt("7", 46, GOLD).move_to(np.array([0, -1.20, 0])), 0.06)
        self.play(FadeIn(left, scale=1.3), run_time=self.T(2))
        self.stage.append(left)
        self.close("It never tried a number.",
                   "It removed the eight that couldn't fit.")

    # ==================================================================
    def p6(self):
        """Why brute force dies: (n-1)!/2, computed."""
        import math
        pts = [np.array([1.05 * np.cos(a), 1.05 * np.sin(a) + 0.30, 0])
               for a in np.linspace(0, 2 * np.pi, 6)[:5]]
        dots = VGroup(*[Dot(p, radius=0.10, fill_color=WHITE_) for p in pts])
        self.play(FadeIn(dots), run_time=self.T(1))
        cap = txt("visit every city once", 22, GREY, bold=False)
        cap.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(cap), run_time=self.T(1))
        self.stage = [dots, cap]

        tours = VGroup()
        for k in range(3):
            order = [0] + list(np.roll([1, 2, 3, 4], k)) + [0]
            t = VGroup(*[seg(pts[order[i]], pts[order[i + 1]], GOLD, 2.0, 0.75)
                         for i in range(5)])
            self.play(ShowCreation(t), run_time=self.T(1))
            if k < 2:
                self.play(FadeOut(t), run_time=self.T(0.5))
            else:
                tours.add(t)
                self.stage.append(t)
        self.wait(self.T(0.5))

        rows = VGroup()
        for i, n in enumerate((5, 10, 30)):
            v = math.factorial(n - 1) // 2
            txt_v = f"{v:,}" if v < 10 ** 9 else "4.4 × 10³⁰"
            row = VGroup(txt(f"{n} cities", 22, GREY, bold=False, w=1.5),
                         txt(txt_v, 24, GOLD if i == 2 else WHITE_, w=2.6))
            row.arrange(RIGHT, buff=0.25)
            if row.get_width() > 4.4:
                row.set_width(4.4)
            row.move_to(np.array([0, -1.05 - i * 0.52, 0]))
            self.play(FadeIn(row, shift=0.1 * RIGHT), run_time=self.T(2),
                      rate_func=rush_from)
            rows.add(row)
        self.stage.append(rows)
        self.close("A billion routes every second.",
                   "30 cities still outlasts the universe.")

    # ==================================================================
    def p7(self):
        """A* — the same target, a fraction of the search."""
        cap = txt("10,461,394,944,000 states", 24, GREY, bold=False)
        cap.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(cap), run_time=self.T(1))
        self.stage = [cap]

        goal = np.array([0, -1.55, 0])
        blobs = VGroup()
        rng = np.random.default_rng(7)
        for side, lab, aimed in ((-1.15, "blind search", False),
                                 (1.15, "with a hunch", True)):
            o = np.array([side, 0.10, 0])
            t = txt(lab, 20, GOLD if aimed else GREY, bold=False, w=1.9)
            t.move_to(np.array([side, 1.25, 0]))
            self.play(FadeIn(t), run_time=self.T(1))
            g = VGroup()
            for _ in range(120 if not aimed else 26):
                if aimed:
                    # a narrow corridor straight at the goal — that is the
                    # whole visual claim, so it has to actually point there
                    u = rng.uniform(0, 1)
                    p = o + (goal - o) * u + np.array(
                        [rng.normal(0, 0.11), rng.normal(0, 0.09), 0])
                else:
                    a, r = rng.uniform(0, 2 * np.pi), rng.uniform(0, 0.85)
                    p = o + np.array([r * np.cos(a), r * np.sin(a), 0])
                g.add(Dot(p, radius=0.036,
                          fill_color=GOLD if aimed else COOL))
            self.play(FadeIn(g, lag_ratio=0.02), run_time=self.T(3))
            blobs.add(t, g)
        self.stage.append(blobs)

        star = Dot(goal, radius=0.13, fill_color=WHITE_)
        lab = txt("solved", 20, WHITE_, bold=False)
        lab.move_to(goal + np.array([0, -0.40, 0]))
        self.play(FadeIn(star), FadeIn(lab), run_time=self.T(2))
        self.stage += [star, lab]
        self.close("Both find it. One barely looks.",
                   "A good guess about distance is the whole trick.")
