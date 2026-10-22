"""The Collatz Conjecture, score v3.

What changed from v2, and why:
  HARMONY   colour chords instead of bare triads: Em(add9), Cmaj7, Cmaj7(#11),
            G(add9), Dsus4 -> D, Bsus4 -> B, and an E open-fifth pedal under the
            opening. The sus4 -> 3 suspension at the end of the coral is the
            oldest trick in film music for "almost there".
  MOTIF     one 3-note cell (B - E - F#: a rising fourth then a step) that opens
            on clarinet, comes back augmented on horns, and is sequenced up a
            fourth in the coral. One idea, developed, instead of new tunes.
  TEXTURE   horns doubled by cellos an octave down (the modern epic unison),
            cello spiccato ostinato in 3+3+2 accents (trailer rhythm), upper
            strings as close voicings that move by step (voice leading).
  RANGE     nothing above E5. Violins sit in their warm middle.
  NOTATION  articulations (accent, tenuto, staccato), hairpins, slurs, ties and
            chord symbols, all of which abc2midi turns into velocity and
            duration, so the sheet music now carries the performance.

Timing is unchanged from v2, so the sync to the picture is unchanged: every
section keeps its start, bar count and tempo.
"""
import json, math

def traj(n):
    s = [n]
    while n != 1: n = n // 2 if n % 2 == 0 else 3 * n + 1; s.append(n)
    return s
HERO = traj(27); assert len(HERO) - 1 == 111 and max(HERO) == 9232
PEAK_K = HERO.index(9232)

SECTIONS = [("intro", 2), ("walk", 7), ("one", 1), ("coral", 6), ("end", 2)]
Q16 = [459, 533, 300, 397, 349]           # same tempos as v2 (quarter-BPM resolution)

# ------------------------------------------------------------- ABC writer
NAMES = ["C", "^C", "D", "^D", "E", "F", "^F", "G", "^G", "A", "^A", "B"]
def note(m, st):
    assert m % 12 != 5, "F natural would read as F# under K:Em"
    n = NAMES[m % 12]; acc, letter = ("^", n[1]) if n[0] == "^" else ("", n)
    o = m // 12 - 1; key = (letter, o); pre = "" if acc == st.get(key, "") else ("^" if acc else "=")
    st[key] = acc
    return pre + (letter.lower() + "'" * (o - 5) if o >= 5 else letter + "," * (4 - o))
def dur(d):
    return "" if d == 1 else "/" if d == 0.5 else "3/2" if d == 1.5 else str(int(d))
def bar(events, chord=None):
    """events: (pitch | [pitches] | None, eighths, 'decorations', tie?)"""
    st, out, total = {}, [], 0
    for i, ev in enumerate(events):
        m, d = ev[0], ev[1]; deco = ev[2] if len(ev) > 2 else ""; tie = ev[3] if len(ev) > 3 else False
        total += d
        g = f'"{chord}"' if (chord and i == 0) else ""
        if m is None: s = "z" + dur(d)
        elif isinstance(m, list): s = "[" + "".join(note(x, st) for x in m) + "]" + dur(d)
        else: s = note(m, st) + dur(d)
        out.append((deco + " " if deco else "") + g + s + ("-" if tie else ""))
    assert abs(total - 8) < 1e-9, (total, events)
    return " ".join(out)
REST = "z8"

# ------------------------------------------------------------- harmony
# voicings: violins (2 notes), violas (2), cello sustain (2), contrabass (1)
V = {
 "Em9":    ([66, 71], [55, 64], [40, 47], 28),
 "Cmaj7":  ([64, 71], [55, 60], [36, 43], 36),
 "Cmaj7#11": ([66, 71], [55, 64], [36, 43], 36),
 "Gadd9":  ([62, 69], [55, 59], [43, 50], 31),
 "Dsus4":  ([62, 69], [57, 67], [38, 45], 38),
 "D":      ([62, 69], [57, 66], [38, 45], 38),
 "D/F#":   ([62, 69], [57, 66], [42, 50], 30),
 "Am7":    ([64, 72], [57, 67], [45, 52], 33),
 "Bsus4":  ([64, 71], [59, 66], [47, 54], 35),
 "B":      ([63, 71], [59, 66], [47, 54], 35),
 "E":      ([68, 71], [56, 64], [40, 47], 28),
 "Asus2":  ([64, 71], [57, 64], [45, 52], 33),
}
for v in V.values():
    assert max(v[0] + v[1]) <= 76, v          # nothing above E5
