"""
name_equation — your name, turned into a curve. 38.4s.

    BPM=150 manimgl name_equation.py NameEquation -w -r 1080x1920

96 beats = 24 bars = 38.400s at 150 BPM.

FOUR SIGNPOSTED STAGES, in the order the viewer asked for them:

    1  TOKENIZE    the name is cut into pieces
    2  VECTORS     every piece becomes a number        a = 1 … z = 26
    3  SPACE X Y   every number becomes a spinning wheel in the plane
    4  EQUATION    the wheels ARE a parametric equation, and its tip draws
                   a closed curve that belongs to that name and no other

THE MAPPING IS A STATED RULE, NOT A CLAIM ABOUT ANY MODEL.
Stages 1 and 2 are true of every language model: text is split into tokens and
the tokens become numbers before anything else happens. Stage 3 onward is OUR
rule, and the video says so on screen — letter k gets a wheel of radius 1/k
turning at a speed equal to the letter's value:

    x(t) = Σ (1/k) · cos(vₖ t)          v = the letters, a=1 … z=26
    y(t) = Σ (1/k) · sin(vₖ t)          r = 1, ½, ⅓, ¼ …

Every vₖ is a whole number, so both sums have period 2π and the curve ALWAYS
closes — asserted below for every name in the file. Different names give
different curves, including anagrams (order changes which radius each speed
gets), asserted below across a list of names.

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
    run_time ALWAYS via self.T(beats)
    Scene.run() is manimlib's OWN entry point — never name a method run()
    ShowCreation(make_thing()) leaves an orphan copy in the scene
    an updater that hard-codes opacity fights every .animate.set_opacity() —
    drive opacity from a ValueTracker the updater reads instead
"""
import os

from manimlib import *
import numpy as np

BPM = float(os.environ.get("BPM", 150.0))
FPS = 60
TOTAL = 96

END_OPEN = 4
END_CARD1, END_TOK = 8, 20
END_CARD2, END_VEC = 24, 38
END_CARD3, END_SPACE = 42, 56
END_CARD4, END_EQN = 60, 80
END_TAKE = 86

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
FAINT  = "#2A2F3A"
GOLD   = "#EBCB8B"
COOL   = "#5E81AC"

FRAME_H = 9.0
CAP_Y   = 1.78
NOTE_Y  = -1.62
LOW_Y   = -2.08          # note line while the drawing owns the middle
LINE_Y  = -2.05

CEN  = np.array([0.0, -0.45, 0.0])       # where the wheels live
CEN2 = CEN + np.array([0.0, 0.55, 0.0])  # where the finished curve settles
RAD  = 1.22                              # on-screen radius of the whole chain
NPTS = 1500

NAME = "MAYA"
MONTAGE = ["ALEX", "SARA"]

# ------------------------------------------------------------ the rule
def vals(name):
    """a = 1 … z = 26.  The only place a letter becomes a number."""
    return [ord(c) - 96 for c in name.lower() if c.isalpha()]


def rads(n):
    """Wheel k is 1/k as big as the first one."""
    return [1.0 / (k + 1) for k in range(n)]


def scale_for(name):
    return RAD / sum(rads(len(vals(name))))


def chain_at(name, t, center=CEN):
    """Every joint of the wheel chain at time t, tail first."""
    v, r, s = vals(name), rads(len(vals(name))), scale_for(name)
    p = np.array(center, dtype=float)
    out = [p.copy()]
    for rk, vk in zip(r, v):
        p = p + s * rk * np.array([np.cos(vk * t), np.sin(vk * t), 0.0])
        out.append(p.copy())
    return out


def path_pts(name, t0=0.0, t1=2 * np.pi, n=NPTS, center=CEN):
    v, r, s = vals(name), rads(len(vals(name))), scale_for(name)
    t = np.linspace(t0, t1, max(int(n), 2))
    x = sum(s * rk * np.cos(vk * t) for rk, vk in zip(r, v)) + center[0]
    y = sum(s * rk * np.sin(vk * t) for rk, vk in zip(r, v)) + center[1]
    return np.stack([x, y, np.zeros_like(x)], axis=1)


# ------------------------------------------------------------ verified here
_CHECK = [NAME] + MONTAGE + ["RAAED", "NOAH", "ZARA", "OMAR", "LUNA", "AMYA",
                             "AYA", "EMMA", "KAI", "SOFIA", "YUSUF", "AISHA"]

assert vals("maya") == [13, 1, 25, 1], vals("maya")
assert vals("a") == [1] and vals("z") == [26]

for _nm in _CHECK:                      # every curve closes: all speeds whole
    _p = path_pts(_nm, n=3000)
    assert np.allclose(_p[0], _p[-1], atol=1e-9), _nm

