FROM python:3.12.6-slim AS builder

# install dependencies system
ARG BUILD_DEPS="curl"
RUN apt-get update && apt-get install --no-install-recommends -y $BUILD_DEPS

RUN pip install --upgrade --no-cache-dir pip && \
	pip install --no-cache-dir poetry

# install dependencies
COPY ./app/pyproject.toml .

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes  && \
	pip install --no-cache-dir -r requirements.txt  --default-timeout=100 future

# copy project
COPY ./app .

RUN alembic revision --autogenerate && alembic upgrade head
