#!/usr/bin/env bash
set -e

# Initialize Chroma vector DB on first run if not present
if [ ! -d "/app/chroma_db" ]; then
  echo "Initializing Chroma DB from knowledge_base..."
  python /app/scripts/rebuild_chroma.py
fi

# Start the server using Render's PORT
echo "Starting Uvicorn on port ${PORT}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT}"