_seen = {}                              # distinct names -> distinct curves
for _nm in _CHECK:
    _k = np.round(path_pts(_nm, n=4000), 6).tobytes()
    assert _k not in _seen, (_nm, _seen[_k])
    _seen[_k] = _nm

assert np.abs(path_pts("MAYA") - path_pts("AMYA")).max() > 0.1   # anagrams differ

VAL_STR = ", ".join(str(v) for v in vals(NAME))
RAD_STR = ", ".join(["1", "½", "⅓", "¼", "⅕", "⅙"][:len(vals(NAME))])


# ------------------------------------------------------------ drawing
def txt(s, size=27, color=WHITE_, bold=True, w=4.4):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


def chip(s, color=WHITE_, size=26, pad=0.17, h=0.62):
    t = txt(s, size, color, bold=True, w=2.4)
    box = Rectangle(width=t.get_width() + pad * 2, height=h, stroke_width=2.2)
    box.set_stroke(color, opacity=0.9)
    box.set_fill(color, opacity=0.10)
    return VGroup(box, t.move_to(box.get_center()))


def chip_row(tokens, color=WHITE_, size=26, buff=0.13, y=0.55, maxw=4.5):
    g = VGroup(*[chip(t, color, size) for t in tokens]).arrange(RIGHT, buff=buff)
    if g.get_width() > maxw:
        g.set_width(maxw)
    return g.move_to(np.array([0, y, 0]))


def curve_mob(name, center=CEN, color=GOLD, w=3.0, n=NPTS):
    m = VMobject(stroke_color=color, stroke_width=w)
    m.set_points_as_corners(path_pts(name, n=n, center=center))
    return m


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


