#!/bin/sh

pipenv run python3 manage.py collectstatic --no-input
pipenv run python3 manage.py migrate --no-input

pipenv run gunicorn -w=$NUM_OF_WORKERS playground.wsgi --bind 0.0.0.0:$PORT