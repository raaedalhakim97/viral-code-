from manimlib import *
import numpy as np

# "LOST IN THE MIDDLE" - why a million-token context window is a lie (~38s, 9:16)
#
# The claim on the box: every frontier model in 2026 reads 1,000,000 tokens.
# The math: attention compares every token to every other token, so a million
# tokens is a trillion comparisons per layer. Nobody pays that. So they don't -
# they window, they sparsify, they compress. And the damage is not spread evenly.
#
# Every number on screen is sourced:
#   n^2 attention                     definitional
#   effective context 50-65%          RULER benchmark
#   17 of 17 models degraded          RULER
#   30-70% depth -> 5-15 pt drop      Liu et al., "Lost in the Middle", TACL 2024
#
# Cut discipline: no shot holds longer than ~2s without a change. The enemy of
# this format is a still frame with a voice over it.
#
# Render (config comes from custom_config.yml in this dir):
#   xvfb-run -a -s "-screen 0 1600x1200x24" manimgl lost_in_the_middle.py LostInTheMiddle -w
#   manimgl lost_in_the_middle.py LostInTheMiddle -w -r 360x640     # preview
#   manimgl lost_in_the_middle.py LostInTheMiddle -w -r 360x640 --safe   # + safe-zone guides
#
# Then grade it:  python3 cinegrade.py videos/LostInTheMiddle.mp4 out.mp4
#
# manimgl 1.7.2: Circle() needs stroke_color=, Dot() needs fill_color= - passing
# color= to either silently renders the default instead.

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"

# ---------------------------------------------------------------------------
# TikTok safe zone. The UI is not decoration - it covers the frame.
#   bottom ~22%  caption, handle, music ticker
#   top    ~12%  search / following bar
#   right  ~15%  like / comment / share rail
# Anything that must be READ lives inside SAFE_TOP..SAFE_BOT. The promo's
# captions sat at y=-2.9, which is under the caption block AND in the vignette
# falloff - legible in the render, gone on the phone.
# ---------------------------------------------------------------------------
FRAME_H  = 9.0
SAFE_TOP = FRAME_H / 2 - 0.12 * FRAME_H      #  +3.42
SAFE_BOT = -FRAME_H / 2 + 0.22 * FRAME_H     #  -2.52
LINE_Y   = -1.95                             # caption line, comfortably inside


def safe_guides():
    """Magenta guides for previewing. Never rendered in a real pass."""
    g = VGroup()
    for y in (SAFE_TOP, SAFE_BOT):
        ln = VMobject(stroke_color="#FF00AA", stroke_width=2)
        ln.set_points_as_corners([np.array([-3, y, 0]), np.array([3, y, 0])])
        g.add(ln)
    return g


def caption(txt, size=27, color=WHITE_):
    t = Text(txt, color=color, font_size=size, weight=BOLD)
    if t.get_width() > 4.3:
        t.set_width(4.3)
    return t


