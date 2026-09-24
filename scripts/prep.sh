#!/usr/bin/env bash
# Extract background + Moby frames into build/ and key Moby onto transparency.
set -euo pipefail
cd "$(dirname "$0")/.."
FFMPEG="${FFMPEG:-$(python3 -c 'import imageio_ffmpeg; print(imageio_ffmpeg.get_ffmpeg_exe())')}"

rm -rf build/bg build/moby_raw build/moby
mkdir -p build/bg build/moby_raw

# 1500x1000 @ 60fps, 480 frames
"$FFMPEG" -loglevel error -y -i assets/background-loop.mp4 -q:v 2 build/bg/%04d.jpg
# Moby clip (2160x2880, ~24fps) scaled down; cropping happens in the scene.
"$FFMPEG" -loglevel error -y -i assets/moby-thinking.mp4 -vf scale=648:864 -fps_mode passthrough build/moby_raw/%04d.png

python3 scripts/key_moby.py
