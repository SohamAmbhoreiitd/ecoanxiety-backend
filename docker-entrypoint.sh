#!/usr/bin/env bash
set -e

# Initialize Chroma vector DB on first run if not present
if [ ! -d "chroma_db" ]; then
  echo "Initializing Chroma DB from knowledge_base..."
  python - <<'PY'
from app.core import create_vector_db
create_vector_db()
PY
fi

exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
