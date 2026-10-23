# Checks the sound lands on the picture: level just before vs just after each sync point,
# and that the two ends of the music match for the loop seam.
import sys
import numpy as np, soundfile as sf

x, SR = sf.read(sys.argv[1] if len(sys.argv) > 1 else "ww_music.wav"); x = x.mean(1)
db = lambda a, b: 20 * np.log10(np.sqrt(np.mean(x[int(a * SR):int(b * SR)] ** 2)) + 1e-9)
for name, t in [("theta piano", 6.4), ("first tick", 12.3), ("tones", 20.0), ("cello", 28.0), ("glides", 35.0),
                ("unison/strings", 44.0), ("rub", 59.0), ("pulse 1", 66.0), ("pulse 8", 68.8),
                ("silence", 73.5), ("C6 burst", 75.0), ("C major", 80.0)]:
    print(f"{name:16s} {t:6.2f}s  before {db(t - 0.3, t - 0.02):6.1f} dB  after {db(t + 0.01, t + 0.25):6.1f} dB")
print(f"loop seam: first 1s {db(0, 1):.1f} dB, last 1s {db(len(x) / SR - 1, len(x) / SR):.1f} dB")
print(f"silence 73.6-74.9 s vs bed 70-72 s: {db(73.6, 74.9) - db(70, 72):.1f} dB")
