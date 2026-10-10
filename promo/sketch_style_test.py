"""
sketch_style_test — a drawing-quality probe, not an episode. Still frame.

    xvfb-run -a -s "-screen 0 1600x1200x24" \
        manimgl sketch_style_test.py SketchStyleTest -s -w -r 1080x1920

Answering "can you draw better than this?" with a frame rather than a
claim. Same beat as the reference clip — a dragon over a snowbound
village, two villagers reacting, dialogue box — rebuilt in vector.

WHAT IS ACTUALLY DIFFERENT FROM THE REFERENCE
    atmospheric perspective: three mountain ranks, each paler and bluer
        than the one in front, so distance reads without outlines
    a dragon with anatomy: tapered neck, horned skull, membrane wings on
        visible struts, a tail that thins to a point
    figures on human proportions, with a gesture (one points, one recoils)
        and soft contact shadows so they stand ON the snow
    warm window light against cold snow — the only warm hue in the frame,
        which is what gives it depth
    foreground trees large and near-black, background trees small and
        washed toward the sky colour
    snowfall in three depths, the near flakes larger and softer

WHAT THIS STILL DOES NOT PROVE
    motion. Every frame here is geometry in code, so fluid character
    animation — squash, overlap, follow-through — is expensive to author
    even though the drawing is cheap. Treat this as the art ceiling, not
    the animation ceiling.

Portrait 1080x1920, because that is where the channel posts; the
reference was 960x540 landscape.
"""
from manimlib import *
import numpy as np

FRAME_H = 9.0
SAFE_X = 1.68

SKY_HI,  SKY_LO  = "#8FB8D0", "#DCEAF2"
MTN_FAR, MTN_MID, MTN_NEAR = "#A9C0CE", "#7D9AAE", "#5A7789"
CAP_FAR, CAP_MID, CAP_NEAR = "#E6F0F6", "#EDF4F9", "#F4F9FC"
SNOW, SNOW_SH = "#E9F2F7", "#C6D9E6"
TREE_FAR, TREE_MID, TREE_NEAR = "#5A7A72", "#3C5C55", "#24403B"
WOOD, ROOF, WINDOW_ = "#8A6244", "#9C4F3A", "#F4C877"
DRG, DRG_DK, MEMB = "#5E8C6A", "#395A44", "#86AE8D"
INK = "#1A2730"
SKIN, CLOAK_A, CLOAK_B = "#E8B98F", "#A8443C", "#46607A"
PAPER, PAPER_INK = "#FBF7EA", "#2A2118"
CHIP = "#F0C04A"


def poly(pts, fill, op=1.0, stroke=None, sw=0.0):
    m = Polygon(*[np.array([x, y, 0]) for x, y in pts])
    m.set_fill(fill, op)
    m.set_stroke(stroke if stroke else fill, sw)
    return m


def rect(cx, cy, w, h, fill, op=1.0, stroke=None, sw=0.0, r=0.0):
    m = (RoundedRectangle(width=w, height=h, corner_radius=r)
         if r else Rectangle(width=w, height=h))
    m.set_fill(fill, op)
    m.set_stroke(stroke if stroke else fill, sw)
    m.move_to(np.array([cx, cy, 0]))
    return m


def blob(cx, cy, rx, ry, fill, op=1.0, stroke=None, sw=0.0):
    m = Circle(radius=1.0)
    m.set_fill(fill, op)
    m.set_stroke(stroke if stroke else fill, sw)
    m.stretch(rx, 0).stretch(ry, 1).move_to(np.array([cx, cy, 0]))
    return m


def ridge(y0, height, color, cap, seed, n=7, span=3.2):
    """One mountain rank: jagged silhouette plus snow caps on each peak."""
    rng = np.random.default_rng(seed)
    xs = np.linspace(-span, span, 2 * n + 1)
    pts, peaks = [(-span, y0)], []
    for i in range(1, len(xs) - 1):
        if i % 2:
            h = height * rng.uniform(0.70, 1.0)
            pts.append((xs[i], y0 + h))
            peaks.append((xs[i], y0 + h, h))
        else:
            pts.append((xs[i], y0 + height * rng.uniform(0.18, 0.38)))
    pts += [(span, y0), (span, y0 - 4.0), (-span, y0 - 4.0)]
    g = VGroup(poly(pts, color))
    for px, py, h in peaks:
        w = h * 0.30
        g.add(poly([(px, py), (px - w, py - h * 0.26),
                    (px - w * 0.35, py - h * 0.15), (px, py - h * 0.24),
                    (px + w * 0.40, py - h * 0.13),
                    (px + w, py - h * 0.26)], cap))
    return g


