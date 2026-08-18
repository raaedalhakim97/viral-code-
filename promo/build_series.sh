#!/usr/bin/env bash
# Stitch the OBSERVER COLLAPSE long cut for YouTube.
#
#   ./build_series.sh
#
# Takes the first 34.400s of each episode — beat 86, exactly 2064 frames, the
# point where every episode in this shell hands over to its follow card — and
# stitches the three together with the connective clips from the_series.py, so
# the long cut ends on ONE signature rather than three in a row.
#
#   open 4.0 + room 34.4 + bridge 3.2 + delay 34.4 + bridge 3.2 + scan 34.4
#   + outro 8.0  =  121.6 s  =  7296 frames at 60fps
#
# Prerequisites, all of which the script checks:
#   the three graded episodes exist
#   the four graded connective clips exist (render them from the_series.py)
set -euo pipefail
cd "$(dirname "$0")"

TRIM=34.4
OUT=observer_collapse_full.mp4

for f in the_room.mp4 the_delay.mp4 the_scan.mp4 \
         videos/SeriesOpen_g.mp4 videos/SeriesBridge1_g.mp4 \
         videos/SeriesBridge2_g.mp4 videos/SeriesOutro_g.mp4; do
    [ -f "$f" ] || { echo "missing $f — render and grade it first" >&2; exit 1; }
done

# One filter_complex rather than the concat demuxer: it re-encodes everything
# through the same path, so a codec or timebase difference between the episodes
# and the bridges cannot produce a silently broken join.
ffmpeg -v error -y \
  -i videos/SeriesOpen_g.mp4 \
  -t "$TRIM" -i the_room.mp4 \
  -i videos/SeriesBridge1_g.mp4 \
  -t "$TRIM" -i the_delay.mp4 \
  -i videos/SeriesBridge2_g.mp4 \
  -t "$TRIM" -i the_scan.mp4 \
  -i videos/SeriesOutro_g.mp4 \
  -filter_complex "[0:v][1:v][2:v][3:v][4:v][5:v][6:v]concat=n=7:v=1:a=0[v]" \
  -map "[v]" -r 60 -pix_fmt yuv420p -c:v libx264 -crf 21 -preset slow \
  -movflags +faststart "$OUT"

FRAMES=$(ffprobe -v error -count_frames -select_streams v:0 \
         -show_entries stream=nb_read_frames -of csv=p=0 "$OUT")
echo "$OUT  $FRAMES frames"
[ "$FRAMES" = "7296" ] || { echo "expected 7296 frames, got $FRAMES" >&2; exit 1; }
