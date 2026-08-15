FROM python:3.13-slim

# запрещает создавать файлы кеш (pyc)
ENV PYTHONDONTWRITEBYTECODE 1
# запрещает буфферизировать сообщения
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=1

# RUN apk update && apk upgrade && apk add bash
# RUN apt-get add --no-cache bash netcat-openbsd
RUN apt-get update \
    && apt-get install -y --no-install-recommends netcat-openbsd \
    && rm -rf /var/lib/apt/lists/*

RUN python -m pip install --upgrade pip
RUN pip install --no-cache-dir poetry==2.3.2

RUN mkdir /backend
RUN mkdir /backend/src

COPY pyproject.toml /backend
COPY poetry.lock /backend
COPY alembic.ini /backend

WORKDIR /backend
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY ./bin /backend/bin
COPY ./src /backend/src

RUN chmod +x /backend/bin/start_project.sh

# ENTRYPOINT ["/bin/sh", "-c" , "./bin/start_project.sh"]
ENTRYPOINT ["/backend/bin/start_project.sh"]