ROOT = {"Em9": 40, "Cmaj7": 36, "Cmaj7#11": 36, "Gadd9": 43, "Dsus4": 38, "D": 38, "D/F#": 42,
        "Am7": 45, "Bsus4": 47, "B": 47, "E": 40, "Asus2": 45}

PLAN = {   # chords per bar; a "a|b" bar changes chord on beat 3
 "intro": ["Em9", "Em9"],
 "walk":  ["Em9", "Cmaj7", "Gadd9", "Dsus4|D", "Em9", "Cmaj7#11", "Bsus4|B"],
 "one":   ["E"],
 "coral": ["Em9", "Cmaj7", "Gadd9", "D/F#", "Am7", "Bsus4|B"],
 "end":   ["Cmaj7#11", "Asus2"],
}

def pad(part, sec, b, c, dyn):
    """sustained strings; a split bar moves by step on beat 3 (voice leading)"""
    idx = {"vln": 0, "vla": 1, "vc": 2}[part]
    if "|" in c:
        a, z = c.split("|"); return bar([(V[a][idx], 4, dyn), (V[z][idx], 4)], a if part == "vln" else None)
    return bar([(V[c][idx], 8, dyn)], c if part == "vln" else None)

# ------------------------------------------------------------- voices
parts = {k: [] for k in ["clar", "horn", "vln", "vla", "vc", "spic", "cb", "harp", "mar", "timp", "perc"]}
SCALE = [40, 43, 45, 47, 50, 52, 55, 57, 59, 62, 64, 67, 69, 71]        # E minor pentatonic
pitch = lambda v: SCALE[round(math.log2(v) / math.log2(9232) * (len(SCALE) - 1))]
walk_slots = [None] + [pitch(v) for v in HERO[:111]]

# the motif: B3 E4 F#4 (rising fourth, then a step), and its answers
CLAR = {("intro", 0): [(59, 3, "!p! !<(!"), (64, 1), (64, 2, "", False), (66, 2, "!<)!")],
        ("intro", 1): [(67, 3, "!mf! !tenuto!"), (66, 1), (64, 4, "!>(!")],
        ("end", 0):   [(59, 3, "!mp!"), (64, 1), (66, 4, "!tenuto!")],
        ("end", 1):   [(67, 2, "!>(!"), (66, 6, "!>)!")]}            # ends on F#: the 9th, unresolved
HORN = {   # coral: the motif augmented, then sequenced up a fourth; 4-3 suspension at the end
 0: [(59, 1, "!f! !accent!"), (64, 2), (66, 1), (67, 3, "!tenuto!"), (66, 1)],
 1: [(64, 3, "!tenuto!"), (62, 1), (64, 2), (59, 2)],
 2: [(62, 1, "!accent!"), (67, 2), (69, 1), (71, 3, "!tenuto!"), (69, 1)],
 3: [(66, 4, "!tenuto!"), (64, 2), (62, 2)],
 4: [(72, 3, "!ff! !accent!"), (71, 1), (69, 2), (64, 2)],
 5: [(64, 4, "!tenuto!"), (63, 4, "!>(!")],                          # E -> D#: sus4 resolving to 3
}
HORN_WALK = {4: [(59, 4, "!mp! !<(!"), (64, 4)], 5: [(66, 6, "!<)!"), (64, 2)], 6: [(64, 4), (63, 4)]}

