#!/usr/bin/env python3
"""
narrate_scene — lay a voice track over a manim render.

Why this exists at all: TikTok transcribes video audio and indexes the transcript.
A silent video forfeits the platform's strongest text signal. Every one of these
scenes is silent, so every one of them is throwing away its best SEO surface.
This is the same argument, and the same voice chain, as OIS tools/narrate.py.

The voice is the OBSERVER's — the one who watches and names things — not a
character's. So it is processed to sit back in the room: rumble trimmed, a
watcher's distance of reverb, never a cathedral. The processing is unchanged
from OIS narrate.py; only the model and the pacing differ.

    python3 narrate_scene.py videos/LostInTheMiddle.mp4 out.mp4
    SCRIPT=not_calculating python3 narrate_scene.py graded.mp4 out.mp4 --stem alan.wav
    SCRIPT=not_calculating python3 narrate_scene.py --check   # timing only

SCRIPT selects a read from SCRIPTS below; it defaults to lost_in_the_middle.

A line that will not fit before the next one starts is spoken slightly faster
rather than clipped, down to a floor of length_scale 0.80. Below that the tool
tells you instead of quietly mangling the read — fix the script, not the speed.

    VOICE=en-gb-alan-low SCRIPT=... python3 narrate_scene.py in.mp4 out.mp4

Models come from the GitHub release mirror because HuggingFace is blocked by
the render container's egress policy — see MODELS below for what that costs.
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
CACHE = os.path.join(os.path.expanduser("~"), ".cache", "observer-voice")

# VOICE picks the model. en-us-ryan-medium is the default: it is 22kHz against
# alan-low's 16k, and the difference is audible in the consonants.
#
# The reason it is not Alan: only alan-LOW exists on the GitHub release mirror,
# and "low" is the quality tier, not a description. en_GB-alan-medium lives on
# HuggingFace, which the render container's egress policy blocks. On a machine
# with HuggingFace reachable, point MODELS at
#   .../rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/...
# and the British voice comes back several tiers better than the original.
MODELS = {
    "en-us-ryan-medium":  ("voice-en-us-ryan-medium",  22050),
    "en-us-ryan-high":    ("voice-en-us-ryan-high",    22050),
    "en-us-libritts-high": ("voice-en-us-libritts-high", 22050),
    "en-us-lessac-medium": ("voice-en-us-lessac-medium", 16000),
    "en-gb-alan-low":     ("voice-en-gb-alan-low",     16000),
}
VOICE = os.environ.get("VOICE", "en-us-ryan-medium")
MODEL = f"{VOICE}.onnx"
MODEL_URL = ("https://github.com/rhasspy/piper/releases/download/v0.0.2/"
             f"{MODELS[VOICE][0]}.tar.gz")
PIPER_SR = MODELS[VOICE][1]

# 1.18 was Alan's pace, inherited from OIS narrate.py where it is right for a
# watcher inside a story. For an explainer it just sounds tired — the first cut
# of this took 22.4s to say what now takes 15.8s, and a third of the runtime was
# dead air. 1.00 plus per-line variation is the fix.
LENGTH_SCALE = float(os.environ.get("PACE", 1.00))

# ---------------------------------------------------------------------------
# The reads. SCRIPT picks one:  SCRIPT=not_calculating python3 narrate_scene.py ...
#
# SPARSE ON PURPOSE. The first draft of the first one narrated every cut and it
# does not fit: cuts land ~1.2s apart and a spoken line needs 2-3s, so
# wall-to-wall VO either clips or forces the animation to crawl. That is the
# same conclusion OIS narrate.py reached — a few spoken lines carrying the
# searchable phrasing, not a documentary track. The on-screen text says the
# numbers; Alan says the meaning; the silence between them is the pacing.
#
# Keep the searchable words spoken aloud — the transcriber indexes them.
# ---------------------------------------------------------------------------
SCRIPTS = {
    # (start_seconds, text, pace).  pace < 1 punches, > 1 gives weight.
    # A single flat pace across every line is what makes a read sound bored,
    # and it is a bigger problem than the model.
    "lost_in_the_middle": [
        (0.30, "Every model claims it reads a million words of context.", 1.00),
        (10.75, "Nobody computes a trillion. So they don't.", 0.90),
        (14.35, "A benchmark called RULER tested seventeen long context models.", 1.02),
        (18.80, "All seventeen degraded.", 0.86),
        (20.60, "And the damage is not spread evenly.", 0.94),
        (23.00, "The beginning is remembered. So is the end.", 1.00),
        (25.80, "Put what matters at the start, or at the end. Never the middle.", 1.06),
    ],
    "not_calculating": [
        (0.40, "No model gets this wrong.", 0.88),
        (2.70, "What it does get wrong is stranger.", 0.96),
        (5.20, "Ask GPT-4 for three digit multiplication. "
               "It is right about fifty nine percent of the time.", 1.02),
        (11.20, "Add one digit. Four percent.", 0.86),
        (14.00, "Nothing about the arithmetic got harder.", 0.94),
        (17.00, "It never sees the number. A tokenizer splits it where language "
                "is common, not where place value is.", 1.02),
        (23.50, "And it cannot carry. You repeat a step until you are done. "
                "A transformer runs the same fixed stack every time.", 1.02),
        (32.60, "So it is not computing the answer. "
                "It is predicting what an answer looks like.", 1.06),
    ],
    "illusion_of_logic": [
        (0.40, "No model gets this wrong.", 0.88),
        (3.20, "But ask it to multiply two four digit numbers, "
               "and it fails ninety six percent of the time.", 1.00),
        (10.60, "Ask GPT-4 for three digit multiplication. "
                "It is right about fifty nine percent of the time.", 1.02),
        (17.00, "Add one digit. Four percent.", 0.86),
        (21.50, "You have an algorithm. Carry, shift, carry, shift. "
                "Bigger number, more steps.", 0.94),
        (32.50, "It never sees the number. A tokenizer splits it where "
                "language is common, not where place value is.", 1.02),
        (43.50, "What it learned instead is a neighbourhood. Words that appear "
                "in the same places sit close together.", 1.00),
        (52.00, "That works beautifully for language. Numbers have no "
                "neighbours.", 0.94),
        (58.00, "And it cannot think for longer. Two plus two gets the same "
                "stack of layers as four thousand times six thousand.", 1.02),
        (68.00, "So it ranks what an answer would look like, and picks the top "
                "one. It never multiplied anything.", 0.98),
        (81.00, "Our intelligence looks for truth by following rules. "
                "Its intelligence looks for what usually comes next.", 1.06),
    ],
}

LINES = SCRIPTS[os.environ.get("SCRIPT", "lost_in_the_middle")]


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
    for i, line in enumerate(LINES):
        at, text = line[0], line[1]
        pace = line[2] if len(line) > 2 else 1.0
        nxt = LINES[i + 1][0] if i + 1 < len(LINES) else total
        room = nxt - at
        base = LENGTH_SCALE * pace
        sig = speak(text, length_scale=base)
        scale = base
        if len(sig) / SR > room:                   # too long: say it a little quicker
            want = max(0.80, base * room / (len(sig) / SR))
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
        print(f"voice = {VOICE}   base pace = {LENGTH_SCALE}")
        print(f"{'at':>6}  gap  pace  line")
        for i, line in enumerate(LINES):
            at, text = line[0], line[1]
            pace = line[2] if len(line) > 2 else 1.0
            nxt = LINES[i + 1][0] if i + 1 < len(LINES) else end + 3
            print(f"{at:6.2f} {nxt - at:5.2f} {pace:5.2f}  {text[:52]}")
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
