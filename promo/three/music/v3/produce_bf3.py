"""Render the Butterfly Effect v3 score (same engine as the Collatz v3 score) with real orchestral samples (VSCO 2 Community Edition,
CC0) and modern production on top. Free end to end.

  sampler     each voice's MIDI is played with VSCO recordings: nearest sampled
              pitch, resampled to the exact note, velocity layer from the
              dynamics, round-robins alternated so repeats are not identical,
              leading silence trimmed so attacks land on time.
  production  sub-bass drops and reversed cymbals into the big moments, a
              filtered noise riser, a soft detuned-saw pad, beat-synced
              sidechain pumping in the epic section, convolution reverb.
"""
import glob, json, os, re, sys
import numpy as np, soundfile as sf, mido
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
DUR = 40.0
N = int(DUR * SR)
LIB = sys.argv[1]
OUT = sys.argv[2] if len(sys.argv) > 2 else "butterfly_v3_mix.wav"
rng = np.random.default_rng(7)

PC = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
def nn(name):
    m = re.match(r"([A-G]#?)(-?\d)", name); return 12 * (int(m.group(2)) + 1) + PC[m.group(1)]

_cache = {}
def load(path):
    if path not in _cache:
        x, sr = sf.read(path, always_2d=True, dtype="float32")
        x = x[:, :2] if x.shape[1] >= 2 else np.repeat(x, 2, axis=1)
        env = np.abs(x).max(1); thr = env.max() * 10 ** (-42 / 20)
        start = max(0, int(np.argmax(env > thr)) - int(0.004 * sr))   # trim leading silence
        _cache[path] = (x[start:], sr)
    return _cache[path]

def index(folder, pat, octave_fix=0):
    """-> {midi: {layer: [paths (round robins)]}}

    octave_fix: VSCO names most instruments with middle C = C3, so the file
    called A2 actually sounds A3. Measured with a YIN pitch estimate on every
    instrument before trusting any name (see check_pitch.py); harp is the
    exception and is named in scientific pitch."""
    out = {}
    for p in sorted(glob.glob(os.path.join(LIB, folder, "*.wav"))):
        m = re.search(pat, os.path.basename(p))
        if not m: continue
        note = nn(m.group(1)) + octave_fix; lay = int(m.group(2)) if m.lastindex and m.lastindex >= 2 and m.group(2) else 1
        out.setdefault(note, {}).setdefault(lay, []).append(p)
    assert out, folder
    return out

INST = {   # folder, filename pattern (note, layer), attack, release, one-shot cap, gain, pan
 "vln":  ("Strings/Violin Section/susVib", r"_([A-G]#?\d)_v(\d)", 0.06, 0.55, None, 0.55, -0.35),
 "vla":  ("Strings/Viola Section/susvib",  r"_([A-G]#?\d)_v(\d)", 0.06, 0.55, None, 0.55, 0.20),
 "vc":   ("Strings/Cello Section/susvib",  r"_([A-G]#?\d)_v(\d)", 0.05, 0.50, None, 0.80, 0.35),
 "spic": ("Strings/Cello Section/spic",    r"_([A-G]#?\d)_v(\d)", 0.002, 0.10, 0.9, 0.62, 0.25),
 "cb":   ("Strings/Solo Contrabass/SusNV", r"_([A-G]#?\d)_v(\d)", 0.05, 0.60, None, 0.85, 0.45),
 "clar": ("Woodwinds/Clarinet/susLong",    r"_([A-G]#?\d)_v(\d)", 0.04, 0.35, None, 0.85, 0.05),
 "horn": ("Brass/F Horn/sus",              r"_([A-G]#?\d)_v(\d)", 0.03, 0.40, None, 0.80, -0.20),
 "harp": ("Strings/Harp",                  r"_([A-G]#?\d)_()",    0.001, 0.0, 3.5, 0.40, -0.45),
}
OCTAVE_FIX = {"vln": 12, "vla": 12, "vc": 12, "spic": 12, "cb": 12, "clar": 12, "horn": 12, "harp": 0, "mar": 12}
INDEX = {k: index(v[0], v[1], OCTAVE_FIX[k]) for k, v in INST.items()}
rr_state = {}