def pine(cx, base, h, color, lean=0.0):
    g = VGroup(rect(cx, base + h * 0.07, h * 0.055, h * 0.16, "#4A3828"))
    for k, f in enumerate((0.0, 0.26, 0.52)):
        w = h * (0.40 - 0.10 * k)
        y = base + h * (0.12 + f)
        tip = h * (0.40 - 0.09 * k)
        g.add(poly([(cx - w / 2 + lean, y), (cx + w / 2 + lean, y),
                    (cx + lean * 1.6, y + tip)], color))
    return g


def house(cx, base, w, h):
    g = VGroup(rect(cx, base + h / 2, w, h, WOOD, stroke=INK, sw=1.6))
    g.add(poly([(cx - w * 0.62, base + h), (cx + w * 0.62, base + h),
                (cx, base + h * 1.60)], ROOF, stroke=INK, sw=1.6))
    g.add(rect(cx, base + h * 0.22, w * 0.26, h * 0.44, "#5A3F2B",
               stroke=INK, sw=1.2))
    for sx in (-1, 1):
        g.add(rect(cx + sx * w * 0.28, base + h * 0.64, w * 0.22, h * 0.26,
                   WINDOW_, stroke=INK, sw=1.2))
    return g


def villager(cx, base, cloak, arm_up=False, scale=1.0):
    """Human proportions: head ~1/6 of height, not 1/3."""
    s = scale
    H = 0.86 * s
    hd = 0.105 * s
    g = VGroup()
    g.add(blob(cx, base + 0.012, 0.15 * s, 0.035 * s, SNOW_SH, 0.55))
    g.add(rect(cx - 0.035 * s, base + H * 0.15, 0.048 * s, H * 0.30,
               "#2E3B47", stroke=INK, sw=1.4))
    g.add(rect(cx + 0.035 * s, base + H * 0.15, 0.048 * s, H * 0.30,
               "#2E3B47", stroke=INK, sw=1.4))
    g.add(poly([(cx - 0.105 * s, base + H * 0.30), (cx + 0.105 * s, base + H * 0.30),
                (cx + 0.085 * s, base + H * 0.70), (cx - 0.085 * s, base + H * 0.70)],
               cloak, stroke=INK, sw=1.6))
    if arm_up:
        # upper arm out, forearm up, then a hand — a single straight limb
        # read as a spear in the first pass
        g.add(poly([(cx + 0.075 * s, base + H * 0.66),
                    (cx + 0.085 * s, base + H * 0.58),
                    (cx + 0.20 * s, base + H * 0.60),
                    (cx + 0.19 * s, base + H * 0.68)],
                   cloak, stroke=INK, sw=1.4))
        g.add(poly([(cx + 0.195 * s, base + H * 0.60),
                    (cx + 0.275 * s, base + H * 0.62),
                    (cx + 0.255 * s, base + H * 0.92),
                    (cx + 0.175 * s, base + H * 0.90)],
                   cloak, stroke=INK, sw=1.4))
        g.add(blob(cx + 0.218 * s, base + H * 0.955, 0.042 * s, 0.040 * s,
                   SKIN, stroke=INK, sw=1.4))
    else:
        g.add(poly([(cx + 0.08 * s, base + H * 0.66), (cx + 0.115 * s, base + H * 0.64),
                    (cx + 0.17 * s, base + H * 0.36), (cx + 0.135 * s, base + H * 0.34)],
                   cloak, stroke=INK, sw=1.4))
    g.add(poly([(cx - 0.08 * s, base + H * 0.66), (cx - 0.115 * s, base + H * 0.64),
                (cx - 0.175 * s, base + H * 0.38), (cx - 0.14 * s, base + H * 0.36)],
               cloak, stroke=INK, sw=1.4))
    g.add(blob(cx, base + H * 0.80, hd * 0.92, hd, SKIN, stroke=INK, sw=1.6))
    g.add(blob(cx, base + H * 0.775, hd * 0.20, hd * 0.26, "#6B3B2E"))
    g.add(poly([(cx - hd * 1.05, base + H * 0.855), (cx + hd * 1.05, base + H * 0.855),
                (cx + hd * 0.80, base + H * 0.955), (cx - hd * 0.80, base + H * 0.955)],
               "#4A3326", stroke=INK, sw=1.3))
    return g


