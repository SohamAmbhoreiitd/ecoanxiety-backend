#!/usr/bin/env bash
set -e

export PYTHONPATH="/app"

# Initialize Chroma vector DB on first run if not present
if [ ! -d "/app/chroma_db" ]; then
  echo "Initializing Chroma DB from knowledge_base..."
  python /app/scripts/rebuild_chroma.py
fi

echo "Starting Uvicorn on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}


