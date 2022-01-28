FROM python:3.7-alpine

LABEL org.opencontainers.image.source="https://github.com/RomanMazyrin/django_playground"

RUN mkdir /app
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers
RUN apk add postgresql-dev gcc python3-dev musl-dev

RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile /app
COPY Pipfile.lock /app

RUN pipenv sync --system

COPY ./docker/entrypoint.sh /app/entrypoint.sh
RUN chmod 777 /app/entrypoint.sh

RUN mkdir /app/src
COPY src /app/src

WORKDIR /app/src

RUN python3 manage.py collectstatic --no-input

ENTRYPOINT [ "/app/entrypoint.sh" ]