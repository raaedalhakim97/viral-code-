"""SMART LOOKUP Part II: sound design + score, built to the brief's spec.

Timings mirror scene_weighted_wave.js. Real instruments are VSCO 2 CE samples
(CC0; upright piano by Simon Dalzell / Ivy Audio, via Versilian Studios); the
hum, ticks, tones, glides and sub hits are synthesised. Writes:
    ww_music.wav   music + sound design, no voice
    ww_mix.wav     the same with the voiceover on top, music ducked under it
"""
import glob, json, os, re, sys
import numpy as np, soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

LIB = sys.argv[1]
SR = 48000; DUR = 95.0; N = int(DUR * SR); t = np.arange(N) / SR
rng = np.random.default_rng(2)
sm = lambda x: (lambda y: y * y * (3 - 2 * y))(np.clip(x, 0, 1))
win = lambda a, fi, fo, b: sm((t - a) / fi) * (1 - sm((t - (b - fo)) / fo))
music = np.zeros((N, 2)); synth = np.zeros((N, 2))

# ---------------------------------------------------------------- samples
PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
_cache = {}
def load(p):
    if p not in _cache:
        x, sr = sf.read(p, always_2d=True, dtype="float32"); x = x[:, :2] if x.shape[1] > 1 else np.repeat(x, 2, 1)
        env = np.abs(x).max(1); s0 = max(0, int(np.argmax(env > env.max() * 0.008)) - int(0.004 * sr)); _cache[p] = (x[s0:], sr)
    return _cache[p]
def index(folder, fix):                 # VSCO names strings with middle C = C3: +12 (measured, see check_pitch.py)
    out = {}
    for p in glob.glob(os.path.join(LIB, folder, "*.wav")):
        m = re.search(r"_([A-G]#?)(-?\d)_v(\d)", os.path.basename(p))
        if m: out.setdefault(12 * (int(m.group(2)) + 1) + PC[m.group(1)] + fix, []).append((int(m.group(3)), p))
    return out
VC = index("Strings/Cello Section/susvib", 12); VLA = index("Strings/Viola Section/susvib", 12)
VLN = index("Strings/Violin Section/susVib", 12); SPIC = index("Strings/Cello Section/spic", 12)
PIANO = {21 + 2 * int(re.search(r"_(\d{3})\.wav", p).group(1)): p for p in glob.glob(os.path.join(LIB, "Keys/Upright Piano/Player_dyn2_rr1_*.wav"))}
PIANO3 = {21 + 2 * int(re.search(r"_(\d{3})\.wav", p).group(1)): p for p in glob.glob(os.path.join(LIB, "Keys/Upright Piano/Player_dyn3_rr1_*.wav"))}

def place(bus, y, t0, gain=1.0, pan=0.0):
    a = int(t0 * SR); b = min(N, a + len(y))
    if a >= N or b <= 0: return
    lg, rg = np.cos((pan + 1) * np.pi / 4) * 1.414, np.sin((pan + 1) * np.pi / 4) * 1.414
    bus[a:b, 0] += y[: b - a, 0] * gain * lg; bus[a:b, 1] += y[: b - a, 1] * gain * rg
def play(idx, note, dur, vel=2, release=0.6):
    if isinstance(idx, dict) and isinstance(next(iter(idx.values())), str):
        src = min(idx, key=lambda s: abs(s - note)); x, sr = load(idx[src])
    else:
        src = min(idx, key=lambda s: abs(s - note)); lay = sorted(idx[src]); p = min(lay, key=lambda vp: abs(vp[0] - vel))[1]; x, sr = load(p)
    ratio = 2 ** ((note - src) / 12) * sr / SR
    n = int((dur + release) * SR); pos = np.arange(n) * ratio; pos = pos[pos < len(x) - 1]
    i0 = pos.astype(int); fr = (pos - i0)[:, None]; y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    tt = np.arange(len(y)) / SR; env = np.minimum(1, tt / 0.05) * np.where(tt < dur, 1, np.clip(1 - (tt - dur) / release, 0, 1))
    return y * env[:, None]
