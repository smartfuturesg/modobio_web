FROM python:3.10
ARG API_VERSION

RUN mkdir /usr/src/app
WORKDIR /usr/src/app

ENV API_VERSION=$API_VERSION
RUN apt update
RUN apt install -y libpq-dev python3-dev build-essential libpango-1.0-0 libpangocairo-1.0-0

COPY ./ /usr/src/app
RUN pip install -U pip wheel
RUN pip install -r requirements/production.txt -r requirements/testing.txt
