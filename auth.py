"""
Authentication routes for DrGreen AI
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from typing import Optional

from .database import get_db
from .models import User
from .schemas import UserCreate, UserLogin, RegisterResponse, LoginResponse, UserResponse

# Create router
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    """
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    hashed_password = get_password_hash(user_data.password)
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password
    )
    
    # Save to database
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return RegisterResponse(
        message="User registered successfully",
        user=UserResponse(
            id=new_user.id,
            email=new_user.email,
            created_at=new_user.created_at
        )
    )

@router.post("/login", response_model=LoginResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login user
    """
    # Find user by email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Check if user exists and password is correct
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
    
    return LoginResponse(
        message="Login successful",
        user=UserResponse(
            id=user.id,
            email=user.email,
            created_at=user.created_at
        )
    )