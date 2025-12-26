
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt

from .database import get_db
from .models import User
from .config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

# Создаем роутер для аутентификации
router = APIRouter(prefix="/auth", tags=["Authentication"])

# Настройка хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Настройка безопасности для JWT
security = HTTPBearer()

# Pydantic схемы для валидации данных
class UserCreate(BaseModel):
    """Схема для создания пользователя - принимает только email и password"""
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    """Схема для входа пользователя"""
    email: EmailStr
    password: str

class Token(BaseModel):
    """Схема JWT токена"""
    access_token: str
    token_type: str

class RegisterResponse(BaseModel):
    """Схема ответа при регистрации"""
    message: str
    access_token: str
    token_type: str
    user: dict

class LoginResponse(BaseModel):
    """Схема ответа при успешном входе"""
    message: str
    access_token: str
    token_type: str
    user: dict

class UserResponse(BaseModel):
    """Схема пользователя для ответа"""
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Проверка пароля пользователя
    
    Args:
        plain_password: Введенный пароль
        hashed_password: Хешированный пароль из БД
        
    Returns:
        bool: True если пароль верный
    """
    # Ограничиваем длину пароля для bcrypt (максимум 72 байта)
    if len(plain_password) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Хеширование пароля
    
    Args:
        password: Пароль в открытом виде
        
    Returns:
        str: Хешированный пароль
    """
    # Ограничиваем длину пароля для bcrypt (максимум 72 байта)
    if len(password) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Создание JWT токена
    
    Args:
        data: Данные для кодирования в токен
        expires_delta: Время жизни токена
        
    Returns:
        str: JWT токен
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего пользователя из JWT токена
    
    Args:
        credentials: HTTP авторизационные данные с токеном
        db: Сессия базы данных
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя с выдачей JWT токена
    
    Args:
        user_data: Данные пользователя (email, password)
        db: Сессия базы данных
        
    Returns:
        RegisterResponse: Результат регистрации с JWT токеном
        
    Raises:
        HTTPException: Если пользователь с таким email уже существует
    """
    print(f"[REGISTER] User data received: {user_data}")
    print(f"[REGISTER] Email: {user_data.email}")
    print(f"[REGISTER] Password: {'*' * len(user_data.password)}")
    
    # Проверяем, существует ли пользователь с таким email
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        print(f"[ERROR] User with email {user_data.email} already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Хешируем пароль
    hashed_password = get_password_hash(user_data.password)
    print(f"[REGISTER] Password hashed")
    
    # Создаем нового пользователя
    new_user = User(
        email=user_data.email,
        password=hashed_password
    )
    
    # Сохраняем в базу данных
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    print(f"[SUCCESS] User {new_user.email} registered with ID {new_user.id}")
    
    # Создаем JWT токен
    access_token = create_access_token(data={"sub": new_user.email})
    
    return RegisterResponse(
        message="User registered successfully",
        access_token=access_token,
        token_type="bearer",
        user={
            "id": new_user.id,
            "email": new_user.email,
            "created_at": new_user.created_at.isoformat()
        }
    )

@router.post("/login", response_model=LoginResponse)
async def login_user(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Вход пользователя в систему с выдачей JWT токена
    
    Args:
        login_data: Данные для входа (email, password)
        db: Сессия базы данных
        
    Returns:
        LoginResponse: Результат входа с JWT токеном
        
    Raises:
        HTTPException: Если email или пароль неверные
    """
    # Ищем пользователя по email
    user = db.query(User).filter(User.email == login_data.email).first()
    
    # Проверяем, существует ли пользователь и верный ли пароль
    if not user or not verify_password(login_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный email или пароль"
        )
    
    # Создаем JWT токен
    access_token = create_access_token(data={"sub": user.email})
    
    return LoginResponse(
        message="Login successful",
        access_token=access_token,
        token_type="bearer",
        user={
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at.isoformat()
        }
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущем пользователе
    
    Args:
        current_user: Текущий пользователь из JWT токена
        
    Returns:
        UserResponse: Информация о пользователе
    """
    return current_user

