#!/usr/bin/env python3
"""Проверка проблемы с предсказаниями - почему модель путает классы"""
import json
from pathlib import Path

print("=" * 80)
print("🔍 АНАЛИЗ ПРОБЛЕМЫ С ПРЕДСКАЗАНИЯМИ")
print("=" * 80)

# Загружаем классы
with open("model/class_names.json", 'r', encoding='utf-8') as f:
    classes = json.load(f)

print(f"\n📋 Всего классов в модели: {len(classes)}")
print("\n🍅 Классы, связанные с томатами:")
tomato_classes = [c for c in classes if 'tomato' in c.lower()]
for i, cls in enumerate(tomato_classes, 1):
    print(f"   {i}. {cls}")

print("\n🔬 Классы с бактериальными болезнями:")
bacterial_classes = [c for c in classes if 'bacterial' in c.lower()]
for i, cls in enumerate(bacterial_classes, 1):
    print(f"   {i}. {cls}")

print("\n🐛 Классы с вредителями (spider mites, etc):")
pest_classes = [c for c in classes if 'spider' in c.lower() or 'mite' in c.lower()]
for i, cls in enumerate(pest_classes, 1):
    print(f"   {i}. {cls}")

print("\n⚠️ ПРОБЛЕМА:")
print("   Модель может путать:")
print("   1. Бактериальную пятнистость (Bacterial_spot) - пятна на листьях")
print("   2. Повреждения вредителями (Spider_mites) - дырки в листьях")
print("   3. Другие болезни с похожими симптомами")
print("\n   Если на листе видны ДЫРКИ (как на вашем изображении), это скорее:")
print("   - Повреждение вредителями (Spider_mites)")
print("   - Или механическое повреждение")
print("   - НЕ бактериальная пятнистость (которая выглядит как пятна, не дырки)")

print("\n💡 РЕШЕНИЕ:")
print("   1. Модель обучена на изображениях из датасета")
print("   2. Если симптомы не совпадают с обученными, модель может ошибиться")
print("   3. Нужно проверить confidence score - если он высокий, но результат странный,")
print("      возможно модель переобучилась на определенные паттерны")
print("   4. Для более точной диагностики нужны:")
print("      - Больше разнообразных примеров в датасете")
print("      - Более четкое разделение симптомов (дырки vs пятна)")

print("\n" + "=" * 80)
