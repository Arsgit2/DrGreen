#!/usr/bin/env python3
"""
Улучшенный скрипт обучения ResNet18 модели с правильным объединением классов
Использует UnifiedDataset для нормализации имен классов из разных датасетов
"""
import argparse
import time
import json
from datetime import datetime
from pathlib import Path
from collections import Counter
import re

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Subset, Dataset
from torchvision import models, transforms
from PIL import Image

try:
    from torchvision.models import ResNet18_Weights
except Exception:
    ResNet18_Weights = None


def normalize_class_name(name):
    """Нормализация имени класса для объединения похожих классов из разных датасетов"""
    text = re.sub(r'[^a-z0-9]+', ' ', name.lower())
    words = text.split()
    stop_words = {'leaf', 'leaves', 'plant', 'feature', 'folder'}
    filtered_words = [w for w in words if w not in stop_words]
    filtered_words.sort()
    return " ".join(filtered_words)


class TransformDataset(Dataset):
    """Dataset wrapper для применения трансформаций к подмножеству данных"""
    def __init__(self, base_dataset, indices, transform):
        self.base_dataset = base_dataset
        self.indices = indices
        self.transform = transform
    
    def __len__(self):
        return len(self.indices)
    
    def __getitem__(self, idx):
        real_idx = self.indices[idx]
        path, label = self.base_dataset.samples[real_idx]
        try:
            img = Image.open(path).convert('RGB')
            if self.transform:
                img = self.transform(img)
            return img, label
        except Exception as e:
            print(f"Ошибка загрузки {path}: {e}")
            # Возвращаем черное изображение
            img = Image.new('RGB', (224, 224))
            if self.transform:
                img = self.transform(img)
            return img, label


class UnifiedDataset(Dataset):
    """Dataset, который правильно объединяет классы из разных датасетов"""
    def __init__(self, root_paths, transform=None):
        self.transform = transform
        self.samples = []  # (path, global_class_idx)
        self.classes = []  # global class names
        self.class_to_idx = {}
        
        norm_map = {}  # normalized_name -> (display_name, global_idx)
        
        for root in root_paths:
            root = Path(root)
            if not root.exists():
                print(f"⚠️ Warning: Path not found: {root}")
                continue
            
            # Проходим по директориям классов
            for class_dir in sorted(root.iterdir()):
                if not class_dir.is_dir():
                    continue
                
                original_class_name = class_dir.name
                norm_name = normalize_class_name(original_class_name)
                
                # Проверяем, есть ли уже такой нормализованный класс
                if norm_name not in norm_map:
                    # Новый глобальный класс
                    global_idx = len(self.classes)
                    self.classes.append(original_class_name)  # Сохраняем первое встреченное имя
                    norm_map[norm_name] = (original_class_name, global_idx)
                else:
                    # Существующий класс - используем его индекс
                    _, global_idx = norm_map[norm_name]
                
                # Собираем изображения
                for ext in ["*.[jJ][pP][gG]", "*.[jJ][pP][eE][gG]", "*.[pP][nN][gG]"]:
                    for img_path in class_dir.glob(ext):
                        self.samples.append((str(img_path), global_idx))
        
        self.class_to_idx = {name: idx for name, idx in norm_map.values()}
        print(f"✅ UnifiedDataset: {len(self.classes)} уникальных классов из {len(self.samples)} изображений")
    
    def __len__(self):
        """Возвращает количество образцов в датасете"""
        return len(self.samples)
    
    def __getitem__(self, idx):
        """Получает образец по индексу"""
        path, label = self.samples[idx]
        try:
            img = Image.open(path).convert('RGB')
            if self.transform:
                img = self.transform(img)
            return img, label
        except Exception as e:
            print(f"Ошибка загрузки {path}: {e}")
            # Возвращаем черное изображение
            img = Image.new('RGB', (224, 224))
            if self.transform:
                img = self.transform(img)
            return img, label


