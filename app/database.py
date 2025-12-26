"""
Database configuration and session management for DrGreen AI
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Создаем папку для базы данных
os.makedirs("data", exist_ok=True)

# URL базы данных SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/agroscan.db"

# Создаем движок
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

# Создаем фабрику сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Базовый класс для моделей
Base = declarative_base()

# Функция для получения сессии базы данных
def get_db():
    """Dependency для получения сессии базы данных"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаем таблицы при импорте
Base.metadata.create_all(bind=engine)

