#!/usr/bin/env python3
"""Демонстрационный скрипт для работы с датасетами
Показывает как загружать и использовать изображения с PlantVillage и PlantDoc
"""

from pathlib import Path
import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader
import sys


def check_datasets():
    """Проверить наличие датасетов"""
    print("\n📊 Проверка датасетов...")
    print("-" * 50)
    
    data_dir = Path("data")
    plantvillage = data_dir / "plantvillage"
    plantdoc = data_dir / "plantdoc"
    
    status = {
        "plantvillage": plantvillage.exists(),
        "plantdoc": plantdoc.exists()
    }
    
    if not any(status.values()):
        print("❌ Датасеты не найдены!")
        print("\n   Загрузите датасеты:")
        print("   $ python download_datasets.py")
        return None
    
    return status


def load_plantvillage(batch_size=32, num_workers=2):
    """Загрузить PlantVillage датасет"""
    print("\n📁 Загрузка PlantVillage датасета...")
    
    path = Path("data/plantvillage")
    
    # Трансформации для тренировки
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    # Трансформации для тестирования
    test_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    try:
        dataset = datasets.ImageFolder(root=str(path), transform=train_transform)
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers
        )
        
        print(f"✅ PlantVillage загружен")
        print(f"   📊 Образцов: {len(dataset)}")
        print(f"   🏷️  Классов: {len(dataset.classes)}")
        print(f"   📦 Батчей: {len(dataloader)}")
        
        return dataloader, dataset
        
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None, None


def load_plantdoc(batch_size=32, num_workers=2, split="train"):
    """Загрузить PlantDoc датасет"""
    print(f"\n📁 Загрузка PlantDoc датасета ({split}/)...")
    
    path = Path(f"data/plantdoc/{split}")
    
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                           std=[0.229, 0.224, 0.225])
    ])
    
    try:
        dataset = datasets.ImageFolder(root=str(path), transform=transform)
        dataloader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=(split == "train"),
            num_workers=num_workers
        )
        
        print(f"✅ PlantDoc ({split}) загружен")
        print(f"   📊 Образцов: {len(dataset)}")
        print(f"   🏷️  Классов: {len(dataset.classes)}")
        print(f"   📦 Батчей: {len(dataloader)}")
        
        return dataloader, dataset
        
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None, None


def demo_batch(dataloader, dataset_name=""):
    """Показать демо батча"""
    if dataloader is None:
        return
    
    print(f"\n🔍 Демо батча {dataset_name}...")
    print("-" * 50)
    
    try:
        images, labels = next(iter(dataloader))
        
        print(f"   📷 Форма батча: {images.shape}")
        print(f"   🏷️  Форма меток: {labels.shape}")
        print(f"   🎨 Размер изображения: {images[0].shape}")
        print(f"   📊 Min/Max значения: {images.min():.3f}/{images.max():.3f}")
        print(f"   📈 Mean: {images.mean():.3f}, Std: {images.std():.3f}")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")


def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🌱 Демонстрация работы с датасетами AgroScan AI")
    print("="*60)
    
    # Проверить датасеты
    status = check_datasets()
    if status is None:
        return 1
    
    # GPU/CPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n💻 Используется: {device.upper()}")
    
    # Загрузить PlantVillage
    if status["plantvillage"]:
        pv_loader, pv_dataset = load_plantvillage(batch_size=16)
        if pv_loader:
            demo_batch(pv_loader, "PlantVillage")
            
            # Показать примеры классов
            print(f"\n📋 Примеры классов PlantVillage (первые 5):")
            for i, cls_name in enumerate(sorted(pv_dataset.classes)[:5], 1):
                count = sum(1 for img_path, label in pv_dataset.imgs 
                          if pv_dataset.class_to_idx[cls_name] == label)
                print(f"   {i}. {cls_name}: {count} изображений")
    
    # Загрузить PlantDoc
    if status["plantdoc"]:
        pd_loader, pd_dataset = load_plantdoc(batch_size=16, split="train")
        if pd_loader:
            demo_batch(pd_loader, "PlantDoc (train)")
            
            # Показать примеры классов
            print(f"\n📋 Примеры классов PlantDoc (первые 5):")
            for i, cls_name in enumerate(sorted(pd_dataset.classes)[:5], 1):
                count = sum(1 for img_path, label in pd_dataset.imgs 
                          if pd_dataset.class_to_idx[cls_name] == label)
                print(f"   {i}. {cls_name}: {count} изображений")
    
    print("\n" + "="*60)
    print("✅ Демонстрация завершена!")
    print("="*60 + "\n")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n⏹️  Прерваны пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
