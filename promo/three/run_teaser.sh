#!/bin/bash
cd "$(dirname "$0")"
for spec in "3840 4140" "4140 4440" "4440 4740"; do set -- $spec
  node render.mjs scene_weighted_wave.js tchunks/c_$1.mp4 1080 1920 $1 $2 > tchunks/log_$1.txt 2>&1 &
done
wait
printf "file 'c_3840.mp4'\nfile 'c_4140.mp4'\nfile 'c_4440.mp4'\n" > tchunks/list.txt
ffmpeg -v error -y -f concat -safe 0 -i tchunks/list.txt -c:v copy ww_teaser_video.mp4
ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames,width,height -show_entries format=duration -of default=nw=1 ww_teaser_video.mp4
grep -h "PAGE ERROR" tchunks/log_*.txt
echo T-DONE
