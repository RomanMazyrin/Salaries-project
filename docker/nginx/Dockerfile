FROM python:3.7-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

# copy project
COPY . .

RUN pipenv run python3 playground/manage.py collectstatic --no-input


FROM nginx:latest

RUN mkdir /app
WORKDIR /app

RUN rm /etc/nginx/conf.d/default.conf
RUN rm -rf *

COPY ./docker/nginx/default.conf /etc/nginx/conf.d/default.conf

COPY --from=builder /usr/src/app/playground/static /app/static

ENTRYPOINT [ "nginx", "-g", "daemon off;" ]