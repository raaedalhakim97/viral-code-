"""
dragonborn — a reusable Skyrim protagonist rig. Three plates.

    for S in DbProportions DbCharacter DbPoses; do
      xvfb-run -a -s "-screen 0 1600x1200x24" \
        manimgl dragonborn.py $S -s -w -r 1080x1920
    done

Built as a RIG, not a picture: every limb is driven by a pose dict, so
the same character can be re-posed for each line of a sketch instead of
redrawn.

WHAT THE RESEARCH SAID

  Helmet. The Skyrim iron helmet's horns are short and curve slightly
  inward on the male model; the Ancient Nord helmet is a variant with
  the same two curved horns. That is the single most recognisable part
  of the silhouette, so it is drawn to that description.

  Fur and shoulders. I found no canonical source. The fur mantle here
  is a design choice that reads as "Nord" at a glance, not a claim about
  the game's model.

  Proportions. Realistic adults are about 7.5-8 heads; chibi is roughly
  1.75-3. Chibi was rejected on purpose: at those proportions the arms
  and legs become stubs and big poses stop reading, and this character
  exists to gesture. Five heads keeps the head large enough to carry
  expression on a phone while the limbs stay long enough to act.

  Silhouette first. The smaller the figure renders, the more the
  outline does the work — hence horns, fur mantle and sword, which are
  readable as a shape before any detail resolves.

POSING. Add an entry to POSES: joint positions in head units, measured
from the top of the skull with y running DOWN. Nothing else changes.

ANIMATING. `lerp_pose(a, b, t)` blends two poses, and `dragonborn()`
takes a blended dict as happily as a name, so a scene can rebuild the
figure from a clock every frame. See dragonborn_anim.py. `DETAIL` is the
number of samples each tapered limb is resampled to — dropped for
animation, where it is paid 60 times a second.
"""
import numpy as np
from manimlib import *

INK      = "#14202A"
PAPER    = "#111820"
LABEL    = "#9BA9B4"
ACCENT   = "#EBCB8B"
GUIDE    = "#35485A"

IRON     = "#6E7C86"
IRON_DK  = "#46535C"
IRON_LT  = "#93A1AA"
LEATHER  = "#6B4B33"
LEATH_DK = "#4A3222"
FUR      = "#C7B9A1"
FUR_DK   = "#9C8C73"
CLOTH    = "#3E4A55"
# the cloak is scenery behind the limbs, so it sits a stop darker
# than them, and every limb carries a light edge against it
CLOAK    = "#26303A"
CLOAK_DK = "#1A222A"
LIMB_EDGE = "#66798A"
SKIN     = "#D9A87C"
SKIN_DK  = "#A87A52"
STEEL    = "#C3CDD4"
WOOD     = "#7A5636"
BLOOD    = "#8C3B33"

# ------------------------------------------------------------------ rig
# every landmark in HEAD UNITS: 1.0 = one head height, y runs DOWN from
# the top of the skull, x from the body's centre line
CHIN      = 1.00
NECK      = 1.08
SHOULDER  = 1.26
SH_HALF   = 0.50
CHEST     = 1.80
WAIST     = 2.45
WA_HALF   = 0.34
HIP       = 2.70
HIP_HALF  = 0.38
TOTAL     = 5.00

