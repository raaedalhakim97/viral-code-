"""Measure the overtone strengths of real recorded A3s (220 Hz): one per instrument.
These numbers become the vector chains on screen. VSCO names strings/horn/clarinet an
octave low (file 'A2' sounds A3, checked in promo/three/music/v3/check_pitch.py); the
upright piano's file index NNN is MIDI 21 + 2*NNN, so A3 = 018."""
import json, sys
import numpy as np, soundfile as sf
LIB = sys.argv[1]
FILES = {"piano": "Keys/Upright Piano/Player_dyn2_rr1_018.wav",
         "violin": "Strings/Violin Section/susVib/VlnEns_susVib_A2_v2.wav",
         "cello": "Strings/Cello Section/susvib/susvib_A2_v3_1.wav",
         "horn": "Brass/F Horn/sus/MOHorn_sus_A2_v2_1.wav",
         "clarinet": None}
import glob
cl = sorted(glob.glob(f"{LIB}/Woodwinds/Clarinet/*/*A2*.wav")) + sorted(glob.glob(f"{LIB}/Woodwinds/Clarinet/*A2*.wav"))
if cl: FILES["clarinet"] = cl[0][len(LIB) + 1:]
out = {}
for name, rel in FILES.items():
    if not rel: continue
    x, sr = sf.read(f"{LIB}/{rel}", always_2d=True); x = x.mean(1)
    env = np.abs(x); s0 = int(np.argmax(env > env.max() * 0.05))
    seg = x[s0 + int(0.25 * sr): s0 + int(0.85 * sr)]
    seg = seg * np.hanning(len(seg)); F = np.abs(np.fft.rfft(seg, 1 << 18)); fr = np.fft.rfftfreq(1 << 18, 1 / sr)
    band = (fr > 150) & (fr < 300); f0 = fr[band][np.argmax(F[band])]
    amps = []
    for k in range(1, 13):
        w = (fr > k * f0 * 0.97) & (fr < k * f0 * 1.03); amps.append(float(F[w].max()))
    amps = np.array(amps) / max(amps)
    out[name] = {"file": rel, "f0": round(float(f0), 2), "harmonics": [round(float(a), 4) for a in amps]}
    print(f"{name:9s} f0={f0:7.2f} Hz  " + " ".join(f"{a:.2f}" for a in amps))
json.dump(out, open("harmonics.json", "w"), indent=1)
