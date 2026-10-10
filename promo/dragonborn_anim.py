"""
dragonborn_anim — the rig, moving. 20.800000s.

    BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" \
      manimgl dragonborn_anim.py DragonbornAnim -w -r 1080x1920

52 beats = 13 bars = 20.800000s at 150 BPM. Silent.

WHAT THIS IS. A motion test for the rig in dragonborn.py, shaped as a
postable sketch rather than a bare turntable, because the only way to
find out whether a pose reads is to watch it arrive at speed.

HOW IT MOVES. Nothing is tweened in pixel space. Every frame the figure
is rebuilt from a blended pose — `lerp_pose` interpolates the joint
coordinates, so the limbs swing to their new positions the way a puppet
would. A cross-fade between two drawings would read as a dissolve; this
reads as movement.

  pose_at(beat)  walks SHOTS, finds the shot in force, and if its move
                 is still running, blends from the previous pose through
                 that shot's easing curve.

  "snap"         back-out: overshoots the target by ~10% and settles.
                 This is the whole reason the gestures land — a linear
                 arm raise looks like a lift, an overshooting one looks
                 like a gesture.
  "sag"          slow-in, for the deflate. Gravity, not a decision.

  bob / sway     movement the body does on its own: one dip per footfall
                 while marching, a slow breath otherwise. Both are
                 exactly zero at the march's in and out beats, so the
                 handover cannot pop.

THE FACE PROBLEM. The helmet has no face, so none of the comedy can come
from one. It is carried by the poses and by a dialogue box, which is how
the game does it anyway.

WHY A MARCH AND NOT A WALK. Front-on, a walk cycle has nowhere to swing
the legs. The march lifts the knee toward the camera and lets the thigh
foreshorten, which is what a raised knee really does from the front.

VERIFIED AT IMPORT
    every shot starts on a 1/4-beat and the shots are strictly ordered
    no move runs past the start of the next shot, or past the end
    every dialogue line opens only after its move has finished settling
    the raised sword is checked to stay inside the frame
    the box, the text and the end card are checked against the safe box
    the figure's boots are checked to clear the top of the box
    the easings are checked to run 0 -> 1, and the snap to overshoot

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    camera.frame IS in scene.mobjects — never hand it to FadeOut
    a group carrying an updater must be self.add()ed and never handed to
    an animation — AnimationGroup rebuilds a fresh VGroup of its children
    and leaves the updater driving the copy that was thrown away
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from manimlib import *
import numpy as np

import dragonborn as DB
from dragonborn import (ACCENT, IRON, IRON_DK, PAPER, POSES, TOTAL as HEADS,
                        dragonborn, lerp_pose)

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 48                       # beats — 12 bars

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
PARCH  = "#E8DFC9"
PANEL  = "#0B1118"

FRAME_H = 9.0
FRAME_W = FRAME_H * 1080 / 1920
SAFE_X, SAFE_BOT = 1.68, -2.58
FRAME_TOP = FRAME_H / 2

# the limbs are resampled 60 times a second here, not once for a plate
DB.set_detail(22)

# ------------------------------------------------------------------ layout
HEAD   = 0.82                    # one head height, in frame units
FIG_CX = 0.0
FEET_Y = -1.32
TOP_Y  = FEET_Y + HEADS * HEAD   # crown of the skull
assert abs(TOP_Y - 2.78) < 1e-9

# the sword's tip, with the arm overhead, is the highest thing in the film
_sw = POSES["sword_up"]
SWORD_TIP_Y = TOP_Y - DB.sword_tip(_sw["hr"], _sw["sang"])[1] * HEAD
assert SWORD_TIP_Y < FRAME_TOP - 0.30, SWORD_TIP_Y

# and the blade must never swing into the action rail, at any angle the
# film passes through — the slump lowers it out to the right
_tips = [DB.sword_tip(p["hr"], p["sang"]) for p in POSES.values()]
assert max(FIG_CX + t[0] * HEAD for t in _tips) < SAFE_X, max(_tips)
assert min(FIG_CX + t[0] * HEAD for t in _tips) > -FRAME_W / 2 + 0.16

# nothing the figure does may reach into the action rail on the right
_far_x = max(abs(p[k][0]) + 0.26 for p in POSES.values() for k in ("hl", "hr"))
assert FIG_CX + _far_x * HEAD < SAFE_X, _far_x * HEAD

SERIES = "SKYRIM, HONESTLY"
LABEL_X, LABEL_Y, LABEL_W = -1.25, 3.95, 2.20
assert LABEL_Y + 0.16 < FRAME_TOP
# the raised blade and the series tag must not share any x
_blade_x = FIG_CX + (_sw["hr"][0] + 0.26) * HEAD
assert LABEL_X + LABEL_W / 2 < FIG_CX + (_sw["hr"][0] - 0.26) * HEAD, _blade_x

BOX_CX, BOX_W = 0.0, 3.36
BOX_TOP, BOX_H = -1.44, 0.82
BOX_Y = BOX_TOP - BOX_H / 2
TXT_W = BOX_W - 0.38
assert BOX_CX + BOX_W / 2 <= SAFE_X                 # clear of the action rail
assert BOX_CX - BOX_W / 2 >= -FRAME_W / 2 + 0.16
assert BOX_Y - BOX_H / 2 >= SAFE_BOT                # clear of the caption block
assert BOX_TOP <= FEET_Y - 0.08                     # clear of the boots

EYE_Y, HANDLE_Y, EYE_W = -1.68, -2.22, 0.95
assert EYE_Y + 0.26 < FEET_Y
assert HANDLE_Y - 0.14 >= SAFE_BOT

# ------------------------------------------------------------------ easing
def ease3(t):
    """Cubic smoothstep, not manimlib's `smooth`. The house curve runs a
    sigmoid steep enough to peak at 1.875x the average speed, which is
    fine for a number sliding across a frame and too brisk for a limb;
    this peaks at 1.5x and leaves headroom for the snap's overshoot."""
    return t * t * (3.0 - 2.0 * t)


