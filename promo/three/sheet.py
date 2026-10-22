import glob, re, subprocess, sys
d = sys.argv[1]; out = sys.argv[2]; per = int(sys.argv[3]) if len(sys.argv) > 3 else 7; tw = int(sys.argv[4]) if len(sys.argv) > 4 else 300
tm = lambda f: float(re.search(r"t(\d+(?:\.\d+)?)\.png", f).group(1))
fs = sorted(glob.glob(f"{d}/t*.png"), key=tm)
th = round(tw * 16 / 9)
for k in range(0, len(fs), 14):
    chunk = fs[k:k+14]
    cmd = ["ffmpeg","-v","error","-y"]
    for f in chunk: cmd += ["-i", f]
    flt = "".join(f"[{i}:v]scale={tw}:{th}[s{i}];" for i in range(len(chunk)))
    flt += "".join(f"[s{i}]" for i in range(len(chunk))) + f"xstack=inputs={len(chunk)}:layout=" + "|".join(f"{(i%per)*tw}_{(i//per)*th}" for i in range(len(chunk)))
    subprocess.run(cmd + ["-filter_complex", flt, "-frames:v", "1", f"{out}{k//14}.png"], check=True)
print([tm(f) for f in fs])
