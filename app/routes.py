
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
from datetime import datetime

from .database import get_db
from .models import Plant, Disease, Scan, User
from .ml import predictor
from .auth import get_current_user
from .llm import generate_disease_info


# Создаем роутер
router = APIRouter()

# Создаем папку для загрузок
os.makedirs("uploads", exist_ok=True)

@router.get("/health")
async def health_check():
    """
    Проверка состояния сервиса
    """
    return {
        "status": "healthy",
        "message": "DrGreen AI service is running",
        "timestamp": datetime.utcnow().isoformat(),
        "model_loaded": predictor.model is not None
    }

@router.post("/predict")
async def predict_disease(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Диагностика болезни растения по изображению (требуется авторизация)
    
    Args:
        file: Изображение растения
        current_user: Текущий авторизованный пользователь
        db: Сессия базы данных
        
    Returns:
        Dict: Результат диагностики
    """
    try:
        # Проверяем тип файла
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Файл должен быть изображением")
        
        # Сохраняем файл
        file_extension = file.filename.split(".")[-1] if "." in file.filename else "jpg"
        filename = f"{uuid.uuid4()}.{file_extension}"
        file_path = f"uploads/{filename}"
        
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Получаем предсказание от ML модели
        prediction = predictor.predict(file_path)
        
        # Получаем дополнительную информацию о болезни (локальный fallback)
        disease_info = predictor.get_disease_info(prediction["disease"])

        # Попытка получить расширенную текстовую информацию от LLM (Groq)
        try:
            llm_info = generate_disease_info(prediction["disease"])
            if isinstance(llm_info, dict) and llm_info is not None:
                # Обновляем только текстовые поля, если LLM вернул значения
                for key in ("description", "symptoms", "treatment"):
                    if llm_info.get(key):
                        disease_info[key] = llm_info[key]
        except Exception:
            # В случае любой ошибки LLM — используем локальные данные (fallback)
            pass
        
        # Сохраняем результат в базу данных с привязкой к пользователю
        scan = Scan(
            user_id=current_user.id,
            image_path=file_path,
            disease_id=None if prediction["is_healthy"] else 1,  # Упрощенная логика
            disease_name=prediction["disease"],
            confidence=prediction["confidence"],
            is_healthy="healthy" if prediction["is_healthy"] else "disease"
        )
        
        db.add(scan)
        db.commit()
        db.refresh(scan)
        
        return {
            "success": True,
            "scan_id": scan.id,
            "disease": prediction["disease"],
            "confidence": prediction["confidence"],
            "is_healthy": prediction["is_healthy"],
            "description": disease_info["description"],
            "treatment": disease_info["treatment"],
            "symptoms": disease_info["symptoms"],
            "all_probabilities": prediction["all_probabilities"],
            "image_path": file_path,
            "created_at": scan.created_at.isoformat()
        }
        
    except Exception as e:
        # Удаляем файл в случае ошибки
        if 'file_path' in locals() and os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=f"Ошибка при обработке изображения: {str(e)}")

@router.get("/plants")
async def get_plants(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Получение списка растений
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        db: Сессия базы данных
        
    Returns:
        List: Список растений
    """
    plants = db.query(Plant).offset(skip).limit(limit).all()
    return plants

@router.post("/plants")
async def create_plant(
    name: str = Form(...),
    scientific_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    care_instructions: Optional[str] = Form(None),
    common_diseases: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Создание нового растения
    
    Args:
        name: Название растения
        scientific_name: Научное название
        description: Описание
        care_instructions: Инструкции по уходу
        common_diseases: Частые болезни
        db: Сессия базы данных
        
    Returns:
        Plant: Созданное растение
    """
    # Проверяем, не существует ли уже растение с таким именем
    existing_plant = db.query(Plant).filter(Plant.name == name).first()
    if existing_plant:
        raise HTTPException(status_code=400, detail="Растение с таким названием уже существует")
    
    plant = Plant(
        name=name,
        scientific_name=scientific_name,
        description=description,
        care_instructions=care_instructions,
        common_diseases=common_diseases
    )
    
    db.add(plant)
    db.commit()
    db.refresh(plant)
    
    return plant

@router.get("/plants/{plant_id}")
async def get_plant(plant_id: int, db: Session = Depends(get_db)):
    """
    Получение растения по ID
    
    Args:
        plant_id: ID растения
        db: Сессия базы данных
        
    Returns:
        Plant: Растение
    """
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Растение не найдено")
    
    return plant

@router.put("/plants/{plant_id}")
async def update_plant(
    plant_id: int,
    name: Optional[str] = Form(None),
    scientific_name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    care_instructions: Optional[str] = Form(None),
    common_diseases: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Обновление растения
    
    Args:
        plant_id: ID растения
        name: Новое название
        scientific_name: Новое научное название
        description: Новое описание
        care_instructions: Новые инструкции по уходу
        common_diseases: Новые частые болезни
        db: Сессия базы данных
        
    Returns:
        Plant: Обновленное растение
    """
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Растение не найдено")
    
    # Обновляем только переданные поля
    if name is not None:
        plant.name = name
    if scientific_name is not None:
        plant.scientific_name = scientific_name
    if description is not None:
        plant.description = description
    if care_instructions is not None:
        plant.care_instructions = care_instructions
    if common_diseases is not None:
        plant.common_diseases = common_diseases
    
    plant.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(plant)
    
    return plant

@router.delete("/plants/{plant_id}")
async def delete_plant(plant_id: int, db: Session = Depends(get_db)):
    """
    Удаление растения
    
    Args:
        plant_id: ID растения
        db: Сессия базы данных
        
    Returns:
        Dict: Результат удаления
    """
    plant = db.query(Plant).filter(Plant.id == plant_id).first()
    if not plant:
        raise HTTPException(status_code=404, detail="Растение не найдено")
    
    db.delete(plant)
    db.commit()
    
    return {"message": "Растение успешно удалено", "plant_id": plant_id}

@router.get("/diseases")
async def get_diseases(db: Session = Depends(get_db)):
    """
    Получение списка болезней
    
    Args:
        db: Сессия базы данных
        
    Returns:
        List: Список болезней
    """
    diseases = db.query(Disease).all()
    return diseases

@router.get("/scans")
async def get_scans(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Получение истории сканирований текущего пользователя
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        current_user: Текущий авторизованный пользователь
        db: Сессия базы данных
        
    Returns:
        List: Список сканирований пользователя
    """
    scans = db.query(Scan).filter(
        Scan.user_id == current_user.id
    ).order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()
    
    # Форматируем ответ
    result = []
    for scan in scans:
        result.append({
            "id": scan.id,
            "disease_name": scan.disease_name,
            "confidence": scan.confidence,
            "is_healthy": scan.is_healthy,
            "image_path": scan.image_path,
            "created_at": scan.created_at.isoformat()
        })
    
    return result

