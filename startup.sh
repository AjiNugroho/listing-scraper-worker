#!/bin/bash
set -e

WORKDIR="/home/sebas/Workdir/FAIR/ScraperWorker/listing-scraper-worker"
VENV="$WORKDIR/.venv/bin"

cd "$WORKDIR"

echo "Starting request worker..."
"$VENV/celery" -A celery_app worker \
  -Q scrape_request_listing \
  -n request@%h \
  --loglevel=info --concurrency=1 &

echo "Starting response worker..."
"$VENV/celery" -A celery_app worker \
  -Q scrape_response_listing \
  -n response@%h \
  --loglevel=info --concurrency=2 &

wait
