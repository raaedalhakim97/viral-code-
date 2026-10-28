#!/bin/bash
# The Shape of Für Elise II: 1920x1080 60fps, 3,342 frames in 3 parallel chunks
cd "$(dirname "$0")"
for spec in "0 1114" "1114 2228" "2228 3342"; do set -- $spec
  node render.mjs scene_elise2.js e2chunks/c_$1.mp4 1920 1080 $1 $2 > e2chunks/log_$1.txt 2>&1 &
done
wait
printf "file 'c_0.mp4'\nfile 'c_1114.mp4'\nfile 'c_2228.mp4'\n" > e2chunks/list.txt
ffmpeg -v error -y -f concat -safe 0 -i e2chunks/list.txt -c:v copy elise2_master_video.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate -show_entries format=duration -of default=nw=1 elise2_master_video.mp4
grep -h "PAGE ERROR" e2chunks/log_*.txt
echo E2-DONE
