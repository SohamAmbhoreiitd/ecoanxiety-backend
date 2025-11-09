# syntax=docker/dockerfile:1
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# System deps (optional; keep slim). psycopg2-binary removes need for libpq-dev.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

# Ensure entrypoint has execute permission
RUN chmod +x docker-entrypoint.sh || true

ENV PORT=8000
EXPOSE 8000

ENTRYPOINT ["/bin/bash", "-lc"]
CMD ["./docker-entrypoint.sh"]
