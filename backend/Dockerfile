ARG PYTHON_VERSION=3.12.6

# build-stage
FROM python:$PYTHON_VERSION-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists

# DL4006 Set the SHELL option -o pipefail before RUN with a pipe in
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# install Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# add Poetry to PATH
ENV PATH="/root/.local/bin:$PATH"

# install dependencies
COPY ./app/pyproject.toml .

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-cache;

# get smaller images
FROM python:$PYTHON_VERSION-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# NOTE: UIDs below 10,000 are a security risk, as a container breakout could
# result in the container being # ran as a more privilged user on the host
# kernel with th same UID.
# Add user 10001 with group 10001
RUN addgroup --gid 10001 nonroot \
    && adduser --disabled-password --home /app --uid 10001 --gid 10001 nonroot \
    && chown -R nonroot:nonroot /app

# copy dependencies from build-stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY --chown=nonroot:nonroot ./app .

USER nonroot

EXPOSE 8000

RUN alembic revision --autogenerate && alembic upgrade head
