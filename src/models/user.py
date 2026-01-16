"""
User Model

Defines the User entity for authentication and authorization.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user model with common fields."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Model for user registration."""
    password: str = Field(..., min_length=8)


class UserLogin(BaseModel):
    """Model for user login."""
    email: EmailStr
    password: str


class User(UserBase):
    """Complete user model."""
    id: int
    is_active: bool = True
    is_admin: bool = False
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserInDB(User):
    """User model with hashed password for database storage."""
    hashed_password: str


class Token(BaseModel):
    """JWT token response model."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    """JWT token payload."""
    sub: int  # user_id
    exp: datetime
    iat: datetime
