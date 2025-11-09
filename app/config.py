import os
from dotenv import load_dotenv

load_dotenv()

# Load the Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
# Default to a local SQLite database if no DATABASE_URL is provided
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data.db")
