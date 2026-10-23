#!/bin/bash
cd "$(dirname "$0")"
for spec in "0 1900" "1900 3800" "3800 5700"; do set -- $spec
  node render.mjs scene_weighted_wave.js wchunks/c_$1.mp4 1920 1080 $1 $2 > wchunks/log_$1.txt 2>&1 &
done
wait
printf "file 'c_0.mp4'\nfile 'c_1900.mp4'\nfile 'c_3800.mp4'\n" > wchunks/list.txt
ffmpeg -v error -y -f concat -safe 0 -i wchunks/list.txt -c:v copy ww_master_video.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,r_frame_rate -show_entries format=duration,size -of default=nw=1 ww_master_video.mp4
grep -h "PAGE ERROR" wchunks/log_*.txt
echo WW-DONE