def render_note(k, note, vel, t_on, t_off, bus):
    folder, _, att, rel, cap, gain, pan = INST[k]
    idx = INDEX[k]
    src = min(idx, key=lambda s: (abs(s - note), s < note))          # nearest sample, prefer from below
    layers = sorted(idx[src]); li = layers[min(len(layers) - 1, int(vel / 128 * len(layers)))]
    paths = idx[src][li]; c = rr_state.get((k, src, li), 0); rr_state[(k, src, li)] = c + 1
    x, sr = load(paths[c % len(paths)])
    ratio = 2 ** ((note - src) / 12) * sr / SR                      # source samples per output sample
    hold = (t_off - t_on) if cap is None else cap
    n_out = int((hold + (rel if cap is None else 0)) * SR)
    pos = np.arange(n_out) * ratio
    pos = pos[pos < len(x) - 1]
    i0 = pos.astype(int); fr = (pos - i0)[:, None]
    y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    n = len(y); t = np.arange(n) / SR
    env = np.minimum(1, t / max(att, 1e-4))
    if cap is None:
        env *= np.where(t < hold, 1.0, np.clip(1 - (t - hold) / rel, 0, 1))
    else:
        env *= np.clip(1 - (t - (cap - 0.25)) / 0.25, 0, 1)
    y = y * env[:, None] * gain * (vel / 127) ** 1.5
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    a = int(t_on * SR); b = min(N, a + n)
    if a < N: bus[a:b, 0] += y[: b - a, 0] * lg * 1.414; bus[a:b, 1] += y[: b - a, 1] * rg * 1.414

def notes_of(path):
    m = mido.MidiFile(path); t = 0.0; on = {}; out = []
    for msg in m:
        t += msg.time
        if msg.type == "note_on" and msg.velocity > 0: on.setdefault(msg.note, []).append((t, msg.velocity))
        elif msg.type in ("note_off", "note_on") and on.get(msg.note):
            t0, v = on[msg.note].pop(0); out.append((t0, t, msg.note, v))
    return out

buses = {k: np.zeros((N, 2), np.float32) for k in ["strings", "winds", "keys", "perc", "synth", "clar", "rush"]}
BUS = {"vln": "strings", "vla": "strings", "vc": "strings", "spic": "strings", "cb": "strings",
       "clar": "clar", "horn": "winds", "harp": "keys"}
for k in INST:
    for (t0, t1, note, vel) in notes_of(f"voices/{k}.mid"):
        render_note(k, note, vel, t0, t1, buses[BUS[k]])
    print("rendered", k, flush=True)

# ---------------------------------------------------------------- timpani + percussion
def f0(x, sr):
    m = x.mean(1)[: int(0.6 * sr)]; F = np.abs(np.fft.rfft(m * np.hanning(len(m)))); f = np.fft.rfftfreq(len(m), 1 / sr)
    band = (f > 55) & (f < 260); return f[band][np.argmax(F[band])]
timps = [(p, f0(*load(p))) for p in sorted(glob.glob(os.path.join(LIB, "Percussion/Timpani/*Hit*.wav")))]
def one_shot(path, t_on, vel, gain, pan, bus, semis=0.0, cap=5.0):
    x, sr = load(path); ratio = 2 ** (semis / 12) * sr / SR
    pos = np.arange(int(cap * SR)) * ratio; pos = pos[pos < len(x) - 1]
    i0 = pos.astype(int); fr = (pos - i0)[:, None]; y = x[i0] * (1 - fr) + x[i0 + 1] * fr
    y = y * gain * (vel / 127) ** 1.4
    lg, rg = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    a = int(t_on * SR); b = min(N, a + len(y))
    if a < N: bus[a:b, 0] += y[: b - a, 0] * lg * 1.414; bus[a:b, 1] += y[: b - a, 1] * rg * 1.414
