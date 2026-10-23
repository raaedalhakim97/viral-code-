"""Master a wav: gentle glue compression, then two-pass loudnorm to -14 LUFS / -1.5 dBTP.
usage: python3 master.py in.wav out.wav"""
import json, subprocess, sys

src, dst = sys.argv[1:3]
GLUE = "acompressor=threshold=-20dB:ratio=2:attack=30:release=250:makeup=1"
LN = "loudnorm=I=-14:TP=-1.5:LRA=11"
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", src, "-af", f"{GLUE},{LN}:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
m = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
ln2 = (f"{LN}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}"
       f":measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", src, "-af", f"{GLUE},{ln2}", "-ar", "48000", "-c:a", "pcm_s24le", dst], check=True)
r = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", dst, "-af", f"{LN}:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True).stderr
o = json.loads(r[r.rindex("{"):r.rindex("}") + 1])
print(f"{dst}: {o['input_i']} LUFS, true peak {o['input_tp']} dBTP")
