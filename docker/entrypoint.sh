#!/bin/sh

TARGET_PORT=${PORT:-8000}
TARGET_NUM_OF_WORKERS=${NUM_OF_WORKERS:-2}
WORKER_TIMEOUT=${WORKER_TIMEOUT:-60}

gunicorn -w=$TARGET_NUM_OF_WORKERS -t=$WORKER_TIMEOUT app.wsgi --bind 0.0.0.0:$TARGET_PORT --reload