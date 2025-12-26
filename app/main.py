
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .routes import router
from .auth import router as auth_router
from .database import engine, Base

# Создаем таблицы
Base.metadata.create_all(bind=engine)

# Создаем папку для загрузок
os.makedirs("uploads", exist_ok=True)

# Создаем приложение FastAPI
app = FastAPI(
    title="DrGreen AI API",
    description="API для диагностики болезней растений с использованием PyTorch",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Настройка CORS для frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Подключаем статические файлы для загруженных изображений
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Подключаем роуты
app.include_router(router, prefix="/api", tags=["API"])
app.include_router(auth_router, tags=["Authentication"])

@app.get("/")
async def root():
    """
    Главная страница API
    """
    return {
        "message": "🌱 DrGreen AI API",
        "description": "API для диагностики болезней растений с системой аутентификации",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
        "auth": {
            "register": "/auth/register",
            "login": "/auth/login"
        }
    }

@app.on_event("startup")
async def startup_event():
    """
    Инициализация при запуске приложения
    """
    print("=" * 50)
    print("Starting DrGreen AI API...")
    print("Initializing database...")
    print("Loading ML model...")
    print("Application ready!")
    print("=" * 50)

@app.on_event("shutdown")
async def shutdown_event():
    """
    Очистка при завершении работы приложения
    """
    print("Shutting down DrGreen AI API...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
