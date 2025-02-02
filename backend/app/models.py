from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    created_at: datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class SearchResult(BaseModel):
    query: str
    results: str
    model_used: str
    created_at: datetime
    user_id: str

class DocumentAnalysis(BaseModel):
    filename: str
    analysis: str
    model_used: str
    created_at: datetime
    user_id: str
