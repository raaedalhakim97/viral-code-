import glob, re, subprocess, sys
d, out, per, tw = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
tm = lambda f: float(re.search(r"t(\d+(?:\.\d+)?)\.png", f).group(1))
fs = sorted(glob.glob(f"{d}/t*.png"), key=tm); th = round(tw * 9 / 16)
for k in range(0, len(fs), per * 3):
    ch = fs[k:k + per * 3]; cmd = ["ffmpeg", "-v", "error", "-y"]
    for f in ch: cmd += ["-i", f]
    flt = "".join(f"[{i}:v]scale={tw}:{th}[s{i}];" for i in range(len(ch)))
    flt += "".join(f"[s{i}]" for i in range(len(ch))) + f"xstack=inputs={len(ch)}:layout=" + "|".join(f"{(i%per)*tw}_{(i//per)*th}" for i in range(len(ch)))
    subprocess.run(cmd + ["-filter_complex", flt, "-frames:v", "1", f"{out}{k//(per*3)}.png"], check=True)
print([tm(f) for f in fs])
