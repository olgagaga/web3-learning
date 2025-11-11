from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    name: str


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: int
    is_active: bool
    current_streak: int
    reading_items_completed: int
    essays_written: int
    badges_earned: int
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: Optional[str] = None


class LoginResponse(BaseModel):
    user: UserResponse
    token: str


class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


class UserPreferences(BaseModel):
    daily_reading_goal: Optional[int] = 5
    daily_writing_goal: Optional[int] = 1
    email_notifications: Optional[bool] = True
    push_notifications: Optional[bool] = True
    difficulty_preference: Optional[str] = "medium"  # easy, medium, hard


class UserPreferencesResponse(UserPreferences):
    class Config:
        from_attributes = True