def snap(t):
    """Overshoots the target by ~9% late in the move and settles back.

    The textbook back-out curve was tried first and thrown out: it leaves
    the rest position at 4.7x the average speed, which on a 0.75-beat
    sword raise moved the blade tip 120px in a single frame — it read as
    a teleport, not a whip. This peaks at 1.7x instead, and starts from
    a standstill, so the limb accelerates into the move."""
    return ease3(t) + 0.12 * np.sin(np.pi * t ** 5)


def sag(t):
    """Slow to start, then it goes. Deflating, not deciding."""
    return ease3(t ** 1.6)


EASES = {"snap": snap, "ease": ease3, "sag": sag}

_ts = np.linspace(0, 1, 2001)
for _n, _f in EASES.items():
    _y = np.array([_f(t) for t in _ts])
    assert abs(_y[0]) < 1e-9 and abs(_y[-1] - 1.0) < 1e-9, _n
    # nothing may leave or arrive at a lurch: cap the peak speed at 2x
    # the average, or a limb jumps a visible distance between frames
    assert (np.diff(_y) * 2000).max() < 2.0, (_n, (np.diff(_y) * 2000).max())
assert np.array([snap(t) for t in _ts]).max() > 1.05   # it really overshoots
for _n in ("ease", "sag"):
    assert np.all(np.diff([EASES[_n](t) for t in _ts]) >= 0), _n

# ------------------------------------------------------------------ timeline
# He does not fade up. He walks on from the left, which puts a whole
# character on screen in frame 1 and spends the entrance on movement
# instead of on an empty plate — the first second is the only one most
# of these get watched for.
ENTER_X = -1.30
MARCH_IN, MARCH_OUT = 0.5, 8.5

#        beat   pose        move   easing
SHOTS = [(0.00, "idle",     0.00, "ease"),
         (0.50, "march_l",  0.50, "snap"),
         (1.50, "march_r",  0.50, "snap"),
         (2.50, "march_l",  0.50, "snap"),
         (3.50, "march_r",  0.50, "snap"),
         (4.50, "march_l",  0.50, "snap"),
         (5.50, "march_r",  0.50, "snap"),
         (6.50, "march_l",  0.50, "snap"),
         (7.50, "march_r",  0.50, "snap"),
         (8.50, "idle",     1.00, "ease"),
         (10.00, "sword_up", 0.75, "snap"),
         (18.00, "point",   0.50, "snap"),
         (26.00, "shrug",   0.75, "snap"),
         (34.00, "slump",   3.00, "sag"),
         (40.00, "idle",    2.00, "ease")]