def dragon(cx, cy, s=1.0):
    """Body, curved neck, horned head, one raised wing on visible struts,
    one far wing behind, tapering tail. The first pass stacked overlapping
    polygons and read as a green blob."""
    g = VGroup()

    # far wing, behind the body and darker
    g.add(poly([(cx - 0.05 * s, cy + 0.04 * s), (cx - 0.55 * s, cy + 0.46 * s),
                (cx - 0.95 * s, cy + 0.40 * s), (cx - 0.60 * s, cy + 0.20 * s),
                (cx - 0.30 * s, cy - 0.02 * s)], DRG_DK, 0.85,
               stroke=DRG_DK, sw=1.6))

    # tail: three tapering segments and a fin
    g.add(poly([(cx - 0.34 * s, cy + 0.04 * s), (cx - 0.36 * s, cy - 0.10 * s),
                (cx - 0.95 * s, cy - 0.30 * s), (cx - 1.45 * s, cy - 0.30 * s),
                (cx - 1.44 * s, cy - 0.22 * s), (cx - 0.98 * s, cy - 0.20 * s)],
               DRG, stroke=DRG_DK, sw=1.8))
    g.add(poly([(cx - 1.38 * s, cy - 0.26 * s), (cx - 1.72 * s, cy - 0.10 * s),
                (cx - 1.66 * s, cy - 0.34 * s)], MEMB, stroke=DRG_DK, sw=1.6))

    # body
    g.add(blob(cx, cy, 0.44 * s, 0.23 * s, DRG, stroke=DRG_DK, sw=2.0))

    # near wing, raised, with three struts so it reads as a membrane
    tip = (cx - 0.10 * s, cy + 1.00 * s)
    g.add(poly([(cx + 0.06 * s, cy + 0.14 * s), tip,
                (cx + 0.62 * s, cy + 0.74 * s), (cx + 0.46 * s, cy + 0.40 * s),
                (cx + 0.30 * s, cy + 0.16 * s)], MEMB, stroke=DRG_DK, sw=2.0))
    for ex, ey in ((cx - 0.10 * s, cy + 1.00 * s),
                   (cx + 0.30 * s, cy + 0.72 * s),
                   (cx + 0.58 * s, cy + 0.70 * s)):
        bar = VMobject(stroke_color=DRG_DK, stroke_width=1.6)
        bar.set_points_as_corners([np.array([cx + 0.08 * s, cy + 0.15 * s, 0]),
                                   np.array([ex, ey, 0])])
        g.add(bar)

    # neck, curving up to the right
    g.add(poly([(cx + 0.26 * s, cy + 0.12 * s), (cx + 0.30 * s, cy - 0.08 * s),
                (cx + 0.66 * s, cy + 0.06 * s), (cx + 0.74 * s, cy + 0.26 * s),
                (cx + 0.58 * s, cy + 0.28 * s), (cx + 0.50 * s, cy + 0.14 * s)],
               DRG, stroke=DRG_DK, sw=1.9))

    # head: skull, snout, jaw, horns, eye
    g.add(blob(cx + 0.80 * s, cy + 0.34 * s, 0.19 * s, 0.135 * s, DRG,
               stroke=DRG_DK, sw=1.9))
    g.add(poly([(cx + 0.90 * s, cy + 0.40 * s), (cx + 1.16 * s, cy + 0.30 * s),
                (cx + 1.14 * s, cy + 0.22 * s), (cx + 0.88 * s, cy + 0.24 * s)],
               DRG, stroke=DRG_DK, sw=1.7))
    g.add(poly([(cx + 0.92 * s, cy + 0.255 * s), (cx + 1.10 * s, cy + 0.225 * s),
                (cx + 0.94 * s, cy + 0.185 * s)], DRG_DK))
    for dx, ln in ((0.0, 0.20), (0.11, 0.15)):
        g.add(poly([(cx + (0.70 + dx) * s, cy + 0.44 * s),
                    (cx + (0.76 + dx) * s, cy + 0.44 * s),
                    (cx + (0.64 + dx) * s, cy + (0.44 + ln) * s)],
                   CAP_NEAR, stroke=DRG_DK, sw=1.4))
    g.add(blob(cx + 0.86 * s, cy + 0.37 * s, 0.038 * s, 0.045 * s, "#F6E27A",
               stroke=DRG_DK, sw=1.0))
    g.add(blob(cx + 0.868 * s, cy + 0.37 * s, 0.013 * s, 0.040 * s, INK))

    # back spines
    for k in range(4):
        bx = cx - 0.28 * s + k * 0.16 * s
        g.add(poly([(bx, cy + 0.17 * s), (bx + 0.07 * s, cy + 0.17 * s),
                    (bx + 0.025 * s, cy + 0.29 * s)], DRG_DK))
    return g


