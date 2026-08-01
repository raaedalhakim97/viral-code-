from manimlib import *
import numpy as np

# "SHARE THE KNOWLEDGE" promo v2 - realistic overflowing glass (~15s, 9:16)
# Rebuilt from a canvas study: water reads as water because of a MOVING
# sine-wave surface (two summed sines), a depth gradient, and an overflow
# SHEET (layered strands) - not trickling dots.
#
# Two asks, in order:
#   SHARE   "You understood this. Someone you know should too."  (over the glass)
#   FOLLOW  "Follow for more AI math" + @observercollaps       (last ~2s)
# The follow ask is the one that matters right now - the page converts views
# into likes far better than it converts them into followers, so the ending
# has to ask for the follow, not just sign off on the brand mark.
#
# On-brand: black bg, white glow water, ONE gold accent (first crest drop).
# Empty space. Ends on eye + PAUSE OBSERVE LEARN + the follow CTA.
#
# Machine rules: np.array everywhere, no \text{}, no TexText, no
# ArcBetweenPoints (bezier strands built with set_points_as_corners on a
# dense sampling instead), no TracedPath. Parametric-free. ALL updaters
# cleared before the ending fade.
#
# Render (resolution, fps and codec come from custom_config.yml in this dir):
#   manimgl share_promo.py SharePromo -w
# Headless box with no display:
#   xvfb-run -a -s "-screen 0 1600x1200x24" manimgl share_promo.py SharePromo -w
# Quick preview pass:
#   manimgl share_promo.py SharePromo -w -r 360x640
#
# Output: videos/SharePromo.mp4  (1440x2560, 60fps, ~18.9s)
#
# manimgl 1.7.2 notes - the API differs from the version this was drafted
# against, so three things are deliberate here:
#   - background is set via camera.background_rgba; Scene.set_background_color
#     does not exist
#   - Circle() hardcodes stroke_color=RED, so it needs stroke_color=, not color=
#   - Dot() hardcodes fill_color=WHITE, so it needs fill_color=, not color=
# Passing color= to either silently renders the default instead.

# ---------------------------------------------------------------------------
# TikTok safe zone. The UI is not decoration - it covers the frame:
# bottom ~22% is caption/handle/music ticker, top ~12% is the search bar.
# This scene originally put its captions at y=-3.0 and the CTA at y=-2.9, both
# UNDER the caption block - legible in the render, invisible on the phone. The
# same band is also where the grade's vignette falls off hardest, so the text
# was being dimmed as well as covered.
# ---------------------------------------------------------------------------
FRAME_H  = 9.0
SAFE_TOP = FRAME_H / 2 - 0.12 * FRAME_H      #  +3.42
SAFE_BOT = -FRAME_H / 2 + 0.22 * FRAME_H     #  -2.52
LINE_Y   = -1.95                             # caption line, comfortably inside

# glass geometry (world units)
TOP_HW = 1.15
BOT_HW = 0.88
CUP_CY = 0.5
CUP_H  = 2.6
BRIM_Y = CUP_CY + CUP_H / 2
BASE_Y = CUP_CY - CUP_H / 2


def hw_at(y):
    t = (y - BASE_Y) / CUP_H
    return BOT_HW + (TOP_HW - BOT_HW) * t