#         in     out    line
LINES = [(11.50, 17.50, "I AM THE DRAGONBORN."),
         (19.00, 25.00, "CHOSEN BY THE GODS."),
         (27.50, 33.50, "I carry 1,847 cheese wheels.")]

END_CARD = 42.0
FADE = 0.5                       # beats, for every text fade

STARTS = [s[0] for s in SHOTS]
assert STARTS == sorted(set(STARTS))
assert all(abs(b * 4 - round(b * 4)) < 1e-9 for b in STARTS)
assert all(s[1] in POSES for s in SHOTS)
assert all(s[3] in EASES for s in SHOTS)
for _i, (_b, _p, _m, _e) in enumerate(SHOTS):
    _nxt = STARTS[_i + 1] if _i + 1 < len(SHOTS) else TOTAL
    assert _b + _m <= _nxt + 1e-9, (_p, _b, _m)     # no move outruns its shot
assert MARCH_IN in STARTS and MARCH_OUT in STARTS
assert float(MARCH_OUT - MARCH_IN).is_integer()     # whole footfalls only

for _a, _b, _s in LINES:
    _i = max(i for i, b in enumerate(STARTS) if b <= _a)
    # a line may only open once its gesture has finished settling
    assert _a >= SHOTS[_i][0] + SHOTS[_i][2] + FADE, _s
    assert _b + FADE <= TOTAL and _b > _a + 2 * FADE
assert END_CARD >= SHOTS[-1][0] + SHOTS[-1][2]
assert END_CARD + FADE < TOTAL
assert LINES[-1][1] + FADE <= END_CARD              # box gone before the eye


def pose_at(beat):
    i = max(k for k, b in enumerate(STARTS) if b <= beat)
    start, name, mv, ez = SHOTS[i]
    cur = POSES[name]
    if i == 0 or mv <= 0 or beat >= start + mv:
        return cur
    return lerp_pose(POSES[SHOTS[i - 1][1]], cur,
                     EASES[ez]((beat - start) / mv))


def bob(beat):
    """One dip per footfall while marching, a slow breath otherwise.
    Both terms vanish at MARCH_IN and MARCH_OUT, so nothing pops."""
    if MARCH_IN <= beat < MARCH_OUT:
        return 0.040 * abs(np.sin(np.pi * (beat - MARCH_IN)))
    return 0.014 * np.sin(2 * np.pi * (beat - MARCH_IN) / 8.0)


def sway(beat):
    """Weight shifts onto whichever leg is still on the ground."""
    if not MARCH_IN <= beat < MARCH_OUT:
        return 0.0
    step = int(beat - MARCH_IN)
    return 0.045 * np.sin(np.pi * (beat - MARCH_IN)) * (1 if step % 2 else -1)


assert abs(bob(MARCH_IN)) < 1e-9 and abs(bob(MARCH_OUT)) < 1e-9
assert abs(bob(MARCH_IN - 1e-9)) < 1e-9 and abs(sway(MARCH_IN)) < 1e-9



def enter(beat):
    """The walk-on. Linear, because a walk covers ground at one speed —
    an eased one looks like the floor is on casters."""
    t = (beat - MARCH_IN) / (MARCH_OUT - MARCH_IN)
    return ENTER_X * (1.0 - min(1.0, max(0.0, t)))


assert abs(sway(MARCH_OUT - 1e-9)) < 1e-6
assert enter(0.0) == ENTER_X and enter(MARCH_IN) == ENTER_X
assert abs(enter(MARCH_OUT)) < 1e-12 and abs(enter(TOTAL)) < 1e-12
_e = [enter(b / 16) for b in range(TOTAL * 16 + 1)]
assert all(y >= x - 1e-12 for x, y in zip(_e, _e[1:]))    # he never backs up
# the walk-on must not put him through the left edge of the frame
assert ENTER_X - 0.90 * HEAD > -FRAME_W / 2

