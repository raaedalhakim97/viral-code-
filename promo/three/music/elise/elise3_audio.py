"""Render elise3_score.json (the F major second part, then the chord part) with real recorded instruments (VSCO 2 CE, CC0; upright piano by Simon Dalzell).
The score is offset by T0 = 2.5 s: the video writes its first equation before the first E sounds.
usage: python3 elise_audio.py <vsco path> <score.json> <out.wav>"""
import glob, json, os, re, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

LIB, SCORE, OUT = sys.argv[1:4]
SR = 48000; T0 = 2.5
score = json.load(open(SCORE)); EV = score["events"]
DUR = round(score["end"] + T0 + 3.5, 2); N = int(DUR * SR); t = np.arange(N) / SR
PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
_cache = {}
def load(p):
    if p not in _cache:
        x, sr = sf.read(p, always_2d=True, dtype="float32"); x = x[:, :2] if x.shape[1] > 1 else np.repeat(x, 2, 1)
        env = np.abs(x).max(1); s0 = max(0, int(np.argmax(env > env.max() * 0.008)) - int(0.003 * sr)); _cache[p] = (x[s0:], sr)
    return _cache[p]
def index(folder, fix):                     # VSCO names these an octave low: file "A2" sounds A3 (measured)
    out = {}
    for p in glob.glob(os.path.join(LIB, folder, "*.wav")):
        m = re.search(r"_([A-G]#?)(-?\d)_v(\d)", os.path.basename(p))
        if m: out.setdefault(12 * (int(m.group(2)) + 1) + PC[m.group(1)] + fix, []).append((int(m.group(3)), p))
    return out
def piano(dyn):                             # Player_dynN_rr1_NNN.wav is MIDI 21 + 2*NNN
    return {21 + 2 * int(re.search(r"_(\d{3})\.wav", p).group(1)): [(1, p)] for p in glob.glob(os.path.join(LIB, f"Keys/Upright Piano/Player_dyn{dyn}_rr1_*.wav"))}
INST = {"RH": piano(2), "LH": piano(2), "STR": index("Strings/Violin Section/susVib", 12),
        "VC": index("Strings/Cello Section/susvib", 12), "HN": index("Brass/F Horn/sus", 12)}
VIOLA = index("Strings/Viola Section/susvib", 12)
def play(idx, note, dur, vel=2, attack=0.004, release=0.5):
    src = min(idx, key=lambda s: abs(s - note)); p = min(idx[src], key=lambda vp: abs(vp[0] - vel))[1]; x, sr = load(p)
    ratio = 2 ** ((note - src) / 12) * sr / SR
    n = int((dur + release) * SR); pos = np.arange(n) * ratio; pos = pos[pos < len(x) - 1]
    i0 = pos.astype(int); fr = (pos - i0)[:, None]; y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    tt = np.arange(len(y)) / SR; env = np.minimum(1, tt / attack) * np.where(tt < dur, 1, np.clip(1 - (tt - dur) / release, 0, 1))
    return y * env[:, None]
bus = {k: np.zeros((N, 2)) for k in ("piano", "strings", "low", "horn")}
def place(b, y, t0, gain, pan=0.0):
    a = int(t0 * SR); e = min(N, a + len(y))
    if a >= N: return
    lg, rg = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    bus[b][a:e, 0] += y[: e - a, 0] * gain * lg; bus[b][a:e, 1] += y[: e - a, 1] * gain * rg

