FROM python:3.7-alpine

ENV PYTHONUNBUFFERED 1

ENV DJANGO_DEVELOPMENT 1

RUN mkdir /code

WORKDIR /code

ADD reqs.txt /code/

RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install -r reqs.txt --no-cache-dir && \
 apk --purge del .build-deps

ADD . /code/
