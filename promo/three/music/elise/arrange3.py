"""Für Elise: the second part (F major, bars 23-38) straight into the chord part (D minor,
bars 59-82), no return of the theme in between. Notes from the Breitkopf & Härtel 1888
edition (public domain; Mutopia Project LilyPond source by Stelios Samelis). Our
arrangement adds strings, cello, horns and soft bass drum. Writes elise3.abc and
elise3_score.json; every bar is checked to hold exactly 3/8."""
import json, re
from fractions import Fraction as Fr

PICK_RH, PICK_LH = "[Ec][Fc][EGc]", "[_B,C][A,C][G,_B,C]"           # the C7 chords that open F major (bar 22)
# ------------------------------------------------------------------ B: the F major second part
B_RH = ["{FA}c4 f3/2e/2", "e2 d2 _b3/2a/2", "agfedc", "_B2 A2 {_B}A/2G/2A/2_B/2", "c4 d^d", "e3 efA", "c4 d3/2B/2",
        "c/2g/2G/2g/2 A/2g/2B/2g/2 c/2g/2d/2g/2", "e/2g/2c'/2b/2 a/2g/2f/2e/2 d/2g/2f/2d/2",
        "c/2g/2G/2g/2 A/2g/2B/2g/2 c/2g/2d/2g/2", "e/2g/2c'/2b/2 a/2g/2f/2e/2 d/2g/2f/2d/2",
        "e/2f/2e/2^d/2 e/2B/2e/2^d/2 e/2B/2e/2^d/2", "e3 Be^d", "e3 Be^d", "e^de^de^d", "e^de B=dc"]
B_LH = ["F,A,CA,CA,", "F,_B,D_B,D_B,", "F,E[F,G,_B,]E[F,G,_B,]E", "F,A,CA,CA,", "F,A,CA,CA,", "E,A,CA,[D,D]F,", "G,EG,EG,F",
        "[CE]2 z[FG][EG][DFG]", "[CE]2 [F,A,]2 [G,B,]2", "C2 z[FG][EG][DFG]", "[CE]2 [F,A,]2 [G,B,]2",
        "[^G,B,]2 z4", "z6", "z6", "z6", "z6"]
B_CH = ["F", "Bb", "C7", "F", "F", "Am", "C7", "C", "G", "C", "G", "E", "E", "E", None, None]
# ------------------------------------------------------------------ C: the chord part, the pounding A (bars 59-82)
P = "A,,A,,A,,A,,A,,A,,"
C_RH = ["A2 z4",                       # 59: the theme's last A; the pedal begins underneath
        "[EG_B^c]6", "[FAd]4 [^ce][df]", "[^Gdf]4 [^Gdf]2", "[Ac=e]6",
        "[Fd]4 [Ec][DB]", "[C^FA]4 [CA]2", "[CA]2 [Ec]2 [DB]2", "[CA]6",
        "[EG_B^c]6", "[FAd]4 [^ce][df]", "[df]4 [df]2", "[df]6",
        "[G_e]4 [Fd][_Ec]", "[DF_B]4 [DFA]2", "[DF^G]4 [DF^G]2", "[CE=A]4 z2", "[EB]2 z4",
        # the sweep up and the chromatic fall (sixteenth triplets: 9 to a bar)
        "(3A,CE (3Ace (3dcB", "(3Ace (3ac'e' (3d'c'b", "(3ac'e' (3a'c''e'' (3d''c''b'",
        "(3_b'a'^g' (3=g'^f'=f' (3e'^d'=d'", "(3^c'=c'b (3_ba^g (3=g^f=f",
        "e^de B=dc", "A6", "[A,CEA]6"]
C_LH = [P, P, P, P, P,
        "[D,,A,,]"*6, "[^D,,A,,]"*6, "[E,,A,,]"*4 + "[E,,^G,,]"*2, "[A,,,A,,]A,,A,,A,,A,,A,,",
        P, P, P, "_B,,"*6, "_B,,"*6, "_B,,"*6, "=B,,"*6, "C,4 z2", "[E,^G,]2 z4",
        "A,,,2 z2 [A,CE]2", "[A,CE]2 z2 [A,CE]2", "[A,CE]2 z2 [A,CE]2", "[A,CE]2 z4", "z6",
        "z6", "A,,E,A, z3", "[A,,,A,,]6"]