POSES = {
    "idle": dict(
        el=(-0.66, 1.98), hl=(-0.76, 2.74),
        er=(0.66, 1.98),  hr=(0.76, 2.74),
        kl=(-0.27, 3.76), fl=(-0.32, 4.94),
        kr=(0.29, 3.76),  fr=(0.34, 4.94), tilt=0.0),
    # the elbow sits OUT at shoulder height, not tucked under the hand.
    # Tucked, the forearm had to be drawn 17% longer than the idle one to
    # reach, and a rubber forearm is exactly what the check below is for.
    "point": dict(
        el=(-0.60, 2.02), hl=(-0.54, 2.76),
        er=(1.02, 1.53),  hr=(1.12, 0.78),
        kl=(-0.30, 3.78), fl=(-0.40, 4.94),
        kr=(0.30, 3.74),  fr=(0.38, 4.94), tilt=-0.06),
    # the shrug carries most of the comedy, so it is pushed further than
    # feels right on paper: elbows pinned in, forearms swung out, hands
    # high and open. A subtle shrug reads as "standing still". The
    # forearms end up well under their idle length, which is correct —
    # swung out toward the camera, they foreshorten.
    "shrug": dict(
        el=(-0.58, 2.01), hl=(-1.14, 1.92),
        er=(0.58, 2.01),  hr=(1.14, 1.92),
        kl=(-0.28, 3.78), fl=(-0.34, 4.94),
        kr=(0.28, 3.78),  fr=(0.36, 4.94), tilt=0.06),
    # sword overhead. Right arm lengths are kept at the idle lengths so
    # the limb does not visibly stretch on the way up: upper 0.675,
    # fore 0.762 against idle's 0.654 and 0.762.
    "sword_up": dict(
        el=(-0.62, 2.00), hl=(-0.40, 2.74),
        er=(0.86, 0.84),  hr=(0.80, 0.08),
        kl=(-0.28, 3.76), fl=(-0.33, 4.94),
        kr=(0.30, 3.76),  fr=(0.35, 4.94), tilt=0.0),
    # a front-on walk cannot swing the legs sideways, so it marches: the
    # knee comes UP toward the camera and the thigh foreshortens, which
    # is what a raised knee actually does from the front.
    "march_l": dict(
        el=(-0.62, 1.94), hl=(-0.74, 2.62),
        er=(0.64, 2.02),  hr=(0.66, 2.82),
        kl=(-0.31, 3.26), fl=(-0.37, 4.26),
        kr=(0.29, 3.80),  fr=(0.34, 4.96), tilt=-0.02),
    "march_r": dict(
        el=(-0.64, 2.02), hl=(-0.66, 2.82),
        er=(0.62, 1.94),  hr=(0.74, 2.62),
        kl=(-0.29, 3.80), fl=(-0.34, 4.96),
        kr=(0.33, 3.26),  fr=(0.39, 4.26), tilt=0.02),
    # the deflation. Arms hang dead straight, knees unlock, head drops —
    # hdrop is the only thing in the rig that moves the helmet DOWN.
    # the sword droops with him. `sang` is kept to a shallow 31 degrees
    # and NOT swung down to point at the floor: a 1.62-head blade
    # rotating past horizontal from a hand this far out puts the point
    # two units to the right mid-swing, straight through the action rail.
    # A shallow droop reads as "lowered" next to the shrug's raised
    # blade, and it still gets the steel off the forearm.
    "slump": dict(
        el=(-0.52, 2.04), hl=(-0.50, 2.80),
        er=(0.58, 2.01),  hr=(0.68, 2.74),
        kl=(-0.34, 3.72), fl=(-0.32, 4.94),
        kr=(0.36, 3.72),  fr=(0.34, 4.94),
        tilt=0.02, hdrop=0.15, sang=0.55),
}

JOINTS = ("el", "hl", "er", "hr", "kl", "fl", "kr", "fr")
SCALARS = {"tilt": 0.0, "hdrop": 0.0, "sang": 0.0}

# fill the defaults in once, so every pose carries every key and
# lerp_pose never has to guess
for _p in POSES.values():
    for _k, _v in SCALARS.items():
        _p.setdefault(_k, _v)
    assert set(_p) == set(JOINTS) | set(SCALARS), sorted(_p)

# A pose is a drawing instruction, but the limbs are still limbs: no
# pose may draw one LONGER than the idle pose draws it, because the
# taper just renders whatever it is handed and an over-long forearm
# reads as rubber rather than as a reach. This is a one-sided check on
# purpose — shorter is legal and often required, since a limb swung
# toward the camera foreshortens: the march's raised thigh and the
# point's upper arm are both well under their idle lengths and both are
# correct. It caught a real one: the slump's forearm was drawn 8% long
# because the hand had been placed further from the shoulder than the
# arm can reach.
_SH = {"l": (-SH_HALF * 0.86, SHOULDER + 0.10),
       "r": (SH_HALF * 0.86, SHOULDER + 0.10)}
_HP = {"l": (-HIP_HALF * 0.7, HIP), "r": (HIP_HALF * 0.7, HIP)}


