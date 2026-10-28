#!/bin/bash
# The Shape of Für Elise III (complete): 1920x1080 30fps, 4,410 frames in 3 parallel chunks
cd "$(dirname "$0")"
for spec in "0 1470" "1470 2940" "2940 4410"; do set -- $spec
  node render.mjs scene_elise3.js e3chunks/c_$1.mp4 1920 1080 $1 $2 > e3chunks/log_$1.txt 2>&1 &
done
wait
printf "file 'c_0.mp4'\nfile 'c_1470.mp4'\nfile 'c_2940.mp4'\n" > e3chunks/list.txt
ffmpeg -v error -y -f concat -safe 0 -i e3chunks/list.txt -c:v copy elise3_master_video.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate -show_entries format=duration -of default=nw=1 elise3_master_video.mp4
grep -h "PAGE ERROR" e3chunks/log_*.txt
echo E3-DONE
