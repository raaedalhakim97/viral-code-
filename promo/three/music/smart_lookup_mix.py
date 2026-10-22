import json, wave, numpy as np
T = json.load(open("timeline.json")); SR = 48000; N = 95 * SR
def load(f):
    w = wave.open(f); x = np.frombuffer(w.readframes(w.getnframes()), dtype=np.int16).reshape(-1, 2).astype(float) / 32768
    out = np.zeros((N, 2)); out[:min(N, len(x))] = x[:N]; return out
o, c, d = load("orch.wav"), load("clar.wav"), load("drums.wav")
t = np.arange(N) / SR
sm = lambda x: (lambda y: y * y * (3 - 2 * y))(np.clip(x, 0, 1))
# clarinet: fades IN and OUT each time it plays
win = lambda a, fi, fo, b: sm((t - a) / fi) * (1 - sm((t - (b - fo)) / fo))
clar_env = np.maximum.reduce([win(0.0, 2.5, 2.6, 16.6), win(64.0, 2.0, 2.5, 79.0), win(92.9, 0.6, 1.4, 95.0)])
# drums: peak ON each downbeat, fall away in 0.3s, rush back up into the next one
bs = np.array(T["bar_starts"] + [95.0])
k = np.clip(np.searchsorted(bs, t, side="right") - 1, 0, len(bs) - 2)
since, blen = t - bs[k], bs[k + 1] - bs[k]
shape = 0.22 + 0.78 * np.maximum((since / blen) ** 2.2, np.exp(-since / 0.30))
lvl = np.interp(t, [0, 16.6, 29.0, 47.0, 64.0, 79.0, 88.6, 95.0], [0.45, 0.6, 0.7, 0.8, 0.6, 0.85, 0.7, 0.5])
mix = o + c * clar_env[:, None] + d * (shape * lvl)[:, None]
mix *= (1 - sm((t - 93.6) / 1.4))[:, None] * sm(t / 0.03)[:, None]     # tail fade into the loop point
mix /= np.abs(mix).max() / 0.89
w = wave.open("mix.wav", "wb"); w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((mix * 32767).astype(np.int16).tobytes()); w.close()
print("mixed", len(mix) / SR, "s")
