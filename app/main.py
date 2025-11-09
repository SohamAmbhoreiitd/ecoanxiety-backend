from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session

# Import local modules
from . import models, schemas, crud
from .core import get_chat_response
from .database import engine, get_db

# --- Database Table Creation ---
# This line tells SQLAlchemy to create all the tables defined in models.py
# if they don't already exist in the database.
models.Base.metadata.create_all(bind=engine)


# --- FastAPI Application Initialization ---
app = FastAPI(
    title="Eco-Anxiety AI Counselor",
    description="An API for the AI-powered eco-anxiety counseling chatbot.",
    version="1.0.0"
)


# --- CORS (Cross-Origin Resource Sharing) Middleware ---
# This allows our React frontend (running on localhost:3000)
# to make API requests to our backend (running on localhost:8000).
origins = [
    "http://localhost:3000",
    "https://*.streamlit.app",
    "https://*.railway.app", 
    "https://*.render.com",
    "*"  # Allow all origins for now - restrict in production
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Safety Layer Constants ---
EMERGENCY_KEYWORDS = [
    "suicide", "kill myself", "hopeless", "can't go on",
    "end my life", "self-harm", "panic attack", "i want to die"
]
EMERGENCY_RESPONSE = (
    "It sounds like you are going through a lot right now. "
    "It's important to talk to a person who can support you. "
    "Please reach out to a crisis hotline or mental health professional. "
    "You can connect with people who can support you by calling or texting 988 anytime in the US and Canada. In the UK, you can call 111."
)


# --- Pydantic Request Models ---
class ChatRequest(BaseModel):
    query: str
    chat_history: list = []


# --- API Endpoints ---

@app.get("/")
def read_root():
    """A simple endpoint to confirm the server is running."""
    return {"message": "Welcome to the Eco-Anxiety AI Counselor API"}


@app.post("/register", response_model=schemas.User)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """
    Endpoint to register a new user.
    Checks if the user already exists and returns an error if so.
    """
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.post("/chat")
def chat_endpoint(request: ChatRequest, db: Session = Depends(get_db)):
    """
    The main chat endpoint. It performs a safety check, gets a memory-aware
    AI response, and logs the interaction to the database.
    """
    user_query = request.query
    chat_history = request.chat_history
    user_query_lower = user_query.lower()

    # Step 1: Safety Check
    if any(keyword in user_query_lower for keyword in EMERGENCY_KEYWORDS):
        return {"response": EMERGENCY_RESPONSE}

    # Step 2: Get AI response (now with memory)
    ai_response = get_chat_response(user_query, chat_history)

    # Step 3: Save the interaction to the database
    db_conversation = models.Conversation(
        user_query=user_query,
        ai_response=ai_response
        # Note: owner_id is not yet linked. We will do this after implementing login.
    )
    db.add(db_conversation)
    db.commit()
    db.refresh(db_conversation)

    return {"response": ai_response}