#!/usr/bin/env python3
"""
cinegrade — put manim output through the Observer house grade.

manimgl writes clean vector frames: pure #000 background, hard-edged strokes, no
falloff. That is a plot, not a photograph. The look the channel already has in the
trailers comes from three passes over those pixels — bloom, vignette, grain — which
is what makes white-on-black read as *light on film* instead of ink on paper.

This runs the same FX ports trailers.py uses, at the same settings, so a manim
scene and a hand-built episode come out of the same room.

    python3 cinegrade.py in.mp4 out.mp4
    python3 cinegrade.py in.mp4 out.mp4 --anamorphic   # + subtle chromatic edge
    python3 cinegrade.py in.mp4 out.mp4 --stills 320   # single frame, before|after
"""
import argparse
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

FFMPEG = "ffmpeg"


class FX:
    """Ported from OIS cineengine/generator.py so this runs standalone."""

    def __init__(self, w, h):
        self.w, self.h = w, h
        yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
        self.xx, self.yy = xx, yy
        self.tcx, self.tcy = xx / w, yy / h

    def bloom(self, img, sigma=7, thr=175, gain=1.4):
        b = np.asarray(Image.fromarray(img.clip(0, 255).astype(np.uint8))
                       .filter(ImageFilter.GaussianBlur(sigma)), np.float32)
        return img + np.clip(b - thr, 0, 255) * gain

    def vignette(self, a, strength=0.45):
        ux = (self.tcx - 0.5) * (self.w / self.h)
        uy = (self.tcy - 0.5)
        d = np.sqrt(ux ** 2 + uy ** 2) * (1 + strength)
        tt = np.clip((d - 0.85) / (0.32 - 0.85), 0, 1)
        return a * (tt * tt * (3 - 2 * tt))[..., None]

    def grain(self, a, t, amt=0.035):
        n = np.sin((self.tcx * self.w + t) * 12.9898
                   + (self.tcy * self.h + t) * 78.233) * 43758.5453
        n = (n - np.floor(n)) * 2 - 1
        return a + n[..., None] * amt * 255

    def chromatic(self, a, amount):
        dx = (self.tcx - 0.5) * amount
        dy = (self.tcy - 0.5) * amount
        xr = np.clip(self.xx + dx, 0, self.w - 1).astype(np.int32)
        yr = np.clip(self.yy + dy, 0, self.h - 1).astype(np.int32)
        xb = np.clip(self.xx - dx, 0, self.w - 1).astype(np.int32)
        yb = np.clip(self.yy - dy, 0, self.h - 1).astype(np.int32)
        o = a.copy()
        o[..., 0] = a[yr, xr, 0]
        o[..., 2] = a[yb, xb, 2]
        return o


# House settings — bloom and grain identical to trailers.py:98-100.
BLOOM = dict(sigma=8, thr=205, gain=0.70)
GRAIN = 0.013
CHROMATIC = 1.6   # only with --anamorphic

# Vignette is the one value that does NOT carry over. trailers.py uses 0.42,
# which was tuned on 16:9 with the content centred. At 9:16 the falloff reaches
# much further into the frame vertically, and it lands exactly on the caption
# line — graded at 0.42, the promo's second caption line dropped to a muddy
# grey. 0.22 keeps the depth without eating the text.
VIGNETTE = 0.22


def grade(fx, frame, n, anamorphic=False):
    a = frame.astype(np.float32)
    a = fx.bloom(a, **BLOOM)
    if anamorphic:
        a = fx.chromatic(a, CHROMATIC)
    a = fx.vignette(a, VIGNETTE)
    a = fx.grain(a, n, amt=GRAIN)
    return a.clip(0, 255).astype(np.uint8)


def probe(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "csv=p=0", path]).decode().strip().split(",")
    w, h = int(out[0]), int(out[1])
    num, den = out[2].split("/")
    return w, h, float(num) / float(den)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--anamorphic", action="store_true",
                    help="subtle chromatic split at frame edges")
    ap.add_argument("--stills", type=int, default=None, metavar="N",
                    help="write a single before|after PNG for frame N instead")
    a = ap.parse_args()

    w, h, fps = probe(a.src)
    fx = FX(w, h)
    fsize = w * h * 3

    if a.stills is not None:
        dec = subprocess.Popen(
            [FFMPEG, "-v", "error", "-i", a.src, "-vf", f"select=eq(n\\,{a.stills})",
             "-vsync", "0", "-frames:v", "1", "-f", "rawvideo",
             "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
        raw = dec.stdout.read(fsize)
        dec.wait()
        before = np.frombuffer(raw, np.uint8).reshape(h, w, 3)
        after = grade(fx, before, a.stills, a.anamorphic)
        pair = np.concatenate([before, np.full((h, 12, 3), 40, np.uint8), after], 1)
        Image.fromarray(pair).save(a.dst)
        print(f"{a.dst}  frame {a.stills}  before | after")
        return

    dec = subprocess.Popen(
        [FFMPEG, "-v", "error", "-i", a.src, "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(
        [FFMPEG, "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
         "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
         "-c:v", "libx264", "-preset", "slow", "-crf", "17",
         "-pix_fmt", "yuv420p", a.dst], stdin=subprocess.PIPE)

    n = 0
    while True:
        raw = dec.stdout.read(fsize)
        if len(raw) < fsize:
            break
        frame = np.frombuffer(raw, np.uint8).reshape(h, w, 3)
        enc.stdin.write(grade(fx, frame, n, a.anamorphic).tobytes())
        n += 1
        if n % 120 == 0:
            print(f"  {n} frames", flush=True)

    enc.stdin.close()
    dec.wait()
    enc.wait()
    print(f"{a.dst}  {n} frames  {w}x{h} @ {fps:g}fps")


if __name__ == "__main__":
    main()
