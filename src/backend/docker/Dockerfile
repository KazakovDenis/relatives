FROM python:3.9-slim as base

ENV PYTHONDONTWRITEBYTECODE 1 \
    PYTHONUNBUFFERED 1

WORKDIR /app
COPY pyproject.toml .

RUN apt update -y && \
    apt upgrade -y && \
    pip install -U pip && \
    pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --only main

RUN pip uninstall -y poetry && \
    rm poetry.lock && \
    rm pyproject.toml && \
    apt autoclean -y && \
    apt autoremove -y

FROM base as backend

COPY src/backend .
COPY src/backend/docker/entrypoint.sh .
CMD ["./entrypoint.sh"]
