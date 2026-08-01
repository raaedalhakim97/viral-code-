#!/usr/bin/env python3
"""
narrate_scene — lay Alan over a manim render.

Why this exists at all: TikTok transcribes video audio and indexes the transcript.
A silent video forfeits the platform's strongest text signal. Every one of these
scenes is silent, so every one of them is throwing away its best SEO surface.
This is the same argument, and the same voice chain, as OIS tools/narrate.py.

The voice is the OBSERVER's — the one who watches and names things — not a
character's. So it is processed to sit back in the room: rumble trimmed, a
watcher's distance of reverb, never a cathedral.

    python3 narrate_scene.py videos/LostInTheMiddle.mp4 out.mp4
    python3 narrate_scene.py videos/LostInTheMiddle.mp4 out.mp4 --stem alan.wav
    python3 narrate_scene.py --check          # timing report, synthesizes nothing

A line that will not fit before the next one starts is spoken slightly faster
rather than clipped, down to a floor of length_scale 0.80. Below that the tool
tells you instead of quietly mangling the read — fix the script, not the speed.

Model: piper en-gb-alan-low. Fetched from the GitHub release mirror, because
HuggingFace is blocked by the render container's egress policy.
"""
import argparse
import os
import subprocess
import sys
import tarfile
import tempfile
import urllib.request
import wave

import numpy as np

SR = 44100                       # matches the OIS score bus
PIPER_SR = 16000                 # what en-gb-alan-low emits
LENGTH_SCALE = 1.18              # Alan's house pace, from narrate.py
MODEL = "en-gb-alan-low.onnx"
MODEL_URL = ("https://github.com/rhasspy/piper/releases/download/v0.0.2/"
             "voice-en-gb-alan-low.tar.gz")
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "observer-voice")

# ---------------------------------------------------------------------------
# The read. (start_seconds, text) — timed against LostInTheMiddle, 31.77s.
#
# SPARSE ON PURPOSE. The first draft of this narrated every cut and it does not
# fit: the escalation rows sit ~1.2s apart and a spoken line needs 2-3s, so
# wall-to-wall VO either clips or forces the animation to crawl. That is the
# same conclusion OIS narrate.py reached — a few spoken lines carrying the
# searchable phrasing, not a documentary track. The on-screen text says the
# numbers; Alan says the meaning; the silence between them is the pacing.
#
# Keep the searchable words spoken aloud — "context window", "attention",
# "RULER", "long context" — those are what the transcriber indexes.
# ---------------------------------------------------------------------------
LINES = [
    (0.30, "Every model claims it reads a million words of context."),
    (10.75, "Nobody computes a trillion. So they don't."),
    (14.35, "A benchmark called RULER tested seventeen long context models."),
    (18.80, "All seventeen degraded."),
    (20.60, "And the damage is not spread evenly."),
    (23.00, "The beginning is remembered. So is the end."),
    (25.80, "Put what matters at the start, or at the end. Never the middle."),
]


# ---------------------------------------------------------------------------
# House voice chain — ported from OIS make_music.reverb + narrate.shape so this
# runs without the OIS tree on the path. Keep the two in step if either moves.
# ---------------------------------------------------------------------------
def reverb(x, mix=1.0):
    """A lush hall: diffuse early reflections + a long, HF-damped tail."""
    x = x.astype(np.float32)
    out = x.copy()
    for d, g in ((0.007, 0.6), (0.013, 0.5), (0.019, 0.42),
                 (0.029, 0.34), (0.041, 0.27)):
        dd = int(d * SR)
        if dd < len(x):
            out[dd:] += x[:-dd] * (g * 0.5 * mix)
    tail = np.zeros_like(x)
    for i in range(1, 16):
        d = int((0.033 * i + 0.006) * SR)
        if d >= len(x):
            break
        w = 3 + i
        damped = np.convolve(x[:-d], np.ones(w) / w, "same")
        tail[d:] += damped * (0.55 * (0.80 ** i) * mix)
    return out + tail


def shape(x, room=0.26):
    """Trim the rumble, set the voice back in the room."""
    if len(x) == 0:
        return x
    k = max(1, int(SR / 90))                       # high-pass under ~90 Hz
    x = x - np.convolve(x, np.ones(k, np.float32) / k, "same")
    x = x / (np.max(np.abs(x)) + 1e-9) * 0.92
    wet = reverb(x, mix=room)
    x = x + (wet - x) * 0.26                       # a watcher's distance
    return (x / (np.max(np.abs(x)) + 1e-9) * 0.9).astype(np.float32)


