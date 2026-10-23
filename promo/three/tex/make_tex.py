import subprocess, pathlib
PRE = r"""\documentclass[border=2pt]{standalone}
\usepackage{amsmath,amssymb,xcolor}
\definecolor{ink}{HTML}{EAF2FF}\definecolor{wt}{HTML}{9B5CF6}\definecolor{gold}{HTML}{FFD166}
\begin{document}\color{ink}"""
EQ = {
 "eq_psi": r"$\displaystyle \psi(x)=\sum_{k=1}^{32}{\color{wt}\theta_k}\,\sin\!\left(2\pi f_k\,x+\varphi_k\right)$",
 "eq_update": r"${\color{wt}\theta}\;\leftarrow\;{\color{wt}\theta}-\eta\,\nabla L$",
}
for k in range(1, 33):
    EQ[f"th_{k}"] = r"${\color{wt}\theta_{%d}}$" % k
for name, body in EQ.items():
    pathlib.Path(f"{name}.tex").write_text(PRE + body + r"\end{document}")
    subprocess.run(["latex", "-interaction=nonstopmode", "-halt-on-error", f"{name}.tex"], check=True, capture_output=True)
    subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "-o", f"{name}.svg", f"{name}.dvi"], check=True, capture_output=True)
print("svgs:", len(list(pathlib.Path(".").glob("*.svg"))))
