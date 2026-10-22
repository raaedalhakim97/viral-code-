from manimlib import *
import numpy as np

# ---- manimgl 1.7.2 compatibility shim (added for rendering) ---------------
# In 1.7.2, color= is silently ignored by Text / Dot / Circle / Rectangle and
# camera.background_color is not read. These wrappers route color= to the
# argument each class actually honours; nothing else in the scene changes.
_Text, _Dot, _Circle, _Rectangle = Text, Dot, Circle, Rectangle


def Text(*a, color=None, **k):
    if color is not None:
        k.setdefault("fill_color", color)
    return _Text(*a, **k)


def Dot(*a, color=None, **k):
    if color is not None:
        k.setdefault("fill_color", color)
    return _Dot(*a, **k)


def Circle(*a, color=None, **k):
    if color is not None:
        k.setdefault("stroke_color", color)
    return _Circle(*a, **k)


def Rectangle(*a, color=None, **k):
    if color is not None:
        k.setdefault("stroke_color", color)
    return _Rectangle(*a, **k)
# ---------------------------------------------------------------------------

# ============================================================================
# SMART LOOKUP — "What If Words Could Learn Inside a Curve?"
# 16:9 • ~105s • 9 beats • manimlib (3b1b) build
#
# Render:
#   manimgl smart_lookup.py SmartLookup -w                  # 720p default
#   manimgl smart_lookup.py SmartLookup -w --hd             # 1080p
#   manimgl smart_lookup.py SmartLookup -w -r 3840,2160     # 4K
#
# For 60fps, edit manimlib/default_config.yml frame_rate.
# For the 9:16 vertical cut, re-lay out (a horizontal 4K cut will clip).
# ============================================================================

BG      = "#05070F"
CURVE   = "#2EE6C8"
TARGET  = "#FF8A2B"
VOCAB   = "#3B6FD4"
WEIGHTS = "#9B5CF6"
INK     = "#EAF2FF"
DIM     = "#1B2740"


# ----------------------------------------------------------------------------
# Single source of truth — the Euler wave
# ----------------------------------------------------------------------------
def euler_curve(t):
    r = np.exp(np.cos(t))
    return np.array([r * np.cos(t), r * np.sin(t), np.sin(2 * t)])


def euler_wave(scale=2.0, z_stretch=1.3, color=CURVE, width=4.0, n=300):
    pts = []
    for t in np.linspace(0, TAU, n):
        c = euler_curve(t)
        pts.append(scale * np.array([c[0], c[1], z_stretch * c[2]]))
    m = VMobject(color=color, stroke_width=width)
    m.set_points_smoothly(pts)
    return m


def curve_samples(n_samples=2144, scale=2.0, z_stretch=1.3):
    pts = []
    for t in np.linspace(0, TAU, n_samples, endpoint=False):
        c = euler_curve(t)
        pts.append(scale * np.array([c[0], c[1], z_stretch * c[2]]))
    return pts


