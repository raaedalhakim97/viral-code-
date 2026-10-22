"""The Butterfly Effect, score v3 (for real orchestral samples).

Same grid as v2, so the sync to the picture is unchanged: 76 BPM, 4/4,
bar = 3.158 s.  bar 5 = 12.63 s the split   bar 8 = 22.11 s the cloud
bar 10, and-of-3 = 30.39 s NOW: EVERYWHERE    bar 12 = 34.74 s the title

The story, in the notes:
  bars 1-4   TOGETHER: clarinet and violas play ONE line in unison over a D
             open-fifth pedal (the two points, one billionth apart).
  bar 5      THE SPLIT: the two lines diverge in contrary motion, low horns
             climbing while cellos fall.
  bars 8-11  THE CLOUD: horns + cellos in unison carry the theme, harp
             arpeggios spread upward, spiccato drives in 3+3+2.
  bar 12     D major with an added 9th: the butterfly, resolved but open.
  bar 13     the clarinet comes back alone and fades.

Harmony: Dm(add9), Bbmaj7 (with the E, its #11), Gm7, A7sus4 -> A, C,
D(add9). Spelled in D minor: Bb, not A#.
Range: nothing above E5; horns kept at or below D4, where VSCO's horn is
sampled every 3-4 semitones (it has nothing between C4 and D5).
"""
import os, json

Q4 = 76
BARS = 13
# spelling for D minor / D major: flats for Bb and Eb, sharps for C# F# G#
SPELL = {0: ("C", ""), 1: ("C", "^"), 2: ("D", ""), 3: ("E", "_"), 4: ("E", ""), 5: ("F", ""),
         6: ("F", "^"), 7: ("G", ""), 8: ("G", "^"), 9: ("A", ""), 10: ("B", "_"), 11: ("B", "=")}
KEY = {"B": "_"}                                   # K:Dm: every B is Bb unless marked

def note(m, st):
    letter, acc = SPELL[m % 12]
    o = m // 12 - 1; key = (letter, o)
    cur = st.get(key, KEY.get(letter, ""))
    want = acc if acc != "=" else ""
    pre = "" if want == cur else ({"^": "^", "_": "_", "": "="}[want])
    st[key] = want
    return pre + (letter.lower() + "'" * (o - 5) if o >= 5 else letter + "," * (4 - o))
def dur(d):
    return "" if d == 1 else "/" if d == 0.5 else str(int(d)) if d == int(d) else f"{int(d * 2)}/2"
def bar(events, chord=None):
    st, out, total = {}, [], 0
    for i, ev in enumerate(events):
        m, d = ev[0], ev[1]; deco = ev[2] if len(ev) > 2 else ""; tie = ev[3] if len(ev) > 3 else False
        total += d; g = f'"{chord}"' if (chord and i == 0) else ""
        if m is None: s = "z" + dur(d)
        elif isinstance(m, list): s = "[" + "".join(note(x, st) for x in m) + "]" + dur(d)
        else: s = note(m, st) + dur(d)
        out.append((deco + " " if deco else "") + g + s + ("-" if tie else ""))
    assert abs(total - 8) < 1e-9, (total, events)
    return " ".join(out)
REST = "z8"

# voicings: violins, violas, cello pad, contrabass (sounding MIDI pitches)
V = {
 "Dm(add9)": ([64, 69], [53, 62], [38, 45], 38),
 "Dm":       ([62, 69], [53, 57], [38, 45], 38),
 "Bbmaj7":   ([65, 69], [58, 62], [46, 53], 34),
 "F":        ([65, 69], [57, 60], [41, 48], 41),
 "C":        ([64, 67], [55, 60], [36, 43], 36),
 "Gm7":      ([65, 70], [55, 62], [43, 50], 43),
 "A7sus4":   ([64, 67], [57, 62], [45, 52], 45),
 "A":        ([64, 67], [57, 61], [45, 52], 45),
 "D(add9)":  ([66, 69], [57, 64], [38, 45], 38),
}
for v in V.values(): assert max(v[0] + v[1]) <= 76
CHORDS = ["Dm", "Dm", "Bbmaj7", "A",                       # 1-4  together
          "Dm(add9)", "Bbmaj7", "F|C",                      # 5-7  the split
          "Dm(add9)", "Bbmaj7", "Gm7|A7sus4", "Bbmaj7|C",   # 8-11 the cloud
          "D(add9)", "D(add9)"]                             # 12-13 the title
ROOT = {"Dm(add9)": 38, "Dm": 38, "Bbmaj7": 46, "F": 41, "C": 36, "Gm7": 43, "A7sus4": 45, "A": 45, "D(add9)": 38}