def get_transforms():
    """Трансформации для обучения и валидации"""
    train_transform = transforms.Compose([
        transforms.RandomResizedCrop(224, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomVerticalFlip(p=0.3),
        transforms.RandomRotation(15),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomAffine(degrees=0, translate=(0.1, 0.1)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    val_transform = transforms.Compose([
        transforms.Resize((256, 256)),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    
    return train_transform, val_transform


def load_datasets(batch_size, num_workers, device):
    """Загрузка и подготовка датасетов"""
    train_transform, val_transform = get_transforms()
    
    # Пути к датасетам
    roots = [
        Path("data/plantvillage/PlantVillage"),
        Path("data/plantdoc/train")
    ]
    
    # Создаем объединенный датасет
    print("\n📊 Загрузка и объединение датасетов...")
    full_dataset = UnifiedDataset(roots, transform=None)
    
    if len(full_dataset) == 0:
        raise RuntimeError("Не найдено изображений в датасетах!")
    
    # Разделяем на train/val с фиксированным seed для воспроизводимости
    generator = torch.Generator()
    generator.manual_seed(42)
    
    train_size = int(0.8 * len(full_dataset))
    val_size = len(full_dataset) - train_size
    
    indices = torch.randperm(len(full_dataset), generator=generator).tolist()
    train_indices = indices[:train_size]
    val_indices = indices[train_size:]
    
    # Создаем обертки для применения разных трансформаций
    train_dataset = TransformDataset(full_dataset, train_indices, train_transform)
    val_dataset = TransformDataset(full_dataset, val_indices, val_transform)
    
    # Вычисляем веса классов для балансировки
    all_train_labels = [full_dataset.samples[i][1] for i in train_indices]
    class_counts = Counter(all_train_labels)
    total_samples = len(all_train_labels)
    
    class_weights = {}
    for cls_idx in range(len(full_dataset.classes)):
        count = class_counts.get(cls_idx, 1)
        class_weights[cls_idx] = total_samples / (count + 1e-6)
    
    print(f"📈 Статистика датасета:")
    print(f"   Всего классов: {len(full_dataset.classes)}")
    print(f"   Train: {len(train_dataset):,} изображений")
    print(f"   Val: {len(val_dataset):,} изображений")
    print(f"   Минимум изображений в классе: {min(class_counts.values()) if class_counts else 0}")
    print(f"   Максимум изображений в классе: {max(class_counts.values()) if class_counts else 0}")
    
    # DataLoaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=(device == 'cuda'),
        drop_last=True  # Для стабильности batch norm
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=(device == 'cuda')
    )
    
    return train_loader, val_loader, class_weights, len(full_dataset.classes), full_dataset.classes


def build_model(pretrained, num_classes):
    """Создание модели ResNet18"""
    print(f"\n🧠 Создание ResNet18 модели для {num_classes} классов...")
    
    if pretrained and ResNet18_Weights is not None:
        model = models.resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
        print("   ✅ Используются pretrained веса ImageNet")
    else:
        try:
            model = models.resnet18(pretrained=pretrained)
        except Exception:
            model = models.resnet18()
            print("   ⚠️ Pretrained веса не загружены")
    
    # Заменяем последний слой
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, num_classes)
    
    return model


def train_model(args):
    """Основная функция обучения"""
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    print(f"\n🖥️ Устройство: {device.upper()}")
    if device == 'cuda':
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Память: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.1f} GB")
    
    # Загрузка датасетов
    train_loader, val_loader, class_weights, num_classes, class_names = load_datasets(
        args.batch_size, args.num_workers, device
    )
    
    # Сохраняем список классов
    Path('model').mkdir(parents=True, exist_ok=True)
    with open('model/class_names.json', 'w', encoding='utf-8') as f:
        json.dump(class_names, f, indent=2, ensure_ascii=False)
    print(f"✅ Список классов сохранен в model/class_names.json")
    
    # Создание модели
    model = build_model(args.pretrained, num_classes)
    model = model.to(device)
    
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print(f"📊 Параметры модели:")
    print(f"   Всего: {total_params:,}")
    print(f"   Обучаемых: {trainable_params:,}")
    
    # Оптимизатор и loss
    if args.fine_tune:
        # Fine-tuning: обучаем все слои, но с разными learning rates
        params = [
            {'params': [p for n, p in model.named_parameters() if 'fc' not in n], 'lr': args.lr * 0.1},
            {'params': model.fc.parameters(), 'lr': args.lr}
        ]
    else:
        # Только последний слой
        for name, param in model.named_parameters():
            if 'fc' not in name:
                param.requires_grad = False
        params = model.fc.parameters()
    
    optimizer = optim.AdamW(params, lr=args.lr, weight_decay=args.weight_decay)
    
    # Learning rate scheduler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer, mode='min', factor=0.5, patience=5, verbose=False
    )
    
    # Loss function с весами классов
    weight_tensor = torch.tensor([class_weights.get(i, 1.0) for i in range(num_classes)], dtype=torch.float32)
    weight_tensor = weight_tensor.to(device)
    criterion = nn.CrossEntropyLoss(weight=weight_tensor)
    
    # Обучение
    print(f"\n🚀 Начало обучения ({args.epochs} эпох)...")
    print("=" * 80)
    
    best_val_acc = 0.0
    best_val_loss = float('inf')
    train_losses = []
    val_losses = []
    train_accs = []
    val_accs = []
    patience_counter = 0
    
    for epoch in range(args.epochs):
        epoch_start = time.time()
        
        # Обучение
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(device)
            labels = labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, labels)
            loss.backward()
            
            # Gradient clipping для стабильности
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            optimizer.step()
            
            running_loss += loss.item()
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)
            
            if (batch_idx + 1) % 50 == 0:
                print(f"   Batch {batch_idx+1}/{len(train_loader)} | Loss: {loss.item():.4f}")
        
        train_loss = running_loss / len(train_loader)
        train_acc = 100.0 * correct / total
        train_losses.append(train_loss)
        train_accs.append(train_acc)
        
        # Валидация
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(device)
                labels = labels.to(device)
                
                outputs = model(images)
                loss = criterion(outputs, labels)
                
                val_loss += loss.item()
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)
        
        val_loss = val_loss / len(val_loader)
        val_acc = 100.0 * val_correct / val_total
        val_losses.append(val_loss)
        val_accs.append(val_acc)
        
        # Обновление learning rate
        scheduler.step(val_loss)
        current_lr = optimizer.param_groups[0]['lr']
        
        epoch_time = time.time() - epoch_start
        
        print(f"Epoch [{epoch+1}/{args.epochs}] | "
              f"Train Loss: {train_loss:.4f} Acc: {train_acc:.2f}% | "
              f"Val Loss: {val_loss:.4f} Acc: {val_acc:.2f}% | "
              f"LR: {current_lr:.2e} | Time: {epoch_time:.1f}s")
        
        # Сохранение лучшей модели
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            best_val_loss = val_loss
            patience_counter = 0
            
            Path('model').mkdir(parents=True, exist_ok=True)
            torch.save(model.state_dict(), 'model/plant_disease_resnet18_improved.pth')
            print(f"   💾 Лучшая модель сохранена! (Val Acc: {val_acc:.2f}%)")
        else:
            patience_counter += 1
        
        # Early stopping
        if patience_counter >= args.early_stop_patience:
            print(f"\n⏹️ Early stopping после {epoch+1} эпох (patience: {args.early_stop_patience})")
            break
        
        print("-" * 80)
    
    # Сохранение информации об обучении
    info = {
        'timestamp': datetime.now().isoformat(),
        'arch': 'resnet18',
        'pretrained': args.pretrained,
        'fine_tune': args.fine_tune,
        'num_classes': num_classes,
        'best_val_acc': best_val_acc,
        'best_val_loss': best_val_loss,
        'train_losses': train_losses,
        'val_losses': val_losses,
        'train_accs': train_accs,
        'val_accs': val_accs,
        'epochs_trained': epoch + 1,
        'class_names': class_names
    }
    
    with open('model/training_info_improved.json', 'w', encoding='utf-8') as f:
        json.dump(info, f, indent=2, ensure_ascii=False)
    
    print("\n" + "=" * 80)
    print("✅ Обучение завершено!")
    print(f"   Лучшая точность валидации: {best_val_acc:.2f}%")
    print(f"   Модель сохранена: model/plant_disease_resnet18_improved.pth")
    print(f"   Информация сохранена: model/training_info_improved.json")
    print("=" * 80)


