#!/bin/bash
set -e

WORKER_TYPE="${WORKER_TYPE:-both}"

if [ "$WORKER_TYPE" = "request" ]; then
    # Request worker needs headful Chromium → start Xvfb
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    export DISPLAY=:99
    sleep 1
    echo "✓ Xvfb started (DISPLAY=$DISPLAY)"

    echo "Starting request worker..."
    exec celery -A celery_app worker \
      -Q scrape_request_listing \
      -n request@%h \
      --loglevel=info --concurrency=1

elif [ "$WORKER_TYPE" = "response" ]; then
    echo "Starting response worker..."
    exec celery -A celery_app worker \
      -Q scrape_response_listing \
      -n response@%h \
      --loglevel=info --concurrency=2

else
    # Default: run both (original behaviour)
    Xvfb :99 -screen 0 1920x1080x24 -ac +extension GLX +render -noreset &
    export DISPLAY=:99
    sleep 1
    echo "✓ Xvfb started (DISPLAY=$DISPLAY)"

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
fi