THEME = [  # bars 1-4: clarinet and violas in unison
 [(62, 3, "!p! !<(!"), (64, 1), (65, 2), (69, 2, "!<)!")],
 [(67, 3, "!tenuto!"), (65, 1), (64, 2), (62, 2)],
 [(65, 3, "!mp!"), (67, 1), (69, 2), (70, 2)],
 [(69, 6, "!mf! !tenuto!"), (73, 2, "!accent!")],
]
UP = [   # bars 5-7: horns climb ...
 [(50, 2, "!f! !accent!"), (52, 2), (53, 2), (57, 2)],
 [(58, 4, "!tenuto!"), (57, 2), (55, 2)],
 [(57, 2), (60, 2), (62, 4, "!tenuto!")],
]
DOWN = [  # ... while cellos fall
 [(50, 2, "!f! !accent!"), (48, 2), (46, 2), (45, 2)],
 [(46, 4, "!tenuto!"), (41, 4)],
 [(45, 4), (43, 4, "!tenuto!")],
]
CLOUD = [  # bars 8-12: horns + cellos (an octave down) in unison
 [(50, 2, "!ff! !accent!"), (53, 1), (57, 3, "!tenuto!"), (55, 1), (53, 1)],
 [(53, 3, "!tenuto!"), (52, 1), (50, 2), (48, 2)],               # E over Bbmaj7: its #11
 [(58, 4, "!tenuto!"), (None, 1), (57, 3, "!ff! !accent!")],     # the hit on the and-of-3
 [(62, 4, "!tenuto!"), (60, 4, "!<(!")],
 [(62, 8, "!fff! !<)!")],
]

parts = {k: [] for k in ["clar", "horn", "vln", "vla", "vc", "spic", "cb", "harp", "timp", "perc", "rush"]}
for b, c in enumerate(CHORDS):
    first = c.split("|")[0]
    def padbar(i, dyn=""):
        if "|" in c:
            x, y = c.split("|"); return bar([(V[x][i], 4, dyn), (V[y][i], 4)], x if i == 0 else None)
        return bar([(V[c][i], 8, dyn)], c if i == 0 else None)
    # clarinet: the theme, then once more alone at the very end
    parts["clar"].append(bar(THEME[b]) if b < 4 else bar([(62, 3, "!mp!"), (64, 1), (66, 4, "!>(!")]) if b == 12 else REST)
    # violas double the clarinet in bars 1-4 (unison: the two points), then pad
    parts["vla"].append(bar(THEME[b]) if b < 4 else padbar(1, "!mp!" if b == 4 else ""))
    parts["vln"].append(REST if b < 4 else padbar(0, "!p!" if b == 4 else ("!mf!" if b == 7 else "")))
    # horns: the climb, then the theme in the cloud
    parts["horn"].append(bar(UP[b - 4]) if 4 <= b < 7 else bar(CLOUD[b - 7]) if 7 <= b < 12 else bar([(62, 8, "!>(!")]) if b == 12 else REST)
    # cellos: open-fifth pedal, the fall, then unison with the horns an octave down
    if b < 4: parts["vc"].append(bar([(V[c.split('|')[0]][2], 8, "!pp!" if b == 0 else "")]))
    elif b < 7: parts["vc"].append(bar(DOWN[b - 4]))
    elif b < 12: parts["vc"].append(bar([(m - 12 if m else None, d, *r) for (m, d, *r) in CLOUD[b - 7]]))
    else: parts["vc"].append(bar([(V["D(add9)"][2], 8, "!>(!")]))
    # contrabass
    if "|" in c:
        x, y = c.split("|"); parts["cb"].append(bar([(V[x][3], 4, "!mf!" if b == 4 else ""), (V[y][3], 4)]))
    else: parts["cb"].append(bar([(V[c][3], 8, "!p!" if b == 0 else ("!f!" if b == 4 else ""))]))
    # spiccato 3+3+2, from the split to the title
    if 4 <= b < 12:
        r = ROOT[first]; r = r if r <= 47 else r - 12
        p = [r, r, r + 12, r, r, r + 12, r, r + 7]
        if b == 9: p = p[:4] + [None] + [ROOT["A7sus4"]] * 3        # break for the hit on the and-of-3
        parts["spic"].append(bar([(x, 1, ("!accent!" if i in (0, 3, 6) and x else "") + (" !f!" if (i == 0 and b == 4) else "")) for i, x in enumerate(p)]))
    else: parts["spic"].append(REST)
    # harp: rising through the chord in the cloud, top note E5
    if 7 <= b < 12:
        tones = sorted(set(V[first][1] + V[first][0] + [ROOT[first]]))
        seq = (tones + [t + 12 for t in tones])[:8]; seq = [x if x <= 76 else x - 12 for x in seq]
        parts["harp"].append(bar([(x, 1, "!mf!" if (b == 7 and i == 0) else "") for i, x in enumerate(seq)]))
    elif b == 11 + 0: parts["harp"].append(REST)
    else: parts["harp"].append(REST)
    # timpani
    if b == 3: parts["timp"].append(bar([(None, 4)] + [(45, 0.5, "!p! !<(!" if i == 0 else ("!<)!" if i == 7 else "")) for i in range(8)]))
    elif b in (4, 7, 11): parts["timp"].append(bar([(38, 2, "!ff! !accent!"), (None, 2), (38, 1, "!mf!"), (38, 1), (45, 2)]))
    elif b == 9: parts["timp"].append(bar([(43, 2, "!f!"), (None, 3), (45, 3, "!ff! !accent!")]))
    elif b == 10: parts["timp"].append(bar([(45, 0.5, "!mf! !<(!" if i == 0 else ("!<)!" if i == 15 else "")) for i in range(16)]))
    else: parts["timp"].append(REST)
    # percussion: gran cassa + crash on the scene changes
    if b in (4, 7, 11): parts["perc"].append(bar([([36, 49], 2, "!ff!"), (None, 6)]))
    elif b == 9: parts["perc"].append(bar([(None, 5), (36, 3, "!ff!")]))
    else: parts["perc"].append(REST)
    # the soft drum rush, every bar but the last; the mixer swells it into each downbeat
    parts["rush"].append(bar([(35, 0.5, "!mp!" if i == 0 else "") for i in range(16)]) if b < 12 else REST)

