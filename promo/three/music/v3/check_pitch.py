"""Measure what pitch each VSCO 2 instrument's samples REALLY sound at.

    python3 check_pitch.py /path/to/VSCO-2-CE

VSCO names most instruments with middle C = C3, so a file called A2 sounds
A3. Trusting the names played strings, clarinet, horn and marimba an octave
too high. This YIN estimate is what produce_v3.py's OCTAVE_FIX table is
built from: +12 for everything measured here except the harp (0)."""
import glob, os, re, sys
import numpy as np, soundfile as sf
LIB = sys.argv[1]
PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}

def f0(path):
    x, sr = sf.read(path, always_2d=True); m = x.mean(1)
    a = int(np.argmax(np.abs(m) > np.abs(m).max() * 0.1))
    seg = m[a + int(0.15 * sr): a + int(0.40 * sr)]
    if len(seg) < 2048: seg = m[a: a + 8192]
    seg = seg - seg.mean(); W = len(seg) // 2
    d = np.array([np.sum((seg[:W] - seg[t:t + W]) ** 2) for t in range(1, W)])
    cmnd = d * np.arange(1, W) / np.cumsum(d); lo, hi = int(sr / 1200), int(sr / 25)
    under = np.where(cmnd[lo:hi] < 0.15)[0]
    tau = lo + (under[0] if len(under) else int(np.argmin(cmnd[lo:hi])))
    while tau + 1 < hi and cmnd[tau + 1] < cmnd[tau]: tau += 1
    return sr / (tau + 1)

for d in ["Strings/Violin Section/susVib", "Strings/Viola Section/susvib", "Strings/Cello Section/susvib",
          "Strings/Cello Section/spic", "Strings/Solo Contrabass/SusNV", "Woodwinds/Clarinet/susLong",
          "Brass/F Horn/sus", "Strings/Harp", "Percussion/Marimba"]:
    files = sorted(glob.glob(os.path.join(LIB, d, "*.wav"))); out = []
    for p in files[:: max(1, len(files) // 5)][:5]:
        n = re.search(r"_([A-G]#?)(-?\d)_", os.path.basename(p)); named = 12 * (int(n.group(2)) + 1) + PC[n.group(1)]
        out.append(round(69 + 12 * np.log2(f0(p) / 440) - named))
    print(f"{d:34s} measured minus named (semitones): {out}")
