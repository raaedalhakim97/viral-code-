"""
build_youtube_queue.py — turn the finished videos into a post-ready manifest.

    python3 build_youtube_queue.py

Writes `youtube_queue.json`: one entry per finished 1080x1920 video, in the
order it should go out, carrying the title, description and tags already
written in that video's brief. Nothing here is invented — every title and
caption is lifted from the .md that was written alongside the video, so the
manifest and the briefs cannot drift apart.

WHY A MANIFEST RATHER THAN POSTING DIRECTLY. The posting step is one HTTP call
(`post_to_n8n.py`). Keeping the *what* separate from the *sending* means the
queue can be reviewed, reordered and diffed in git before anything is public,
and a failed send can be retried without rebuilding anything.

ORDER IS NOT ALPHABETICAL. Two rules decide it:

  PREREQUISITES. Some videos only make sense after another one has run —
  red_ball_2 reveals red_ball's answer, rotate_it spends what angle_to_place
  earned. Those are asserted below: a video never appears before its parent.

  STRONGEST HOOKS FIRST, otherwise. A channel with no history gets judged on
  its first few uploads, so the ones that need no setup lead.
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "youtube_queue.json")

# Posting order. Prerequisites are declared, not assumed — see the assert below.
ORDER = [
    # strongest standalone hooks first
    ("red_ball.mp4",           None),
    ("how_ai_reads.mp4",       None),
    ("calculator_vs_ai.mp4",   None),
    ("circle_ladder.mp4",      None),
    ("sales_line.mp4",         None),
    # then the series, each after what it depends on
    ("red_ball_2.mp4",         "red_ball.mp4"),
    ("angle_to_place.mp4",     None),
    ("cosine_similarity.mp4",  None),
    ("neuron.mp4",             "sales_line.mp4"),
    ("gradient_descent.mp4",   "sales_line.mp4"),
    ("best_line.mp4",          "sales_line.mp4"),
    ("rotate_it.mp4",          "angle_to_place.mp4"),
    ("sine_unroll.mp4",        None),
    ("square_ladder.mp4",      None),
    ("linear_geometry.mp4",    None),
    # the "where you actually use it" companions
    ("map_bearing.mp4",        "angle_to_place.mp4"),
    ("revision_line.mp4",      "best_line.mp4"),
    ("car_eyes.mp4",           "rotate_it.mp4"),
    ("name_equation.mp4",      None),
    # the puzzle shorts and the long-form tail
    ("ai_puzzle_1.mp4",        None),
    ("ai_puzzle_2.mp4",        None),
    ("ai_puzzle_3.mp4",        None),
    ("ai_puzzle_4.mp4",        None),
    ("ai_puzzle_5.mp4",        None),
    ("ai_puzzle_6.mp4",        None),
    ("ai_puzzle_7.mp4",        None),
    ("rope_puzzle.mp4",        None),
    ("carwash_puzzle.mp4",     None),
    ("no_calculator.mp4",      None),
    ("dimensions.mp4",         None),
    ("stadium_rave.mp4",       None),
    ("illusion_of_logic.mp4",  None),
]

# The seven puzzle shorts share one brief, so their titles live here instead —
# each names the puzzle and the algorithm, taken from the table in AI_PUZZLES.md.
PUZZLE_TITLES = {
    "ai_puzzle_1.mp4": "How AI solves a maze — breadth-first search",
    "ai_puzzle_2.mp4": "Wolf, goat, cabbage — how AI turns a story into a map",
    "ai_puzzle_3.mp4": "How AI plays tic-tac-toe — minimax",
    "ai_puzzle_4.mp4": "Six queens — how AI wins by being wrong cheaply",
    "ai_puzzle_5.mp4": "How AI solves sudoku — it never tries a number",
    "ai_puzzle_6.mp4": "The travelling salesman — why AI stops trying to be perfect",
    "ai_puzzle_7.mp4": "The sliding tile puzzle — A* and one good guess",
}

# No brief of its own — the long-form OIS piece.
LOOSE_TITLES = {
    "illusion_of_logic.mp4": "The illusion of logic — what AI is really doing",
}

BRIEF_OVERRIDE = {
    "ai_puzzle_1.mp4": "AI_PUZZLES.md", "ai_puzzle_2.mp4": "AI_PUZZLES.md",
    "ai_puzzle_3.mp4": "AI_PUZZLES.md", "ai_puzzle_4.mp4": "AI_PUZZLES.md",
    "ai_puzzle_5.mp4": "AI_PUZZLES.md", "ai_puzzle_6.mp4": "AI_PUZZLES.md",
    "ai_puzzle_7.mp4": "AI_PUZZLES.md",
}


def brief_for(video):
    name = BRIEF_OVERRIDE.get(video) or video[:-4].upper() + ".md"
    path = os.path.join(HERE, name)
    return path if os.path.exists(path) else None


def parse_brief(path):
    """Pull the title, the caption block and the hashtags out of a brief."""
    if not path:
        return None, None, []
    src = open(path).read()
    m = re.search(r"YouTube title:\*\*\s*`?([^`\n]+)`?", src)
    title = m.group(1).strip() if m else None
    cap = None
    blocks = re.findall(r"## Caption\s*\n+```\n(.*?)\n```", src, re.S)
    if blocks:
        cap = blocks[0].strip()
    tags = []
    if cap:
        tags = [t.lstrip("#") for t in re.findall(r"#(\w+)", cap)]
        cap = "\n".join(l for l in cap.splitlines()
                        if not l.strip().startswith("#")).strip()
    return title, cap, tags


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-show_entries", "format=duration,size",
         "-of", "default=nw=1:nk=1", path],
        capture_output=True, text=True).stdout.split()
    if len(out) < 4:
        return None
    return {"width": int(out[0]), "height": int(out[1]),
            "duration": round(float(out[2]), 3), "bytes": int(out[3])}


def main():
    seen, queue, missing, untitled = set(), [], [], []
    for i, (video, needs) in enumerate(ORDER, 1):
        path = os.path.join(HERE, video)
        if not os.path.exists(path):
            missing.append(video)
            continue
        assert needs is None or needs in seen, \
            f"{video} is queued before its prerequisite {needs}"
        seen.add(video)
        meta = probe(path)
        assert meta and (meta["width"], meta["height"]) == (1080, 1920), \
            f"{video} is not 1080x1920"
        bp = brief_for(video)
        title, desc, tags = parse_brief(bp)
        title = PUZZLE_TITLES.get(video, LOOSE_TITLES.get(video, title))
        if not title:
            untitled.append(video)
        queue.append({
            "slot": i,
            "file": video,
            "path": path,
            "title": title,
            "description": desc,
            "tags": tags[:15],
            "brief": os.path.basename(bp) if bp else None,
            "requires": needs,
            **(meta or {}),
        })

    json.dump({"count": len(queue), "videos": queue},
              open(OUT, "w"), indent=2, ensure_ascii=False)

    print(f"queued {len(queue)} videos -> {os.path.basename(OUT)}")
    if missing:
        print(f"  not on disk ({len(missing)}): {', '.join(missing)}")
    if untitled:
        print(f"  NO TITLE IN BRIEF ({len(untitled)}) — needs one before "
              f"posting: {', '.join(untitled)}")
    longs = [v["file"] for v in queue if v["duration"] > 60]
    if longs:
        print(f"  over 60s ({len(longs)}) — fine under the 3-min Shorts rule "
              f"but not classic Shorts: {', '.join(longs)}")
    print(f"\n  at 5/day that is {len(queue) / 5:.1f} days of runway.")


if __name__ == "__main__":
    main()
