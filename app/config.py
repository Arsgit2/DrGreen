
import os
from datetime import timedelta

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database Configuration
DATABASE_URL = "sqlite:///./data/agroscan.db"

# CORS Configuration
ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # React dev server
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
]

# Security Configuration
PASSWORD_MIN_LENGTH = 6
BCRYPT_ROUNDS = 12

# API Configuration
API_V1_PREFIX = "/api"
AUTH_PREFIX = "/auth"

# File Upload Configuration
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/webp"]

# ML Model Configuration
MODEL_PATH = "model/plant_disease_model.pth"
IMAGE_SIZE = (224, 224)
CONFIDENCE_THRESHOLD = 0.5

