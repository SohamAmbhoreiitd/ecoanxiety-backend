#!/usr/bin/env python3
from app.core import create_vector_db

if __name__ == "__main__":
    create_vector_db()
    print("Chroma DB rebuilt from knowledge_base/")
