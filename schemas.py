"""
Pydantic schemas for DrGreen AI
"""
from pydantic import BaseModel, EmailStr
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for user creation"""
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    """Schema for user response"""
    id: int
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class RegisterResponse(BaseModel):
    """Schema for registration response"""
    message: str
    user: UserResponse

class LoginResponse(BaseModel):
    """Schema for login response"""
    message: str
    user: UserResponse