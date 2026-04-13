#!/bin/bash
set -e

echo "Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
export DISPLAY=:99

echo "Starting scraper worker..."

# Start both Celery workers in the background
echo "Starting request worker..."
celery -A celery_app worker -Q scrape_request_listing -n request@%h --loglevel=info --concurrency=1 &

echo "Starting response worker..."
celery -A celery_app worker -Q scrape_response_listing -n response@%h --loglevel=info --concurrency=2 &

# Wait for all background processes
wait