class SharePromo(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        frame = self.camera.frame
        frame.set_height(9)

        white = "#F7FAFC"
        grey  = "#8A94A6"
        faint = "#2A2F3A"
        gold  = "#EBCB8B"

        # a shared clock so every updater shares the same time base
        clock = ValueTracker(0.0)
        level = ValueTracker(BASE_Y + 0.12)

        def surface_y(x, lv, t):
            # two summed sines = organic water surface
            return lv + 0.09 * np.sin(x * 3.0 + t * 2.2) + 0.05 * np.sin(x * 6.5 - t * 3.1)

        # ============================================================
        # THE WATER BODY (wavy top, redrawn live)
        # ============================================================
        def make_water():
            t = clock.get_value()
            lv = min(level.get_value(), BRIM_Y)
            hw = hw_at(lv)
            pts = [np.array([-BOT_HW, BASE_Y, 0])]
            N = 40
            for i in range(N + 1):
                x = -hw + 2 * hw * (i / N)
                pts.append(np.array([x, surface_y(x, lv, t), 0]))
            pts.append(np.array([BOT_HW, BASE_Y, 0]))
            body = VMobject(stroke_width=0)
            body.set_points_as_corners(pts + [pts[0]])
            body.set_fill(white, opacity=0.20)
            return body

        def make_surface_line():
            t = clock.get_value()
            lv = min(level.get_value(), BRIM_Y)
            hw = hw_at(lv)
            pts = []
            N = 40
            for i in range(N + 1):
                x = -hw + 2 * hw * (i / N)
                pts.append(np.array([x, surface_y(x, lv, t), 0]))
            ln = VMobject(color=white, stroke_width=2.4)
            ln.set_points_as_corners(pts)
            ln.set_stroke(opacity=0.9)
            return ln

        water = always_redraw(make_water)
        surface = always_redraw(make_surface_line)

        # ============================================================
        # THE GLASS (outline, drawn on top)
        # ============================================================
        glass = VMobject(color=white, stroke_width=2.6)
        glass.set_points_as_corners([
            np.array([-TOP_HW, BRIM_Y, 0]),
            np.array([-BOT_HW, BASE_Y, 0]),
            np.array([BOT_HW, BASE_Y, 0]),
            np.array([TOP_HW, BRIM_Y, 0]),
        ])
        brim = Circle(radius=TOP_HW, stroke_color=white, stroke_width=2.2)
        brim.stretch_to_fit_height(0.30).move_to(np.array([0, BRIM_Y, 0]))

        # caption
        cap = Text("You understood this.", color=white, font_size=25, weight=BOLD)
        cap2 = Text("Someone you know should too.", color=white, font_size=25, weight=BOLD)
        cap_g = VGroup(cap, cap2).arrange(DOWN, buff=0.14)
        if cap_g.get_width() > 4.4:
            cap_g.set_width(4.4)
        cap_g.move_to(np.array([0, LINE_Y, 0])).fix_in_frame()

        # ============================================================
        # BUILD: glass draws, water added, caption in
        # ============================================================
        self.play(ShowCreation(glass), ShowCreation(brim), run_time=1.2)
        self.add(water, surface)
        self.add(glass, brim)   # keep outline above water
        self.play(FadeIn(cap_g), run_time=0.5)

        # run the clock continuously in the background of every play
        clock.add_updater(lambda m, dt: m.increment_value(dt))

        # ============================================================
        # FILL to the brim   (~0 - 5s)
        # ============================================================
        self.play(level.animate.set_value(BRIM_Y), run_time=3.6, rate_func=smooth)

        # ============================================================
        # GOLD FIRST CREST over the brim (the one accent)
        # ============================================================
        crest = Dot(np.array([TOP_HW, BRIM_Y, 0]), radius=0.07, fill_color=gold)
        ring = Circle(radius=0.08, stroke_color=gold, stroke_width=2.5)
        ring.move_to(np.array([TOP_HW, BRIM_Y, 0]))
        self.add(ring)
        self.play(
            FadeIn(crest, scale=0.5),
            ring.animate.scale(14).set_stroke(width=0, opacity=0),
            run_time=0.9, rate_func=rush_from,
        )
        self.play(crest.animate.move_to(np.array([TOP_HW + 0.4, -4.8, 0]))
                              .set_opacity(0.15),
                  run_time=1.1, rate_func=rush_into)
        self.remove(crest)

        # ============================================================
        # OVERFLOW SHEET - layered strands down both sides, updater-driven
        # ============================================================
        def make_sheet():
            t = clock.get_value()
            grp = VGroup()
            for side in (-1, 1):
                ex = side * TOP_HW
                for k in range(6):
                    wob = 0.10 * np.sin(t * 4 + k * 1.3 + side)
                    x0 = ex + side * (0.04 + k * 0.05)
                    pts = []
                    M = 28
                    for i in range(M + 1):
                        u = i / M
                        # curve outward near the brim, then straight down off frame
                        x = x0 + side * (0.35 * np.sin(u * 1.2) + wob * u)
                        y = BRIM_Y - u * (BRIM_Y + 5.0)
                        pts.append(np.array([x, y, 0]))
                    strand = VMobject(color=white,
                                      stroke_width=max(2.2 - k * 0.25, 0.6))
                    strand.set_points_as_corners(pts)
                    strand.set_stroke(opacity=max(0.5 - k * 0.06, 0.1))
                    grp.add(strand)
            return grp

        def make_drops():
            t = clock.get_value()
            grp = VGroup()
            for side in (-1, 1):
                ex = side * TOP_HW
                for d in range(4):
                    u = (t * 0.6 + d * 0.25 + (0.12 if side > 0 else 0)) % 1.0
                    x = ex + side * (0.28 + 0.10 * np.sin(u * 6))
                    y = BRIM_Y - u * (BRIM_Y + 5.0)
                    op = 0.7 * np.sin(np.pi * min(u / 0.95, 1.0))
                    dot = Dot(np.array([x, y, 0]), radius=0.045, fill_color=white)
                    dot.set_opacity(max(op, 0))
                    grp.add(dot)
            return grp

        sheet = always_redraw(make_sheet)
        drops = always_redraw(make_drops)
        # insert BELOW the glass outline so strands read as coming over the rim
        self.add(sheet, drops)
        self.add(glass, brim)

        # hold the continuous overflow (the loop body)
        self.play(clock.animate.increment_value(0.0), run_time=0.1)  # sync tick
        self.wait(4.2)

        # ============================================================
        # ENDING
        # ============================================================
        # clear ALL updaters before any fade (inviolable rule)
        clock.clear_updaters()
        water.clear_updaters()
        surface.clear_updaters()
        sheet.clear_updaters()
        drops.clear_updaters()

        self.play(
            FadeOut(sheet), FadeOut(drops), FadeOut(water), FadeOut(surface),
            FadeOut(glass), FadeOut(brim), FadeOut(cap_g),
            run_time=1.0,
        )

        eye = observer_eye(white)
        eye.move_to(np.array([0, 1.3, 0])).scale(0.8)
        self.play(ShowCreation(eye), run_time=1.8)
        words_end = VGroup(
            Text("PAUSE", color=white, font_size=22, weight=BOLD),
            Text("OBSERVE", color=white, font_size=22, weight=BOLD),
            Text("LEARN", color=white, font_size=22, weight=BOLD),
        ).arrange(RIGHT, buff=0.45).move_to(np.array([0, -0.6, 0]))
        for w in words_end:
            self.play(FadeIn(w, shift=0.1 * UP), run_time=0.55)
        self.wait(0.5)

        # ------------------------------------------------------------
        # FOLLOW CTA - the last thing on screen, held ~2s.
        # The glass sequence asks for a SHARE; this asks for the FOLLOW.
        # Kept white, not gold: the first crest drop is the only gold in
        # the piece and that rule is what makes the accent land.
        # ------------------------------------------------------------
        cta = Text("Follow for more AI math",
                   color=white, font_size=30, weight=BOLD)
        handle = Text("@observercollaps", color=grey, font_size=24)
        cta_g = VGroup(cta, handle).arrange(DOWN, buff=0.22)
        if cta_g.get_width() > 4.4:
            cta_g.set_width(4.4)
        cta_g.move_to(np.array([0, LINE_Y, 0]))

        self.play(FadeIn(cta_g, shift=0.12 * UP), run_time=0.6)
        self.wait(1.4)
        self.play(FadeOut(eye), FadeOut(words_end), FadeOut(cta_g), run_time=0.8)
        # ~19.5s


# ===========================================================================
# Shared ending signature (byte-identical to transformer_block.py / rlhf.py)
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
