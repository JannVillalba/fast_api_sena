from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserPreferences(BaseModel):
    theme: str
    language: str
    timezone: str

class User(BaseModel):
    id: int
    username: str
    email: EmailStr
    full_name: str
    created_at: datetime
    preferences: UserPreferences

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    preferences: UserPreferences
