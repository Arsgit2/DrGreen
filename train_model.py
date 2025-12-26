import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, ConcatDataset
from torchvision import datasets, transforms
from pathlib import Path
import argparse
import sys
import time
from datetime import datetime
import json


class PlantDiseaseModel(nn.Module):
    """Оптимизированная CNN модель для GTX 1660 Ti (6GB памяти)"""
    
    def __init__(self, num_classes: int):
        super(PlantDiseaseModel, self).__init__()
        
        # Облегченная архитектура для 6GB GPU
        self.features = nn.Sequential(
            # Block 1
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(0.25),
            
            # Block 2
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(0.25),
            
            # Block 3
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.Conv2d(128, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.Dropout(0.25),
        )
        
        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))
        
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = self.classifier(x)
        return x


class ModelTrainer:
    """Тренер для обучения модели"""
    
    def __init__(self, device='cuda' if torch.cuda.is_available() else 'cpu'):
        self.device = device
        self.model = None
        self.optimizer = None
        self.criterion = None
        self.train_losses = []
        self.val_losses = []
        
        print(f"\n  Используется устройство: {device.upper()}")
        if device == 'cuda':
            print(f"   GPU: {torch.cuda.get_device_name(0)}")
            print(f"   CUDA версия: {torch.version.cuda}")
    
    def load_datasets(self, batch_size=32, num_workers=4):
        """Загрузить датасеты PlantVillage и PlantDoc"""
        print("\n Загрузка датасетов...")
        
        # Трансформации для тренировки (с аугментацией)
        train_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.RandomHorizontalFlip(),
            transforms.RandomVerticalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        # Трансформации для валидации (без аугментации)
        val_transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406],
                               std=[0.229, 0.224, 0.225])
        ])
        
        datasets_loaded = []
        all_classes = set()
        
        # Загрузить PlantVillage
        pv_path = Path("data/plantvillage")
        if pv_path.exists():
            print(f"   📁 PlantVillage: {pv_path}")
            pv_dataset = datasets.ImageFolder(str(pv_path), transform=train_transform)
            datasets_loaded.append(pv_dataset)
            all_classes.update(pv_dataset.classes)
            print(f"      ✅ Загружено: {len(pv_dataset)} изображений, {len(pv_dataset.classes)} классов")
        
        # Загрузить PlantDoc
        pd_train_path = Path("data/plantdoc/train")
        if pd_train_path.exists():
            print(f"   📁 PlantDoc: {pd_train_path}")
            pd_dataset = datasets.ImageFolder(str(pd_train_path), transform=train_transform)
            datasets_loaded.append(pd_dataset)
            all_classes.update(pd_dataset.classes)
            print(f"      ✅ Загружено: {len(pd_dataset)} изображений, {len(pd_dataset.classes)} классов")
        
        if not datasets_loaded:
            print("❌ Датасеты не найдены!")
            return None, None
        
        # Объединить датасеты
        combined_dataset = ConcatDataset(datasets_loaded)
        
        # Разделить на тренировку и валидацию (80/20)
        train_size = int(0.8 * len(combined_dataset))
        val_size = len(combined_dataset) - train_size
        train_dataset, val_dataset = torch.utils.data.random_split(
            combined_dataset, [train_size, val_size]
        )
        
        # Изменить трансформы для валидации
        val_dataset.dataset.transform = val_transform
        
        # DataLoaders
        train_loader = DataLoader(
            train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=num_workers,
            pin_memory=True if self.device == 'cuda' else False
        )
        
        val_loader = DataLoader(
            val_dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=num_workers,
            pin_memory=True if self.device == 'cuda' else False
        )
        
        print(f"\n   📊 Объединённый датасет:")
        print(f"      Всего изображений: {len(combined_dataset):,}")
        print(f"      Всего классов: {len(all_classes)}")
        print(f"      Тренировка: {train_size:,} (80%)")
        print(f"      Валидация: {val_size:,} (20%)")
        
        return train_loader, val_loader, len(all_classes)
    
    def create_model(self, num_classes):
        """Создать модель"""
        print("\n🧠 Создание модели...")
        self.model = PlantDiseaseModel(num_classes=num_classes).to(self.device)
        
        # Параметры модели
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        
        print(f"   Всего параметров: {total_params:,}")
        print(f"   Обучаемых параметров: {trainable_params:,}")
        
        # Оптимизатор и loss функция
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001, weight_decay=1e-4)
        self.criterion = nn.CrossEntropyLoss()
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer, mode='min', factor=0.5, patience=5
        )
        
        print("   ✅ Модель создана")
    
    def train_epoch(self, train_loader):
        """Обучить одну эпоху"""
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_idx, (images, labels) in enumerate(train_loader):
            images = images.to(self.device)
            labels = labels.to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            outputs = self.model(images)
            loss = self.criterion(outputs, labels)
            
            # Backward pass
            loss.backward()
            self.optimizer.step()
            
            # Статистика
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            correct += (predicted == labels).sum().item()
            total += labels.size(0)
            
            # Прогресс
            if (batch_idx + 1) % 10 == 0:
                print(f"      Батч [{batch_idx + 1}/{len(train_loader)}], "
                      f"Loss: {loss.item():.4f}, "
                      f"Точность: {100 * correct / total:.2f}%")
        
        avg_loss = total_loss / len(train_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def validate(self, val_loader):
        """Валидация модели"""
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for images, labels in val_loader:
                images = images.to(self.device)
                labels = labels.to(self.device)
                
                outputs = self.model(images)
                loss = self.criterion(outputs, labels)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                correct += (predicted == labels).sum().item()
                total += labels.size(0)
        
        avg_loss = total_loss / len(val_loader)
        accuracy = 100 * correct / total
        
        return avg_loss, accuracy
    
    def train(self, train_loader, val_loader, epochs=10):
        """Обучить модель"""
        print(f"\n🚀 Начало обучения ({epochs} эпох)...\n")
        
        start_time = time.time()
        best_val_loss = float('inf')
        patience = 10
        patience_counter = 0
        
        for epoch in range(epochs):
            epoch_start = time.time()
            
            print(f"Эпоха [{epoch + 1}/{epochs}]")
            print("-" * 50)
            
            # Тренировка
            train_loss, train_acc = self.train_epoch(train_loader)
            
            # Валидация
            val_loss, val_acc = self.validate(val_loader)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            
            epoch_time = time.time() - epoch_start
            
            print(f"\n   📊 Результаты эпохи:")
            print(f"      Тренировка - Loss: {train_loss:.4f}, Точность: {train_acc:.2f}%")
            print(f"      Валидация  - Loss: {val_loss:.4f}, Точность: {val_acc:.2f}%")
            print(f"      Время: {epoch_time:.1f}с")
            print()
            
            # Сохранить лучшую модель
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_model("model/plant_disease_model_best.pth")
                print("   ✅ Лучшая модель сохранена!\n")
            else:
                patience_counter += 1
            
            # Learning rate scheduler
            self.scheduler.step(val_loss)
            
            # Early stopping
            if patience_counter >= patience:
                print(f"⏹️  Early stopping при эпохе {epoch + 1}")
                break
        
        total_time = time.time() - start_time
        
        print("\n" + "="*50)
        print("✅ Обучение завершено!")
        print("="*50)
        print(f"Всего времени: {total_time/60:.1f} минут")
        print(f"Лучшая loss валидации: {best_val_loss:.4f}")
    
    def save_model(self, path):
        """Сохранить модель"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        torch.save(self.model.state_dict(), path)
        print(f"   💾 Модель сохранена: {path}")
    
    def save_training_info(self, num_classes):
        """Сохранить информацию об обучении"""
        info = {
            "timestamp": datetime.now().isoformat(),
            "model": "PlantDiseaseModel",
            "num_classes": num_classes,
            "device": self.device,
            "train_losses": self.train_losses,
            "val_losses": self.val_losses,
            "epochs_trained": len(self.train_losses)
        }
        
        with open("model/training_info.json", 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"   📊 Информация об обучении сохранена")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(
        description="Обучение модели на датасетах PlantVillage и PlantDoc"
    )
    
    parser.add_argument(
        "--epochs",
        type=int,
        default=20,
        help="Количество эпох для обучения (по умолчанию: 20)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=32,
        help="Размер батча (по умолчанию: 32)"
    )
    parser.add_argument(
        "--lr",
        type=float,
        default=0.001,
        help="Learning rate (по умолчанию: 0.001)"
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🌱 Обучение модели диагностики болезней растений")
    print("="*60)
    
    # Инициализировать тренер
    trainer = ModelTrainer()
    
    # Загрузить датасеты
    datasets_result = trainer.load_datasets(batch_size=args.batch_size)
    if datasets_result[0] is None:
        print("❌ Не удалось загрузить датасеты!")
        return 1
    
    train_loader, val_loader, num_classes = datasets_result
    
    # Создать модель
    trainer.create_model(num_classes)
    
    # Обучить модель
    trainer.train(train_loader, val_loader, epochs=args.epochs)
    
    # Сохранить финальную модель
    trainer.save_model("model/plant_disease_model_final.pth")
    trainer.save_training_info(num_classes)
    
    print("\n" + "="*60)
    print("✅ Проект полностью обучен!")
    print("="*60)
    print("\nОбученные модели:")
    print("   - model/plant_disease_model_best.pth (лучшая)")
    print("   - model/plant_disease_model_final.pth (финальная)")
    print("   - model/training_info.json (информация об обучении)")
    print("\nМодель готова к использованию в FastAPI! 🚀")
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⏹️  Обучение прервано пользователем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
