"""
dragon_study — build the dragon from its skeleton outward. Three stills.

    for S in DragonSkeleton DragonMembrane DragonFinished; do
      xvfb-run -a -s "-screen 0 1600x1200x24" \
        manimgl dragon_study.py $S -s -w -r 1080x1920
    done

WHY THIS EXISTS. The first dragon I drew was a green ellipse with
triangles stuck on it, because I drew the SHAPE I remembered instead of
the structure underneath. This builds it the other way round.

WHAT THE RESEARCH ACTUALLY SAID

  Layout. A wyvern has two hind legs and wings IN PLACE OF forelimbs; a
  four-legged European dragon has wings as a separate fifth pair of
  limbs. Skyrim's are the two-legged kind — though that is fan consensus
  and terminology, not a Bethesda statement, so it is a design choice
  here rather than a fact.

  The wing is a HAND. This is the part I had wrong and it is real
  biology, borrowed from bats:
    humerus      short upper arm, shoulder to elbow
    radius       long forearm, elbow to wrist; the ulna is reduced
    digits II-V  enormously elongated fingers that carry the membrane,
                 each a long metacarpal plus one to three phalanges
    thumb        SHORT, clawed, and sitting OUTSIDE the wing surface at
                 the wrist — the detail that stops a wing reading as a
                 kite

  The membrane has named regions, not one flat sheet:
    propatagium       shoulder -> wrist, the leading edge
    dactylopatagium   between the fingers, the main fan
    plagiopatagium    last finger -> body -> ANKLE. The wing is anchored
                      to the back leg, which is why a bat's hindlimb
                      steers its wing, and why a wing drawn floating
                      free of the body looks pinned on
    uropatagium       between the legs, across the tail base

Everything above is laid out as geometry first (DragonSkeleton), then
skinned (DragonMembrane), then rendered (DragonFinished), so the final
drawing inherits the structure instead of approximating it.
"""
import os
import sys

from manimlib import *
import numpy as np

INK      = "#1A2730"
BONE     = "#EFE7D6"
BONE_DK  = "#8C7F68"
JOINT    = "#D4703F"
LABEL    = "#9BA9B4"
ACCENT   = "#EBCB8B"
PAPER    = "#111820"

HIDE     = "#2E4A3C"
HIDE_DK  = "#1E3328"
HIDE_LT  = "#43miss"
MEMB     = "#6E5147"
MEMB_LT  = "#8A6657"
BELLY    = "#9C8A5E"
HORN     = "#D8CDB4"
EYE      = "#F2B544"

HIDE_LT  = "#43674F"

S = 0.80
OX, OY = 0.42, -0.20


def P(x, y):
    return np.array([x * S + OX, y * S + OY, 0])


# ---------------------------------------------------------------- skeleton
PELVIS   = (-0.90, -0.20)
SHOULDER = (0.50, 0.25)
NECK_1   = (0.95, 0.62)
NECK_2   = (1.32, 0.98)
SKULL    = (1.78, 1.18)
SNOUT    = (2.34, 1.02)
JAW      = (2.18, 0.84)

ELBOW    = (0.10, 1.18)
WRIST    = (0.78, 2.08)
THUMB    = (0.99, 2.38)
D2       = (1.62, 2.76)
D3       = (0.68, 3.06)
D4       = (-0.38, 2.62)
D5       = (-1.08, 1.74)

KNEE     = (-0.52, -0.98)
ANKLE    = (-0.96, -1.62)
TOE      = (-0.50, -1.88)

TAIL = [PELVIS, (-1.70, -0.44), (-2.48, -0.22), (-3.06, 0.22)]

SPINE = [PELVIS, (-0.30, 0.02), (0.14, 0.18), SHOULDER]
NECK = [SHOULDER, NECK_1, NECK_2, SKULL]


def bone(a, b, w=7.0, color=BONE):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners([P(*a), P(*b)])
    return m


def curve(pts, w=7.0, color=BONE):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_smoothly([P(*p) for p in pts])
    return m


def joint(p, r=0.055, color=JOINT):
    return Dot(P(*p), radius=r, fill_color=color)


def tag(text, p, dx=0.0, dy=0.0, size=15, color=LABEL):
    t = Text(text, fill_color=color, font_size=size, weight=BOLD)
    t.move_to(P(*p) + np.array([dx, dy, 0]))
    return t


