#!/usr/bin/env python3
"""Скрипт для сохранения списка классов из датасета"""
from pathlib import Path
import json
import sys
sys.path.insert(0, str(Path(__file__).parent))

from train_model import UnifiedDataset

def main():
    roots = [
        Path("data/plantvillage/PlantVillage"),
        Path("data/plantdoc/train")
    ]
    
    print("Загрузка датасета для получения списка классов...")
    dataset = UnifiedDataset(roots, transform=None)
    
    print(f"Найдено классов: {len(dataset.classes)}")
    
    # Сохраняем классы
    output_path = Path("model/class_names.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset.classes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Список классов сохранен в {output_path}")
    print(f"\nПервые 10 классов:")
    for i, cls in enumerate(dataset.classes[:10]):
        print(f"  {i}: {cls}")

if __name__ == '__main__':
    main()
