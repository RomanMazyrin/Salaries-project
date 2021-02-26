FROM python:3.7-alpine

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk add --no-cache jpeg-dev zlib-dev
RUN apk add --no-cache --virtual .build-deps build-base linux-headers
RUN apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
RUN pip install pipenv

COPY Pipfile .
COPY Pipfile.lock .

RUN pipenv install

# copy project
COPY . .

COPY ./docker/app/entrypoint.sh /usr/src/entrypoint.sh

RUN chmod 777 /usr/src/entrypoint.sh

WORKDIR /usr/src/app/playground

ENTRYPOINT [ "/usr/src/entrypoint.sh" ]