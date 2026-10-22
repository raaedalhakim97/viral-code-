"""Smart Lookup score: original, E minor, low register (top note <= E5).
Each section gets its own tempo so it holds a whole number of bars and every
scene change in the video lands on a downbeat. Writes full.abc (preview) and
three stems (orch / clar / drums) plus timeline.json for the mixer."""
import json

# (name, video start, video end, bars, chords)
SECTIONS = [
    ("hook",      0.0,  4.6, 2, ["Em", "Em"]),
    ("words",     4.6, 16.6, 5, ["Em", "C", "G", "D", "Em"]),
    ("universe", 16.6, 29.0, 5, ["Em", "C", "G", "D", "C"]),
    ("equation", 29.0, 34.6, 2, ["Am", "B"]),
    ("curve",    34.6, 47.0, 5, ["Em", "Em", "C", "G", "D"]),
    ("points",   47.0, 64.0, 7, ["Em", "C", "G", "D", "Em", "C", "D"]),
    ("loop",     64.0, 79.0, 6, ["Am", "Em", "C", "G", "Am", "B"]),
    ("stats",    79.0, 88.6, 4, ["Em", "C", "G", "D"]),
    ("outro",    88.6, 95.0, 3, ["C", "E", "E"]),
]
CH = {"Em": (40, [0, 3, 7]), "C": (36, [0, 4, 7]), "G": (43, [0, 4, 7]), "D": (38, [0, 4, 7]),
      "Am": (45, [0, 3, 7]), "B": (35, [0, 4, 7]), "E": (40, [0, 4, 7])}   # root (MIDI) + triad

# ---------------- ABC writer with correct per-bar accidental tracking ------
NAMES = ["C", "^C", "D", "^D", "E", "F", "^F", "G", "^G", "A", "^A", "B"]
def tok(m, dur, state):
    if m is None: return "z" + (str(dur) if dur != 1 else "")
    n = NAMES[m % 12]; acc, letter = ("^", n[1]) if n[0] == "^" else ("", n)
    octv = m // 12 - 1                      # MIDI octave, C4 = 60 = "C"
    key = (letter, octv)
    cur = state.get(key, "")
    pre = "" if acc == cur else ("^" if acc == "^" else "=")
    state[key] = acc
    if octv >= 5: s = letter.lower() + "'" * (octv - 5)
    else: s = letter + "," * (4 - octv)
    d = "" if dur == 1 else ("/" if dur == 0.5 else str(int(dur)))
    return pre + s + d
def bar(events):                            # events: [(midi|None|[chord], dur_in_eighths)]
    st, out = {}, []
    for m, d in events:
        if isinstance(m, list): out.append("[" + "".join(tok(x, 1, st)[:None] for x in m) + "]" + (str(d) if d != 1 else ""))
        else: out.append(tok(m, d, st))
    return " ".join(out)

