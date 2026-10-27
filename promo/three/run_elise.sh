#!/bin/bash
# The Shape of Für Elise: 1920x1080 60fps, 3,720 frames in 3 parallel chunks
cd "$(dirname "$0")"
for spec in "0 1240" "1240 2480" "2480 3720"; do set -- $spec
  node render.mjs scene_elise.js echunks/c_$1.mp4 1920 1080 $1 $2 > echunks/log_$1.txt 2>&1 &
done
wait
printf "file 'c_0.mp4'\nfile 'c_1240.mp4'\nfile 'c_2480.mp4'\n" > echunks/list.txt
ffmpeg -v error -y -f concat -safe 0 -i echunks/list.txt -c:v copy elise_master_video.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate -show_entries format=duration -of default=nw=1 elise_master_video.mp4
grep -h "PAGE ERROR" echunks/log_*.txt
echo E-DONE
