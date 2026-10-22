"""Collatz score. While 27 walks to 1, each step is one sixteenth note on
marimba and its pitch follows log2 of the number: the tune climbs as 27 rises
to 9,232 and falls back to 1. Step 111 (the 1) lands on a downbeat."""
import json, math

def traj(n):
    s = [n]
    while n != 1: n = n // 2 if n % 2 == 0 else 3 * n + 1; s.append(n)
    return s
HERO = traj(27); assert len(HERO) - 1 == 111 and max(HERO) == 9232
PEAK_K = HERO.index(9232); assert PEAK_K == 77
T_WALK0, T_WALK1 = 4.3, 16.8
DT = (T_WALK1 - T_WALK0) / 111                     # one step = one sixteenth
WALK_START = T_WALK0 - DT                          # one-sixteenth pickup so step 111 is a downbeat

SECTIONS = [  # name, start, end, bars, chords
    ("intro", 0.0, WALK_START, 2, ["Em", "Em"]),
    ("walk", WALK_START, T_WALK1, 7, ["Em", "C", "G", "D", "Em", "C", "D"]),
    ("one", T_WALK1, 20.0, 1, ["E"]),
    ("coral", 20.0, 34.5, 6, ["Em", "C", "G", "D", "Am", "B"]),
    ("end", 34.5, 40.0, 2, ["Am", "Csus2"]),
]
CH = {"Em": (40, [0, 3, 7]), "C": (36, [0, 4, 7]), "G": (43, [0, 4, 7]), "D": (38, [0, 4, 7]),
      "Am": (45, [0, 3, 7]), "B": (35, [0, 4, 7]), "E": (40, [0, 4, 7]), "Csus2": (36, [0, 2, 7])}

NAMES = ["C", "^C", "D", "^D", "E", "F", "^F", "G", "^G", "A", "^A", "B"]
def tok(m, dur, st):
    if m is None: return "z" + ("" if dur == 1 else "/" if dur == 0.5 else str(int(dur)))
    n = NAMES[m % 12]; acc, letter = ("^", n[1]) if n[0] == "^" else ("", n)
    o = m // 12 - 1; key = (letter, o); pre = "" if acc == st.get(key, "") else ("^" if acc else "=")
    st[key] = acc
    s = letter.lower() + "'" * (o - 5) if o >= 5 else letter + "," * (4 - o)
    return pre + s + ("" if dur == 1 else "/" if dur == 0.5 else str(int(dur)))
def bar(ev):
    st, out = {}, []
    for m, d, *dyn in ev:
        pre = (dyn[0] + " ") if dyn else ""
        if isinstance(m, list):
            out.append(pre + "[" + "".join(tok(x, 1, st) for x in m) + "]" + ("" if d == 1 else str(int(d))))
        else: out.append(pre + tok(m, d, st))
    return " ".join(out)
