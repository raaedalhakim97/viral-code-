# Notes for Claude

## Save context tokens with Headroom

Cloud sessions install [Headroom](https://github.com/headroomlabs-ai/headroom) at startup
(`.claude/hooks/session-start.sh`) and put `tools/` on the PATH. Before reading a large
JSON file or a long command output, pass it through `hrc`:

```bash
hrc promo/three/elise4_score.json        # a file
some_command | hrc -                     # a command's output
```

The stats line on stderr shows the saving (the complete Für Elise score: 44,016 → 20,968
tokens). JSON compresses best; dense text passes through unchanged, so read source code
and short outputs directly. Trimmed lists keep a `<<ccr:...>>` marker; open the original
file when exact values matter.

## Rendering

`promo/three/README.md` explains the headless three.js renderer and every film's checks.