class SketchStyleTest(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(SKY_LO, 1.0))
        self.camera.frame.set_height(FRAME_H)

        bands = VGroup()
        for i in range(44):
            t = i / 43
            bands.add(rect(0, 4.5 - t * 7.0 - 0.08, 6.0, 0.17,
                           interpolate_color(SKY_HI, SKY_LO, t ** 0.85)))
        self.add(bands)

        snow_far = VGroup()
        rng = np.random.default_rng(7)
        for _ in range(130):
            x, y = rng.uniform(-2.6, 2.6), rng.uniform(-1.4, 4.3)
            r = rng.uniform(0.008, 0.019)
            snow_far.add(blob(x, y, r, r, "#FFFFFF", rng.uniform(0.30, 0.70)))
        self.add(snow_far)

        self.add(ridge(0.55, 1.55, MTN_FAR, CAP_FAR, 11, 8, 3.0))
        self.add(ridge(0.05, 2.05, MTN_MID, CAP_MID, 5, 6, 3.0))
        self.add(ridge(-0.55, 2.35, MTN_NEAR, CAP_NEAR, 23, 5, 3.1))

        # the ground has to run behind the dialogue box, or a band of bare
        # sky shows between the snow line and the box
        self.add(poly([(-3.2, -0.62), (-1.6, -0.50), (0.2, -0.60),
                       (1.8, -0.48), (3.2, -0.58), (3.2, -5.0), (-3.2, -5.0)],
                      SNOW))
        self.add(poly([(-3.2, -1.45), (-1.2, -1.30), (0.9, -1.42),
                       (3.2, -1.28), (3.2, -1.9), (-3.2, -1.9)], SNOW_SH, 0.5))

        far_trees = VGroup()
        for x in np.linspace(-2.5, 2.5, 13):
            far_trees.add(pine(x + float(rng.uniform(-0.09, 0.09)), -0.60,
                               0.44, TREE_FAR))
        self.add(far_trees)

        self.add(house(-1.62, -0.72, 0.52, 0.42))
        self.add(house(1.52, -0.70, 0.56, 0.46))
        self.add(house(-0.42, -0.76, 0.46, 0.36))

        mid_trees = VGroup()
        for x in (-2.35, -1.05, 0.30, 0.96, 2.22):
            mid_trees.add(pine(x, -0.95, 0.66, TREE_MID))
        self.add(mid_trees)

        self.add(dragon(0.30, 2.30, 0.80))

        self.add(villager(-0.72, -1.22, CLOAK_A, arm_up=True, scale=1.08))
        self.add(villager(0.10, -1.26, CLOAK_B, arm_up=False, scale=1.00))

        near_trees = VGroup()
        for x, h in ((-2.70, 1.25), (2.72, 1.35), (-2.15, 0.95)):
            near_trees.add(pine(x, -1.70, h, TREE_NEAR))
        self.add(near_trees)

        snow_near = VGroup()
        for _ in range(42):
            x, y = rng.uniform(-2.7, 2.7), rng.uniform(-2.2, 4.4)
            r = rng.uniform(0.022, 0.044)
            snow_near.add(blob(x, y, r, r, "#FFFFFF", rng.uniform(0.55, 0.9)))
        self.add(snow_near)

        bar = rect(0, 3.72, 4.5, 0.62, "#20303A", 0.96, stroke="#8FB8D0",
                   sw=2.0, r=0.16)
        title = Text("THE DRAGON ARRIVES", fill_color="#F2F7FA",
                     font_size=31, weight=BOLD)
        title.move_to(np.array([0, 3.72, 0]))
        self.add(bar, title)

        box = rect(0, -2.80, 4.6, 1.05, PAPER, 1.0, stroke=INK, sw=3.0, r=0.16)
        chip = rect(-1.52, -2.46, 1.05, 0.30, CHIP, 1.0, stroke=INK, sw=2.0,
                    r=0.11)
        who = Text("GUARD", fill_color=PAPER_INK, font_size=19, weight=BOLD)
        who.move_to(np.array([-1.52, -2.46, 0]))
        line = Text("A DRAGON!", fill_color=PAPER_INK, font_size=36,
                    weight=BOLD)
        line.move_to(np.array([0, -2.98, 0]))
        line.align_to(np.array([-2.02, 0, 0]), LEFT)
        self.add(box, chip, who, line)

        self.wait(0.1)
