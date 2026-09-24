"""
comment_googolplexian — answering a comment on times_table_dance. Still.

    BPM=150 xvfb-run -a -s "-screen 0 1600x1200x24" \
        manimgl comment_googolplexian.py CommentGoogolplexian -s -w -r 1080x1920

@vyaas_2011 commented "1 googolplexian to the pentation of 1 googolplexian"
on the times-table video, whose ask was "comment a times table and I'll
run it". So: run it.

THE PICTURE ONLY EVER NEEDS k mod N. Dot n joins dot (n*k) mod 400, so
two multipliers that agree mod 400 draw exactly the same figure. The
number itself is beyond writing down; its remainder is not.

    googol         = 10^100
    googolplex     = 10^googol
    googolplexian  = 10^googolplex          -- a power of ten either way

    G^^^G, pentation, unwraps to G^(something enormous)
                   = (10^M)^E = 10^(M*E)    -- still a power of ten

    10^4 = 10000 = 400 * 25, so 400 divides 10^k for every k >= 4

    => G^^^G  ==  0  (mod 400)

And k = 0 is the ONE multiplier out of 400 whose chords all land on the
same dot. The largest number anybody has ever put in the comments draws
the simplest picture in the entire set: a single fan.

VERIFIED AT IMPORT
    400 divides 10^k for every k >= 4, checked directly
    the 400 chords are confirmed to share exactly one far end
    k = 0 is confirmed to be the only multiplier in 0..399 that does this

manimgl traps, all silent:
    Text -> fill_color=   Circle -> stroke_color=   Dot -> fill_color=
"""
from manimlib import *
import numpy as np

N = 400
K = 0

assert all(pow(10, k, N) == 0 for k in range(4, 2000))
assert len({(n * K) % N for n in range(N)}) == 1
assert [k for k in range(N)
        if len({(n * k) % N for n in range(N)}) == 1] == [K]

WHITE_ = "#F7FAFC"
GREY   = "#8A94A6"
DIM    = "#5A6272"
GOLD   = "#EBCB8B"
SKY    = "#88C0D0"
ROSE   = "#D08770"

FRAME_H = 9.0
SAFE_X = 1.68
NOTE_Y = -2.36
READ_Y = 2.62

RING_C = np.array([0.0, 0.15, 0])
R = 1.62
IDX = np.arange(N)


def P(u):
    a = 2 * np.pi * u / N + np.pi / 2
    return RING_C + R * np.array([np.cos(a), np.sin(a), 0])


def wheel(n):
    stops = [GOLD, ROSE, SKY, GOLD]
    t = (n / N) * 3.0
    i = min(int(t), 2)
    return interpolate_color(stops[i], stops[i + 1], t - i)


def txt(s, size=27, color=WHITE_, bold=True, w=2 * SAFE_X - 0.15):
    t = Text(s, fill_color=color, font_size=size,
             weight=BOLD if bold else NORMAL)
    if t.get_width() > w:
        t.set_width(w)
    return t


class CommentGoogolplexian(Scene):
    def construct(self):
        self.camera.background_rgba = list(color_to_rgba(BLACK, 1.0))
        self.camera.frame.set_height(FRAME_H)

        chords = VGroup()
        for n in range(N):
            m = VMobject(stroke_color=wheel(n), stroke_width=0.95)
            m.set_points_as_corners([P(n), P((n * K) % N)])
            m.set_stroke(opacity=0.42)
            chords.add(m)

        head = txt("googolplexian ↑↑↑ googolplexian", 24, DIM, bold=False)
        head.move_to(np.array([0, READ_Y + 0.30, 0]))
        sub = txt("≡  0   (mod 400)", 30, GOLD)
        sub.move_to(np.array([0, READ_Y - 0.34, 0]))
        foot = txt("the biggest number in my comments", 26, WHITE_, bold=False)
        foot.move_to(np.array([0, NOTE_Y + 0.38, 0]))
        foot2 = txt("draws the simplest picture I've got", 26, GOLD, bold=False)
        foot2.move_to(np.array([0, NOTE_Y - 0.34, 0]))

        self.add(chords, head, sub, foot, foot2)
        self.wait(0.1)
