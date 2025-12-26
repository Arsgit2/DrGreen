# ⚡ ШПАРГАЛКА: Команды для работы с датасетами

## 🚀 ОСНОВНЫЕ КОМАНДЫ

### Загрузить датасеты
```powershell
# Активировать окружение (всегда первым)
cd c:\drgreen\agroscan-ai\backend
.\venv\Scripts\activate

# Загрузить оба датасета (PlantVillage + PlantDoc)
python download_datasets.py

# Только PlantVillage
python download_datasets.py --plantvillage

# Только PlantDoc
python download_datasets.py --plantdoc
```

### Проверить статус
```powershell
# Быстрая проверка (есть/нет датасеты)
python verify_datasets.py

# С информацией о классах
python verify_datasets.py --detailed

# Полная статистика (рекомендуется)
python verify_datasets.py --stats

# Сохранить отчет в JSON
python verify_datasets.py --report
```

### Демонстрация
```powershell
# Показать примеры использования с PyTorch
python demo_datasets.py
```

---

## 📚 ДОКУМЕНТАЦИЯ

```powershell
# Быстрый старт (3 шага, 2-3 часа)
notepad QUICK_START_DATASETS.md

# Полное руководство (все детали)
notepad README_DATASETS.md

# Итоговый отчет и справочник
notepad INSTALL_REPORT.md

# Это резюме
notepad SUMMARY.md
```

---

## 🔑 НАСТРОЙКА KAGGLE

### Получить ключи
1. https://www.kaggle.com/settings/account
2. Нажать "Create New Token"
3. Загрузится kaggle.json

### Разместить ключи (Windows)
```powershell
# Создать папку
mkdir $env:USERPROFILE\.kaggle

# Скопировать kaggle.json (замените ПУТЬ)
Copy-Item "ПУТЬ\kaggle.json" "$env:USERPROFILE\.kaggle\"

# Установить права
icacls "$env:USERPROFILE\.kaggle\kaggle.json" /inheritance:r /grant:r "%USERNAME%:F"

# Проверить
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"
```

---

## 🐍 ИСПОЛЬЗОВАНИЕ В КОДЕ

### Загрузить PlantVillage
```python
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                       std=[0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder('data/plantvillage', transform=transform)
dataloader = DataLoader(dataset, batch_size=32, shuffle=True)
```

### Загрузить PlantDoc
```python
# train/ или test/ или val/
dataset = datasets.ImageFolder('data/plantdoc/train', transform=transform)
```

### Получить информацию
```python
print(f"Изображений: {len(dataset)}")
print(f"Классов: {len(dataset.classes)}")
print(f"Классы: {dataset.classes}")  # список всех классов
```

---

## 🧹 УДАЛЕНИЕ И ПЕРЕУСТАНОВКА

### Удалить датасеты (полностью)
```powershell
# Удалить папки (будут потеряны данные!)
Remove-Item -Path "data/plantvillage" -Recurse -Force
Remove-Item -Path "data/plantdoc" -Recurse -Force
```

### Удалить только архивы (.zip)
```powershell
cd data
Remove-Item -Path *.zip -Force
```

### Переустановить один датасет
```powershell
# Удалить
Remove-Item -Path "data/plantvillage" -Recurse -Force

# Переустановить
python download_datasets.py --plantvillage
```

---

## 🔍 ОТЛАДКА

### Проверить Kaggle
```powershell
python -c "import kaggle; print('OK')"
```

### Проверить credentials
```powershell
Test-Path "$env:USERPROFILE\.kaggle\kaggle.json"
```

### Проверить диск
```powershell
# Свободное место
Get-Volume C:
```

### Подробная информация
```powershell
python verify_datasets.py --detailed --stats
```

---

## 📊 ИНФОРМАЦИЯ

### Размеры
```
PlantVillage: 7-10 ГБ (сжато ~2-3 ГБ)
PlantDoc:     1-2 ГБ (сжато ~500 МБ)
Время:        30-60 минут (зависит от интернета)
```

### Классы
```
PlantVillage: 38 классов болезней
PlantDoc:     30+ классов болезней
```

### Изображения
```
PlantVillage: 54,306 изображений
PlantDoc:     2,598 изображений
```

---

## ⚠️ ЧАСТЫЕ ОШИБКИ

| Ошибка | Решение |
|--------|---------|
| kaggle.json not found | Проверьте ~/.kaggle/kaggle.json |
| 401 Unauthorized | Обновите API ключ на Kaggle |
| Dataset not found | Проверьте спелл (регистр важен) |
| Out of disk space | Удалите .zip файлы или освободите место |
| ConnectionError | Проверьте интернет-соединение |

---

## 📂 СТРУКТУРА ФАЙЛОВ

```
backend/
├── download_datasets.py    ← Запустить для загрузки
├── verify_datasets.py      ← Запустить для проверки
├── demo_datasets.py        ← Запустить для примеров
│
├── QUICK_START_DATASETS.md ← Прочитать первым
├── README_DATASETS.md      ← Полное руководство
├── INSTALL_REPORT.md       ← Техническая справка
├── SUMMARY.md              ← Это резюме
│
├── data/
│   ├── agroscan.db         ← Ваша БД (не удалять!)
│   ├── plantvillage/       ← PlantVillage датасет (после загрузки)
│   └── plantdoc/           ← PlantDoc датасет (после загрузки)
│
└── venv/                   ← Виртуальное окружение
```

---

## 🎯 ПЛАН ДЕЙСТВИЙ

### Сегодня (30 минут)
- [ ] Получить Kaggle API ключи
- [ ] Запустить `python download_datasets.py`

### Завтра (проверка)
- [ ] Запустить `python verify_datasets.py --stats`
- [ ] Запустить `python demo_datasets.py`

### На неделе (разработка)
- [ ] Обновить ML модель
- [ ] Обучить новую модель на реальных данных
- [ ] Тестировать на PlantDoc

---

## 🌐 ССЫЛКИ

- [Kaggle API](https://github.com/Kaggle/kaggle-api)
- [PlantVillage датасет](https://www.kaggle.com/datasets/emmarex/plantdisease)
- [PlantDoc датасет](https://www.kaggle.com/datasets/pratikkayal/plantdoc-dataset)
- [PyTorch DataLoader](https://pytorch.org/vision/stable/generated/torchvision.datasets.ImageFolder.html)

---

## 💡 СОВЕТЫ

```powershell
# Запустить проверку пока идет загрузка
# (в отдельном PowerShell окне)
python verify_datasets.py

# Проверять каждый час, если загрузка долгая
# Это показывает прогресс

# Использовать PlantDoc первым (меньше размер)
python download_datasets.py --plantdoc

# Потом PlantVillage
python download_datasets.py --plantvillage
```

---

**Все готово! Просто запустите и наслаждайтесь! 🚀**
