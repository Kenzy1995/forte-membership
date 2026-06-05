FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY server-api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY server-api/app ./app
COPY web ./web

ENV PORT=8080
ENV PYTHONUNBUFFERED=1

# Phase 1: single worker for in-process redemption locks
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 120 \
    --worker-class uvicorn.workers.UvicornWorker app.main:app
