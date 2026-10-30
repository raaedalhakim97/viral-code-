"""hrc: compress a large command output or file with Headroom before reading it.

usage:  hrc FILE          or    some_command | hrc -
Prints the compressed text, then one line of stats on stderr.

It hands the text to Headroom as a shell tool result (Headroom deliberately leaves
file-read results alone) with protect_recent=0 (by default it leaves the newest
messages alone, and this is always the newest). JSON arrays compress best, often to
half; text that is already dense passes through unchanged. Lists that are trimmed
keep a <<ccr:...>> marker: the original is cached locally by Headroom."""
import sys, time
from headroom import compress
src = sys.stdin.read() if sys.argv[1] == "-" else open(sys.argv[1], errors="replace").read()
msgs = [{"role": "user", "content": "Inspect this output."},
        {"role": "assistant", "content": [{"type": "tool_use", "id": "t1", "name": "Bash", "input": {"command": "cat"}}]},
        {"role": "user", "content": [{"type": "tool_result", "tool_use_id": "t1", "content": src}]},
        {"role": "assistant", "content": "Read."}, {"role": "user", "content": "Go on."}]
t0 = time.time(); r = compress(msgs, model="claude-sonnet-4-5", protect_recent=0)
out = r.messages[2]["content"][0]["content"]
print(out if isinstance(out, str) else "\n".join(b.get("text", "") for b in out))
print(f"[headroom] {r.tokens_before} -> {r.tokens_after} tokens ({r.compression_ratio:.0%} saved, {(time.time()-t0)*1000:.0f} ms) {[t for t in r.transforms_applied if 'protected' not in t]}", file=sys.stderr)