META = {"clar": ("Clarinet", 71, 108), "vla": ("Violas", 41, 90), "vln": ("Violins", 40, 84), "horn": ("Horns", 60, 104),
        "vc": ("Cellos", 42, 100), "spic": ("Cello spiccato", 45, 92), "cb": ("Contrabass", 43, 104), "harp": ("Harp", 46, 80),
        "timp": ("Timpani", 47, 112), "perc": ("Percussion", None, 104), "rush": ("Drum rush", None, 96)}
BASS = {"vc", "spic", "cb", "timp", "perc", "rush"}
MARKS = {0: '"Together"', 4: '"The split"', 7: '"The cloud"', 11: '"The butterfly"'}
def write(path, names, title):
    o = ["X:1", f"T:{title}", "C:original score for @observer.collapse", "M:4/4", "L:1/8", f'Q:"Together" 1/4={Q4}',
         "%%MIDI gchordoff", "%%MIDI chordname add9 0 4 7 14", "%%MIDI chordname m(add9) 0 3 7 14", "%%MIDI chordname 7sus4 0 5 7 10",
         "%%score " + " ".join(str(i + 1) for i in range(len(names)))]
    for i, k in enumerate(names, 1):
        nm, prog, vol = META[k]
        o.append(f'V:{i} name="{nm}"' + (" clef=bass" if k in BASS else ""))
        o += ["%%MIDI channel 10"] if prog is None else [f"%%MIDI program {prog}"]
        o.append(f"%%MIDI control 7 {vol}")
    o.append("K:Dm")
    for i, k in enumerate(names, 1):
        o.append(f"V:{i}")
        line = []
        for b in range(BARS):
            mark = (f'"^{MARKS[b][1:-1]}"' + " ") if (i == 1 and b in MARKS and b) else ""
            line.append(mark + parts[k][b])
        o.append("% bars 1-4 together | 5-7 split | 8-11 cloud | 12-13 butterfly")
        o.append(" | ".join(line[:4]) + " |\n" + " | ".join(line[4:7]) + " |\n" + " | ".join(line[7:11]) + " |\n" + " | ".join(line[11:]) + " |]")
    open(path, "w").write("\n".join(o) + "\n")
write("butterfly_v3.abc", list(META), "The Butterfly Effect")
write("preview_v3.abc", ["clar", "vla", "horn", "vc", "spic"], "The Butterfly Effect (clarinet + violas together, then horns up / cellos down)")
os.makedirs("voices", exist_ok=True)
for k in META: write(f"voices/{k}.abc", [k], f"Butterfly v3: {META[k][0]}")
json.dump({"q4": Q4, "bars": BARS}, open("score_meta.json", "w"))
print("written", list(META))