# ------------------------------------------------------------------ the gate
# walk the finished motion frame by frame at the real frame rate and
# measure how far the furthest joint travels between frames. Over about
# a third of a head in one frame and a limb stops reading as a limb and
# starts reading as a cut. The sword raise is the worst offender and sets
# this number; if a shot is ever shortened past what it can carry, the
# build fails here instead of shipping a teleport.
#
# The same loop walks the sword's point. Checking the poses alone was
# not enough and had already let one through: between the shrug and the
# slump the blade rotates down past horizontal, and for about a second
# mid-swing the tip reached further right than at either end of the
# move — 2.00 units out, well inside the action rail. Keyframes are not
# the film. This sweeps every frame.
_FPB = FPS * 60.0 / BPM                             # frames per beat
assert abs(_FPB - round(_FPB)) < 1e-9, _FPB
_prev, _worst, _at = None, 0.0, None
_tipx, _tipx_at, _tipy = -9.0, None, -9.0
for _f in range(int(round(TOTAL * _FPB)) + 1):
    _b = _f / _FPB
    _q = pose_at(_b)
    _v = np.array([_q[j][i] for j in DB.JOINTS for i in (0, 1)])
    if _prev is not None:
        _d = float(np.abs(_v - _prev).max())
        if _d > _worst:
            _worst, _at = _d, _b
    _prev = _v
    _tp = DB.sword_tip(_q["hr"], _q["sang"])
    _x = FIG_CX + enter(_b) + sway(_b) + _tp[0] * HEAD
    if _x > _tipx:
        _tipx, _tipx_at = _x, _b
    _tipy = max(_tipy, TOP_Y - bob(_b) - _tp[1] * HEAD)
assert _worst < 0.30, (_worst, _at)
assert _tipx < SAFE_X, (_tipx, _tipx_at)
assert _tipy < FRAME_TOP - 0.22, _tipy
MAX_STEP, MAX_STEP_AT = _worst, _at
TIP_MAX_X, TIP_MAX_Y = _tipx, _tipy

# ------------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=2 * SAFE_X - 0.15):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def dialog(line):
    """The game's own device: a dark panel with a thin double frame. The
    helmet has no face, so the box is where the sarcasm has to live."""
    pan = Rectangle(width=BOX_W, height=BOX_H, stroke_color=IRON,
                    stroke_width=2.4, fill_color=PANEL, fill_opacity=1.0)
    # the inner frame is filled with the panel colour, not left hollow:
    # the whole box is faded with set_opacity, which sets fill opacity
    # too, and a hollow rect would have bloomed into a default-coloured
    # slab over the text
    inner = Rectangle(width=BOX_W - 0.11, height=BOX_H - 0.11,
                      stroke_color=IRON_DK, stroke_width=1.4,
                      fill_color=PANEL, fill_opacity=1.0)
    t = txt(line, 29, PARCH, bold=False, w=TXT_W)
    g = VGroup(pan, inner, t)
    g.move_to(np.array([BOX_CX, BOX_Y, 0]))
    return g


def observer_eye(color):
    grp = VGroup()
    for sign in (1, -1):
        m = VMobject(color=color, stroke_width=2.2)
        m.set_points_smoothly(
            [np.array([x, sign * 0.9 * np.sin(np.pi * ((x + 1.6) / 3.2)), 0])
             for x in np.linspace(-1.6, 1.6, 20)])
        grp.add(m)
    grp.add(Circle(radius=0.42, stroke_color=color, stroke_width=2.2))
    grp.add(Dot(ORIGIN, radius=0.12, fill_color=color))
    rng = np.random.default_rng(2)
    for _ in range(5):
        s = rng.uniform(0.05, 0.12)
        sq = Square(side_length=s, color=color, stroke_width=1.5)
        sq.move_to([rng.uniform(1.7, 2.4), rng.uniform(-0.6, 0.6), 0])
        sq.set_fill(color, opacity=0.5)
        grp.add(sq)
    return grp


def window(beat, b0, b1):
    """Trapezoid: up over FADE beats, hold, down over FADE beats."""
    if beat <= b0 - FADE or beat >= b1 + FADE:
        return 0.0
    if beat < b0:
        return smooth((beat - b0 + FADE) / FADE)
    if beat <= b1:
        return 1.0
    return smooth(1.0 - (beat - b1) / FADE)


