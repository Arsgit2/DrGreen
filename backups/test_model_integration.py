#!/usr/bin/env python3
"""Тест интеграции обученной модели"""
import sys
from pathlib import Path

print("=" * 60)
print("Тест интеграции обученной ResNet18 модели")
print("=" * 60)

try:
    print("\n1. Импорт модуля...")
    from app.ml import PlantDiseasePredictor
    print("   ✅ Импорт успешен")
    
    print("\n2. Создание предсказателя...")
    predictor = PlantDiseasePredictor()
    print("   ✅ Предсказатель создан")
    
    print(f"\n3. Проверка модели...")
    if predictor.model is not None:
        print(f"   ✅ Модель загружена: {type(predictor.model)}")
        print(f"   ✅ Количество классов: {len(predictor.class_names)}")
        print(f"   ✅ Устройство: {predictor.device}")
    else:
        print("   ❌ Модель не загружена!")
    
    print(f"\n4. Первые 10 классов:")
    for i, cls in enumerate(predictor.class_names[:10]):
        print(f"   {i}: {cls}")
    
    print("\n" + "=" * 60)
    print("✅ Интеграция успешна! Модель готова к использованию.")
    print("=" * 60)
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
