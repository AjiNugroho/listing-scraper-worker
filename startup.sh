#!/bin/bash
set -e

# Start virtual display (required for headful Chromium)
Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
XVFB_PID=$!
export DISPLAY=:99

# Give Xvfb a moment to initialize
sleep 1
echo "✓ Xvfb started (PID $XVFB_PID, DISPLAY=$DISPLAY)"

echo "Starting request worker..."
celery -A celery_app worker \
  -Q scrape_request_listing \
  -n request@%h \
  --loglevel=info --concurrency=1 &

echo "Starting response worker..."
celery -A celery_app worker \
  -Q scrape_response_listing \
  -n response@%h \
  --loglevel=info --concurrency=2 &

wait