def _d(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def _limbs(p):
    out = {}
    for k in ("l", "r"):
        out["upper" + k] = _d(_SH[k], p["e" + k])
        out["fore" + k] = _d(p["e" + k], p["h" + k])
        out["thigh" + k] = _d(_HP[k], p["k" + k])
        out["shin" + k] = _d(p["k" + k], p["f" + k])
    return out


_REF = _limbs(POSES["idle"])
for _nm, _p in POSES.items():
    for _part, _len in _limbs(_p).items():
        _hi = _REF[_part] * 1.05
        assert _len <= _hi, (_nm, _part, round(_len, 3), round(_hi, 3))

# number of samples a tapered limb is resampled to. 34 for a still
# plate; an animated scene lowers it, because it pays this 60x a second.
DETAIL = 34


def set_detail(n):
    global DETAIL
    DETAIL = n


def lerp_pose(a, b, t):
    """Blend two poses. Joint-space, not pixel-space: limbs swing to
    their new positions instead of the whole drawing cross-fading."""
    out = {k: (a[k][0] + (b[k][0] - a[k][0]) * t,
               a[k][1] + (b[k][1] - a[k][1]) * t) for k in JOINTS}
    for k in SCALARS:
        out[k] = a[k] + (b[k] - a[k]) * t
    return out


class Rig:
    """Maps head units into frame space for one figure."""

    def __init__(self, head, cx, top):
        self.h, self.cx, self.top = head, cx, top

    def p(self, x, y):
        return np.array([self.cx + x * self.h, self.top - y * self.h, 0])

    def w(self, u):
        return u * self.h


def taper(rig, pts, w0, w1, fill, stroke=None, sw=2.2, n=None):
    n = DETAIL if n is None else n
    path = VMobject()
    path.set_points_smoothly([rig.p(*q) for q in pts])
    samp = [path.point_from_proportion(i / (n - 1)) for i in range(n)]
    left, right = [], []
    for i, q in enumerate(samp):
        t = i / (n - 1)
        wd = rig.w(w0 + (w1 - w0) * t)
        tg = (samp[1] - samp[0] if i == 0 else
              samp[-1] - samp[-2] if i == n - 1 else
              samp[i + 1] - samp[i - 1])
        tg = tg / (np.linalg.norm(tg) + 1e-9)
        nm = np.array([-tg[1], tg[0], 0.0])
        left.append(q + nm * wd / 2)
        right.append(q - nm * wd / 2)
    out = left + right[::-1]
    m = VMobject()
    m.set_points_smoothly(out + [out[0]])
    m.set_fill(fill, 1.0)
    m.set_stroke(stroke if stroke else fill, sw)
    return m


def shape(rig, pts, fill, stroke=None, sw=2.2, op=1.0, smooth=True):
    m = VMobject()
    q = [rig.p(*a) for a in pts]
    if smooth:
        m.set_points_smoothly(q + [q[0]])
    else:
        m.set_points_as_corners(q + [q[0]])
    m.set_fill(fill, op)
    m.set_stroke(stroke if stroke else fill, sw)
    return m


def disc(rig, x, y, rx, ry, fill, stroke=None, sw=2.0):
    m = Circle(radius=1.0)
    m.set_fill(fill, 1.0)
    m.set_stroke(stroke if stroke else fill, sw)
    m.stretch(rig.w(rx), 0).stretch(rig.w(ry), 1).move_to(rig.p(x, y))
    return m


# ------------------------------------------------------------------ parts
def helmet(rig, tilt=0.0, hdrop=0.0):
    g = VGroup()
    t = tilt
    rig = Rig(rig.h, rig.cx, rig.top - hdrop * rig.h)
    # skull cap
    g.add(shape(rig, [(-0.42 + t, 0.62), (-0.40 + t, 0.26), (-0.22 + t, 0.02),
                      (0.22 + t, 0.02), (0.40 + t, 0.26), (0.42 + t, 0.62)],
                IRON, IRON_DK, 2.4))
    # brow band
    g.add(shape(rig, [(-0.43 + t, 0.60), (0.43 + t, 0.60), (0.43 + t, 0.48),
                      (-0.43 + t, 0.48)], IRON_DK, IRON_DK, 1.6, smooth=False))
    # face opening, nose guard down the middle
    g.add(shape(rig, [(-0.34 + t, 0.60), (0.34 + t, 0.60), (0.32 + t, 0.86),
                      (-0.32 + t, 0.86)], "#1B262E", "#1B262E", 1.4,
                smooth=False))
    g.add(shape(rig, [(-0.05 + t, 0.60), (0.05 + t, 0.60), (0.04 + t, 0.90),
                      (-0.04 + t, 0.90)], IRON, IRON_DK, 1.6, smooth=False))
    # eyes in the slot
    for sx in (-0.19, 0.19):
        g.add(disc(rig, sx + t, 0.71, 0.050, 0.038, "#F0D9A0", None, 0))
    # horns: short, curving slightly INWARD, per the iron helmet description
    for sd in (-1, 1):
        g.add(taper(rig, [(sd * 0.40 + t, 0.40), (sd * 0.60 + t, 0.18),
                          (sd * 0.52 + t, -0.16)], 0.17, 0.045,
                    FUR, IRON_DK, 1.8))
    # jaw / beard shadow below the helmet
    g.add(shape(rig, [(-0.28 + t, 0.86), (0.28 + t, 0.86), (0.20 + t, 1.06),
                      (-0.20 + t, 1.06)], SKIN_DK, None, 0))
    return g


def body(rig, pose):
    g = VGroup()
    t = pose["tilt"]

    # Cloak behind. Darker and narrower than it first was: at the legs'
    # own colour it ate them, and once the figure started MOVING a thigh
    # that does not read against the cloak stops reading as a leg at all.
    # It is background, so it is lit like background.
    g.add(shape(rig, [(-0.54, SHOULDER), (0.54, SHOULDER), (0.72, 3.16),
                      (0.26, 3.32), (-0.26, 3.32), (-0.72, 3.16)],
                CLOAK, CLOAK_DK, 2.2))

    # legs
    for k, f in (("l", -1), ("r", 1)):
        # the light edge is what separates the thigh from the cloak
        g.add(taper(rig, [(f * HIP_HALF * 0.7, HIP), pose["k" + k]],
                    0.40, 0.30, CLOTH, LIMB_EDGE, 2.0))
        g.add(taper(rig, [pose["k" + k], pose["f" + k]],
                    0.30, 0.26, LEATHER, LEATH_DK, 2.0))
        fx, fy = pose["f" + k]
        g.add(shape(rig, [(fx - 0.16, fy - 0.10), (fx + 0.20, fy - 0.10),
                          (fx + 0.24, fy + 0.06), (fx - 0.18, fy + 0.06)],
                    LEATH_DK, "#33230F", 2.0))
        g.add(shape(rig, [(fx - 0.19, fy - 0.34), (fx + 0.19, fy - 0.34),
                          (fx + 0.21, fy - 0.12), (fx - 0.21, fy - 0.12)],
                    FUR, FUR_DK, 1.8))

    # torso: cuirass
    g.add(shape(rig, [(-SH_HALF * 0.82, SHOULDER + 0.06),
                      (SH_HALF * 0.82, SHOULDER + 0.06),
                      (WA_HALF + 0.06, WAIST), (WA_HALF, HIP + 0.10),
                      (-WA_HALF, HIP + 0.10), (-WA_HALF - 0.06, WAIST)],
                LEATHER, LEATH_DK, 2.6))
    # chest straps
    for a, b in (((-0.30, SHOULDER + 0.10), (0.22, WAIST - 0.04)),
                 ((0.30, SHOULDER + 0.10), (-0.22, WAIST - 0.04))):
        g.add(taper(rig, [a, b], 0.10, 0.09, LEATH_DK, None, 0))
    # belt
    g.add(shape(rig, [(-WA_HALF - 0.05, WAIST + 0.02),
                      (WA_HALF + 0.05, WAIST + 0.02),
                      (WA_HALF + 0.05, WAIST + 0.20),
                      (-WA_HALF - 0.05, WAIST + 0.20)],
                LEATH_DK, "#33230F", 2.0, smooth=False))
    g.add(disc(rig, 0.0, WAIST + 0.11, 0.075, 0.065, IRON_LT, IRON_DK, 1.6))

    # arms
    for k, f in (("l", -1), ("r", 1)):
        g.add(taper(rig, [(f * SH_HALF * 0.86, SHOULDER + 0.10),
                          pose["e" + k]], 0.34, 0.26, LEATHER, "#8A6240", 2.0))
        g.add(taper(rig, [pose["e" + k], pose["h" + k]],
                    0.26, 0.21, IRON, IRON_DK, 2.0))
        hx, hy = pose["h" + k]
        g.add(disc(rig, hx, hy + 0.06, 0.115, 0.105, SKIN, SKIN_DK, 1.8))

    # fur mantle over the shoulders, drawn after the arms so it sits on top
    # one ragged band. A row of discs along the hem read as a bead
    # necklace rather than fur.
    top_edge, hem = [], []
    for i in range(11):
        a = -1.0 + i * 0.2
        top_edge.append((a * 0.64, SHOULDER - 0.12 + 0.10 * abs(a) ** 1.6))
    for i in range(10):
        a = 1.0 - i * 0.222
        # alternate the hem in and out so the edge tufts
        depth = 0.52 if i % 2 == 0 else 0.38
        hem.append((a * 0.66, SHOULDER + depth))
    g.add(shape(rig, top_edge + hem, FUR, FUR_DK, 2.4))
    for i in range(6):
        a = -0.78 + i * 0.31
        m = VMobject(stroke_color=FUR_DK, stroke_width=1.5)
        m.set_points_smoothly([rig.p(a * 0.64, SHOULDER - 0.02),
                               rig.p(a * 0.64 + 0.03, SHOULDER + 0.20),
                               rig.p(a * 0.64 - 0.02, SHOULDER + 0.40)])
        g.add(m)
    return g


def sword(rig, hand, ang=0.0):
    """Pommel below the fist, guard above it, blade beyond. The first
    pass floated the blade next to an open hand with the hilt nowhere.

    `ang` rotates the whole weapon about the fist, 0 being straight up
    and positive swinging the tip out to the figure's right. It is a
    rotation and not a flag because the slump has to LOWER the sword,
    and a boolean can only cut to it — worse, with the blade upright the
    slump's own forearm ran straight down the blade and the sword read
    as floating with no arm attached."""
    g = VGroup()
    hx, hy = hand
    c, s = np.cos(ang), np.sin(ang)

    def q(du, dv):
        """A point du right / dv down of the fist, swung by `ang`."""
        return (hx + du * c - dv * s, hy + du * s + dv * c)

    tip = -1.62
    g.add(disc(rig, *q(0, 0.22), 0.075, 0.070, IRON_LT, IRON_DK, 1.6))
    g.add(taper(rig, [q(0, 0.20), q(0, -0.16)], 0.095, 0.095,
                LEATH_DK, "#33230F", 1.6))
    g.add(shape(rig, [q(-0.26, -0.16), q(0.26, -0.16),
                      q(0.23, -0.27), q(-0.23, -0.27)],
                IRON_LT, IRON_DK, 1.8, smooth=False))
    g.add(shape(rig, [q(-0.085, -0.27), q(0.085, -0.27),
                      q(0.07, tip + 0.20), q(0, tip), q(-0.07, tip + 0.20)],
                STEEL, IRON_DK, 2.0, smooth=False))
    # the fist closes over the grip, so it is drawn after the hilt
    g.add(disc(rig, *q(0, 0.04), 0.115, 0.105, SKIN, SKIN_DK, 1.8))
    return g


def sword_tip(hand, ang=0.0):
    """Where the point of the blade ends up, in head units."""
    return (hand[0] + 1.62 * np.sin(ang), hand[1] - 1.62 * np.cos(ang))


def shield(rig, cx, cy, r=0.46):
    g = VGroup(disc(rig, cx, cy, r, r, WOOD, LEATH_DK, 2.6))
    g.add(disc(rig, cx, cy, r * 0.74, r * 0.74, "#8C6440", LEATH_DK, 1.6))
    g.add(disc(rig, cx, cy, r * 0.22, r * 0.22, IRON_LT, IRON_DK, 1.8))
    return g


def dragonborn(head, cx, top, pose="idle", with_sword=False, with_shield=True):
    """`pose` is a POSES key or a blended dict from lerp_pose()."""
    rig = Rig(head, cx, top)
    p = POSES[pose] if isinstance(pose, str) else pose
    g = VGroup()
    if with_shield:
        g.add(shield(rig, -0.80, CHEST + 0.16, 0.40))
    g.add(body(rig, p))
    g.add(helmet(rig, p["tilt"], p["hdrop"]))
    if with_sword:
        g.add(sword(rig, p["hr"], p["sang"]))
    return g


# ------------------------------------------------------------------ plates
def header(a, b):
    g = VGroup()
    t = Text(a, fill_color=ACCENT, font_size=30, weight=BOLD)
    t.move_to(np.array([0, 3.74, 0]))
    s = Text(b, fill_color=LABEL, font_size=19)
    if s.get_width() > 3.4:
        s.set_width(3.4)
    s.move_to(np.array([0, 3.30, 0]))
    g.add(t, s)
    return g


class _B(Scene):
    def bg(self):
        self.camera.background_rgba = list(color_to_rgba(PAPER, 1.0))
        self.camera.frame.set_height(9.0)


class DbProportions(_B):
    def construct(self):
        self.bg()
        self.add(header("1 — FIVE HEADS",
                        "chibi kills the pose; realistic kills the face"))
        head, cx, top = 1.08, 0.30, 2.60
        rig = Rig(head, cx, top)
        for i in range(6):
            y = top - i * head
            ln = VMobject(stroke_color=GUIDE, stroke_width=1.6)
            ln.set_points_as_corners([np.array([-2.15, y, 0]),
                                      np.array([1.95, y, 0])])
            self.add(ln)
            lab = Text(str(i), fill_color=GUIDE, font_size=19, weight=BOLD)
            lab.move_to(np.array([-2.34, y, 0]))
            self.add(lab)
        self.add(dragonborn(head, cx, top, "idle", with_shield=False)
                 .set_opacity(0.30))
        p = POSES["idle"]
        arm = VGroup()
        for k, f in (("l", -1), ("r", 1)):
            for a, b in (((f * SH_HALF * 0.86, SHOULDER + 0.10), p["e" + k]),
                         (p["e" + k], p["h" + k]),
                         ((f * HIP_HALF * 0.7, HIP), p["k" + k]),
                         (p["k" + k], p["f" + k])):
                m = VMobject(stroke_color=ACCENT, stroke_width=4.0)
                m.set_points_as_corners([rig.p(*a), rig.p(*b)])
                arm.add(m)
        sp = VMobject(stroke_color=ACCENT, stroke_width=4.0)
        sp.set_points_as_corners([rig.p(0, NECK), rig.p(0, HIP)])
        arm.add(sp)
        for j in (p["el"], p["er"], p["hl"], p["hr"], p["kl"], p["kr"],
                  (0, NECK), (0, HIP), (-SH_HALF * 0.86, SHOULDER + 0.10),
                  (SH_HALF * 0.86, SHOULDER + 0.10)):
            arm.add(Dot(rig.p(*j), radius=0.045, fill_color="#D4703F"))
        self.add(arm)
        note = Text("head  ·  shoulders 1.26  ·  waist 2.45  ·  knee 3.76  ·  foot 5.0",
                    fill_color=LABEL, font_size=16)
        if note.get_width() > 3.4:
            note.set_width(3.4)
        note.move_to(np.array([0, -3.40, 0]))
        self.add(note)
        self.wait(0.1)


class DbCharacter(_B):
    def construct(self):
        self.bg()
        self.add(header("2 — THE DRAGONBORN",
                        "horned iron helm, fur mantle, sword — read as a shape"))
        self.add(dragonborn(1.10, 0.0, 2.55, "idle", with_sword=True))
        self.wait(0.1)


class DbPoses(_B):
    def construct(self):
        self.bg()
        self.add(header("3 — IT IS A RIG",
                        "same character, three poses, one dict each"))
        for cx, name, lab, sw in ((-1.55, "idle", "IDLE", False),
                                  (0.0, "point", "A DRAGON!", True),
                                  (1.55, "shrug", "...sure.", False)):
            self.add(dragonborn(0.60, cx, 1.95, name,
                                with_sword=sw, with_shield=False))
            t = Text(lab, fill_color=LABEL, font_size=18, weight=BOLD)
            if t.get_width() > 1.4:
                t.set_width(1.4)
            t.move_to(np.array([cx, -1.65, 0]))
            self.add(t)
        note = Text("add a pose by adding joint positions — nothing is redrawn",
                    fill_color="#6F7E89", font_size=17)
        if note.get_width() > 3.4:
            note.set_width(3.4)
        note.move_to(np.array([0, -3.40, 0]))
        self.add(note)
        self.wait(0.1)
