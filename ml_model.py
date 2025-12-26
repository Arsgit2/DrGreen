"""
Machine Learning model for plant disease detection using PyTorch
Использует обученную ResNet18 модель
"""
import torch
import torch.nn as nn
import torchvision.transforms as transforms
from torchvision import models
from PIL import Image
import io
import numpy as np
from typing import Dict, List, Optional
from pathlib import Path
import json
import re

# Глобальная переменная для модели
_model = None
_class_names = None
_device = None

def normalize_class_name(name):
    """Нормализация имени класса (как в train_model.py)"""
    text = re.sub(r'[^a-z0-9]+', ' ', name.lower())
    words = text.split()
    stop_words = {'leaf', 'leaves', 'plant', 'feature', 'folder'}
    filtered_words = [w for w in words if w not in stop_words]
    filtered_words.sort()
    return " ".join(filtered_words)

def get_class_names_from_datasets() -> List[str]:
    """Получить список классов из датасетов (как в train_model.py)"""
    from train_model import UnifiedDataset
    
    roots = [
        Path("data/plantvillage/PlantVillage"),
        Path("data/plantdoc/train")
    ]
    
    dataset = UnifiedDataset(roots, transform=None)
    return dataset.classes

def load_class_names() -> List[str]:
    """Загрузить список классов из файла или датасета"""
    global _class_names
    
    if _class_names is not None:
        return _class_names
    
    # Пытаемся загрузить из файла
    class_file = Path("model/class_names.json")
    if class_file.exists():
        try:
            with open(class_file, 'r', encoding='utf-8') as f:
                _class_names = json.load(f)
                print(f"[OK] Загружено {len(_class_names)} классов из {class_file}")
                return _class_names
        except Exception as e:
            print(f"[WARNING] Ошибка загрузки классов из файла: {e}")
    
    # Если файла нет, получаем из датасета
    try:
        _class_names = get_class_names_from_datasets()
        print(f"[OK] Загружено {len(_class_names)} классов из датасета")
        
        # Сохраняем для будущего использования
        class_file.parent.mkdir(parents=True, exist_ok=True)
        with open(class_file, 'w', encoding='utf-8') as f:
            json.dump(_class_names, f, indent=2, ensure_ascii=False)
        print(f"[OK] Список классов сохранен в {class_file}")
        
        return _class_names
    except Exception as e:
        print(f"[ERROR] Не удалось загрузить классы: {e}")
        # Возвращаем базовый список для совместимости
        return [
            "Здоровое растение",
            "Фитофтороз",
            "Мучнистая роса",
            "Черная пятнистость",
            "Антракноз"
        ]

def get_model():
    """Получение обученной ResNet18 модели (ленивая загрузка)"""
    global _model, _device
    
    if _model is not None:
        return _model
    
    _device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[INFO] Используется устройство: {_device}")
    
    # Загружаем классы
    class_names = load_class_names()
    num_classes = len(class_names)
    
    # Создаем модель ResNet18
    print(f"[INFO] Создание ResNet18 модели для {num_classes} классов...")
    model = models.resnet18(weights=None)  # Не используем pretrained, т.к. модель уже обучена
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    # Загружаем веса обученной модели
    model_paths = [
        "model/plant_disease_resnet18_ft.pth",  # Самая последняя модель
        "model/plant_disease_resnet18.pth",
        "model/plant_disease_model_best.pth",
        "model/plant_disease_model_final.pth"
    ]
    
    model_loaded = False
    for model_path in model_paths:
        path = Path(model_path)
        if path.exists():
            try:
                print(f"[INFO] Загрузка модели из {model_path}...")
                state_dict = torch.load(model_path, map_location=_device)
                
                # Пытаемся загрузить строго
                try:
                    model.load_state_dict(state_dict, strict=True)
                    print(f"[OK] Модель успешно загружена из {model_path}")
                    model_loaded = True
                    break
                except Exception as e:
                    print(f"[WARNING] Строгая загрузка не удалась: {e}")
                    # Пытаемся нестрого
                    try:
                        model.load_state_dict(state_dict, strict=False)
                        print(f"[OK] Модель загружена (нестрого) из {model_path}")
                        model_loaded = True
                        break
                    except Exception as e2:
                        print(f"[WARNING] Нестрогая загрузка тоже не удалась: {e2}")
                        continue
            except Exception as e:
                print(f"[WARNING] Ошибка при загрузке {model_path}: {e}")
                continue
    
    if not model_loaded:
        print("[WARNING] Не удалось загрузить обученную модель. Используется ненастроенная модель.")
        print("[WARNING] Предсказания будут неточными!")
    
    model.to(_device)
    model.eval()
    _model = model
    
    return _model

def preprocess_image(image_bytes: bytes) -> torch.Tensor:
    """
    Предобработка изображения для модели (как в обучении)
    
    Args:
        image_bytes: Байты изображения
        
    Returns:
        torch.Tensor: Предобработанный тензор
    """
    try:
        # Открываем изображение из байтов
        image = Image.open(io.BytesIO(image_bytes))
        
        # Конвертируем в RGB если нужно
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Трансформации для предобработки (как в обучении)
        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Применяем трансформации
        image_tensor = transform(image)
        
        # Добавляем batch dimension
        image_tensor = image_tensor.unsqueeze(0)
        
        return image_tensor
        
    except Exception as e:
        print(f"Ошибка предобработки изображения: {e}")
        # Возвращаем пустой тензор
        return torch.zeros(1, 3, 224, 224)

def predict_disease(image_bytes: bytes) -> Dict[str, any]:
    """
    Предсказание болезни растения с использованием обученной модели
    
    Args:
        image_bytes: Байты изображения
        
    Returns:
        Dict: Результат предсказания с полями 'disease' и 'confidence'
    """
    try:
        # Получаем модель
        model = get_model()
        class_names = load_class_names()
        
        # Предобрабатываем изображение
        image_tensor = preprocess_image(image_bytes)
        image_tensor = image_tensor.to(_device)
        
        # Получаем предсказание
        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = torch.softmax(outputs, dim=1)
            confidence, predicted_class = torch.max(probabilities, 1)
        
        # Получаем название болезни
        predicted_idx = predicted_class.item()
        if predicted_idx < len(class_names):
            predicted_disease = class_names[predicted_idx]
        else:
            predicted_disease = "Неизвестная болезнь"
        
        confidence_score = confidence.item()
        
        # Если уверенность очень низкая, добавляем предупреждение
        if confidence_score < 0.1:
            print(f"[WARNING] Низкая уверенность предсказания: {confidence_score:.2f}")
        
        return {
            "disease": predicted_disease,
            "confidence": confidence_score
        }
        
    except Exception as e:
        print(f"Ошибка предсказания: {e}")
        import traceback
        traceback.print_exc()
        # Возвращаем базовый результат
        return {
            "disease": "Ошибка предсказания",
            "confidence": 0.0
        }