def triad(c, lo):                           # chord tones at/above `lo`
    r, iv = CH[c]; t = [r + i for i in iv]
    t = [x + 12 * ((lo - x + 11) // 12) for x in t]
    return sorted(t)

# theme motifs per chord (MIDI, eighths) — chord-tone melody, E4..B4
THEME = {"Em": [(64, 2), (67, 2), (71, 3), (69, 1)], "C": [(67, 4), (64, 2), (60, 2)],
         "G": [(62, 3), (67, 1), (71, 4)], "D": [(69, 4), (66, 2), (62, 2)],
         "Am": [(69, 8)], "B": [(71, 4), (75, 4)], "E": [(68, 8)]}
CLAR_LOOP = {"Am": [(57, 3), (60, 1), (64, 4)], "Em": [(64, 4), (59, 4)], "C": [(60, 3), (64, 1), (67, 4)],
             "G": [(67, 4), (62, 4)], "B": [(63, 4), (66, 4)]}

V = {k: [] for k in ["clar", "horns", "pad", "ost", "harp", "choir", "bass", "timp", "drums"]}
dyn = {"hook": "!p!", "words": "!mp!", "universe": "!mf!", "equation": "!f!", "curve": "!mp!",
       "points": "!f!", "loop": "!mp!", "stats": "!ff!", "outro": "!f!"}
REST = "z8"
for name, t0, t1, nb, chords in SECTIONS:
    for b, c in enumerate(chords):
        D = dyn[name] + " " if b == 0 else ""
        r = CH[c][0]; tri = triad(c, 48); root2 = r + 12 * ((40 - r + 11) // 12)   # root in E2..D#3
        # clarinet: opens alone, returns for the loop, echoes in the last bar
        if name == "hook":
            V["clar"].append(D + bar([(64, 4), (67, 4)] if b == 0 else [(71, 6), (69, 2)]))
        elif name == "words":
            V["clar"].append(D + bar(THEME[c] if b < 4 else [(64, 8)]))
        elif name == "loop":
            V["clar"].append(D + bar(CLAR_LOOP[c]))
        elif name == "outro" and b == 2:
            V["clar"].append(D + bar([(64, 4), (68, 4)]))
        else: V["clar"].append(REST)
        # horns: the theme, low
        if name in ("universe", "points", "stats") or (name == "equation"):
            V["horns"].append(D + bar(THEME[c]))
        elif name == "outro" and b < 2:
            V["horns"].append(D + bar([(67, 4), (64, 4)] if b == 0 else [(68, 8)]))
        else: V["horns"].append(REST)
        # string pad: chord third, held
        V["pad"].append((D + bar([(tri[1], 8)])) if name != "hook" else REST)
        # ostinato: low eighths root-fifth-octave-fifth
        if name in ("universe", "equation", "points", "stats") or (name == "words" and b >= 1) or (name == "loop" and b >= 2):
            p = [root2, root2 + 7, root2 + 12, root2 + 7] * 2
            V["ost"].append(D + bar([(x, 1) for x in p]))
        else: V["ost"].append(REST)
        # harp: rising sixteenths over two octaves, top <= E5
        if (name == "words" and b == 3) or name == "curve" or (name == "points" and b >= 4):
            notes = []
            base = triad(c, 40)
            for o in range(4): notes += [x + 12 * o for x in base] + [base[0] + 12 * (o + 1)]
            notes = [x for x in notes if x <= 76][:16]
            while len(notes) < 16: notes.append(notes[-1])
            V["harp"].append(D + bar([(x, 0.5) for x in notes]))
        else: V["harp"].append(REST)
        # choir: close triad around C3-C4
        if (name == "curve" and b >= 3) or name in ("points", "stats", "outro"):
            V["choir"].append(D + bar([(triad(c, 48), 8)]))
        else: V["choir"].append(REST)
        # contrabass: root, low
        V["bass"].append(D + bar([(r - 12 if r - 12 >= 28 else r, 8)]))
        # timpani: the hits that mark a new scene
        rt = root2 if root2 <= 50 else root2 - 12
        hit = (b == 0 and name in ("hook", "universe", "equation", "points", "outro")) or name == "stats" or (name == "outro" and b == 1)
        if name == "equation" and b == 1:
            V["timp"].append(D + bar([(rt, 0.5)] * 16))           # the roll under the zoom-through
        elif hit:
            V["timp"].append(D + bar([(rt, 2), (None, 2), (rt, 1), (rt, 1), (rt + 7 if rt + 7 <= 50 else rt - 5, 2)]))
        else: V["timp"].append(REST)
        # drums: soft low tom rush every bar where the music moves (shaped later by the mixer)
        if (name == "words" and b == 4) or name in ("universe", "points", "stats") or (name == "equation" and b == 1) or (name == "outro" and b < 2):
            V["drums"].append(D + "[C,,F,,]/F,,/G,,/F,,/ G,,/F,,/G,,/F,,/ [C,,F,,]/F,,/G,,/F,,/ G,,/F,,/G,,/F,,/")
        else: V["drums"].append(REST)

# tempo per section, at quarter-BPM resolution (Q:1/16)
tempos, starts, t = [], [], 0.0
for name, t0, t1, nb, _ in SECTIONS:
    bpm = nb * 4 * 60 / (t1 - t0); q16 = round(bpm * 4)
    tempos.append(q16)
    real = nb * 4 * 60 / (q16 / 4)
    starts += [t + k * real / nb for k in range(nb)]; t += real
drift = max(abs(sum(nb * 240 / (q / 4) for (_, _, _, nb, _), q in zip(SECTIONS[:i], tempos[:i])) - SECTIONS[i][1]) for i in range(len(SECTIONS)))
assert drift < 0.03, drift

PROG = {"clar": (71, 110, "Clarinet"), "horns": (60, 104, "Horns"), "pad": (48, 80, "Strings"),
        "ost": (48, 78, "Ostinato"), "harp": (46, 76, "Harp"), "choir": (52, 88, "Choir"),
        "bass": (43, 112, "Contrabass"), "timp": (47, 116, "Timpani"), "drums": (None, 110, "Drums")}
def write(path, voices):
    out = "X:1\nT:Smart Lookup\nC:original score for @observer.collapse\nM:4/4\nL:1/8\nQ:1/16=%d\n" % tempos[0]
    for i, v in enumerate(voices, 1):
        prog, vol, nm = PROG[v]
        out += f'V:{i} name="{nm}"' + (" clef=bass" if v in ("ost", "bass", "timp", "drums") else "") + "\n"
        out += ("%%MIDI channel 10\n" if prog is None else f"%%MIDI program {prog}\n") + f"%%MIDI control 7 {vol}\n"
    out += "K:C\n"
    for i, v in enumerate(voices, 1):
        out += f"V:{i}\n"; k = 0
        for s, (name, *_rest) in enumerate(SECTIONS):
            nb = SECTIONS[s][3]
            q = f"[Q:1/16={tempos[s]}] " if i == 1 and s > 0 else ""
            out += f"% {name}\n" + q + " | ".join(V[v][k:k + nb]) + " |\n"; k += nb
        out = out.rstrip(" |\n") + " |]\n"
    open(path, "w").write(out)
ALL = ["clar", "horns", "pad", "ost", "harp", "choir", "bass", "timp", "drums"]
write("full.abc", ALL)
# every stem carries voice 1 = a silent clarinet-length carrier? No: tempo lives in V:1 of each file.
write("orch.abc", ["horns", "pad", "ost", "harp", "choir", "bass", "timp"])
write("clar.abc", ["clar"]); write("drums.abc", ["drums"])
json.dump({"bar_starts": starts, "tempos_q16": tempos,
           "sections": [(n, a, b, nb) for n, a, b, nb, _ in SECTIONS]}, open("timeline.json", "w"), indent=1)
print("tempos (BPM):", [q / 4 for q in tempos]); print("max section-start drift: %.3fs" % drift)
print("bars:", len(starts))