def skeleton(label=True):
    g = VGroup()
    g.add(curve(TAIL, 6.0), curve(SPINE, 8.0), curve(NECK, 7.0))
    # skull
    sk = Polygon(P(*SKULL), P(SKULL[0] + 0.30, SKULL[1] + 0.12),
                 P(*SNOUT), P(*JAW), P(SKULL[0] + 0.12, SKULL[1] - 0.20))
    sk.set_fill(BONE, 0.9).set_stroke(BONE, 3.0)
    g.add(sk)
    # the wing, as an arm
    g.add(bone(SHOULDER, ELBOW, 8.0), bone(ELBOW, WRIST, 8.0))
    g.add(bone(WRIST, THUMB, 5.0, ACCENT))
    for d in (D2, D3, D4, D5):
        g.add(bone(WRIST, d, 6.0))
    # hind limb
    g.add(bone(PELVIS, KNEE, 8.0), bone(KNEE, ANKLE, 7.0), bone(ANKLE, TOE, 5.0))
    for p in (PELVIS, SHOULDER, ELBOW, WRIST, KNEE, ANKLE, NECK_2):
        g.add(joint(p))
    g.add(joint(THUMB, 0.040, ACCENT))
    for d in (D2, D3, D4, D5):
        g.add(joint(d, 0.040))
    if label:
        g.add(tag("HUMERUS", (0.30, 0.72), -0.52, 0.0))
        g.add(tag("RADIUS", (0.44, 1.63), -0.46, 0.0))
        g.add(tag("THUMB  (clawed,", THUMB, 0.70, 0.12, 14, ACCENT))
        g.add(tag("outside the wing)", THUMB, 0.70, -0.06, 14, ACCENT))
        for name, d, dx, dy in (("II", D2, 0.20, 0.10), ("III", D3, 0.04, 0.20),
                                ("IV", D4, -0.18, 0.16), ("V", D5, -0.26, 0.04)):
            g.add(tag(name, d, dx, dy, 17, BONE))
        g.add(tag("DIGITS II-V carry the membrane", (0.10, 3.40), 0.0, 0.0, 15))
        g.add(tag("FEMUR", KNEE, -0.46, 0.14))
        g.add(tag("ANKLE", ANKLE, -0.46, -0.02))
        g.add(tag("CERVICAL", NECK_1, 0.42, -0.10))
        g.add(tag("PELVIS", PELVIS, -0.48, 0.10))
    return g



def taper(pts, w0, w1, fill, stroke=None, sw=2.4, n=46):
    """A limb with thickness that falls off along its length. A plain
    stroke gives a constant-width tube, which is what made the neck, tail
    and legs read as sticks."""
    path = VMobject()
    path.set_points_smoothly([P(*p) for p in pts])
    samp = [path.point_from_proportion(i / (n - 1)) for i in range(n)]
    left, right = [], []
    for i, p in enumerate(samp):
        t = i / (n - 1)
        w = (w0 + (w1 - w0) * t) * S
        tg = (samp[1] - samp[0] if i == 0 else
              samp[-1] - samp[-2] if i == n - 1 else
              samp[i + 1] - samp[i - 1])
        tg = tg / (np.linalg.norm(tg) + 1e-9)
        nrm = np.array([-tg[1], tg[0], 0.0])
        left.append(p + nrm * w / 2)
        right.append(p - nrm * w / 2)
    out = left + right[::-1]
    m = VMobject()
    m.set_points_smoothly(out + [out[0]])
    m.set_fill(fill, 1.0)
    m.set_stroke(stroke if stroke else fill, sw)
    return m


def smooth_shape(pts, fill, stroke=None, sw=2.6, op=1.0):
    m = VMobject()
    m.set_points_smoothly([P(*p) for p in pts] + [P(*pts[0])])
    m.set_fill(fill, op)
    m.set_stroke(stroke if stroke else fill, sw)
    return m


def scallop(a, b, toward, amount=0.16):
    """Midpoint of a-b pulled toward a third point. A membrane hangs in
    concave arcs between the finger tips; straight edges read as a kite."""
    m = np.array([(a[0] + b[0]) / 2, (a[1] + b[1]) / 2])
    t = np.array(toward[:2])
    v = m + (t - m) * amount
    return (float(v[0]), float(v[1]))


