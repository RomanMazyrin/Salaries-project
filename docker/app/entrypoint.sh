#!/bin/sh

TARGET_PORT=${PORT:-8000}
TARGET_NUM_OF_WORKERS=${NUM_OF_WORKERS:-2}

pipenv run python3 manage.py collectstatic --no-input
pipenv run python3 manage.py migrate --no-input

pipenv run gunicorn -w=$TARGET_NUM_OF_WORKERS playground.wsgi --bind 0.0.0.0:$TARGET_PORT