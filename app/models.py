"""
SQLAlchemy models for DrGreen AI database
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base
from datetime import datetime

class User(Base):
    """Модель пользователя в базе данных"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Plant(Base):
    """Модель растения в базе данных"""
    __tablename__ = "plants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    scientific_name = Column(String(150))
    description = Column(Text)
    care_instructions = Column(Text)
    common_diseases = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Disease(Base):
    """Модель болезни растения"""
    __tablename__ = "diseases"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    treatment = Column(Text, nullable=False)
    symptoms = Column(Text)
    prevention = Column(Text)
    image_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

class Scan(Base):
    """Модель сканирования растения"""
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Связь с пользователем
    image_path = Column(String(255), nullable=False)
    disease_id = Column(Integer, ForeignKey("diseases.id"), nullable=True)  # Может быть null для здоровых растений
    disease_name = Column(String(100), nullable=True)  # Название болезни
    confidence = Column(Float, nullable=False)
    is_healthy = Column(String(10), nullable=False)  # 'healthy' или 'disease'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Связи
    user = relationship("User", foreign_keys=[user_id], backref="scans")
    disease = relationship("Disease", foreign_keys=[disease_id])
