#!/usr/bin/env python3
"""
Скрипт для автоматической загрузки датасетов с Kaggle для AgroScan AI
Поддерживает: PlantVillage и PlantDoc датасеты

Использование:
    python download_datasets.py                    # Загрузить оба датасета
    python download_datasets.py --plantvillage    # Только PlantVillage
    python download_datasets.py --plantdoc        # Только PlantDoc
"""

import os
import sys
import subprocess
import argparse
import shutil
from pathlib import Path
import zipfile


class DatasetDownloader:
    """Загрузчик датасетов с Kaggle"""
    
    # Информация о датасетах
    DATASETS = {
        "plantvillage": {
            "kaggle_id": "emmarex/plantdisease",
            "zip_name": "plantdisease.zip",
            "extract_to": "plantvillage",
            "size": "7-10 GB",
            "images": "~54,306",
            "classes": "38",
            "description": "PlantVillage - овощи и фрукты"
        },
        "plantdoc": {
            "kaggle_id": "pratikkayal/plantdoc-dataset",
            "zip_name": "plantdoc-dataset.zip",
            "extract_to": "plantdoc",
            "size": "1-2 GB",
            "images": "~2,598",
            "classes": "30+",
            "description": "PlantDoc - деревья и кустарники"
        }
    }
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def check_kaggle_api(self) -> bool:
        """Проверка наличия установленного kaggle"""
        try:
            import kaggle
            print("✅ Kaggle API установлена")
            return True
        except ImportError:
            print("❌ Kaggle API не установлена!")
            print("   Установите: pip install kaggle")
            return False
    
    def check_kaggle_credentials(self) -> bool:
        """Проверка наличия Kaggle API ключей"""
        kaggle_json = Path.home() / ".kaggle" / "kaggle.json"
        
        if not kaggle_json.exists():
            print("❌ Kaggle credentials не найдены!")
            print(f"   Ожидаемый путь: {kaggle_json}")
            print("\n   Инструкция:")
            print("   1. Перейдите на https://www.kaggle.com/settings/account")
            print("   2. Нажмите 'Create New Token'")
            print("   3. Сохраните kaggle.json в ~/.kaggle/")
            return False
        
        print(f"✅ Kaggle credentials найдены: {kaggle_json}")
        return True

    ...