def resample(x, src, dst):
    if src == dst:
        return x
    n = int(round(len(x) * dst / src))
    return np.interp(np.linspace(0, len(x) - 1, n),
                     np.arange(len(x)), x).astype(np.float32)


_voice = None


def ensure_model():
    os.makedirs(CACHE, exist_ok=True)
    onnx = os.path.join(CACHE, MODEL)
    if not os.path.exists(onnx):
        print(f"fetching {MODEL} ...", flush=True)
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as f:
            tmp = f.name
        urllib.request.urlretrieve(MODEL_URL, tmp)
        with tarfile.open(tmp) as t:
            t.extractall(CACHE)
        os.unlink(tmp)
    return onnx


def speak(text, length_scale=LENGTH_SCALE):
    """One line -> float32 mono at SR."""
    global _voice
    from piper import PiperVoice, SynthesisConfig
    if _voice is None:
        onnx = ensure_model()
        _voice = PiperVoice.load(onnx, config_path=onnx + ".json")
    cfg = SynthesisConfig(length_scale=length_scale, noise_scale=0.60,
                          noise_w_scale=0.75, normalize_audio=True)
    chunks = [np.frombuffer(a.audio_int16_bytes, dtype=np.int16)
              for a in _voice.synthesize(text, syn_config=cfg)]
    raw = np.concatenate(chunks).astype(np.float32) / 32768.0
    return resample(raw, PIPER_SR, SR)


def duration(path):
    out = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", path]).decode().strip()
    return float(out)


def build(total, verbose=True):
    """Render the full voice track, silent everywhere Alan is not speaking."""
    track = np.zeros(int(total * SR) + SR, np.float32)
    report = []
    for i, (at, text) in enumerate(LINES):
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else total
        room = nxt - at
        sig = speak(text)
        scale = LENGTH_SCALE
        if len(sig) / SR > room:                   # too long: say it a little quicker
            want = max(0.80, LENGTH_SCALE * room / (len(sig) / SR))
            sig = speak(text, length_scale=want)
            scale = want
        over = len(sig) / SR - room
        report.append((at, len(sig) / SR, room, scale, over, text))
        sig = shape(sig)
        s = int(at * SR)
        e = min(s + len(sig), len(track))
        track[s:e] += sig[:e - s]

    if verbose:
        print(f"{'at':>6} {'len':>6} {'room':>6} {'scale':>6}  line")
        for at, ln, room, scale, over, text in report:
            flag = "  <-- OVERRUNS" if over > 0.05 else ""
            print(f"{at:6.2f} {ln:6.2f} {room:6.2f} {scale:6.2f}  "
                  f"{text[:44]}{flag}")
        worst = max((r[4] for r in report), default=0)
        print(f"\ntotal {total:.2f}s   worst overrun {worst:+.2f}s")

    peak = np.max(np.abs(track)) + 1e-9
    return (track / peak * 0.85).astype(np.float32)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="?")
    ap.add_argument("dst", nargs="?")
    ap.add_argument("--stem", help="also write Alan alone as a wav, for CapCut")
    ap.add_argument("--check", action="store_true",
                    help="timing report only, synthesize nothing")
    a = ap.parse_args()

    if a.check:
        end = LINES[-1][0]
        print(f"{'at':>6}  gap   line")
        for i, (at, text) in enumerate(LINES):
            nxt = LINES[i + 1][0] if i + 1 < len(LINES) else end + 3
            print(f"{at:6.2f} {nxt - at:5.2f}  {text}")
        return

    if not a.src or not a.dst:
        sys.exit("need src and dst (or --check)")

    total = duration(a.src)
    track = build(total)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        wav = f.name
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((track * 32767).astype(np.int16).tobytes())

    if a.stem:
        subprocess.run(["cp", wav, a.stem], check=True)
        print(f"stem -> {a.stem}")

    # video is copied, never re-encoded: no render time, no quality loss
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", a.src, "-i", wav,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", a.dst], check=True)
    os.unlink(wav)
    print(f"{a.dst}")


if __name__ == "__main__":
    main()