# orchestra under the chord part: strings double the right hand an octave down, cello holds the bass
C_STR = [None, "[E,G,_B,]6", "[F,A,D]6", "[^G,DF]6", "[A,CE]6", "[F,A,D]6", "[^F,A,C]6", "[A,CE]6", "[A,CE]6",
         "[E,G,_B,]6", "[F,A,D]6", "[F,A,D]6", "[F,A,D]6", "[G,_B,_E]6", "[D,F,_B,]6", "[D,F,^G,]6", "[A,CE]4 z2", "[^G,B,E]2 z4",
         "[A,CE]6", "[A,CE]6", "[A,CE]6", None, None, None, None, None]
C_VC = [None, "A,,6", "A,,6", "A,,6", "A,,6", "D,,6", "^D,,6", "E,,6", "A,,6", "A,,6", "A,,6", "A,,6", "A,,6",
        "_B,,6", "_B,,6", "=B,,6", "C,4 z2", "E,,2 z4", "A,,6", "A,,6", "A,,6", None, None, None, None, None]
C_HN = [None, "[E,A,]6", "[F,A,]6", None, "[E,A,]6", None, None, None, None, "[E,A,]6", "[F,A,]6", "[F,A,]6", "[F,A,]6",
        "[G,_B,]6", "[F,_B,]6", None, None, None, None, None, None, None, None, None, None, None]
# drums: soft bass-drum rolls swelling under the pedal ("R"), single hits on the big chords ("H")
C_DR = [None, "H", None, None, "H", None, None, None, None, "H", "R", "R", "R", "H", None, None, "H", None,
        None, None, None, None, None, None, None, None]
STR = {"F": "[F,A,C]6", "Bb": "[F,_B,D]6", "C7": "[G,_B,E]6", "Am": "[A,CE]6", "C": "[G,CE]6", "G": "[G,B,D]6", "E": "[^G,B,E]6"}
VC = {"F": "F,,6", "Bb": "_B,,6", "C7": "C,6", "Am": "A,,6", "C": "C,6", "G": "G,,6", "E": "E,,6"}
HN = {"F": "[F,C]6", "Bb": "[F,D]6", "C7": "[E,_B,]6", "Am": "[A,E]6", "C": "[C,G,]6", "G": "[G,,D,]6", "E": "[E,B,]6"}
REST = "z6"

bars = []        # (section, tempo, rh, lh, str, vc, hn, drum)
for i, (r, l, c) in enumerate(zip(B_RH, B_LH, B_CH)):
    bars.append(("Second part (F major)" if i == 0 else None, 50 if i == 0 else None, r, l,
                 STR[c] if c else REST, VC[c] if c and i < 14 else REST, HN[c] if c and 4 <= i <= 11 else REST, None))
for i in range(len(C_RH)):
    name = {0: "The chord part (D minor)", 18: "The sweep", 23: "Ending"}.get(i)
    q = {0: 54, 18: 50, 23: 46}.get(i)
    bars.append((name, q, C_RH[i], C_LH[i], C_STR[i] or REST, C_VC[i] or REST, C_HN[i] or REST, C_DR[i]))

TOK = re.compile(r"(\(3)|(\{[^}]*\})|(\[[^\]]+\]|[\^=_]?[A-Ga-gz][,']*)(\d*)(/?)(\d*)")
NOTE = re.compile(r"[\^=_]?[A-Ga-g][,']*")
def durs(s):
    trip = 0
    for m in TOK.finditer(s):
        if m.group(1): trip = 3; continue
        if m.group(2): yield m, None; continue
        num = int(m.group(4)) if m.group(4) else 1
        d = Fr(num, int(m.group(6)) if m.group(6) else 2) if m.group(5) else Fr(num)
        if trip: d *= Fr(2, 3); trip -= 1
        yield m, d
