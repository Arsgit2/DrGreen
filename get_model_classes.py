#!/usr/bin/env python3
"""Получить список классов из датасетов для модели"""
from pathlib import Path
from torchvision import datasets
import json

def get_all_classes():
    """Получить все классы из датасетов"""
    all_classes = []
    
    # PlantVillage
    pv_path = Path('data/plantvillage')
    if pv_path.exists():
        pv_dataset = datasets.ImageFolder(str(pv_path))
        all_classes.extend(pv_dataset.classes)
        print(f"PlantVillage: {len(pv_dataset.classes)} classes")
    
    # PlantDoc
    pd_path = Path('data/plantdoc/train')
    if pd_path.exists():
        pd_dataset = datasets.ImageFolder(str(pd_path))
        all_classes.extend(pd_dataset.classes)
        print(f"PlantDoc: {len(pd_dataset.classes)} classes")
    
    # Удаляем дубликаты, сохраняя порядок
    seen = set()
    unique_classes = []
    for cls in all_classes:
        if cls not in seen:
            seen.add(cls)
            unique_classes.append(cls)
    
    return unique_classes

if __name__ == '__main__':
    classes = get_all_classes()
    print(f"\nВсего уникальных классов: {len(classes)}")
    
    # Сохраняем
    output_path = Path("model/class_names.json")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(classes, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Сохранено в {output_path}")
    print(f"\nПервые 10 классов:")
    for i, cls in enumerate(classes[:10]):
        print(f"  {i}: {cls}")