class NameEquation(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)
        self.B = 60.0 / BPM
        self.used = 0.0
        self.note = None
        self.stage = []
        self.marker = None

        self.tt = ValueTracker(0.0)     # time along the curve
        self.dim = ValueTracker(1.0)    # how visible the wheels are

        self.open_card()
        self.section_card(1, "TOKENIZE", END_CARD1)
        self.part1_tokenize()
        self.section_card(2, "VECTORS", END_CARD2)
        self.part2_vectors()
        self.section_card(3, "SPACE  X Y", END_CARD3)
        self.part3_space()
        self.section_card(4, "EQUATION", END_CARD4, dim_drawing=True)
        self.part4_equation()
        self.takeaway()
        self.signature()

    # ------------------------------------------------------------------
    def T(self, beats):
        f0 = round(self.used * self.B * FPS)
        self.used += beats
        f1 = round(self.used * self.B * FPS)
        return (f1 - f0) / FPS

    def pad_to(self, target):
        rem = target - self.used
        if rem < -0.01:
            raise ValueError(f"overruns by {-rem:.2f} beats — trim it")
        if rem > 0.01:
            self.wait(self.T(rem))

    def say(self, s, beats=2, color=WHITE_, size=24, y=NOTE_Y):
        new = txt(s, size, color, bold=False, w=4.5)
        new.move_to(np.array([0, y, 0]))
        if self.note is None:
            self.note = new
            self.play(FadeIn(new), run_time=self.T(beats))
        else:
            self.play(FadeOut(self.note, shift=0.10 * UP),
                      FadeIn(new, shift=0.10 * UP), run_time=self.T(beats))
            self.note = new

    def clear_stage(self, beats=1):
        keep = self.stage + ([self.note] if self.note else [])
        if keep:
            for m in keep:
                m.clear_updaters()
            self.play(*[FadeOut(m) for m in keep], run_time=self.T(beats))
            self.stage, self.note = [], None
        else:
            self.wait(self.T(beats))

    # ------------------------------------------------------------------
    def open_card(self):
        big = VGroup(txt("YOUR NAME", 54, WHITE_, w=4.6),
                     txt("IS AN EQUATION", 44, GOLD, w=4.6)).arrange(DOWN, buff=0.24)
        big.move_to(np.array([0, 0.85, 0]))
        sub = txt("follower #1000 gets theirs", 24, GREY, bold=False)
        sub.move_to(np.array([0, -0.25, 0]))
        self.add(big, sub)
        self.wait(self.T(3))          # the hook owns 1.2s — it is the whole scroll-stop
        self.title = txt("YOUR NAME IS AN EQUATION", 20, GREY, bold=False, w=4.0)
        self.title.move_to(np.array([0, 3.30, 0]))
        self.play(FadeOut(big), FadeOut(sub), FadeIn(self.title),
                  run_time=self.T(1))
        self.pad_to(END_OPEN)

    def section_card(self, n, name, end, dim_drawing=False):
        self.clear_stage(1)
        big = VGroup(txt(f"{n}", 74, GOLD),
                     txt(name, 34, WHITE_, w=4.4)).arrange(DOWN, buff=0.30)
        big.move_to(np.array([0, 0.35, 0]))
        anims = [FadeIn(big, scale=1.12)]
        if dim_drawing:
            anims.append(self.dim.animate.set_value(0.10))
        self.play(*anims, run_time=self.T(1), rate_func=rush_from)
        new = txt(f"{n} / 4   {name}", 20, GOLD, bold=False, w=3.8)
        new.move_to(np.array([0, 2.62, 0]))
        self.pad_to(end - 1)
        if self.marker is None:
            self.marker = new
            self.play(FadeOut(big), FadeIn(new), run_time=self.T(1))
        else:
            self.play(FadeOut(big), Transform(self.marker, new), run_time=self.T(1))

    # ==================================================================
    # 1 — TOKENIZE.  The name comes apart before anything else happens.
    # ==================================================================
    def part1_tokenize(self):
        head = txt("give it a name", 26, WHITE_, w=4.4)
        head.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(head), run_time=self.T(1))
        self.stage.append(head)

        word = txt(NAME, 62, WHITE_, w=4.2)
        word.move_to(np.array([0, 0.62, 0]))
        self.play(FadeIn(word, scale=1.10), run_time=self.T(2), rate_func=rush_from)
        self.stage.append(word)
        self.say("a model never sees the word", 2)

        row = chip_row(list(NAME), WHITE_, 30, y=0.62)
        self.play(Transform(word, row), run_time=self.T(2))
        self.say("it cuts it into tokens first", 2, GOLD)
        self.say("a short name — one letter, one token", 2)
        self.pad_to(END_TOK)

    # ==================================================================
    # 2 — VECTORS.  Letters become numbers.  True of every model, this part.
    # ==================================================================
    def part2_vectors(self):
        rule = txt("a = 1     b = 2     …     z = 26", 24, GOLD, bold=False, w=4.5)
        rule.move_to(np.array([0, CAP_Y, 0]))
        self.play(FadeIn(rule), run_time=self.T(2))
        self.stage.append(rule)

        row = chip_row(list(NAME), WHITE_, 30, y=0.72)
        self.play(FadeIn(row), run_time=self.T(1))
        self.stage.append(row)

        nums = VGroup()
        for c, ch in zip(vals(NAME), row):
            n = txt(str(c), 32, GOLD)
            n.move_to(np.array([ch.get_center()[0], -0.08, 0]))
            nums.add(n)
        self.play(LaggedStart(*[FadeIn(n, shift=0.14 * DOWN) for n in nums],
                              lag_ratio=0.28), run_time=self.T(2))
        self.stage.append(nums)
        self.say("every token is just a number", 2)

        vec = txt(f"[ {VAL_STR} ]", 36, GOLD, w=4.3)
        vec.move_to(np.array([0, -0.92, 0]))
        self.play(FadeIn(vec, scale=1.10), run_time=self.T(2), rate_func=rush_from)
        self.stage.append(vec)
        self.say("this is all a model ever holds", 2)
        self.say("now watch what the numbers can do", 2, GOLD)
        self.pad_to(END_VEC)

    # ==================================================================
    # 3 — SPACE X Y.  Each number becomes a wheel, and wheels have a tip.
    # ==================================================================
    def part3_space(self):
        ax = VGroup(
            Line(np.array([-2.15, CEN[1], 0]), np.array([2.15, CEN[1], 0]),
                 stroke_color=FAINT, stroke_width=2.4),
            Line(np.array([0, CEN[1] - 1.70, 0]), np.array([0, CEN[1] + 1.35, 0]),
                 stroke_color=FAINT, stroke_width=2.4))
        xl = txt("x", 20, GREY, bold=False).move_to(
            np.array([2.02, CEN[1] + 0.26, 0]))
        yl = txt("y", 20, GREY, bold=False).move_to(
            np.array([0.26, CEN[1] + 1.24, 0]))
        self.play(ShowCreation(ax), FadeIn(xl), FadeIn(yl), run_time=self.T(1))
        self.stage += [ax, xl, yl]
        self.say("drop the numbers into x-y space", 2, y=LOW_Y)

        self.chain = VGroup(*self.build_chain(0.0, 1.0))
        self.chain.add_updater(
            lambda m: m.become(VGroup(*self.build_chain(self.tt.get_value(),
                                                        self.dim.get_value()))))
        self.trail = VMobject(stroke_color=GOLD, stroke_width=3.2)
        self.trail.add_updater(lambda m: self.redraw_trail(m))
        self.add(self.trail, self.chain)
        self.play(FadeIn(self.chain), run_time=self.T(2))

        self.say("each number is a wheel — and the number is its SPEED",
                 2, GOLD, size=22, y=LOW_Y)
        self.play(self.tt.animate.set_value(0.55),
                  run_time=self.T(3), rate_func=linear)
        self.say("four numbers, one moving point", 2, y=LOW_Y)
        self.pad_to(END_SPACE)

    def build_chain(self, t, dim):
        pts = chain_at(NAME, t)
        r, s = rads(len(pts) - 1), scale_for(NAME)
        g = VGroup()
        for i in range(len(pts) - 1):
            ring = Circle(radius=s * r[i], stroke_color=COOL, stroke_width=1.6)
            ring.move_to(pts[i]).set_stroke(opacity=0.35 * dim)
            spoke = Line(pts[i], pts[i + 1], stroke_color=WHITE_, stroke_width=2.6)
            spoke.set_stroke(opacity=0.85 * dim)
            g.add(ring, spoke)
            g.add(Dot(pts[i], radius=0.035,
                      fill_color=WHITE_).set_opacity(0.8 * dim))
        g.add(Dot(pts[-1], radius=0.085, fill_color=GOLD).set_opacity(dim))
        return g

    def redraw_trail(self, m):
        t = self.tt.get_value()
        # the trail reads self.dim too — otherwise the section-4 card lands on
        # top of a full-brightness gold arc and the number is unreadable
        m.set_stroke(GOLD, 3.2, opacity=self.dim.get_value())
        if t <= 1e-4:
            p = chain_at(NAME, 0.0)[-1]
            m.set_points_as_corners([p, p])
            return
        n = max(int(NPTS * t / (2 * np.pi)) + 2, 2)
        m.set_points_as_corners(path_pts(NAME, 0.0, t, n))

    # ==================================================================
    # 4 — EQUATION.  The wheels ARE the equation.  Let it finish the lap.
    # ==================================================================
    def part4_equation(self):
        eq = VGroup(
            txt("x(t) = Σ rₖ · cos(vₖ t)", 25, WHITE_, w=4.4),
            txt("y(t) = Σ rₖ · sin(vₖ t)", 25, WHITE_, w=4.4))
        eq[0].move_to(np.array([0, 2.15, 0]))
        eq[1].move_to(np.array([0, 1.74, 0]))
        key = txt(f"v = {VAL_STR}      r = {RAD_STR}", 19, GOLD, bold=False, w=4.5)
        key.move_to(np.array([0, 1.30, 0]))
        self.play(FadeIn(eq), FadeIn(key),
                  self.dim.animate.set_value(1.0), run_time=self.T(2))

        self.play(self.tt.animate.set_value(2 * np.pi),
                  run_time=self.T(8), rate_func=linear)

        self.chain.clear_updaters()
        self.trail.clear_updaters()
        final = curve_mob(NAME, CEN2, GOLD, 3.4)
        self.play(FadeOut(self.chain), FadeOut(eq), FadeOut(key),
                  Transform(self.trail, final), run_time=self.T(1.5))

        label = txt(NAME, 40, GOLD, w=4.2)
        label.move_to(np.array([0, -1.72, 0]))
        self.play(FadeIn(label, shift=0.12 * UP), run_time=self.T(1))
        tag = txt("one name. one curve.", 24, WHITE_, bold=False, w=4.4)
        tag.move_to(np.array([0, -2.18, 0]))
        self.play(FadeIn(tag), run_time=self.T(1.5))
        self.stage += [self.trail, label, tag]

        for other in MONTAGE:
            # morph, then HOLD. Without the hold each name is only fully formed
            # on the frame the transform ends and is immediately morphed away.
            nxt = curve_mob(other, CEN2, GOLD, 3.4)
            nl = txt(other, 40, GOLD, w=4.2).move_to(label.get_center())
            self.play(Transform(self.trail, nxt), Transform(label, nl),
                      run_time=self.T(1.5))
            self.wait(self.T(1.5))
        self.pad_to(END_EQN)

    # ------------------------------------------------------------------
    def takeaway(self):
        self.clear_stage(1)
        a = txt("FOLLOWER #1000", 44, GOLD, w=4.5)
        a.move_to(np.array([0, 0.80, 0]))
        self.play(FadeIn(a, scale=1.12), run_time=self.T(2), rate_func=rush_from)
        b = txt("gets their name drawn like this", 25, WHITE_, bold=False, w=4.5)
        b.move_to(np.array([0, 0.05, 0]))
        self.play(FadeIn(b), run_time=self.T(1.5))
        c = txt("comment your name", 27, GOLD, w=4.4)
        c.move_to(np.array([0, -0.72, 0]))
        self.play(FadeIn(c, shift=0.10 * UP), run_time=self.T(0.5))
        self.pad_to(END_TAKE - 1)
        self.play(FadeOut(a), FadeOut(b), FadeOut(c), FadeOut(self.title),
                  FadeOut(self.marker), run_time=self.T(1))

    def signature(self):
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