for n, b in enumerate(bars, 1):
    for v in b[2:7]:
        tot = sum(d for m, d in durs(v) if d is not None)
        assert tot == 6, (n, v, tot)

# ------------------------------------------------------------------ ABC for the player
V = [("RH", "Piano", 0), ("LH", "Piano LH", 0), ("STR", "Strings", 48), ("VC", "Cello", 42), ("HN", "Horn", 60)]
out = ["X:1", "T:Für Elise: the second part and the chord part (arr.)", "C:L. van Beethoven, arr. for this video", "M:3/8", "L:1/16",
       "Q:3/8=50", "K:Am", "%%score {RH LH} STR VC HN"]
for vid, name, prog in V:
    out.append(f'V:{vid} name="{name}"' + (" clef=bass" if vid in ("LH", "VC") else ""))
for i, (vid, name, prog) in enumerate(V):
    out.append(f"[V:{vid}] %%MIDI program {prog}")
    line = [{"RH": PICK_RH, "LH": PICK_LH}.get(vid, "z3") + " |"]
    for n, b in enumerate(bars):
        pre = ""
        if b[1] and vid == "RH" and n > 0: pre = f"[Q:3/8={b[1]}] "
        if b[0] and vid == "RH": pre += f'"^{b[0]}" '
        line.append(pre + b[2 + i] + " |" + ("\n" if (n + 1) % 5 == 0 else ""))
    out.append(" ".join(line).replace("\n ", "\n").rstrip(" |") + " |]")
open("elise3.abc", "w").write("\n".join(out) + "\n")

# ------------------------------------------------------------------ note events
LET = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
def midi(tok, acc):
    m = re.match(r"([\^=_]?)([A-Ga-g])([,']*)", tok); a, l, o = m.groups()
    n = 60 + LET[l.upper()] + (12 if l.islower() else 0) - 12 * o.count(",") + 12 * o.count("'")
    key = (l.upper(), n // 12)
    if a: acc[key] = {"^": 1, "=": 0, "_": -1}[a]
    return n + acc.get(key, 0)
def events_of(s, t0, sx, voice):
    ev = []; t = t0; acc = {}
    for m, d in durs(s):
        if d is None:
            gs = NOTE.findall(m.group(2)); g = 0.055
            for k, nt in enumerate(gs):
                ev.append({"t": round(t - g * (len(gs) - k), 4), "dur": g, "midi": midi(nt, acc), "voice": voice, "grace": True})
            continue
        tok = m.group(3); d = float(d)
        if not tok.startswith("z"):
            for nt in (NOTE.findall(tok) if tok.startswith("[") else [tok]):
                ev.append({"t": round(t, 4), "dur": round(d * sx, 4), "midi": midi(nt, acc), "voice": voice})
        t += d * sx
    return ev
q = 50; sx = 60 / q / 6
EV = events_of(PICK_RH, 0.0, sx, "RH") + events_of(PICK_LH, 0.0, sx, "LH"); t = 3 * sx; sections = []; bar_t = []
for b in bars:
    if b[1]: q = b[1]; sx = 60 / q / 6
    if b[0]: sections.append({"name": b[0], "t": round(t, 4)})
    bar_t.append(round(t, 4))
    for i, v in enumerate(["RH", "LH", "STR", "VC", "HN"]):
        EV += events_of(b[2 + i], t, sx, v)
    if b[7]: EV.append({"t": round(t, 4), "dur": round(6 * sx, 4), "midi": 0, "voice": "DR", "kind": b[7]})
    t += 6 * sx
EV.sort(key=lambda e: (e["t"], e["midi"]))
json.dump({"events": EV, "sections": sections, "bars": bar_t, "end": round(t, 4)}, open("elise3_score.json", "w"), indent=0)
mel = [e for e in EV if e["voice"] != "DR"]
print(len(bars), "bars,", len(mel), "notes,", round(t, 1), "s of music; sections:", [(s["name"], round(s["t"], 1)) for s in sections])
print("range", min(e["midi"] for e in mel), "-", max(e["midi"] for e in mel))
