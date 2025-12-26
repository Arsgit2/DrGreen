"""
Скрипт для создания демонстрационной PyTorch модели
Запускать после установки зависимостей
"""
import torch
import torch.nn as nn
import os

# Создаем папку для модели
os.makedirs("model", exist_ok=True)

class PlantDiseaseClassifier(nn.Module):
    """
    CNN модель для классификации болезней растений
    """
    def __init__(self, num_classes: int = 5):
        super(PlantDiseaseClassifier, self).__init__()
        
        # Простая CNN архитектура
        self.features = nn.Sequential(
            # Первый блок
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Второй блок
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Третий блок
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            # Четвертый блок
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        # Классификатор
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

def create_demo_model():
    """Создание и сохранение демонстрационной модели"""
    print("🤖 Создание демонстрационной PyTorch модели...")
    
    # Создаем модель
    model = PlantDiseaseClassifier(num_classes=5)
    
    # Инициализируем веса (для демонстрации)
    def init_weights(m):
        if isinstance(m, nn.Conv2d):
            nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
        elif isinstance(m, nn.Linear):
            nn.init.normal_(m.weight, 0, 0.01)
            nn.init.constant_(m.bias, 0)
    
    model.apply(init_weights)
    
    # Сохраняем модель
    model_path = "model/plant_disease_model.pth"
    torch.save(model.state_dict(), model_path)
    
    print(f"✅ Модель сохранена в {model_path}")
    print(f"📊 Параметры модели: {sum(p.numel() for p in model.parameters()):,}")
    
    return model_path

if __name__ == "__main__":
    create_demo_model()
