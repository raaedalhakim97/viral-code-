"""Voiceover for Part II, from the brief's script and timestamps. Piper (free,
offline, en-us-ryan-high). Every line must end before the next one starts;
if one would not fit, it is sped up by at most 8%, otherwise the build fails."""
import subprocess, json, soundfile as sf, numpy as np
import os
PIPER = os.environ.get("PIPER", "libs/piper")      # piper release 2023.11.14-2 + en_US-ryan-high voice
LINES = [
 (0.0,  "In Part One, we placed two thousand, one hundred and forty-four points on a curve."),
 (5.0,  "But a point doesn't move on its own."),
 (9.0,  "Something has to move it. Something has to weight it."),
 (13.0, "This is the weight. We call it theta."),
 (18.0, "Every word has thirty-two weights. Every weight is a wave."),
 (25.0, "On its own, a wave is flat. It carries no meaning."),
 (31.0, "Two waves meet. They add. They subtract. They interfere."),
 (37.0, "This is superposition."),
 (42.0, "Thirty-two waves, stacked, become one word."),
 (48.0, "The peak of that stack tells us where the word lives."),
 (54.0, "But the peaks are wrong. The word sits in the wrong place."),
 (60.0, "So we adjust theta. Wave by wave. Weight by weight."),
 (66.0, "Watch the bloom. The waves converge."),
 (73.0, "The peak lands where it belongs."),
 (80.0, "This is what training actually does."),
 (86.0, "Not magic. Not understanding. Geometry."),
 (89.3, "And in Part Three, we ask: what happens when the waves learn to teach each other?"),
]
SR = 48000; out = []
for i, (t0, text) in enumerate(LINES):
    raw = f"vo/l{i:02d}_raw.wav"
    subprocess.run([f"{PIPER}/bin/piper/piper", "--model", f"{PIPER}/voice/en-us-ryan-high.onnx", "--length_scale", "1.04",
                    "--sentence_silence", "0.25", "--output_file", raw], input=text.encode(), check=True, capture_output=True)
    x, sr = sf.read(raw)
    lead = np.argmax(np.abs(x) > 0.01); tail = len(x) - np.argmax(np.abs(x[::-1]) > 0.01)
    x = x[max(0, lead - int(0.02 * sr)): tail + int(0.08 * sr)]
    d = len(x) / sr
    nxt = LINES[i + 1][0] if i + 1 < len(LINES) else 95.0
    room = nxt - t0 - 0.25
    tempo = 1.0
    if d > room:
        tempo = d / room
        assert tempo <= 1.08, f"line {i} needs {tempo:.2f}x to fit: {text}"
    out.append({"i": i, "t0": t0, "dur": d / tempo, "tempo": round(tempo, 3), "room": round(room, 2), "file": raw, "text": text})
    print(f"{t0:5.1f}s  {d:4.2f}s (room {room:4.2f}s) tempo {tempo:.2f}  {text}")
json.dump(out, open("vo_lines.json", "w"), indent=1)
