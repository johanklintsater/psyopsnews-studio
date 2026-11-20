#!/usr/bin/env bash
# Requires separate streaming server and authorized YouTube stream key.
set -euo pipefail
: "${YOUTUBE_STREAM_KEY:?Set stream key securely}"
INPUT="${1:?Usage: loop_stream.sh episode.mp4}"
ffmpeg -re -stream_loop -1 -i "$INPUT" -c:v libx264 -preset veryfast -b:v 3500k -maxrate 3500k -bufsize 7000k -pix_fmt yuv420p -g 50 -r 25 -c:a aac -b:a 128k -ar 44100 -f flv "rtmp://a.rtmp.youtube.com/live2/${YOUTUBE_STREAM_KEY}"