# ---------------------------------------------------------------- membrane
def membranes(op=0.55):
    g = VGroup()
    pro = Polygon(P(*SHOULDER), P(*ELBOW), P(*WRIST), P(WRIST[0] - 0.10, WRIST[1] - 0.35))
    pro.set_fill(MEMB_LT, op).set_stroke(MEMB_LT, 2.0)
    g.add(pro)
    fan = Polygon(P(*WRIST), P(*D2), P(*D3), P(*D4), P(*D5))
    fan.set_fill(MEMB, op).set_stroke(MEMB, 2.0)
    g.add(fan)
    plag = Polygon(P(*D5), P(*SHOULDER), P(*PELVIS), P(*ANKLE))
    plag.set_fill(MEMB_LT, op * 0.85).set_stroke(MEMB_LT, 2.0)
    g.add(plag)
    uro = Polygon(P(*ANKLE), P(*PELVIS), P(-1.70, -0.44), P(-1.30, -1.20))
    uro.set_fill(MEMB, op * 0.7).set_stroke(MEMB, 2.0)
    g.add(uro)
    return g


def membrane_tags():
    """A legend below the figure. Labels laid over the membranes were
    unreadable — dark text on a mid-brown fill."""
    rows = [(MEMB_LT, "PROPATAGIUM", "shoulder to wrist, the leading edge"),
            (MEMB_LT, "DACTYLOPATAGIUM", "between the four long fingers"),
            (MEMB,    "PLAGIOPATAGIUM", "last finger, down the flank, to the ankle")]
    g = VGroup()
    for i, (col, name, desc) in enumerate(rows):
        y = -2.16 - i * 0.44
        sw = Square(side_length=0.19)
        sw.set_fill(col, 1.0).set_stroke("#8C7F68", 1.6)
        sw.move_to(np.array([-2.10, y, 0]))
        n = Text(name, fill_color="#C9A08C", font_size=17, weight=BOLD)
        n.move_to(np.array([0, y + 0.085, 0]))
        n.align_to(np.array([-1.88, 0, 0]), LEFT)
        d = Text(desc, fill_color=LABEL, font_size=14)
        if d.get_width() > 3.4:
            d.set_width(3.4)
        d.move_to(np.array([0, y - 0.105, 0]))
        d.align_to(np.array([-1.88, 0, 0]), LEFT)
        g.add(sw, n, d)
    return g


