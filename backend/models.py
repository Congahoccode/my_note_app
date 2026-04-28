from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class NoteBase(BaseModel):
    title: str
    content: str
    tags: Optional[List[str]] = []


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    pass


class NoteResponse(NoteBase):
    id: str
    created_at: datetime
    updated_at: datetime


class LoginRequest(BaseModel):
    email: str
    password: str