def sustain(idx, note, t0, t1, gain, pan=0.0, vel=2, fade_in=1.0):
    """hold a note longer than any one sample: overlapping takes, crossfaded"""
    seg, xf = 5.0, 1.6; s = t0
    while s < t1:
        d = min(seg + xf, t1 - s + 0.8); y = play(idx, note, d, vel, release=0.8)
        tt = np.arange(len(y)) / SR
        e = np.minimum(1, tt / (fade_in if s == t0 else xf))
        place(music, y * e[:, None], s, gain, pan); s += seg

# ---------------------------------------------------------------- 45 Hz hum: Part I continuity, both ends equal (loop seam)
# a bed, not a drone: it sits ~10 dB under the instruments, nearly vanishes for the 73-75 s
# silence, and the 86 s lift falls back before the seam so frame 0 and the last frame match
hum_level = 0.032 * (1 + 0.26 * win(6.0, 1.2, 2.0, 12.0)) * (1 - 0.85 * win(73.0, 0.3, 0.4, 75.0)) * (1 + 0.3 * win(86.0, 2.0, 1.7, 93.3))
hum = (np.sin(2 * np.pi * 45 * t) + 0.3 * np.sin(2 * np.pi * 90 * t + 0.4)) * (1 + 0.06 * np.sin(2 * np.pi * 0.11 * t))
synth += (hum * hum_level)[:, None]

# 0:06 a single piano note as theta blooms
place(music, play(PIANO, 72, 3.5, release=1.5), 6.4, 0.55, 0.1)

# 0:12 32 ticks rising, one per bar: 440 + 35k Hz
for k in range(32):
    tk = 12.3 + 0.19 * k; f = 440 + 35 * k; L = int(0.25 * SR); tt = np.arange(L) / SR
    y = np.sin(2 * np.pi * f * tt) * np.minimum(1, tt / 0.003) * np.exp(-tt / 0.07)
    place(synth, np.stack([y, y], 1), tk, 0.05, -0.6 + 1.2 * k / 31)
# 0:20 tick -> tone x32: each bar's tick becomes a held tone as the bar becomes its wave
for k in range(32):
    t0 = 20.0 + 0.06 * k; f = 440 + 35 * k
    y = np.sin(2 * np.pi * f * (t - t0) + rng.random() * 6.28) * win(t0, 0.8, 1.6, 28.6) * (t >= t0)
    synth += (y * 0.010)[:, None] * np.array([1 - k / 62, 0.5 + k / 62])