for (t0, t1, note, vel) in notes_of("voices/timp.mid"):
    hz = 440 * 2 ** ((note - 69) / 12)
    p, f = min(timps, key=lambda pf: abs(np.log2(pf[1] / hz)))       # the drum nearest in pitch, tuned to the note
    one_shot(p, t0, vel, 0.9, 0.0, buses["perc"], 12 * np.log2(hz / f))
PERC = {36: sorted(glob.glob(os.path.join(LIB, "Percussion/BDrumNewhit*.wav"))),
        49: sorted(glob.glob(os.path.join(LIB, "Percussion/cymbal-crash1_m*.wav"))),
        35: sorted(glob.glob(os.path.join(LIB, "Percussion/bassdrum_rub*.wav")))}
pc = {}
for (t0, t1, note, vel, bus) in [e + ("perc",) for e in notes_of("voices/perc.mid")] + [e + ("rush",) for e in notes_of("voices/rush.mid")]:
    lst = PERC[note]; c = pc.get(note, 0); pc[note] = c + 1
    if note == 36: lst = [p for p in lst if f"_v{min(7, 1 + vel * 7 // 128)}_" in p] or lst
    one_shot(lst[c % len(lst)], t0, vel, {36: 0.9, 49: 0.28, 35: 0.35}[note], 0.0, buses[bus], cap={49: 5, 36: 4, 35: 1.2}[note])
print("rendered percussion", flush=True)

# ---------------------------------------------------------------- sound design
t = np.arange(N) / SR
BAR = 4 * 60 / 76
HITS = [(4 * BAR, 0.85), (7 * BAR, 0.8), (9 * BAR + 2.5 * BAR / 4, 0.9), (11 * BAR, 1.0)]   # split, cloud, everywhere, title
syn = buses["synth"]
for (th, g) in HITS:                                       # sub-bass drop: 68 -> 38 Hz, felt more than heard
    a = int(th * SR); L = int(2.4 * SR); tt = np.arange(L) / SR
    fr = 38 + 30 * np.exp(-tt / 0.18); ph = 2 * np.pi * np.cumsum(fr) / SR
    s = np.tanh(1.6 * np.sin(ph)) * np.exp(-tt / 0.9) * np.minimum(1, tt / 0.004) * 0.55 * g
    b = min(N, a + L); syn[a:b] += s[: b - a, None]
crash = sorted(glob.glob(os.path.join(LIB, "Percussion/cymbal-crash1_ff*.wav")))[0]
cx, csr = load(crash)
for (th, g) in [(4 * BAR, 0.45), (7 * BAR, 0.35), (11 * BAR, 0.5)]:   # reversed cymbal swelling INTO the hit
    L = int(1.9 * csr); y = cx[:L][::-1] * np.linspace(0, 1, L)[:, None] ** 2
    y = np.stack([np.interp(np.arange(int(1.9 * SR)) * csr / SR, np.arange(L), y[:, ch]) for ch in (0, 1)], 1)
    a = int((th - 1.9) * SR); syn[a:a + len(y)] += y * g * 0.5
