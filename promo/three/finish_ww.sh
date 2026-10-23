#!/bin/bash
# Part II deliverables from ${MASTER:-ww_master_fixed.mp4} (+ the portrait teaser render) and the mastered audio.
set -e
cd "$(dirname "$0")"
A=${A:-ww_audio}; OUT=ww_out; mkdir -p $OUT
GRAIN="noise=alls=${GRAIN:-2}:allf=t,format=yuv420p"
ENC="-c:v libx264 -preset slow -crf ${CRF:-20} -pix_fmt yuv420p -profile:v high -tune grain"
AAC="-c:a aac -b:a 192k -movflags +faststart"

# 1. 95 s master, with VO and without. Two-pass 2.3 Mbps keeps each under ~30 MB.
M2="-c:v libx264 -preset slow -b:v 2300k -maxrate 4500k -bufsize 9000k -pix_fmt yuv420p -profile:v high"
ffmpeg -v error -y -i ${MASTER:-ww_master_fixed.mp4} -vf "$GRAIN" $M2 -pass 1 -passlogfile $OUT/p1 -an -f null /dev/null
for v in "ww_mix_m:smart_lookup_part2_weighted_wave" "ww_music_m:smart_lookup_part2_no_vo"; do
 ffmpeg -v error -y -i ${MASTER:-ww_master_fixed.mp4} -i $A/${v%%:*}.wav -vf "$GRAIN" $M2 -pass 2 -passlogfile $OUT/p1 \
  -map 0:v -map 1:a $AAC -shortest $OUT/${v##*:}.mp4
done

# 2. 30 s hero loop: 50.5-81.3 s (land -> burst -> reveal), music only, its tail crossfaded
#    over its head so the last frame flows into the first
T0=50.5; L=30.8; X=0.8; B=$(echo "$L-$X" | bc)
ffmpeg -v error -y -i ${MASTER:-ww_master_fixed.mp4} -i $A/ww_music_m.wav -filter_complex "
 [0:v]trim=start=$T0:duration=$L,setpts=PTS-STARTPTS,split=3[a][b][c];
 [a]trim=0:$X,setpts=PTS-STARTPTS[head]; [b]trim=$X:$B,setpts=PTS-STARTPTS[body]; [c]trim=$B:$L,setpts=PTS-STARTPTS[tail];
 [tail][head]xfade=transition=fade:duration=$X:offset=0[seam]; [body][seam]concat=n=2:v=1:a=0,$GRAIN[v];
 [1:a]atrim=start=$T0:duration=$L,asetpts=PTS-STARTPTS,asplit=3[p][q][r];
 [p]atrim=0:$X,asetpts=PTS-STARTPTS[ah]; [q]atrim=$X:$B,asetpts=PTS-STARTPTS[ab]; [r]atrim=$B:$L,asetpts=PTS-STARTPTS[at];
 [at]afade=t=out:d=$X:curve=qsin[at2]; [ah]afade=t=in:d=$X:curve=qsin[ah2]; [at2][ah2]amix=inputs=2:normalize=0[as]; [ab][as]concat=n=2:v=0:a=1[aout]" \
 -map "[v]" -map "[aout]" $ENC $AAC $OUT/smart_lookup_part2_hero_loop_30s.mp4

# 3. 15 s vertical teaser: frames 3840-4740 (64-79 s) rendered in portrait, with the VO mix
if [ -f ww_teaser_video.mp4 ]; then
ffmpeg -v error -y -i ww_teaser_video.mp4 -ss 64 -t 15 -i $A/ww_mix_m.wav \
 -vf "$GRAIN" -af "afade=t=in:d=0.25,afade=t=out:st=14.6:d=0.4,alimiter=limit=0.708:attack=1:release=60:level=false" $ENC -map 0:v -map 1:a $AAC -shortest $OUT/smart_lookup_part2_teaser_15s_vertical.mp4
fi
for f in $OUT/*.mp4; do
 printf "%-60s %6.2f MB  " $f $(echo "$(stat -c%s $f)/1048576" | bc -l)
 ffprobe -v error -show_entries format=duration -show_entries stream=width,height,r_frame_rate -of csv=p=0 $f | tr '\n' ' '; echo
done
