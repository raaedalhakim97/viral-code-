# Butterfly Effect score, v2. Writes the full score (for the sheet-music
# preview) plus three stems rendered separately, so the clarinet fades and
# the drum "rush" can be smooth volume curves instead of velocity steps.
HEAD = """X:1
T:The Butterfly Effect (v2)
C:original score for @observer.collapse
M:4/4
L:1/8
Q:1/4=76
"""
VOICES = [  # (stem, name, header lines, body)
 ("orch", "Horns", ["%%MIDI program 60", "%%MIDI control 7 104"], """
z8 | z8 | z8 | z8 |
!f! D2 E2 F2 A2 | B4 A2 G2 | A2 c2 e4 |
!ff! d6 c2 | B6 A2 | G4 z A3 | B4 c4 |
!fff! d8 | d8 |]"""),
 ("orch", "Strings", ["%%MIDI program 48", "%%MIDI control 7 84"], """
!p! D3 E F2 A2 | G3 F E2 D2 | F3 G A2 B2 | A6 ^c2 |
!f! D2 C2 B,2 A,2 | B,4 F,4 | A,4 G,4 |
!f! F8 | F8 | D4 z ^C3 | D4 E4 |
!ff! ^F8 | ^F8 |]"""),
 ("orch", "Harp", ["%%MIDI program 46", "%%MIDI control 7 78"], """
z8 | z8 | z8 | z8 | z8 | z8 | z8 |
!mf! D,/F,/A,/D/ F,/A,/D/F/ A,/D/F/A/ D/F/A/d/ | B,,/D,/F,/B,/ D,/F,/B,/D/ F,/B,/D/F/ B,/D/F/B/ |
G,,/B,,/D,/G,/ B,,/D,/G,/B,/ z A,,/^C,/ E,/A,/^C/E/ | B,,/D,/F,/B,/ D,/F,/B,/D/ C,/E,/G,/C/ E,/G,/C/E/ |
D,/^F,/A,/D/ ^F,/A,/D/^F/ A,/D/^F/A/ D2 | z8 |]"""),
 ("orch", "Choir", ["%%MIDI program 52", "%%MIDI control 7 92"], """
z8 | z8 | z8 | z8 | z8 | z8 | z8 |
!f! [D,F,A,]8 | [D,F,B,]8 | [D,G,B,]4 z [^C,E,A,]3 | [D,F,B,]4 [E,G,C]4 |
!ff! [D,^F,A,]8 | [D,^F,A,]8 |]"""),
 ("orch", "Ostinato", ["%%MIDI program 48", "%%MIDI control 7 80"], """
!pp! D,A,DA, D,A,DA, | D,A,DA, D,A,DA, | !p! B,,F,B,F, B,,F,B,F, | !mf! A,,E,A,E, A,,E,A,E, |
!f! D,A,DA, D,A,DA, | B,,F,B,F, B,,F,B,F, | F,,C,F,C, C,G,CG, |
!ff! D,A,DA, D,A,DA, | B,,F,B,F, B,,F,B,F, | G,,D,G,D, z A,,E,A, | B,,F,B,F, C,G,CG, |
!fff! D,A,DA, D,A,DA, | D,8 |]"""),
 ("orch", "Contrabass", ["%%MIDI program 43", "%%MIDI control 7 112"], """
!p! D,,8 | D,,8 | B,,,8 | !mf! A,,,8 |
!f! D,,8 | B,,,8 | F,,4 C,,4 |
!ff! D,,8 | B,,,8 | G,,,4 z A,,,3 | B,,,4 C,,4 |
!fff! D,,8 | D,,8 |]"""),
 ("orch", "Timpani", ["%%MIDI program 47", "%%MIDI control 7 116"], """
z8 | z8 | z8 | !mf! z6 A,,2 |
!ff! D,,2 z2 D,,D,, A,,2 | D,,2 z2 D,,D,, A,,2 | D,,2 z2 z2 A,,2 |
!ff! D,,4 z4 | D,,2 z2 D,,D,, A,,2 | D,,2 z2 z A,,3 | D,,2 z2 A,,2 z2 |
!fff! D,,2 z2 D,,2 z2 | D,,2 z6 |]"""),
 ("clar", "Clarinet", ["%%MIDI program 71", "%%MIDI control 7 110"], """
!mf! D3 E F2 A2 | G3 F E2 D2 | F3 G A2 B2 | A6 ^c2 |
z8 | z8 | z8 | z8 | z8 | z8 | z8 | z8 |
!mf! D3 E ^F2 A2 |]"""),
 ("drums", "Drums", ["%%MIDI channel 10", "%%MIDI control 7 110"], """
""" + " ".join(["!mf! [C,,F,,]/F,,/G,,/F,,/ G,,/F,,/G,,/F,,/ [C,,F,,]/F,,/G,,/F,,/ G,,/F,,/G,,/F,,/ |"] * 12) + """
[C,,F,,]2 z6 |]"""),
]

def score(stems, title_suffix=""):
    vs = [v for v in VOICES if v[0] in stems]
    out = HEAD
    for i, (_, name, hdr, _) in enumerate(vs, 1):
        out += f'V:{i} name="{name}"' + (" clef=bass" if name in ("Ostinato", "Contrabass", "Timpani", "Drums") else "") + "\n"
        out += "\n".join(hdr) + "\n"
    out += "K:Dm\n"
    for i, (_, _, _, body) in enumerate(vs, 1):
        out += f"V:{i}\n" + body.strip() + "\n"
    return out

open("full.abc", "w").write(score({"orch", "clar", "drums"}))
for st in ("orch", "clar", "drums"):
    open(f"{st}.abc", "w").write(score({st}))

# highest written pitch, per voice (C = middle C = MIDI 60)
import re
def midi(tok):
    m = re.match(r"([_^=]?)([A-Ga-g])([,']*)", tok)
    acc, n, oc = m.groups()
    base = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}[n.upper()] + (60 if n.isupper() else 72)
    base += 12 * oc.count("'") - 12 * oc.count(",")
    return base + (1 if acc == "^" else -1 if acc == "_" else 0) - (1 if n.upper() == "B" and acc == "" else 0)
names = "C C# D Eb E F F# G Ab A Bb B".split()
for st, name, _, body in VOICES:
    if name == "Drums": continue
    toks = re.findall(r"[_^=]?[A-Ga-g][,']*", re.sub(r"![^!]*!", "", body))
    top = max(midi(t) for t in toks)
    print(f"{name:11s} highest note {names[top % 12]}{top // 12 - 1}")