class LostInTheMiddle(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)

        if "--safe" in sys.argv:
            self.add(safe_guides())

        self.beat_hook()
        self.beat_quadratic()
        self.beat_nobody_pays()
        self.beat_ruler()
        self.beat_middle()
        self.beat_close()

    # ------------------------------------------------------------------
    # 0-3s   HOOK. Motion inside the first 12 frames or the scroll wins.
    # ------------------------------------------------------------------
    def beat_hook(self):
        big = Text("1,000,000", color=WHITE_, font_size=76, weight=BOLD)
        big.move_to(np.array([0, 0.9, 0]))
        sub = caption("words your AI says it can read", size=26, color=GREY)
        sub.next_to(big, DOWN, buff=0.42)

        self.play(FadeIn(big, scale=1.12), run_time=0.45, rate_func=rush_from)
        self.play(FadeIn(sub), run_time=0.3)
        self.wait(0.7)

        strike = VMobject(stroke_color=GOLD, stroke_width=5)
        strike.set_points_as_corners([
            np.array([-big.get_width() / 2 - 0.15, 0.9, 0]),
            np.array([big.get_width() / 2 + 0.15, 0.9, 0]),
        ])
        self.play(ShowCreation(strike), run_time=0.35, rate_func=rush_into)

        lie = caption("It doesn't.", size=34)
        lie.move_to(np.array([0, -0.9, 0]))
        self.play(FadeIn(lie, shift=0.15 * UP), run_time=0.35)
        self.wait(0.65)
        self.play(*[FadeOut(m) for m in (big, sub, strike, lie)], run_time=0.35)

    # ------------------------------------------------------------------
    # 3-13s   THE n^2 WALL. Show it, then let the numbers do the violence.
    # ------------------------------------------------------------------
    def beat_quadratic(self):
        lead = caption("Attention compares every word", size=26)
        lead2 = caption("to every other word.", size=26)
        VGroup(lead, lead2).arrange(DOWN, buff=0.16).move_to(np.array([0, 2.4, 0]))
        self.play(FadeIn(lead), FadeIn(lead2), run_time=0.4)

        # six tokens on a ring, every pair joined - 15 edges, visibly too many
        n = 6
        R = 1.35
        pts = [np.array([R * np.cos(TAU * i / n + PI / 2),
                         R * np.sin(TAU * i / n + PI / 2) + 0.3, 0]) for i in range(n)]
        dots = VGroup(*[Dot(p, radius=0.085, fill_color=WHITE_) for p in pts])
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in dots],
                              lag_ratio=0.06), run_time=0.6)

        edges = VGroup()
        for i in range(n):
            for j in range(i + 1, n):
                e = VMobject(stroke_color=WHITE_, stroke_width=1.6)
                e.set_points_as_corners([pts[i], pts[j]])
                e.set_stroke(opacity=0.45)
                edges.add(e)
        self.play(LaggedStart(*[ShowCreation(e) for e in edges],
                              lag_ratio=0.03), run_time=1.1)
        self.wait(0.3)
        self.play(FadeOut(lead), FadeOut(lead2),
                  FadeOut(dots), FadeOut(edges), run_time=0.35)

        # the escalation - each line lands as a cut, not a crossfade
        rows = [
            ("10 words", "100 comparisons"),
            ("1,000 words", "1,000,000"),
            ("1,000,000 words", "1,000,000,000,000"),
        ]
        prev = None
        for k, (left, right) in enumerate(rows):
            a = Text(left, color=GREY, font_size=30, weight=BOLD)
            b = Text(right, color=WHITE_ if k < 2 else GOLD,
                     font_size=40 if k < 2 else 46, weight=BOLD)
            grp = VGroup(a, b).arrange(DOWN, buff=0.26)
            if grp.get_width() > 4.4:
                grp.set_width(4.4)
            grp.move_to(np.array([0, 0.5, 0]))
            if prev is not None:
                self.play(FadeOut(prev, shift=0.25 * DOWN), run_time=0.22)
            self.play(FadeIn(grp, shift=0.25 * UP), run_time=0.34,
                      rate_func=rush_from)
            self.wait(0.62 if k < 2 else 0.95)
            prev = grp

        tail = caption("Per layer.", size=28, color=GREY)
        tail.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(tail), run_time=0.25)
        self.wait(0.55)
        self.play(FadeOut(prev), FadeOut(tail), run_time=0.3)

    # ------------------------------------------------------------------
    # 13-19s   NOBODY PAYS THAT. The grid goes dark except a sparse few.
    # ------------------------------------------------------------------
    def beat_nobody_pays(self):
        line = caption("Nobody computes a trillion.", size=28)
        line.move_to(np.array([0, 2.5, 0]))
        self.play(FadeIn(line), run_time=0.3)

        cols = rows = 11
        cell = 0.30
        grid = VGroup()
        idx = {}
        for r in range(rows):
            for c in range(cols):
                s = Square(side_length=cell * 0.82, stroke_width=0,
                           fill_color=WHITE_)
                s.set_fill(WHITE_, opacity=0.55)
                s.move_to(np.array([(c - cols / 2 + 0.5) * cell,
                                    (rows / 2 - 0.5 - r) * cell + 0.45, 0]))
                idx[(r, c)] = s
                grid.add(s)
        self.play(FadeIn(grid, lag_ratio=0.004), run_time=0.7)
        self.wait(0.35)

        # sparse attention: keep a diagonal band + the first column (the sink)
        keep = {(r, c) for r in range(rows) for c in range(cols)
                if abs(r - c) <= 1 or c == 0}
        drop = [idx[k] for k in idx if k not in keep]
        self.play(*[m.animate.set_fill(opacity=0.05) for m in drop],
                  run_time=0.65)

        sub = caption("So they skip. Window. Compress.", size=25, color=GREY)
        sub.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(sub), run_time=0.3)
        self.wait(1.0)
        self.play(FadeOut(line), FadeOut(grid), FadeOut(sub), run_time=0.35)

    # ------------------------------------------------------------------
    # 19-26s   RULER. 17 bars, all of them fall.
    # ------------------------------------------------------------------
    def beat_ruler(self):
        head = caption("A benchmark called RULER tested", size=25, color=GREY)
        head2 = caption("17 long-context models.", size=27)
        VGroup(head, head2).arrange(DOWN, buff=0.16).move_to(np.array([0, 2.5, 0]))
        self.play(FadeIn(head), FadeIn(head2), run_time=0.4)

        N = 17
        w = 0.19
        base_y = -0.9
        H = 2.5
        bars = VGroup()
        for i in range(N):
            b = Rectangle(width=w * 0.72, height=H, stroke_width=0)
            b.set_fill(WHITE_, opacity=0.75)
            b.move_to(np.array([(i - N / 2 + 0.5) * w, base_y + H / 2, 0]))
            bars.add(b)
        self.play(LaggedStart(*[FadeIn(b, shift=0.2 * UP) for b in bars],
                              lag_ratio=0.02), run_time=0.7)
        self.wait(0.3)

        # Ghosts hold the advertised height. Without them the bars shrink
        # against nothing and the drop is invisible - the gap IS the point.
        ghosts = VGroup()
        for b in bars:
            g = Rectangle(width=w * 0.72, height=H, stroke_width=1.4)
            g.set_stroke(FAINT, opacity=0.9)
            g.move_to(b.get_center())
            ghosts.add(g)
        self.add(ghosts)
        bars.set_z_index(1)

        # every one of them shrinks - the point is that there is no exception
        rng = np.random.default_rng(7)
        anims = []
        for b in bars:
            f = rng.uniform(0.50, 0.65)          # effective context 50-65%
            anims.append(b.animate.stretch_to_fit_height(H * f)
                          .move_to(np.array([b.get_x(), base_y + H * f / 2, 0]))
                          .set_fill(GREY, opacity=0.6))
        self.play(*anims, run_time=1.0, rate_func=rush_into)

        out = caption("All 17 degraded.", size=30)
        out.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(out, shift=0.12 * UP), run_time=0.3)
        self.wait(0.75)

        out2 = caption("Real usable context: 50-65%", size=25, color=GOLD)
        out2.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeOut(out), run_time=0.2)
        self.play(FadeIn(out2), run_time=0.28)
        self.wait(0.9)
        self.play(FadeOut(head), FadeOut(head2), FadeOut(bars),
                  FadeOut(ghosts), FadeOut(out2), run_time=0.35)

    # ------------------------------------------------------------------
    # 26-34s   THE MIDDLE. The U-curve is the whole video in one shape.
    # ------------------------------------------------------------------
    def beat_middle(self):
        head = caption("And the damage isn't even.", size=27)
        head.move_to(np.array([0, 2.5, 0]))
        self.play(FadeIn(head), run_time=0.3)

        L, RGT = -2.0, 2.0
        base = 0.15

        axis = VMobject(stroke_color=FAINT, stroke_width=2)
        axis.set_points_as_corners([np.array([L, base, 0]), np.array([RGT, base, 0])])
        self.play(ShowCreation(axis), run_time=0.3)

        # recall as a function of depth: strong at both ends, sagging in the middle
        def recall(u):
            return 1.0 - 0.62 * np.sin(np.pi * u) ** 1.6

        pts = []
        M = 90
        for i in range(M + 1):
            u = i / M
            x = L + (RGT - L) * u
            pts.append(np.array([x, base + 1.55 * recall(u), 0]))
        curve = VMobject(stroke_color=WHITE_, stroke_width=4)
        curve.set_points_as_corners(pts)
        self.play(ShowCreation(curve), run_time=1.15, rate_func=smooth)

        s = caption("start", size=21, color=GREY)
        e = caption("end", size=21, color=GREY)
        s.move_to(np.array([L, base - 0.34, 0]))
        e.move_to(np.array([RGT, base - 0.34, 0]))
        self.play(FadeIn(s), FadeIn(e), run_time=0.28)
        self.wait(0.4)

        # the 30-70% band, the actual finding
        band = Rectangle(width=(RGT - L) * 0.4, height=1.95, stroke_width=0)
        band.set_fill(GOLD, opacity=0.14)
        band.move_to(np.array([(L + RGT) / 2, base + 1.95 / 2 - 0.02, 0]))
        self.play(FadeOut(head), FadeIn(band), run_time=0.35)

        lab = caption("30-70% depth", size=22, color=GOLD)
        lab.move_to(np.array([0, base + 1.95 + 0.34, 0]))
        self.play(FadeIn(lab), run_time=0.28)

        hit = caption("5-15 points worse", size=29, color=WHITE_)
        hit.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(hit, shift=0.12 * UP), run_time=0.32)
        self.wait(1.15)

        self.play(FadeOut(axis), FadeOut(curve), FadeOut(s),
                  FadeOut(e), FadeOut(band), FadeOut(lab), FadeOut(hit),
                  run_time=0.4)

    # ------------------------------------------------------------------
    # 34-38s   PAYOFF + CTA. Give them something to DO, then ask.
    # ------------------------------------------------------------------
    def beat_close(self):
        p1 = caption("Put what matters", size=30)
        p2 = caption("at the start or the end.", size=30)
        p3 = caption("Never the middle.", size=30, color=GOLD)
        grp = VGroup(p1, p2, p3).arrange(DOWN, buff=0.2)
        grp.move_to(np.array([0, 0.9, 0]))
        for m in grp:
            self.play(FadeIn(m, shift=0.1 * UP), run_time=0.3)
        self.wait(1.1)
        self.play(FadeOut(grp), run_time=0.4)

        eye = observer_eye(WHITE_)
        eye.move_to(np.array([0, 1.35, 0])).scale(0.8)
        self.play(ShowCreation(eye), run_time=1.2)

        words = VGroup(
            Text("PAUSE", color=WHITE_, font_size=21, weight=BOLD),
            Text("OBSERVE", color=WHITE_, font_size=21, weight=BOLD),
            Text("LEARN", color=WHITE_, font_size=21, weight=BOLD),
        ).arrange(RIGHT, buff=0.45).move_to(np.array([0, -0.55, 0]))
        for w in words:
            self.play(FadeIn(w, shift=0.08 * UP), run_time=0.32)

        cta = Text("Follow for the math behind AI",
                   color=WHITE_, font_size=28, weight=BOLD)
        handle = Text("@observer.collapse", color=GREY, font_size=22)
        cg = VGroup(cta, handle).arrange(DOWN, buff=0.2)
        if cg.get_width() > 4.3:
            cg.set_width(4.3)
        cg.move_to(np.array([0, LINE_Y, 0]))
        self.play(FadeIn(cg, shift=0.1 * UP), run_time=0.45)
        self.wait(1.5)
        self.play(FadeOut(eye), FadeOut(words), FadeOut(cg), run_time=0.7)


# ===========================================================================
# Shared ending signature - byte-identical to share_promo.py
# ===========================================================================
def observer_eye(color):
    grp = VGroup()
    up = VMobject(color=color, stroke_width=2.2)
    up.set_points_smoothly([np.array([x, 0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
                            for x in np.linspace(-1.6, 1.6, 20)])
    dn = VMobject(color=color, stroke_width=2.2)
    dn.set_points_smoothly([np.array([x, -0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
                            for x in np.linspace(-1.6, 1.6, 20)])
    grp.add(up, dn)
    pupil = Circle(radius=0.42, stroke_color=color, stroke_width=2.2).move_to(ORIGIN)
    pupil_fill = Dot(ORIGIN, radius=0.12, fill_color=color)
    grp.add(pupil, pupil_fill)
    rng = np.random.default_rng(2)
    for _ in range(5):
        s = rng.uniform(0.05, 0.12)
        sq = Square(side_length=s, color=color, stroke_width=1.5)
        sq.move_to([rng.uniform(1.7, 2.4), rng.uniform(-0.6, 0.6), 0])
        sq.set_fill(color, opacity=0.5)
        grp.add(sq)
    return grp
