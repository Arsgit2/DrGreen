# DrGreen AI Backend

Backend для диагностики болезней растений с использованием PyTorch и FastAPI.

## 🚀 Быстрый старт

### 1. Создание виртуального окружения
```bash
python -m venv venv

# Активация (Windows)
venv\Scripts\activate

# Активация (Linux/Mac)
source venv/bin/activate
```

### 2. Установка зависимостей
```bash
pip install -r requirements.txt
```

### 3. Создание демонстрационной модели
```bash
python create_demo_model.py
```

### 4. Запуск сервера
```bash
uvicorn app.main:app --reload
```

## 📁 Структура проекта

```
backend/
├── venv/                    # Виртуальное окружение
├── app/                     # Основное приложение
│   ├── __init__.py
│   ├── main.py             # Точка входа FastAPI
│   ├── routes.py           # API роуты
│   ├── models.py           # SQLAlchemy модели
│   ├── database.py         # Конфигурация БД
│   └── ml.py              # ML модуль с PyTorch
├── model/                  # Папка для ML моделей
│   └── plant_disease_model.pth
├── uploads/                # Загруженные изображения
├── data/                   # База данных SQLite
│   └── agroscan.db
├── requirements.txt        # Зависимости Python
├── create_demo_model.py    # Создание демо модели
└── README.md              # Документация
```

## 🔧 API Endpoints

### Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Вход в систему

### Основные
- `GET /` - Главная страница
- `GET /api/health` - Проверка состояния
- `POST /api/predict` - Диагностика по изображению

### Растения (CRUD)
- `GET /api/plants` - Список растений
- `POST /api/plants` - Создание растения
- `GET /api/plants/{id}` - Получение растения
- `PUT /api/plants/{id}` - Обновление растения
- `DELETE /api/plants/{id}` - Удаление растения


### Дополнительные
- `GET /api/diseases` - Список болезней
- `GET /api/scans` - История сканирований

## 🤖 ML Модель

### Архитектура
- **Тип**: CNN (Convolutional Neural Network)
- **Фреймворк**: PyTorch
- **Входные данные**: RGB изображения 224x224
- **Выходные данные**: 5 классов болезней

### Классы болезней
1. Здоровое растение
2. Фитофтороз
3. Мучнистая роса
4. Черная пятнистость
5. Антракноз

### Использование
```python
from app.ml import predictor

# Предсказание
result = predictor.predict("path/to/image.jpg")
print(f"Болезнь: {result['disease']}")
print(f"Уверенность: {result['confidence']:.2f}")
```

## 🗄 База данных

### Таблицы
- **plants** - Растения в справочнике
- **diseases** - Болезни растений
- **scans** - История сканирований

### SQLite
База данных создается автоматически в `data/agroscan.db`

## 📊 Примеры использования

### Диагностика растения
```bash
curl -X POST "http://localhost:8000/api/predict" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@plant_leaf.jpg"
```

### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Вход в систему
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "password123"}'
```

### Создание растения
```bash
curl -X POST "http://localhost:8000/api/plants" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "name=Томат&scientific_name=Solanum lycopersicum&description=Популярное овощное растение"
```

### Получение списка растений
```bash
curl "http://localhost:8000/api/plants"
```

## 🔍 Документация API

После запуска сервера доступна интерактивная документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🛠 Разработка

### Структура кода
- **app/main.py** - Конфигурация FastAPI
- **app/routes.py** - API эндпоинты
- **app/models.py** - SQLAlchemy модели
- **app/database.py** - Настройка БД
- **app/ml.py** - ML логика с PyTorch

### Добавление новых эндпоинтов
1. Добавьте функцию в `app/routes.py`
2. Зарегистрируйте роут в `app/main.py`
3. Обновите документацию

### Добавление новых моделей БД
1. Создайте класс в `app/models.py`
2. Импортируйте в `app/database.py`
3. Таблица создастся автоматически

## 🚨 Устранение неполадок

### Проблемы с PyTorch
```bash
# Проверка установки
python -c "import torch; print(torch.__version__)"

# Переустановка
pip uninstall torch torchvision torchaudio
pip install torch torchvision torchaudio
```

### Проблемы с базой данных
```bash
# Удаление и пересоздание БД
rm data/agroscan.db
python -c "from app.database import engine, Base; Base.metadata.create_all(bind=engine)"
```

### Проблемы с моделью
```bash
# Пересоздание демо модели
python create_demo_model.py
```

## 📈 Производительность

### Оптимизация
- Использование CPU для PyTorch
- Кэширование модели в памяти
- Асинхронная обработка файлов

### Мониторинг
- Логирование запросов
- Метрики времени отклика
- Отслеживание использования памяти

## 🔒 Безопасность

### Валидация
- Проверка типов файлов
- Ограничение размера изображений
- Санитизация входных данных

### Ограничения
- Максимальный размер файла: 10MB
- Поддерживаемые форматы: JPG, PNG, WEBP
- Таймаут обработки: 30 секунд