# ============================================================================
# MASTER SCENE
# ============================================================================
class SmartLookup(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BG, 1.0))
        frame = self.camera.frame
        frame.set_height(8.5)

        cam = {"phi": 0.0, "theta": 0.0}

        # ------------------------------------------------------------------
        # Transition primitives
        # ------------------------------------------------------------------
        def slam(mob, run_time=0.28):
            mob.save_state()
            mob.scale(1.38).set_opacity(0)
            self.play(mob.animate.restore().set_opacity(1),
                      rate_func=rush_from, run_time=run_time)

        def card_flip(old, new, run_time=0.6):
            half = run_time / 2
            self.play(Rotate(old, PI / 2, axis=UP),
                      run_time=half, rate_func=smooth)
            self.remove(old)
            new.rotate(PI / 2, axis=UP)
            self.add(new)
            self.play(Rotate(new, -PI / 2, axis=UP),
                      run_time=half, rate_func=smooth)

        def zoom_through(target, factor=0.35, run_time=1.0):
            self.play(
                frame.animate
                     .move_to(target.get_center())
                     .set_width(frame.get_width() * factor),
                rate_func=rush_into, run_time=run_time,
            )

        def orbit_cam(d_theta, d_phi, run_time=3.0):
            cam["theta"] += d_theta
            cam["phi"]   += d_phi
            self.play(
                frame.animate.set_euler_angles(phi=cam["phi"], theta=cam["theta"]),
                rate_func=smooth, run_time=run_time,
            )

        def set_cam(phi, theta, run_time=1.5, height=8.5, center=ORIGIN):
            cam["phi"] = phi
            cam["theta"] = theta
            self.play(
                frame.animate.set_euler_angles(phi=phi, theta=theta)
                     .set_height(height).move_to(center),
                rate_func=smooth, run_time=run_time,
            )

        def caption(text, hold=1.0):
            t = Text(text, color=INK, font_size=28, weight=BOLD).fix_in_frame()
            t.move_to([0, -3.5, 0])
            self.play(FadeIn(t, shift=0.1 * UP), run_time=0.3)
            self.wait(hold)
            self.play(FadeOut(t), run_time=0.25)

        # ==================================================================
        # BEAT 1 — HOOK  (0:00–0:06)
        # ==================================================================
        intro_dot = Dot(ORIGIN, radius=0.09, color=CURVE)
        intro_halo = Dot(ORIGIN, radius=0.32, color=CURVE).set_opacity(0.15)
        self.play(FadeIn(intro_dot), FadeIn(intro_halo), run_time=0.6)
        self.play(intro_halo.animate.scale(2.2).set_opacity(0),
                  run_time=0.9, rate_func=rush_from)
        self.wait(0.4)

        hook = Text("THIS IS WATER.", color=INK, font_size=68, weight=BOLD)
        hook.move_to(ORIGIN)
        slam(hook, run_time=0.3)
        self.wait(0.9)

        self.play(FadeOut(hook), run_time=0.3)
        self.play(FadeOut(intro_dot), FadeOut(intro_halo), run_time=0.25)

        # ==================================================================
        # BEAT 2 — WORDS → NUMBERS → SPACE  (0:06–0:18)
        # ==================================================================
        para_lines = [
            "Water is a polar molecule.",
            "Two hydrogen atoms bond",
            "to one oxygen atom, forming",
            "a chemical compound essential",
            "to all known life.",
        ]
        para = VGroup(*[Text(t, color=INK, font_size=30) for t in para_lines])
        para.arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        para.move_to([0, 0.5, 0])

        self.play(LaggedStart(*[FadeIn(l, shift=0.1 * UP) for l in para],
                              lag_ratio=0.12), run_time=1.8)
        self.wait(0.5)

        # fake cursor taps WATER
        fake_cursor = VGroup(
            Dot(ORIGIN, radius=0.05, color=INK),
            Circle(radius=0.12, color=INK).set_stroke(width=1.2, opacity=0.6),
        )
        fake_cursor.fix_in_frame().move_to([3.0, 1.8, 0])
        self.play(FadeIn(fake_cursor, scale=0.5), run_time=0.3)
        self.play(fake_cursor.animate.move_to([1.6, 0.7, 0]), run_time=0.5)
        ripple = Circle(radius=0.05, color=TARGET).set_stroke(width=2)
        ripple.move_to([1.6, 0.7, 0]).fix_in_frame()
        self.play(ripple.animate.scale(3).set_opacity(0), run_time=0.5)
        self.play(FadeOut(fake_cursor), run_time=0.2)

        self.play(para.animate.set_opacity(0.18), run_time=0.4)

        key_words = ["WATER", "MOLECULE", "HYDROGEN", "CHEMICAL", "COMPOUND"]
        floating = VGroup()
        for i, w in enumerate(key_words):
            word = Text(w, color=TARGET, font_size=30, weight=BOLD)
            angle = i * TAU / 5 + 0.4
            word.move_to([3.2 * np.cos(angle), 2.7 * np.sin(angle) + 0.3, 0])
            floating.add(word)

        self.play(LaggedStart(*[FadeIn(fw, scale=0.6) for fw in floating],
                              lag_ratio=0.1), run_time=1.5)
        self.wait(0.4)

        num_groups = VGroup()
        rng = np.random.default_rng(11)
        for fw in floating:
            s = "  ".join([f"{v:+.2f}" for v in rng.uniform(-0.99, 0.99, 5)])
            n = Text(s, color=VOCAB, font_size=13)
            n.next_to(fw, DOWN, buff=0.15)
            num_groups.add(n)
        self.play(LaggedStart(*[FadeIn(n, shift=0.1 * DOWN) for n in num_groups],
                              lag_ratio=0.1), run_time=1.5)
        self.wait(0.4)

        # LAUNCH into space
        self.play(FadeOut(para), FadeOut(floating), FadeOut(num_groups),
                  run_time=0.6)

        rng2 = np.random.default_rng(7)
        scatter = VGroup(*[
            Dot(np.array([rng2.uniform(-3.5, 3.5),
                          rng2.uniform(-2.5, 2.5),
                          rng2.uniform(-1.5, 1.5)]),
                radius=0.045, color=CURVE).set_opacity(0.85)
            for _ in range(60)
        ])
        self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in scatter],
                              lag_ratio=0.015), run_time=1.2)
        self.play(frame.animate.set_height(11), run_time=0.6)
        self.play(LaggedStart(*[
            p.animate.shift(np.array([rng2.uniform(-1, 1),
                                      rng2.uniform(-1, 1),
                                      rng2.uniform(-0.6, 0.6)]))
            for p in scatter
        ], lag_ratio=0.008), run_time=1.0)
        self.play(FadeOut(scatter),
                  frame.animate.set_height(8.5).move_to(ORIGIN), run_time=0.6)

        # ==================================================================
        # BEAT 3 — WORD UNIVERSE  (0:18–0:30)
        # ==================================================================
        set_cam(70 * DEGREES, -30 * DEGREES, run_time=1.5)

        origin = np.array([-4.0, -2.5, -1.5])
        ax_x = Line(origin, np.array([5.0, -2.5, -1.5]), stroke_width=1.5, color=DIM)
        ax_y = Line(origin, np.array([-4.0, 2.8, -1.5]), stroke_width=1.5, color=DIM)
        ax_z = Line(origin, np.array([-4.0, -2.5, 2.5]), stroke_width=1.5, color=DIM)
        xl = Tex("x", color=INK, font_size=30).move_to([5.3, -2.5, -1.5])
        yl = Tex("y", color=INK, font_size=30).move_to([-4.0, 3.1, -1.5])
        zl = Tex("z", color=INK, font_size=30).move_to([-4.0, -2.5, 2.8])
        self.play(ShowCreation(ax_x), ShowCreation(ax_y), ShowCreation(ax_z),
                  FadeIn(xl), FadeIn(yl), FadeIn(zl), run_time=1.5)

        rng3 = np.random.default_rng(42)
        positions = [
            np.array([rng3.uniform(-3, 4.5),
                      rng3.uniform(-2, 2.3),
                      rng3.uniform(-1.2, 2.2)]) for _ in range(67)
        ]
        target_names = ["WATER", "CHEMICAL", "COMPOUND", "H2O", "POLAR"]
        target_idx = [0, 1, 2, 3, 4]
        center = np.array([1.2, 0.5, 0.6])
        offsets = [np.array([0, 0, 0]),
                   np.array([0.7, 0.35, 0.15]),
                   np.array([-0.55, 0.45, 0.25]),
                   np.array([0.35, -0.55, 0.15]),
                   np.array([-0.35, -0.45, -0.1])]
        for i, off in zip(target_idx, offsets):
            positions[i] = center + off

        blues = VGroup(*[Dot(p, radius=0.06, color=VOCAB).set_opacity(0.85)
                         for i, p in enumerate(positions) if i not in target_idx])
        oranges = VGroup(*[Dot(positions[i], radius=0.11, color=TARGET)
                           for i in target_idx])

        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in blues],
                              lag_ratio=0.015), run_time=1.8)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in oranges],
                              lag_ratio=0.1), run_time=0.9)

        labels = VGroup()
        for name, i in zip(target_names, range(5)):
            lbl = Text(name, color=TARGET, font_size=20)
            lbl.next_to(oranges[i], UP, buff=0.15)
            labels.add(lbl)
        self.play(LaggedStart(*[FadeIn(l, shift=0.1 * UP) for l in labels],
                              lag_ratio=0.1), run_time=1.0)
        self.wait(0.3)

        # connect nearby
        connects = VGroup()
        for i in range(5):
            for j in range(i + 1, 5):
                if np.linalg.norm(positions[target_idx[i]] - positions[target_idx[j]]) < 1.3:
                    connects.add(Line(positions[target_idx[i]],
                                      positions[target_idx[j]],
                                      stroke_width=1.5, color=CURVE)
                                 .set_stroke(opacity=0.7))
        self.play(LaggedStart(*[ShowCreation(l) for l in connects],
                              lag_ratio=0.15), run_time=1.2)
        self.wait(0.3)

        # boundary ripple
        boundary_pts = [center + np.array([1.05 * np.cos(a),
                                           1.05 * np.sin(a),
                                           0.15 * np.sin(3 * a)])
                        for a in np.linspace(0, TAU, 60)]
        boundary = VMobject(color=CURVE, stroke_width=1.5).set_stroke(opacity=0.7)
        boundary.set_points_smoothly(boundary_pts)
        self.play(ShowCreation(boundary), run_time=1.0)
        self.wait(0.4)

        orbit_cam(0.35, -0.05, run_time=1.5)

        self.play(FadeOut(VGroup(ax_x, ax_y, ax_z, xl, yl, zl)),
                  FadeOut(blues), FadeOut(oranges),
                  FadeOut(labels), FadeOut(connects), FadeOut(boundary),
                  run_time=1.0)
        set_cam(0, 0, run_time=1.0)

        # ==================================================================
        # BEAT 4 — THE EQUATION  (0:30–0:36)
        # ==================================================================
        eq = Tex(r"z(\theta) = e^{\cos\theta}\left(\cos\theta + i\sin\theta\right)",
                 color=INK, font_size=56)
        eq.move_to([0, 1.5, 0]).fix_in_frame()
        slam(eq, run_time=0.35)
        self.wait(1.8)

        # ZOOM-THROUGH into the exp
        fake_zoom_target = Dot(eq.get_center() + np.array([-0.5, 0.1, 0]),
                               radius=0.01, color=INK).fix_in_frame()
        self.add(fake_zoom_target)
        zoom_through(fake_zoom_target, factor=0.4, run_time=0.8)
        self.wait(0.2)
        self.play(FadeOut(eq), FadeOut(fake_zoom_target), run_time=0.3)
        self.play(frame.animate.set_height(8.5).move_to(ORIGIN), run_time=0.6)

        # ==================================================================
        # BEAT 5 — 2D → 3D EULER CURVE  (0:36–0:48)
        # ==================================================================
        # Complex plane
        re_ax = Line([-3.6, -0.3, 0], [3.6, -0.3, 0], stroke_width=1.4, color=DIM)
        im_ax = Line([0, -3.0, 0], [0, 3.0, 0], stroke_width=1.4, color=DIM)
        re_lab = Tex("Re", color=INK, font_size=22).move_to([3.9, -0.3, 0])
        im_lab = Tex("Im", color=INK, font_size=22).move_to([0, 3.3, 0])
        self.play(ShowCreation(re_ax), ShowCreation(im_ax),
                  FadeIn(re_lab), FadeIn(im_lab), run_time=1.0)

        # θ ValueTracker drives radius vector + tracing dot
        theta_t = ValueTracker(0)

        radius_line = Line(ORIGIN, ORIGIN, color=WEIGHTS, stroke_width=3)
        trace_dot = Dot(ORIGIN, radius=0.09, color=TARGET)

        def update_radius(m):
            t = theta_t.get_value()
            c = euler_curve(t)
            m.put_start_and_end_on(ORIGIN, 2.0 * np.array([c[0], c[1], 0]))

        def update_dot(m):
            t = theta_t.get_value()
            c = euler_curve(t)
            m.move_to(2.0 * np.array([c[0], c[1], 0]))

        radius_line.add_updater(update_radius)
        trace_dot.add_updater(update_dot)
        self.add(radius_line, trace_dot)

        # closed 2D curve
        pts_2d = [2.0 * np.array([*(euler_curve(t)[:2]), 0])
                  for t in np.linspace(0, TAU, 240)]
        euler_2d = VMobject(color=CURVE, stroke_width=4.0)
        euler_2d.set_points_smoothly(pts_2d)

        self.play(
            ShowCreation(euler_2d, rate_func=linear),
            theta_t.animate.set_value(TAU),
            run_time=3.5,
        )
        radius_line.clear_updaters()
        trace_dot.clear_updaters()
        self.wait(0.3)

        # fade 2D, lift to 3D
        self.play(FadeOut(re_ax), FadeOut(im_ax), FadeOut(re_lab), FadeOut(im_lab),
                  FadeOut(radius_line), FadeOut(trace_dot), FadeOut(euler_2d),
                  run_time=0.6)

        set_cam(62 * DEGREES, -25 * DEGREES, run_time=1.5)

        zstretch_t = ValueTracker(0.001)
        wave = VMobject(color=CURVE, stroke_width=4.0)

        def update_wave(m):
            zs = zstretch_t.get_value()
            pts = []
            for t in np.linspace(0, TAU, 300):
                c = euler_curve(t)
                pts.append(2.0 * np.array([c[0], c[1], zs * c[2]]))
            m.set_points_smoothly(pts)

        wave.add_updater(update_wave)
        self.add(wave)
        self.play(zstretch_t.animate.set_value(1.3),
                  run_time=2.5, rate_func=smooth)
        wave.clear_updaters()
        self.wait(0.4)

        eq3d = Tex(r"x=e^{\cos\theta}\cos\theta\quad y=e^{\cos\theta}\sin\theta\quad z=\sin 2\theta",
                   color=INK, font_size=26)
        eq3d.move_to([0, 3.2, 0]).fix_in_frame()
        self.play(FadeIn(eq3d, shift=0.1 * UP), run_time=1.0)
        self.wait(1.0)
        orbit_cam(0.35, -0.05, run_time=2.5)
        self.play(FadeOut(eq3d), run_time=0.5)

        # ==================================================================
        # BEAT 6 — 2,144 POINTS  (0:48–1:05)
        # ==================================================================
        N_PART = 2144
        targets = curve_samples(N_PART)
        rng4 = np.random.default_rng(9)

        particles = VGroup()
        for _ in range(N_PART):
            particles.add(
                Dot(np.array([rng4.uniform(-4, 4),
                              rng4.uniform(-4, 4),
                              rng4.uniform(-3, 3)]),
                    radius=0.018, color=VOCAB).set_opacity(0.0)
            )
        self.add(particles)

        move_t = ValueTracker(0)
        fade_t = ValueTracker(0)
        for p, tgt in zip(particles, targets):
            start = p.get_center().copy()
            p.add_updater(
                lambda m, s=start, tt=tgt:
                m.move_to(s + move_t.get_value() * (tt - s))
            )
            p.add_updater(
                lambda m, ft=fade_t:
                m.set_opacity(0.7 * ft.get_value())
            )
        self.play(move_t.animate.set_value(1.0),
                  fade_t.animate.set_value(1.0),
                  run_time=3.0, rate_func=smooth)
        for p in particles:
            p.clear_updaters()
            p.set_opacity(0.7)
        self.wait(0.4)

        orbit_cam(0.30, -0.05, run_time=2.5)

        # WATER (first 32) → orange
        def pop_word(start_k, label_text):
            grp = VGroup(*[particles[k] for k in range(start_k, start_k + 32)])
            self.play(grp.animate.set_color(TARGET).set_opacity(1.0),
                      run_time=0.9)
            lbl = Text(label_text, color=TARGET, font_size=24, weight=BOLD)
            lbl.move_to([0, 3.3, 0]).fix_in_frame()
            self.play(FadeIn(lbl), run_time=0.4)
            self.wait(0.5)
            self.play(grp.animate.set_color(VOCAB).set_opacity(0.7),
                      FadeOut(lbl), run_time=0.6)

        pop_word(0,   "WATER")
        pop_word(32,  "MOLECULE")
        pop_word(64,  "HYDROGEN")

        # ==================================================================
        # BEAT 7 — LEARNING LOOP  (1:05–1:20)
        # ==================================================================
        set_cam(45 * DEGREES, -15 * DEGREES, run_time=1.2, height=8.5)
        # fade particles to dim so the UI reads
        self.play(particles.animate.set_opacity(0.25), run_time=0.6)

        # typing card
        question = Text("WHAT IS WATER?", color=INK, font_size=44, weight=BOLD)
        question.move_to([0, 1.5, 0]).fix_in_frame()
        self.play(ShowIncreasingSubsets(question, int_func=lambda x: int(x)),
                  run_time=1.8, rate_func=linear)
        self.wait(0.4)

        answer = Text("Water is a polar molecule, H2O — a chemical compound.",
                      color=INK, font_size=24)
        answer.next_to(question, DOWN, buff=0.5).fix_in_frame()
        self.play(FadeIn(answer, shift=0.15 * UP), run_time=1.0)
        self.wait(0.6)
        self.play(FadeOut(question), FadeOut(answer), run_time=0.5)

        # learning loop arrows
        def step_box(txt, clr):
            t = Text(txt, color=clr, font_size=22, weight=BOLD)
            b = Rectangle(width=t.get_width() + 0.6,
                          height=t.get_height() + 0.4,
                          color=clr, stroke_width=1.6).set_fill(BG, opacity=0.8)
            t.move_to(b.get_center())
            return VGroup(b, t)

        boxes = VGroup(
            step_box("QUESTION", INK),
            step_box("ANSWER", INK),
            step_box("ERROR", TARGET),
            step_box("UPDATE WEIGHTS", WEIGHTS),
        ).arrange(RIGHT, buff=0.5).move_to([0, 0.5, 0]).fix_in_frame()

        arrows = VGroup(*[
            Arrow(boxes[i].get_right(), boxes[i + 1].get_left(),
                  buff=0.08, color=INK, stroke_width=1.4)
            for i in range(3)
        ]).fix_in_frame()

        self.play(LaggedStart(*[FadeIn(b, shift=0.1 * UP) for b in boxes],
                              lag_ratio=0.15), run_time=1.4)
        self.play(LaggedStart(*[ShowCreation(a) for a in arrows],
                              lag_ratio=0.15), run_time=0.9)
        self.wait(0.5)

        # weight update: 10 particles purple, shift along curve
        shift_idx = [0, 5, 10, 15, 20, 25, 40, 50, 60, 70]
        shift_parts = VGroup(*[particles[k] for k in shift_idx])
        self.play(shift_parts.animate.set_color(WEIGHTS).set_opacity(1.0),
                  run_time=0.8)
        moves = []
        for i, k in enumerate(shift_idx):
            theta_new = (k + 0.5) * TAU / N_PART
            c = euler_curve(theta_new)
            new_p = 2.0 * np.array([c[0], c[1], 1.3 * c[2]])
            moves.append(shift_parts[i].animate.move_to(new_p))
        self.play(*moves, run_time=1.2, rate_func=smooth)
        self.play(shift_parts.animate.set_color(VOCAB).set_opacity(0.7),
                  run_time=0.6)

        self.play(FadeOut(boxes), FadeOut(arrows), run_time=0.5)

        # ==================================================================
        # BEAT 8 — STATS  (1:20–1:35)
        # ==================================================================
        self.play(particles.animate.set_opacity(0.15), run_time=0.5)

        def stat_card(number, label, accent):
            num = Text(number, color=accent, font_size=88, weight=BOLD)
            lbl = Text(label, color=INK, font_size=22).next_to(num, DOWN, buff=0.25)
            grp = VGroup(num, lbl)
            box = Rectangle(width=4.2, height=2.6, color=accent,
                            stroke_width=1.5).set_fill(BG, opacity=0.85)
            grp.move_to(box.get_center())
            return VGroup(box, grp)

        stats_data = [
            ("67",    "vocabulary words",         CURVE),
            ("32",    "components per word",      VOCAB),
            ("516/516", "training questions",     TARGET),
            ("74.4%", "accuracy · unseen test",   WEIGHTS),
        ]

        for num, lbl, clr in stats_data:
            card = stat_card(num, lbl, clr).fix_in_frame().move_to(ORIGIN)
            card.scale(0.85)
            slam(card, run_time=0.28)
            self.wait(0.9)
            self.play(FadeOut(card, scale=1.1), run_time=0.3)

        # ==================================================================
        # BEAT 9 — OUTRO  (1:35–1:45)  — LOOP POINT
        # ==================================================================
        self.play(particles.animate.set_opacity(0.7), run_time=0.6)
        set_cam(58 * DEGREES, 10 * DEGREES, run_time=1.2, height=11)
        orbit_cam(0.35, -0.05, run_time=4.0)

        # final title card over the wave
        title = Text("SMART LOOKUP", color=INK, font_size=64, weight=BOLD)
        title.move_to([0, 1.6, 0]).fix_in_frame()
        subtitle = VGroup(
            Text("From Words to Numbers.", color=INK, font_size=22),
            Text("From Numbers to Geometry.", color=INK, font_size=22),
            Text("From Geometry to Learning.", color=INK, font_size=22),
        ).arrange(DOWN, buff=0.15).move_to([0, -1.6, 0]).fix_in_frame()
        tbc = Text("TO BE CONTINUED...", color=CURVE,
                   font_size=20, weight=BOLD).move_to([0, -3.1, 0]).fix_in_frame()

        self.play(FadeIn(title, shift=0.1 * UP), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(s, shift=0.1 * UP) for s in subtitle],
                              lag_ratio=0.2), run_time=1.2)
        self.play(FadeIn(tbc), run_time=0.6)
        self.wait(2.5)

        # LOOP-POINT: resolve to same turquoise-dot-on-black frame
        self.play(FadeOut(title), FadeOut(subtitle), FadeOut(tbc),
                  FadeOut(particles),
                  frame.animate.set_euler_angles(phi=0, theta=0)
                       .set_height(8.5).move_to(ORIGIN),
                  run_time=1.4)

        end_dot = Dot(ORIGIN, radius=0.09, color=CURVE)
        end_halo = Dot(ORIGIN, radius=0.32, color=CURVE).set_opacity(0.15)
        self.play(FadeIn(end_dot), FadeIn(end_halo), run_time=0.5)
        self.wait(0.6)
        self.play(end_halo.animate.scale(2.2).set_opacity(0),
                  run_time=0.9, rate_func=rush_from)
        self.wait(0.4)
        # fade out — loops cleanly to first frame
        self.play(FadeOut(end_dot), FadeOut(end_halo), run_time=0.3)
