"""Fur Elise (Beethoven, WoO 59, public domain): our arrangement for 'The Shape of Fur Elise'.
Solo piano -> strings + cello -> full orchestra climax -> solo piano. Writes elise.abc.
Every bar is checked to hold exactly 3/8 (6 sixteenths); the pickup holds 2."""
import re

THEME = ["e^de B=dc", "A2 zCEA", "B2 zE^GB", "c2 zEe^d", "e^de B=dc", "A2 zCEA", "B2 zEcB"]
TH_LH = ["z6", "A,,E,A, z3", "E,,E,^G, z3", "A,,E,A, z3", "z6", "A,,E,A, z3", "E,,E,^G, z3"]
TH_CH = ["E", "Am", "E", "Am", "E", "Am", "E"]          # harmony under each theme bar
MID = ["A2 zBcd", "e3 Gfe", "d3 Fed", "c3 Edc", "B2 zEe^d"]
MID_LH = ["A,,E,A, z3", "C,G,C z3", "G,,G,B, z3", "A,,E,A, z3", "E,,E,^G, z3"]
MID_CH = ["Am", "C", "G", "Am", "E"]
STR = {"E": "[^G,B,E]6", "Am": "[A,CE]6", "C": "[G,CE]6", "G": "[G,B,D]6"}
VC = {"E": "E,,6", "Am": "A,,6", "C": "C,6", "G": "G,,6"}
HN = {"E": "[E,B,]6", "Am": "[A,E]6", "C": "[C,G,]6", "G": "[G,,D,]6"}
REST = "z6"

bars = []        # (section label, tempo or None, rh, lh, strings, cello, horn)
def add(sec, rh, lh, ch, strings=False, cello=False, horn=False, q=None):
    for i, (r, l, c) in enumerate(zip(rh, lh, ch)):
        bars.append((sec if i == 0 else None, q if i == 0 else None, r, l,
                     STR[c] if strings else REST, VC[c] if cello else REST, HN[c] if horn else REST))

# 1. solo piano: theme, repeat, second ending into the middle phrase  (~0:00-0:22)
add("Solo piano", THEME + ["A2 z2e^d"], TH_LH + ["A,,E,A, z3"], TH_CH + ["Am"], q=55)
add(None, THEME + MID[:1], TH_LH + MID_LH[:1], TH_CH + MID_CH[:1])
add(None, MID[1:], MID_LH[1:], MID_CH[1:])
# 2. strings and cello join the theme                                 (~0:22-0:31)
add("Strings + cello", THEME + ["A2 z2e^d"], TH_LH + ["A,,E,A, z3"], TH_CH + ["Am"], strings=True, cello=True)
# 3. climax: full orchestra, broadening                               (~0:31-0:48)
add("Full orchestra", THEME + MID[:1], TH_LH + MID_LH[:1], TH_CH + MID_CH[:1], True, True, True, q=48)
add(None, MID[1:], MID_LH[1:], MID_CH[1:], True, True, True)
# 4. solo piano again, the final phrase, ending on A                  (~0:48-1:00)
add("Solo piano", THEME + ["A6"], TH_LH + ["A,,E,A, z3"], TH_CH + ["Am"], q=52)
bars.append((None, None, "[A,CEA]6", "[A,,,A,,]6", REST, REST, REST))

def dur(s):
    tot = 0
    for m in re.finditer(r"(\[[^\]]+\]|[\^=_]?[A-Ga-gz][,']*)(\d*)", s):
        tot += int(m.group(2) or 1)
    return tot
for n, b in enumerate(bars, 1):
    for v in b[2:]:
        assert dur(v) == 6, (n, v, dur(v))

V = [("RH", "Piano", 0), ("LH", "Piano LH", 0), ("STR", "Strings", 48), ("VC", "Cello", 42), ("HN", "Horn", 60)]
out = ["X:1", "T:Fur Elise - The Shape of Fur Elise (arr.)", "C:L. van Beethoven, arr. for this video", "M:3/8", "L:1/16", "Q:3/8=55", "K:Am",
       "%%score {RH LH} STR VC HN"]
for vid, name, prog in V:
    out.append(f'V:{vid} name="{name}"' + (" clef=bass" if vid in ("LH", "VC") else ""))
for i, (vid, name, prog) in enumerate(V):
    out.append(f"[V:{vid}] %%MIDI program {prog}")
    line = ["e^d |" if vid == "RH" else "z2 |"]
    for n, b in enumerate(bars):
        pre = ""
        if b[1] and vid == "RH" and n > 0: pre = f"[Q:3/8={b[1]}] "
        if b[0] and vid == "RH": pre += f'"^{b[0]}" '
        line.append(pre + b[2 + i] + " |" + ("\n" if (n + 1) % 6 == 0 else ""))
    out.append(" ".join(line).replace("\n ", "\n").rstrip(" |") + " |]")
open("elise.abc", "w").write("\n".join(out) + "\n")
sec = 0.0; q = 55
for b in bars:
    if b[1]: q = b[1]
    sec += 60 / q
print(len(bars), "bars,", round(sec + 2 * 60 / 55 / 6, 1), "s")

# ---------------------------------------------------------------- note events for the sampler and the scene
import json
LET = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
def midi(tok, acc_state):
    m = re.match(r"([\^=_]?)([A-Ga-g])([,']*)", tok); acc, l, octs = m.groups()
    n = 60 + LET[l.upper()] + (12 if l.islower() else 0) - 12 * octs.count(",") + 12 * octs.count("'")
    key = (l.upper(), n // 12)
    if acc: acc_state[key] = {"^": 1, "=": 0, "_": -1}[acc]
    return n + acc_state.get(key, 0)
def events_of(s, t0, sx, voice, acc):
    ev = []; t = t0
    for m in re.finditer(r"(\[[^\]]+\]|[\^=_]?[A-Ga-gz][,']*)(\d*)", s):
        tok, d = m.group(1), int(m.group(2) or 1)
        if not tok.startswith("z"):
            for nt in (re.findall(r"[\^=_]?[A-Ga-g][,']*", tok) if tok.startswith("[") else [tok]):
                ev.append({"t": round(t, 4), "dur": round(d * sx, 4), "midi": midi(nt, acc), "voice": voice})
        t += d * sx
    return ev, t
EV = []; t = 0.0; q = 55; sx = 60 / q / 6
for vi, v in enumerate(["RH", "LH"]):
    if v == "RH": EV += events_of("e^d", 0.0, sx, "RH", {})[0]
T0 = 2 * sx; t = T0; sections = []
for b in bars:
    if b[1]: q = b[1]; sx = 60 / q / 6
    if b[0]: sections.append({"name": b[0], "t": round(t, 4)})
    for i, v in enumerate(["RH", "LH", "STR", "VC", "HN"]):
        EV += events_of(b[2 + i], t, sx, v, {})[0]
    t += 6 * sx
EV.sort(key=lambda e: (e["t"], e["midi"]))
json.dump({"events": EV, "sections": sections, "end": round(t, 4)}, open("elise_score.json", "w"), indent=0)
print(len(EV), "events; sections", sections, "end", round(t, 2))
