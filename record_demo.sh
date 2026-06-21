#!/bin/bash
set -e

OUTDIR="/home/kali/mahdiesta/TheCompleteMahdiestaArsenal"
OUTFILE="$OUTDIR/mahdiesta-arsenal-demo.mp4"
TMPFILE="/tmp/demo_raw.mkv"
DISPLAY_NUM=":99"
URL="http://localhost:8766/demo.html"
WIDTH=1280
HEIGHT=720
FPS=30
RECORD_SECS=57

echo "[1] Starting Xvfb on display $DISPLAY_NUM..."
Xvfb $DISPLAY_NUM -screen 0 ${WIDTH}x${HEIGHT}x24 &
XVFB_PID=$!
sleep 1

echo "[2] Starting Chromium..."
DISPLAY=$DISPLAY_NUM /usr/bin/chromium \
  --no-sandbox \
  --disable-gpu \
  --disable-dev-shm-usage \
  --window-size=${WIDTH},${HEIGHT} \
  --window-position=0,0 \
  --app="$URL" \
  --disable-infobars \
  --noerrdialogs \
  --hide-scrollbars \
  --disable-extensions \
  --disable-translate \
  --no-first-run \
  --disable-default-apps \
  --disable-session-crashed-bubble &
CHROME_PID=$!

echo "[3] Waiting 4s for page to load and animation to start..."
sleep 4

echo "[4] Recording ${RECORD_SECS}s with ffmpeg..."
DISPLAY=$DISPLAY_NUM ffmpeg -y \
  -f x11grab \
  -video_size ${WIDTH}x${HEIGHT} \
  -framerate $FPS \
  -i $DISPLAY_NUM.0 \
  -t $RECORD_SECS \
  -c:v libx264 \
  -preset fast \
  -crf 18 \
  -pix_fmt yuv420p \
  "$OUTFILE" 2>&1 | grep -E "frame=|fps=|time=|error" || true

echo "[5] Cleaning up..."
kill $CHROME_PID 2>/dev/null || true
kill $XVFB_PID  2>/dev/null || true

echo ""
if [ -f "$OUTFILE" ]; then
  SIZE=$(du -sh "$OUTFILE" | cut -f1)
  echo "✓ VIDEO SAVED: $OUTFILE ($SIZE)"
else
  echo "✗ Recording failed - file not found"
fi