# ------------------------------------------------------------------ scene
class DragonbornAnim(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(PAPER, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0

        # the figure is rebuilt from the clock, so the whole film is one
        # wait and every moving thing is an updater. Nothing is handed to
        # an animation, which is what keeps the updaters attached.
        self._pose_key = None
        self._applied = np.zeros(3)
        self.fig = VGroup()
        self.fig.add_updater(lambda m: self.repose(m))
        self.add(self.fig)

        tag = txt(SERIES, 19, ACCENT, w=LABEL_W)
        tag.move_to(np.array([LABEL_X, LABEL_Y, 0]))
        tag.add_updater(lambda m: m.set_opacity(window(self.beat(), 0.0, TOTAL)))
        self.add(tag)

        for b0, b1, line in LINES:
            d = dialog(line)
            d.add_updater(
                lambda m, b0=b0, b1=b1: m.set_opacity(window(self.beat(), b0, b1)))
            self.add(d)

        eye = observer_eye(WHITE_)
        eye.set_width(EYE_W).move_to(np.array([0, EYE_Y, 0]))
        handle = txt("@observer.collapse", 21, GREY, bold=False)
        handle.move_to(np.array([0, HANDLE_Y, 0]))
        end = VGroup(eye, handle)
        end.add_updater(
            lambda m: m.set_opacity(window(self.beat(), END_CARD, TOTAL)))
        self.add(end)

        self.wait(self.T(TOTAL))

    # ------------------------------------------------------------------
    def T(self, beats):
        f0 = round(self.used * self.B * FPS)
        self.used += beats
        f1 = round(self.used * self.B * FPS)
        return (f1 - f0) / FPS

    def beat(self):
        return self.get_time() / self.B

    def repose(self, holder):
        """Rebuild the figure from the blended pose — but only when the
        pose actually changed. The walk-on, the bob and the sway are a
        shift of what is already there, so the holds (most of the film)
        cost nothing and only the beats of real movement pay a rebuild."""
        beat = self.beat()
        p = pose_at(beat)
        key = (tuple(round(v, 5) for j in DB.JOINTS for v in p[j]),
               tuple(round(p[s], 5) for s in DB.SCALARS))
        if key != self._pose_key:
            self._pose_key = key
            g = dragonborn(HEAD, FIG_CX, TOP_Y, p,
                           with_sword=True, with_shield=False)
            holder.set_submobjects(list(g.submobjects))
            self._applied = np.zeros(3)
        want = np.array([enter(beat) + sway(beat), -bob(beat), 0.0])
        if not np.allclose(want, self._applied, atol=1e-6):
            holder.shift(want - self._applied)
            self._applied = want


# ------------------------------------------------------------------ QA plate
SHEET = [(0.00, "walk on"), (2.75, "march"), (6.75, "march"),
         (10.75, "sword"), (18.50, "point"), (26.75, "shrug"),
         (37.00, "slump"), (43.00, "idle")]


class DbAnimSheet(Scene):
    """Eight beats of the finished motion, side by side.

        xvfb-run -a -s "-screen 0 1600x1200x24" \
          manimgl dragonborn_anim.py DbAnimSheet -s -w -r 1080x1920

    A contact sheet, not a shot: the point is to see every pose the film
    passes through at once, before paying for 1248 frames of render."""

    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(PAPER, 1.0))
        self.camera.frame.set_height(FRAME_H)
        t = txt("THE MOTION, EIGHT BEATS OF IT", 24, ACCENT, w=4.4)
        self.add(t.move_to(np.array([0, 4.00, 0])))
        h = HEAD * 0.46
        for i, (beat, name) in enumerate(SHEET):
            cx = -1.75 + (i % 4) * 1.17
            ty = 2.55 - (i // 4) * 3.45
            g = dragonborn(h, cx, ty, pose_at(beat),
                           with_sword=True, with_shield=False)
            g.shift(np.array([(enter(beat) + sway(beat)) * 0.46,
                              -bob(beat) * 0.46, 0]))
            self.add(g)
            lab = txt(f"{beat:g}  {name}", 15, GREY, bold=False, w=1.05)
            self.add(lab.move_to(np.array([cx, ty - 5.3 * h - 0.22, 0])))
        self.wait(0.1)