for sec, nb in SECTIONS:
    for b in range(nb):
        c = PLAN[sec][b]; first = c.split("|")[0]
        # clarinet
        parts["clar"].append(bar(CLAR[(sec, b)]) if (sec, b) in CLAR else REST)
        # horns: hint of the motif in the walk, the full theme in the coral, held 5th on the 1
        # horns sit an octave down, in the dark low-horn register: VSCO's horn has
        # no samples between C4 and D5, and down here it is sampled every 3-4
        # semitones, so no note is stretched more than 2 semitones
        low = lambda evs: [(m - 12, d, *r) for (m, d, *r) in evs]
        if sec == "coral": parts["horn"].append(bar(low(HORN[b])))
        elif sec == "walk" and b in HORN_WALK: parts["horn"].append(bar(low(HORN_WALK[b])))
        elif sec == "one": parts["horn"].append(bar([([47, 52], 8, "!ff! !accent!")]))
        else: parts["horn"].append(REST)
        # upper strings
        dyn = {"intro": "!pp!", "walk": "!p!", "one": "!f!", "coral": "!mf!", "end": "!mp!"}[sec] if b == 0 else ""
        parts["vln"].append(pad("vln", sec, b, c, dyn) if not (sec == "intro") else REST)
        parts["vla"].append(pad("vla", sec, b, c, dyn) if not (sec == "intro" and b == 0) else REST)
        # cellos: open-fifth pedal in the intro, pads in the walk, the theme an octave down in the coral
        if sec == "intro":
            parts["vc"].append(bar([([40, 47], 8, "!pp!" if b == 0 else "", b == 0)]))
        elif sec == "coral":       # cellos in unison with the low horns: the modern epic doubling
            parts["vc"].append(bar([(m - 12, d, *rest) for (m, d, *rest) in HORN[b]]))
        else:
            parts["vc"].append(pad("vc", sec, b, c, dyn))
        # spiccato ostinato, 3+3+2: accents on eighths 1, 4 and 7
        if (sec == "walk" and b >= 1) or sec == "coral":
            r = ROOT[first] - 12 if ROOT[first] >= 48 else ROOT[first]
            p = [r, r, r + 12, r, r, r + 12, r, r + 7]
            ev = [(x, 1, ("!accent!" if i in (0, 3, 6) else "") + ("" if i or b else " " + ("!mp!" if sec == "walk" else "!f!")))
                  for i, x in enumerate(p)]
            parts["spic"].append(bar([(m, d, deco.strip()) for m, d, deco in ev]))
        else: parts["spic"].append(REST)
        # contrabass
        cb = V[first][3]
        parts["cb"].append(bar([(cb, 8, "!pp!" if (sec == "intro" and b == 0) else "")]) if not (sec == "intro" and b == 0) else REST)
        # harp: rising eighths through the chord, mid register, in the coral and the last walk bars
        if sec == "coral" or (sec == "walk" and b >= 4):
            vv = sorted(set(V[first][1] + V[first][0] + [ROOT[first] + 12]))
            seq = (vv * 3)[:8] if len(vv) >= 4 else (vv + [x + 12 for x in vv])[:8]
            seq = [x if x <= 76 else x - 12 for x in seq]
            parts["harp"].append(bar([(x, 1, "!mp!" if (i == 0 and b in (0, 4) and sec == "walk") else "") for i, x in enumerate(seq)]))
        else: parts["harp"].append(REST)
        # marimba: the sonified walk; then the 1 itself
        if sec == "walk":
            ev = []
            for j in range(16):
                k = b * 16 + j; m = walk_slots[k]
                deco = "!ff! !accent!" if k == PEAK_K + 1 else ("!mf!" if k in (1, PEAK_K + 2) else "")
                ev.append((m, 0.5, deco))
            parts["mar"].append(bar(ev))
        elif sec == "one": parts["mar"].append(bar([(40, 8, "!ff!")]))
        else: parts["mar"].append(REST)
        # timpani and percussion: the scene changes
        hit = (sec in ("one", "coral", "end") and b == 0) or (sec == "coral" and b == 4)
        if sec == "walk" and b == PEAK_K // 16:
            pos = (PEAK_K + 1) % 16
            parts["timp"].append(bar([(None, pos * 0.5), (40, 0.5, "!ff!"), (None, (15 - pos) * 0.5)]))
        elif hit: parts["timp"].append(bar([(40, 2, "!ff! !accent!"), (None, 2), (40, 1, "!mf!"), (40, 1), (47, 2)]))
        elif sec == "walk" and b == 6: parts["timp"].append(bar([(None, 4)] + [(40, 0.5, "!p! !<(!" if i == 0 else ("!<)!" if i == 7 else "")) for i in range(8)]))
        else: parts["timp"].append(REST)
        # percussion (GM drum map): 36 gran cassa, 49 crash, 35 soft rolled bass drum
        if hit or (sec == "intro" and b == 0):
            parts["perc"].append(bar([([36, 49], 2, "!ff!" if sec != "intro" else "!p!"), (None, 6)]))
        elif sec == "coral":
            parts["perc"].append(bar([(35, 0.5, "!mp!" if i == 0 else "") for i in range(16)]))
        else: parts["perc"].append(REST)