def parse_args():
    parser = argparse.ArgumentParser(description='Улучшенное обучение ResNet18 для диагностики болезней растений')
    parser.add_argument('--pretrained', action='store_true', default=True,
                        help='Использовать pretrained веса ImageNet (по умолчанию: True)')
    parser.add_argument('--fine-tune', dest='fine_tune', action='store_true', default=True,
                        help='Fine-tune все слои (по умолчанию: True)')
    parser.add_argument('--epochs', type=int, default=50,
                        help='Количество эпох (по умолчанию: 50)')
    parser.add_argument('--batch-size', type=int, default=32,
                        help='Размер батча (по умолчанию: 32)')
    parser.add_argument('--lr', type=float, default=1e-4,
                        help='Learning rate (по умолчанию: 1e-4)')
    parser.add_argument('--weight-decay', type=float, default=1e-4,
                        help='Weight decay (по умолчанию: 1e-4)')
    parser.add_argument('--num-workers', type=int, default=0,
                        help='Количество worker процессов (по умолчанию: 0 для Windows)')
    parser.add_argument('--early-stop-patience', type=int, default=10,
                        help='Patience для early stopping (по умолчанию: 10)')
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()
    
    print("=" * 80)
    print("🌱 УЛУЧШЕННОЕ ОБУЧЕНИЕ RESNET18 ДЛЯ ДИАГНОСТИКИ БОЛЕЗНЕЙ РАСТЕНИЙ")
    print("=" * 80)
    print(f"Параметры:")
    print(f"  Pretrained: {args.pretrained}")
    print(f"  Fine-tune: {args.fine_tune}")
    print(f"  Epochs: {args.epochs}")
    print(f"  Batch size: {args.batch_size}")
    print(f"  Learning rate: {args.lr}")
    print(f"  Weight decay: {args.weight_decay}")
    print(f"  Early stopping patience: {args.early_stop_patience}")
    print("=" * 80)
    
    train_model(args)

