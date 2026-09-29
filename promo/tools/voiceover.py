"""
voiceover.py — lay a beat-timed .srt over a silent render, free and offline.

    python3 tools/voiceover.py lissajous_dance

Reads promo/<name>.srt and promo/<name>.mp4, speaks each cue with Piper at
the timestamp the cue carries, and writes promo/<name>_voiced.mp4.

WHY THIS EXISTS. The renders are silent and beat-locked, so the voice has
to land on the stage boundaries rather than wherever a sentence happens to
end. Every cue is synthesised separately and placed at its own timestamp;
nothing is stretched to fit, and a cue that will not fit its window fails
the run instead of running over the next one.

VOICE. Piper, MIT-licensed, running locally — no account and no per-use
cost. Model: en-us-ryan-high (22.05 kHz), from the piper v0.0.2 GitHub
release, because the current voice catalogue is on HuggingFace and that
host is refused by this environment's network policy.

    curl -sL -o ryan.tgz https://github.com/rhasspy/piper/releases/\
download/v0.0.2/voice-en-us-ryan-high.tar.gz

LEVELS. Piper normalises every clip it makes to 0 dBFS, so boosting clips
it. Each cue is pulled to 0.70 instead, landing the finished track at
-3 dB peak and leaving room for a music bed underneath.
"""
import json
import os
import subprocess
import sys
import wave

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VOICE_GAIN = 0.70          # piper clips are already at 0 dBFS
DURATION = 40.0


def cues(path):
    def secs(ts):
        h, m, rest = ts.split(":")
        s, ms = rest.split(",")
        return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
    out = []
    for block in open(path).read().strip().split("\n\n"):
        lines = block.strip().split("\n")
        a, z = lines[1].split(" --> ")
        out.append((secs(a), secs(z), " ".join(lines[2:]).strip()))
    return out


def main(name, model):
    from piper import PiperVoice
    srt = os.path.join(HERE, f"{name}.srt")
    mp4 = os.path.join(HERE, f"{name}.mp4")
    work = os.path.join(HERE, ".vo", name)
    os.makedirs(work, exist_ok=True)

    voice = PiperVoice.load(model, config_path=model + ".json")
    parts = []
    for i, (a, z, text) in enumerate(cues(srt), 1):
        wav = os.path.join(work, f"{i:02d}.wav")
        with wave.open(wav, "wb") as w:
            voice.synthesize_wav(text, w)
        with wave.open(wav) as w:
            spoken = w.getnframes() / w.getframerate()
        if spoken > z - a:
            raise SystemExit(
                f"cue {i} runs {spoken:.2f}s in a {z - a:.2f}s window — "
                f"shorten the line, do not stretch the audio:\n  {text}")
        parts.append((a, wav))

    ins, filt, labs = [], [], []
    for i, (a, wav) in enumerate(parts):
        ins += ["-i", wav]
        ms = int(a * 1000)
        filt.append(f"[{i}:a]aresample=48000,adelay={ms}|{ms},"
                    f"volume={VOICE_GAIN}[v{i}]")
        labs.append(f"[v{i}]")
    filt.append(f"{''.join(labs)}amix=inputs={len(parts)}:normalize=0,"
                f"apad,atrim=0:{DURATION},asetpts=N/SR/TB[vo]")
    track = os.path.join(work, "track.wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex",
                    ";".join(filt), "-map", "[vo]", "-c:a", "pcm_s16le",
                    track], check=True)

    out = os.path.join(HERE, f"{name}_voiced.mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-i", track,
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", out], check=True)
    print(out)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    main(sys.argv[1], os.environ.get(
        "PIPER_MODEL", os.path.expanduser("~/piper/en-us-ryan-high.onnx")))
