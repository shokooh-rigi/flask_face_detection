from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserLoginRequest(BaseModel):
    username: str
    password: str


class UserCreateRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None


class UserResponse(BaseModel):
    id: int
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    portrait_path: Optional[str] = None
    is_superuser: bool
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True


class RecognitionLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    timestamp: datetime
    snapshot_filename: Optional[str] = None

    class Config:
        orm_mode = True