PERC = os.path.join(LIB, "Percussion")
ROLL = sorted(glob.glob(os.path.join(PERC, "bassdrum_rub*.wav"))); HIT = sorted(glob.glob(os.path.join(PERC, "BDrumNewhit_v4_rr*_Sum.wav")))
bus["drum"] = np.zeros((N, 2))
for i, e in enumerate(EV):
    v, m, t0, d = e["voice"], e["midi"], e["t"] + T0, e["dur"]
    if v == "DR":                                                         # soft orchestral bass drum: a roll that swells, or one hit
        if e["kind"] == "H":
            x, sr = load(HIT[i % len(HIT)]); y = x[: int(2.5 * sr)]
            place("drum", sosfilt(butter(2, 900, fs=SR, output="sos"), y, axis=0), t0, 0.55)
        else:
            x, sr = load(ROLL[i % len(ROLL)]); n = min(len(x), int((d + 0.4) * SR)); y = x[:n].copy()
            tt = np.arange(n) / SR; y *= ((tt / d) ** 1.6 * np.clip(1 - (tt - d) / 0.4, 0, 1))[:, None]   # up, then gone
            place("drum", y, t0, 0.9)
        continue
    if v in ("RH", "LH"):
        nxt = next((o["t"] for o in EV[i + 1:] if o["midi"] == m and o["voice"] == v), 1e9) + T0
        ring = min(nxt - t0, d + 0.9)                                     # the pedal: notes ring past their length
        g = (0.55 if m <= 84 else 0.36) if v == "RH" else 0.42                 # the high sweep stays soft
        place("piano", play(INST[v], m, ring, release=0.25), t0, g, -0.15 if v == "LH" else 0.12)
    elif v == "STR":                                                      # violins on top, violas below
        idx = INST["STR"] if m >= 59 else VIOLA
        place("strings", play(idx, m, d + 0.05, vel=1, attack=0.18, release=0.45), t0, 0.34, -0.4 + 0.08 * (m - 56))
    elif v == "VC":
        place("low", play(INST["VC"], m, d + 0.05, vel=2, attack=0.12, release=0.5), t0, 0.68, 0.2)
    elif v == "HN":
        place("horn", play(INST["HN"], m, d + 0.05, vel=1, attack=0.15, release=0.5), t0, 0.42, 0.3)
# orchestra swells with the sections (smooth curves, never steps)
sm = lambda x: (lambda y: y * y * (3 - 2 * y))(np.clip(x, 0, 1))
secs = {s["name"] + str(i): s["t"] + T0 for i, s in enumerate(score["sections"])}
# the orchestra swells into the episode's cascade, settles for the trill, then builds through the chord part
sec = {x["name"].split()[0]: x["t"] + T0 for x in score["sections"]}
B0, C0, W0 = sec["Second"], sec["The"] if "The" in sec else 0, 0
C0 = next(x["t"] for x in score["sections"] if "chord" in x["name"]) + T0; W0 = next(x["t"] for x in score["sections"] if "sweep" in x["name"]) + T0
BAR, CBAR = 60 / 50, 60 / 54
orch = (0.8 + 0.6 * sm((t - (B0 + 3 * BAR)) / (4 * BAR)) * (1 - sm((t - (B0 + 11 * BAR)) / (1.5 * BAR)))
        + 0.55 * sm((t - C0) / (8 * CBAR)) * (1 - sm((t - (W0 - 2 * CBAR)) / (3 * CBAR))))
for b in ("strings", "low", "horn"): bus[b] *= orch[:, None]
# the piano and the orchestra are reverberated separately, so the orchestra can be turned down
# without moving the piano: the output is scaled exactly as the full-orchestra mix would be
# orchestra gain: a number, or "musical": about -10 dB under the melody, lifting to about -8 dB
# for the cascade and the heaviest chords of the chord part, always on smooth curves
ARG = sys.argv[4] if len(sys.argv) > 4 else "1.0"
if ARG == "musical":
    bt = [b + T0 for b in score["bars"]]
    swell = lambda a, b, fi, fo: sm((t - a) / fi) * (1 - sm((t - (b - fo)) / fo))
    ORCH = (0.31 + 0.09 * swell(bt[7], bt[11], 1.2, 1.0) + 0.09 * swell(bt[25], bt[30], 1.0, 1.5))[:, None]
else:
    ORCH = float(ARG)
piano = bus["piano"]; orch_dry = bus["strings"] + bus["low"] + bus["horn"] + bus["drum"]
L = int(2.6 * SR); tt = np.arange(L) / SR; rng = np.random.default_rng(5)
ir = rng.standard_normal((L, 2)) * np.exp(-6.9 * tt / 2.6)[:, None]
ir = sosfilt(butter(2, 6000, fs=SR, output="sos"), ir, axis=0); ir[: int(0.018 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
verb = lambda x: x + 0.3 * np.stack([fftconvolve(x[:, c], ir[:, c])[:N] for c in (0, 1)], 1)
fade = (1 - sm((t - (DUR - 1.2)) / 1.2))[:, None]
p_mix, o_mix = verb(piano) * fade, verb(orch_dry) * fade
ref = 0.89 / np.abs(p_mix + o_mix).max()                       # the full-orchestra mix's scale
mix = (p_mix + ORCH * o_mix) * ref
sf.write(OUT, mix.astype(np.float32), SR, subtype="PCM_24")
print("orchestra gain:", ARG)
print("wrote", OUT, f"{DUR}s")
