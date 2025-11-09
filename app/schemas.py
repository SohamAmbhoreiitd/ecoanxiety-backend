from pydantic import BaseModel

# Schema for receiving user creation data in a request body
class UserCreate(BaseModel):
    email: str
    password: str

# Schema for returning user data in a response (never includes the password)
class User(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True # Allows creating this Pydantic model from a database object