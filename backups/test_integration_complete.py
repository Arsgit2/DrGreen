#!/usr/bin/env python3
"""Полная проверка интеграции обученной модели"""
import sys
from pathlib import Path

print("=" * 80)
print("🔍 ПОЛНАЯ ПРОВЕРКА ИНТЕГРАЦИИ")
print("=" * 80)

# 1. Проверка файлов модели
print("\n1️⃣ Проверка файлов модели...")
model_files = [
    "model/plant_disease_resnet18_improved.pth",
    "model/training_info_improved.json",
    "model/class_names.json"
]

for file_path in model_files:
    path = Path(file_path)
    if path.exists():
        size = path.stat().st_size
        if path.suffix == '.pth':
            print(f"   ✅ {file_path} ({size / 1024 / 1024:.2f} MB)")
        else:
            print(f"   ✅ {file_path} ({size / 1024:.2f} KB)")
    else:
        print(f"   ❌ {file_path} - НЕ НАЙДЕН")

# 2. Проверка информации об обучении
print("\n2️⃣ Проверка информации об обучении...")
try:
    import json
    with open("model/training_info_improved.json", 'r', encoding='utf-8') as f:
        info = json.load(f)
    
    print(f"   ✅ Архитектура: {info.get('arch', 'N/A')}")
    print(f"   ✅ Количество классов: {info.get('num_classes', 'N/A')}")
    print(f"   ✅ Pretrained: {info.get('pretrained', 'N/A')}")
    print(f"   ✅ Fine-tune: {info.get('fine_tune', 'N/A')}")
    print(f"   ✅ Эпох обучено: {info.get('epochs_trained', 'N/A')}")
    
    if 'best_val_acc' in info:
        print(f"   ✅ Лучшая точность валидации: {info['best_val_acc']:.2f}%")
    if 'val_accs' in info and info['val_accs']:
        final_acc = info['val_accs'][-1]
        print(f"   ✅ Финальная точность валидации: {final_acc:.2f}%")
except Exception as e:
    print(f"   ❌ Ошибка чтения training_info: {e}")

# 3. Проверка классов
print("\n3️⃣ Проверка списка классов...")
try:
    with open("model/class_names.json", 'r', encoding='utf-8') as f:
        classes = json.load(f)
    print(f"   ✅ Загружено классов: {len(classes)}")
    print(f"   ✅ Первые 5 классов: {', '.join(classes[:5])}")
except Exception as e:
    print(f"   ❌ Ошибка чтения классов: {e}")

# 4. Проверка загрузки модели в приложении
print("\n4️⃣ Проверка загрузки модели в приложении...")
try:
    sys.path.insert(0, str(Path(__file__).parent))
    from app.ml import PlantDiseasePredictor
    
    print("   Загрузка предсказателя...")
    predictor = PlantDiseasePredictor()
    
    if predictor.model is not None:
        print(f"   ✅ Модель загружена: {type(predictor.model)}")
        print(f"   ✅ Устройство: {predictor.device}")
        print(f"   ✅ Количество классов: {len(predictor.class_names)}")
    else:
        print("   ❌ Модель не загружена!")
except Exception as e:
    print(f"   ❌ Ошибка загрузки модели: {e}")
    import traceback
    traceback.print_exc()

# 5. Проверка структуры скрипта обучения
print("\n5️⃣ Проверка скрипта обучения...")
try:
    from train_improved import (
        UnifiedDataset, TransformDataset, 
        build_model, load_datasets, train_model
    )
    print("   ✅ Все компоненты скрипта обучения импортируются")
except Exception as e:
    print(f"   ❌ Ошибка импорта: {e}")

print("\n" + "=" * 80)
print("✅ ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 80)