# 0:28 one sustained cello note (G2), resolving to C at 0:44
sustain(VC, 43, 28.0, 44.4, 0.85, 0.15, vel=2, fade_in=2.0)
sustain(VC, 36, 44.0, 60.0, 0.9, 0.15, vel=2, fade_in=0.4)
# 0:35 two pure tones: one rises from 260 Hz, one falls from 390 Hz (a fifth: 3:2). They pass
# through a minor third (6:5) at ~40 s and meet in unison at 0:44: the resolution
u = np.clip((t - 35.0) / 9.0, 0, 1); env = win(35.0, 1.0, 0.8, 45.0)
fa = 260 + 70 * sm(u); fb = 390 - 60 * sm(u)
vib = 1 + 0.003 * np.sin(2 * np.pi * 4.6 * t)
ga = np.sin(2 * np.pi * np.cumsum(fa * vib) / SR); gb = np.sin(2 * np.pi * np.cumsum(fb * vib) / SR)
synth[:, 0] += ga * env * 0.05 + gb * env * 0.03; synth[:, 1] += gb * env * 0.05 + ga * env * 0.03
# 0:44 strings enter; 0:52 full pad
for n_ in (48, 55): sustain(VLA, n_, 44.2, 59.2, 0.45, -0.2, vel=1, fade_in=2.0)
for n_ in (62, 64): sustain(VLN, n_, 52.0, 59.2, 0.32, -0.45, vel=1, fade_in=2.5)
# 0:59 the problem: three notes rubbing (E, F, F#), flickering with the curve
rub = np.zeros((N, 2)); bak = music; music = rub
for n_ in (64, 65, 66): sustain(VLN if n_ > 64 else VLA, n_, 59.0, 66.2, 0.33, -0.3 + 0.3 * (n_ - 64), vel=1, fade_in=1.0)
music = bak; music += rub * (1 - 0.3 * (0.5 + 0.5 * np.sin(t * 7.3) * np.sin(t * 3.1)))[:, None]
# 1:06 training: a bass pulse every 0.4 s, 8 of them, getting warmer
for n_ in range(8):
    th = 66.0 + 0.4 * n_; L = int(0.9 * SR); tt = np.arange(L) / SR
    f = 42 + 18 * np.exp(-tt / 0.05); kick = np.tanh(1.8 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * np.exp(-tt / 0.28)
    warm = 0.55 + 0.45 * n_ / 7
    place(synth, np.stack([kick, kick], 1), th, 0.15 * warm)
    sp = play(SPIC, 36, 0.4, vel=1 + (n_ > 3), release=0.3)
    cut = 250 * (900 / 250) ** (n_ / 7)                                     # warmer = more of the body comes through
    sp = sosfilt(butter(2, cut, fs=SR, output="sos"), sp, axis=0)
    place(music, sp, th, 0.9 * warm, 0.1)
sustain(VC, 36, 69.2, 73.2, 0.55, 0.15, vel=1, fade_in=1.5)
for n_ in (55, 64): sustain(VLA, n_, 69.6, 73.2, 0.3, -0.2, vel=1, fade_in=2.0)
# 1:15 after two seconds of near-silence, one piano note: C6, bright, decaying over 1.6 s
c6 = play(PIANO3, 84, 2.2, release=0.4); tt = np.arange(len(c6)) / SR
place(music, c6 * np.exp(-tt / 0.55)[:, None], 75.0, 0.95, 0.0)
# 1:20 resolution: C major, spread across the piano, fading; strings beneath
for i, n_ in enumerate((48, 55, 64, 72)):
    place(music, play(PIANO, n_, 5.0, release=1.5), 80.0 + 0.11 * i, 0.5, -0.3 + 0.2 * i)
for n_, g in ((48, 0.4), (55, 0.35)): sustain(VLA, n_, 80.0, 86.5, g, -0.2, vel=1, fade_in=1.0)
sustain(VLN, 64, 80.3, 86.5, 0.3, -0.45, vel=1, fade_in=1.2)
sustain(VC, 36, 80.0, 90.5, 0.6, 0.15, vel=1, fade_in=1.0)

# ---------------------------------------------------------------- the two seconds of near-silence before the C6
quiet = 1 - 0.96 * win(73.0, 0.35, 0.05, 75.0)
music *= quiet[:, None]                                                      # (the hum is already lowered there)

# ---------------------------------------------------------------- reverb and stems
L = int(2.8 * SR); tt = np.arange(L) / SR
ir = rng.standard_normal((L, 2)) * np.exp(-6.9 * tt / 2.8)[:, None]
ir = sosfilt(butter(2, 5000, fs=SR, output="sos"), ir, axis=0); ir[: int(0.015 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
wet = np.stack([fftconvolve(music[:, c] + 0.5 * synth[:, c], ir[:, c])[:N] for c in (0, 1)], 1)
bed = music + synth + 0.32 * wet
bed *= (sm(t / 0.02))[:, None]
sf.write("ww_music.wav", (bed / np.abs(bed).max() * 0.89).astype(np.float32), SR, subtype="PCM_24")

# ---------------------------------------------------------------- voice on top, music ducked under it
vo = np.zeros(N)
for ln in json.load(open("vo_lines.json")):
    x, sr = sf.read(ln["file"]); x = x if x.ndim == 1 else x.mean(1)
    if sr != SR: x = np.interp(np.arange(int(len(x) * SR / sr)) * sr / SR, np.arange(len(x)), x)
    a = int(ln["t0"] * SR); b = min(N, a + len(x)); vo[a:b] += x[: b - a]
vo = sosfilt(butter(2, 90, btype="high", fs=SR, output="sos"), vo)
act = fftconvolve((np.abs(vo) > 0.01).astype(float), np.ones(int(0.25 * SR)) / int(0.25 * SR), mode="same")
duck = 1 - 0.5 * np.clip(act * 3, 0, 1)                                        # about -6 dB under the voice
mix = bed / np.abs(bed).max() * 0.6 * duck[:, None] + (vo / np.abs(vo).max() * 0.62)[:, None]
sf.write("ww_mix.wav", (mix / np.abs(mix).max() * 0.89).astype(np.float32), SR, subtype="PCM_24")
print("wrote ww_music.wav, ww_mix.wav")