for (t0, t1, g) in [(4 * BAR - 3.0, 4 * BAR, 0.15), (HITS[2][0] - 3.0, HITS[2][0], 0.15)]:          # filtered noise riser
    L = int((t1 - t0) * SR); noise = rng.standard_normal((L, 2)).astype(np.float32)
    out = np.zeros_like(noise); steps = 24
    for i in range(steps):
        sl = slice(i * L // steps, (i + 1) * L // steps); fc = 250 * (3200 / 250) ** (i / (steps - 1))
        sos = butter(2, [fc * 0.7, fc * 1.3], btype="band", fs=SR, output="sos"); out[sl] = sosfilt(sos, noise[sl], axis=0)
    out *= (np.linspace(0, 1, L) ** 2.2)[:, None] * g
    a = int(t0 * SR); syn[a:a + L] += out
# detuned-saw pad under the strings, low-passed so it is warmth, not brightness
sys.path.insert(0, "."); import score_butterfly_v3 as S
pad = np.zeros((N, 2), np.float32)
for b, c in enumerate(S.CHORDS):
    if b < 4: continue                         # bars 1-4 stay acoustic: the two points, alone
    t0, bl = b * BAR, BAR; chord = c.split("|")[0]
    notes = S.V[chord][0] + S.V[chord][1]
    L = int((bl + 1.2) * SR); tt = np.arange(L) / SR; y = np.zeros(L, np.float32)
    for m in notes:
        f = 440 * 2 ** ((m - 69) / 12)
        for d in (-0.11, -0.05, 0.0, 0.06, 0.12):
            ph = (f * 2 ** (d / 12) * tt + rng.random()) % 1.0; y += (2 * ph - 1)
    y *= np.minimum(1, tt / 0.6) * np.clip(1 - (tt - bl) / 1.2, 0, 1) / (len(notes) * 5)
    a = int(t0 * SR); b2 = min(N, a + L)
    if a < N: pad[a:b2, 0] += y[: b2 - a]; pad[a:b2, 1] += np.roll(y, 37)[: b2 - a]
pad = sosfilt(butter(4, 1300, fs=SR, output="sos"), pad, axis=0).astype(np.float32) * 0.22

# ---------------------------------------------------------------- sidechain pump in the epic section
beat = 60 / 76
duck = np.ones(N, np.float32)
k = 0
while 7 * BAR + k * beat < 12 * BAR:             # the cloud and the title: gentle pumping on every beat
    a = int((7 * BAR + k * beat) * SR); L = int(beat * SR); tt = np.arange(L) / SR
    duck[a:a + L] = np.minimum(duck[a:a + L], 1 - 0.28 * np.exp(-tt / 0.11)); k += 1
for kname in ("strings", "keys"): buses[kname] *= duck[:, None]
pad *= duck[:, None]

# ---------------------------------------------------------------- the two curves you asked for
sm = lambda x: (lambda y: y * y * (3 - 2 * y))(np.clip(x, 0, 1))
win = lambda a, fi, fo, b: sm((t - a) / fi) * (1 - sm((t - (b - fo)) / fo))
clar_env = np.maximum(win(0.0, 3.0, 2.4, 12.9), win(12 * BAR, 0.7, 1.4, 40.0))   # fades in, fades out, twice
buses["clar"] *= clar_env[:, None]
bs = np.arange(0, 13) * BAR; kk = np.clip(np.searchsorted(bs, t, side="right") - 1, 0, 12)
since = t - bs[kk]                                 # the rush: peak ON the downbeat, fall away, swell into the next
shape = 0.22 + 0.78 * np.maximum((since / BAR) ** 2.2, np.exp(-since / 0.30))
level = np.interp(t, [0, 4 * BAR, 7 * BAR, 11 * BAR, 12 * BAR, 40], [0.30, 0.62, 0.75, 0.85, 0.7, 0.4])
buses["rush"] *= (shape * level)[:, None]

# ---------------------------------------------------------------- reverb (synthetic hall, 2.6 s)
L = int(2.6 * SR); tt = np.arange(L) / SR
ir = rng.standard_normal((L, 2)).astype(np.float32) * np.exp(-6.9 * tt / 2.6)[:, None]
ir = sosfilt(butter(2, 5200, fs=SR, output="sos"), ir, axis=0)
ir[: int(0.012 * SR)] = 0; ir /= np.sqrt((ir ** 2).sum(0))
SEND = {"strings": 0.38, "winds": 0.30, "keys": 0.34, "perc": 0.22, "synth": 0.20, "clar": 0.32, "rush": 0.18}
dry = sum(buses.values()) + pad
wet = np.zeros_like(dry)
for kname, s in SEND.items():
    src = buses[kname] + (pad if kname == "strings" else 0)
    for ch in (0, 1): wet[:, ch] += fftconvolve(src[:, ch], ir[:, ch])[:N] * s
mix = dry + wet * 0.9
mix *= (1 - np.clip((t - 38.0) / 2.0, 0, 1) ** 1.5)[:, None]
mix /= np.abs(mix).max() / 0.9
sf.write(OUT, mix, SR, subtype="PCM_24")
print("wrote", OUT)
