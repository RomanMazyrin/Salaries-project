#!/bin/sh

if [ $RUN_MIGRATIONS ]
then
    poetry run python manage.py migrate --no-input
fi

if [ $CREATE_SUPERUSER ]
then
    poetry run python manage.py createsuperuser --no-input
fi

poetry run gunicorn -w=$G_NUM_OF_WORKERS --worker-class=gevent --worker-connections=$G_WORKER_CONNECTIONS -t=$G_WORKER_TIMEOUT --bind 0.0.0.0:$G_PORT --reload salaries.wsgi