ARG PYTHON_VERSION=3.12.6

FROM python:$PYTHON_VERSION-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python -

# Добавляем Poetry в PATH
ENV PATH="/root/.local/bin:$PATH"

# install dependencies
COPY ./app/pyproject.toml .

RUN poetry config virtualenvs.create false && \
    poetry install --only main --no-interaction --no-ansi --no-cache;

# Финальный этап для Python, без Poetry.
FROM python:$PYTHON_VERSION-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

# Копируем зависимости из builder-этапа
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

COPY ./app .

EXPOSE 8000

RUN alembic revision --autogenerate && alembic upgrade head
