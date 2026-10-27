"""Equations for 'The Shape of Fur Elise' (latex + dvisvgm, ink #EAF2FF, frequency in gold)."""
import subprocess, pathlib
PRE = r"""\documentclass[border=2pt]{standalone}
\usepackage{amsmath,amssymb,xcolor}
\definecolor{ink}{HTML}{EAF2FF}\definecolor{gold}{HTML}{FFD166}\definecolor{tq}{HTML}{2EE6C8}\definecolor{vi}{HTML}{9B5CF6}
\begin{document}\color{ink}"""
EQ = {
 "eq_note":    r"$y = A\,e^{-t/\tau}\,\sin\!\left(2\pi {\color{gold}f}\,t\right)$",
 "eq_beat":    r"$\displaystyle \sin a+\sin b \;=\; 2\cos\frac{a-b}{2}\,\sin\frac{a+b}{2}$",
 "eq_chord":   r"$\vec p(t)=\big(\sin 2\pi {\color{gold}f_1} t,\;\; \sin(2\pi {\color{gold}f_2} t+\varphi_2),\;\; \sin(2\pi {\color{gold}f_3} t+\varphi_3)\big)$",
 "eq_series":  r"$\displaystyle x(t)=\sum_{n=1}^{12} a_n\,\sin\!\left(2\pi\, n{\color{gold}f_0}\, t+\varphi_n\right)$",
 "eq_fourier": r"$\displaystyle X({\color{gold}f})=\int_{-\infty}^{\infty} x(t)\, e^{-i\,2\pi {\color{gold}f}\, t}\,dt$",
}
for name, body in EQ.items():
    pathlib.Path(f"{name}.tex").write_text(PRE + body + r"\end{document}")
    subprocess.run(["latex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"], check=True, capture_output=True)
    subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "-o", f"{name}.svg", f"{name}.dvi"], check=True, capture_output=True)
print("svgs:", sorted(p.name for p in pathlib.Path(".").glob("*.svg")))