# ---------------------------------------------------------------- finished
def finished():
    """Draw order matters as much as shape: anything belonging to the far
    side goes down first, the torso covers the wing roots, and the spines
    go on last along the actual back curve."""
    g = VGroup()

    # --- far side, behind everything ---------------------------------
    far = [(0.30, 0.30), (-0.30, 1.55), (-1.15, 1.95), (-1.30, 1.20),
           (-0.60, 0.85), (-0.20, 0.40)]
    g.add(smooth_shape(far, HIDE_DK, HIDE_DK, 2.0, 0.9))

    # --- the wing, drawn BEFORE the body so the torso covers its root --
    # leading edge: a slim strip shoulder->elbow->wrist. Bowing this one
    # hard made a sheet that draped over the neck.
    pro = [SHOULDER, ELBOW, WRIST, scallop(WRIST, SHOULDER, ELBOW, 0.40)]
    g.add(smooth_shape(pro, MEMB_LT, HIDE_DK, 2.2))
    fanpts = [WRIST, D2, scallop(D2, D3, WRIST), D3,
              scallop(D3, D4, WRIST), D4, scallop(D4, D5, WRIST), D5]
    g.add(smooth_shape(fanpts, MEMB_LT, HIDE_DK, 2.6))
    plag = [D5, (0.28, 0.34), PELVIS, ANKLE,
            scallop(ANKLE, D5, (-0.55, 0.40), -0.10)]
    g.add(smooth_shape(plag, MEMB, HIDE_DK, 2.4))
    for d in (D2, D3, D4, D5):
        g.add(taper([WRIST, d], 0.12, 0.035, HIDE, HIDE_DK, 1.6))
    g.add(taper([SHOULDER, ELBOW], 0.26, 0.17, HIDE, HIDE_DK, 2.0))
    g.add(taper([ELBOW, WRIST], 0.17, 0.12, HIDE, HIDE_DK, 2.0))
    g.add(taper([WRIST, THUMB], 0.10, 0.04, HIDE, HIDE_DK, 1.6))
    g.add(taper([THUMB, (THUMB[0] + 0.20, THUMB[1] + 0.18)], 0.05, 0.01,
                HORN, HIDE_DK, 1.2))

    # --- tail ---------------------------------------------------------
    g.add(taper(TAIL, 0.44, 0.05, HIDE, HIDE_DK, 2.4))
    g.add(smooth_shape([(-2.62, 0.08), (-3.18, 0.62), (-3.02, 0.04),
                        (-3.34, -0.22), (-2.70, -0.06)],
                       MEMB_LT, HIDE_DK, 2.0))

    # --- body ---------------------------------------------------------
    torso = [(0.74, 0.28), (0.48, 0.60), (-0.24, 0.56), (-0.84, 0.34),
             (-1.14, -0.06), (-0.88, -0.40), (-0.18, -0.36), (0.48, -0.12)]
    g.add(smooth_shape(torso, HIDE, HIDE_DK, 2.8))
    g.add(smooth_shape([(0.48, -0.10), (-0.18, -0.32), (-0.88, -0.36),
                        (-0.98, -0.14), (-0.24, -0.10), (0.40, 0.04)],
                       BELLY, None, 0.0, 0.8))

    # --- hind limb, thicker: it carries the whole animal ---------------
    g.add(taper([(-0.98, 0.14), (-0.72, -0.54), KNEE], 0.62, 0.26,
                HIDE, HIDE_DK, 2.4))
    g.add(taper([KNEE, ANKLE], 0.24, 0.15, HIDE, HIDE_DK, 2.2))
    g.add(taper([ANKLE, TOE], 0.17, 0.11, HIDE, HIDE_DK, 2.0))
    for t in ((-0.22, -1.98), (-0.48, -2.08), (-0.74, -1.98)):
        g.add(taper([TOE, t], 0.08, 0.016, HORN, HIDE_DK, 1.2))

    # --- neck and head -------------------------------------------------
    g.add(taper(NECK, 0.40, 0.21, HIDE, HIDE_DK, 2.6))
    g.add(smooth_shape([(1.56, 1.06), (1.66, 1.32), (2.02, 1.34),
                        (2.36, 1.06), (2.30, 0.92), (1.92, 0.90),
                        (1.60, 0.92)], HIDE, HIDE_DK, 2.6))
    g.add(smooth_shape([(1.88, 0.94), (2.28, 0.92), (2.10, 0.74),
                        (1.82, 0.84)], HIDE_DK, HIDE_DK, 2.0))
    for hx, hy, lx, ly in ((1.62, 1.28, 1.18, 1.80), (1.78, 1.33, 1.44, 1.90)):
        g.add(taper([(hx, hy), (lx, ly)], 0.13, 0.02, HORN, HIDE_DK, 1.6))
    g.add(Dot(P(1.90, 1.14), radius=0.042, fill_color=EYE))
    g.add(Dot(P(1.905, 1.14), radius=0.013, fill_color=INK))

    # --- spines LAST, following the back and up the neck ---------------
    back = [(-0.92, 0.34), (-0.40, 0.56), (0.18, 0.58), (0.62, 0.42),
            (0.98, 0.64), (1.30, 0.98)]
    for i, (bx, by) in enumerate(back):
        h = 0.30 - 0.035 * i
        g.add(smooth_shape([(bx - 0.07, by), (bx + 0.08, by),
                            (bx + 0.01, by + h)], HORN, HIDE_DK, 1.3))
    return g


# ---------------------------------------------------------------- scenes
def header(line1, line2):
    g = VGroup()
    a = Text(line1, fill_color=ACCENT, font_size=30, weight=BOLD)
    a.move_to(np.array([0, 3.72, 0]))
    b = Text(line2, fill_color=LABEL, font_size=20)
    if b.get_width() > 3.3:
        b.set_width(3.3)
    b.move_to(np.array([0, 3.28, 0]))
    g.add(a, b)
    return g


def footer(text):
    t = Text(text, fill_color="#6F7E89", font_size=18)
    if t.get_width() > 3.3:
        t.set_width(3.3)
    t.move_to(np.array([0, -3.45, 0]))
    return t


class _Base(Scene):
    def setup_bg(self):
        self.camera.background_rgba = list(color_to_rgba(PAPER, 1.0))
        self.camera.frame.set_height(9.0)


class DragonSkeleton(_Base):
    def construct(self):
        self.setup_bg()
        self.add(header("1 — THE ARMATURE",
                        "the wing is a hand: humerus, radius, four long fingers"))
        self.add(skeleton(label=True))
        self.add(footer("two hind legs, wings in place of forelimbs — a wyvern"))
        self.wait(0.1)


class DragonMembrane(_Base):
    def construct(self):
        self.setup_bg()
        self.add(header("2 — THE MEMBRANE",
                        "four regions, not one flat sheet"))
        self.add(membranes(0.60))
        self.add(skeleton(label=False).set_opacity(0.45))
        self.add(membrane_tags())
        
        self.wait(0.1)


class DragonFinished(_Base):
    def construct(self):
        self.setup_bg()
        self.add(header("3 — THE DRAWING",
                        "same geometry, skinned"))
        self.add(finished())
        self.add(footer("every edge above sits on a bone from panel 1"))
        self.wait(0.1)