def triad(c, lo):
    r, iv = CH[c]; t = [r + i for i in iv]; return sorted(x + 12 * ((lo - x + 11) // 12) for x in t)

SCALE = [40, 43, 45, 47, 50, 52, 55, 57, 59, 62, 64, 67, 69, 71]        # E minor pentatonic, E2..B4
pitch = lambda v: SCALE[round(math.log2(v) / math.log2(9232) * (len(SCALE) - 1))]
assert pitch(1) == 40 and pitch(9232) == 71

THEME = {"Em": [(64, 2), (67, 2), (71, 3), (69, 1)], "C": [(67, 4), (64, 2), (60, 2)],
         "G": [(62, 3), (67, 1), (71, 4)], "D": [(69, 4), (66, 2), (62, 2)],
         "Am": [(69, 4), (64, 4)], "B": [(71, 4), (66, 4)]}
V = {k: [] for k in ["clar", "mar", "horns", "pad", "ost", "choir", "bass", "timp", "drums"]}
R8 = "z8"
walk_slots = [None] + [pitch(v) for v in HERO[:111]]                   # slot 0 = pickup rest
assert len(walk_slots) == 112
for name, t0, t1, nb, chords in SECTIONS:
    for b, c in enumerate(chords):
        r = CH[c][0]; root2 = r + 12 * ((40 - r + 11) // 12)
        # clarinet: alone at the start (fades in, then out under the walk), back at the end
        if name == "intro": V["clar"].append(bar([(64, 4, "!mf!"), (67, 4)] if b == 0 else [(71, 6), (69, 2)]))
        elif name == "end": V["clar"].append(bar([(57, 3, "!mf!"), (60, 1), (64, 4)] if b == 0 else [(62, 8)]))
        else: V["clar"].append(R8)
        # marimba: the sonified walk; then the 1 itself, low, on the downbeat
        if name == "walk":
            ev = []
            for j in range(16):
                k = b * 16 + j; m = walk_slots[k]
                dyn = "!ff!" if k == PEAK_K + 1 else ("!mf!" if k in (1, PEAK_K + 2) else None)
                ev.append((m, 0.5, dyn) if dyn else (m, 0.5))
            V["mar"].append(bar(ev))
        elif name == "one": V["mar"].append(bar([(40, 8, "!ff!")]))
        else: V["mar"].append(R8)
        # horns: the theme, only once the coral grows
        V["horns"].append(bar([(m, d, "!f!") if i == 0 and b == 0 else (m, d) for i, (m, d) in enumerate(THEME[c])]) if name == "coral" else R8)
        # pad
        V["pad"].append(R8 if (name == "intro" and b == 0) else bar([(triad(c, 48), 8, "!p!" if b == 0 else "!mp!")]))
        # ostinato under the coral
        V["ost"].append(bar([(x, 1) for x in [root2, root2 + 7, root2 + 12, root2 + 7] * 2]) if name == "coral" else R8)
        # choir
        V["choir"].append(bar([(triad(c, 48), 8, "!f!")]) if name in ("one", "end") or (name == "coral" and b >= 2) else R8)
        # contrabass
        V["bass"].append(bar([(r - 12 if r - 12 >= 28 else r, 8, "!mf!")]))
        # timpani: the hook, the peak, the 1, the coral, the last line
        rt = root2 if root2 <= 50 else root2 - 12
        if name == "walk" and b == PEAK_K // 16:
            pos = (PEAK_K + 1) % 16
            V["timp"].append(bar([(None, pos * 0.5)] if pos else [] ) + (" " if pos else "") + bar([(rt, 0.5, "!ff!")] + [(None, 0.5)] * (15 - pos)))
        elif (b == 0 and name in ("intro", "one", "coral", "end")) or (name == "coral" and b == 4):
            V["timp"].append(bar([(rt, 2, "!ff!"), (None, 2), (rt, 1), (rt, 1), (rt + 7 if rt + 7 <= 50 else rt - 5, 2)]))
        else: V["timp"].append(R8)
        # drums: soft rush in the walk and the coral (shaped by the mixer)
        V["drums"].append("!mf! [C,,F,,]/F,,/G,,/F,,/ G,,/F,,/G,,/F,,/ [C,,F,,]/F,,/G,,/F,,/ G,,/F,,/G,,/F,,/"
                          if name in ("walk", "coral") else R8)

tempos, starts, t = [], [], 0.0
for name, t0, t1, nb, _ in SECTIONS:
    q16 = round(nb * 16 * 60 / (t1 - t0)); tempos.append(q16)
    real = nb * 16 * 60 / q16
    starts += [t + k * real / nb for k in range(nb)]; t += real
    assert abs(t - t1) < 0.03, (name, t, t1)
PROG = {"clar": (71, 110, "Clarinet"), "mar": (12, 112, "Marimba"), "horns": (60, 100, "Horns"), "pad": (48, 80, "Strings"),
        "ost": (48, 76, "Ostinato"), "choir": (52, 86, "Choir"), "bass": (43, 112, "Contrabass"),
        "timp": (47, 116, "Timpani"), "drums": (None, 104, "Drums")}
def write(path, voices, title="The Collatz Conjecture"):
    out = f"X:1\nT:{title}\nC:original score for @observer.collapse\nM:4/4\nL:1/8\nQ:1/16={tempos[0]}\n"
    for i, v in enumerate(voices, 1):
        prog, vol, nm = PROG[v]
        out += f'V:{i} name="{nm}"' + (" clef=bass" if v in ("ost", "bass", "timp", "drums") else "") + "\n"
        out += ("%%MIDI channel 10\n" if prog is None else f"%%MIDI program {prog}\n") + f"%%MIDI control 7 {vol}\n"
    out += "K:C\n"
    for i, v in enumerate(voices, 1):
        out += f"V:{i}\n"; k = 0
        for s, sec in enumerate(SECTIONS):
            nb = sec[3]; q = f"[Q:1/16={tempos[s]}] " if i == 1 and s > 0 else ""
            out += q + " | ".join(V[v][k:k + nb]) + " |\n"; k += nb
        out = out.rstrip(" |\n") + " |]\n"
    open(path, "w").write(out)
write("full.abc", list(PROG))
write("orch.abc", ["mar", "horns", "pad", "ost", "choir", "bass", "timp"])
write("clar.abc", ["clar"]); write("drums.abc", ["drums"])
write("preview.abc", ["clar", "mar", "bass"], "The Collatz Conjecture (clarinet, marimba = the numbers, bass)")
json.dump({"bar_starts": starts, "sections": [(n, a, b, nb) for n, a, b, nb, _ in SECTIONS],
           "peak_time": T_WALK0 + PEAK_K * DT}, open("timeline.json", "w"), indent=1)
print("tempos BPM:", [q / 4 for q in tempos]); print("peak note at %.3fs" % (T_WALK0 + PEAK_K * DT))
print("walk pitches (first 12):", walk_slots[1:13], " top:", max(p for p in walk_slots if p))