# ------------------------------------------------------------- write
META = {  # name, GM program (for the preview / abc2midi), volume
 "clar": ("Clarinet", 71, 108), "horn": ("Horns", 60, 104), "vln": ("Violins", 48, 84), "vla": ("Violas", 48, 84),
 "vc": ("Cellos", 42, 100), "spic": ("Cello spiccato", 45, 92), "cb": ("Contrabass", 43, 104), "harp": ("Harp", 46, 80),
 "mar": ("Marimba", 12, 108), "timp": ("Timpani", 47, 112), "perc": ("Percussion", None, 104)}
BASS = {"vc", "spic", "cb", "timp", "perc"}
def write(path, names, title):
    o = [f"X:1", f"T:{title}", "C:original score for @observer.collapse", "M:4/4", "L:1/8",
         f'Q:"Mysterioso" 1/16={Q16[0]}', "%%MIDI gchordoff",
         "%%MIDI chordname add9 0 4 7 14", "%%MIDI chordname maj7#11 0 4 7 11 18",
         "%%score " + " ".join(str(i + 1) for i in range(len(names)))]
    for i, k in enumerate(names, 1):
        nm, prog, vol = META[k]
        o.append(f'V:{i} name="{nm}"' + (" clef=bass" if k in BASS else ""))
        o += ["%%MIDI channel 10"] if prog is None else [f"%%MIDI program {prog}"]
        o.append(f"%%MIDI control 7 {vol}")
    o.append("K:Em")
    marks = ['"Mysterioso"', '"Pulsing: 27 walks"', '"Arrival"', '"Epic"', '"Unresolved"']
    for i, k in enumerate(names, 1):
        o.append(f"V:{i}"); n = 0
        for s, (sec, nb) in enumerate(SECTIONS):
            q = f'[Q:{marks[s]} 1/16={Q16[s]}] ' if i == 1 and s > 0 else ""
            o.append(f"% {sec}\n" + q + " | ".join(parts[k][n:n + nb]) + " |"); n += nb
        o[-1] = o[-1][:-2] + " |]"
    open(path, "w").write("\n".join(o) + "\n")
ALL = list(META)
write("collatz_v3.abc", ALL, "The Collatz Conjecture")
write("preview_v3.abc", ["clar", "horn", "vc", "spic", "mar"], "The Collatz Conjecture (clarinet, horns, cellos, spiccato, marimba)")
json.dump({"order": ALL, "q16": Q16, "sections": SECTIONS, "peak_k": PEAK_K}, open("score_meta.json", "w"))
print("written:", ALL)

# one file per voice: unambiguous track mapping for the sampler
import os
os.makedirs("voices", exist_ok=True)
for k in ALL:
    write(f"voices/{k}.abc", [k], f"Collatz v3: {META[k][0]}")
