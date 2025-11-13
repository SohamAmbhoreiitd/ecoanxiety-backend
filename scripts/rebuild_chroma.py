import sys, os
sys.path.append("/app")

from app.core import create_vector_db

if __name__ == "__main__":
    create_vector_db()
