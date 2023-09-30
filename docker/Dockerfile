FROM python:3.11-alpine

LABEL org.opencontainers.image.source="https://github.com/RomanMazyrin/django_playground"

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PROMETHEUS_MULTIPROC_DIR /app/src/prometheus_metrics

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers
RUN apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip

COPY requirements.txt /app
RUN pip install -r requirements.txt

COPY ./docker/entrypoint.sh /app/entrypoint.sh
RUN chmod 777 /app/entrypoint.sh

COPY . /app

WORKDIR /app/src

RUN python manage.py collectstatic --no-input

ENTRYPOINT [ "/app/entrypoint.sh" ]