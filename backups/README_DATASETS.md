# 📊 Установка датасетов для AgroScan AI

## 📋 Краткое резюме

В вашем проекте **нет загруженных датасетов**. Проверено: папка `data/` содержит только БД (0.07 МБ).

### Доступные датасеты:

| № | Название | Размер | Классов | Источник |
|---|----------|--------|---------|----------|
| 1️⃣ | **PlantVillage** (emmarex/plantdisease) | ~7-10 ГБ | 38 классов | Овощи, фрукты |
| 2️⃣ | **PlantDoc** (pratikkayal/plantdoc-dataset) | ~1-2 ГБ | 30+ классов | Деревья, кустарники |

---

## 🚀 Быстрая установка (3 шага)

### Шаг 1️⃣: Получить Kaggle API ключи

1. Перейдите на https://www.kaggle.com/settings/account
2. Прокрутите вниз до "API" и нажмите "Create New Token"
3. Загрузится файл `kaggle.json` - **сохраните его**

### Шаг 2️⃣: Разместить kaggle.json

**Windows:**
```powershell
# Создать папку
mkdir $env:USERPROFILE\.kaggle

# Скопировать файл (замените ПУТЬ на папку, где вы загрузили kaggle.json)
Copy-Item "ПУТЬ\kaggle.json" "$env:USERPROFILE\.kaggle\"

# Установить права доступа (ограничить доступ только текущему пользователю)
icacls "$env:USERPROFILE\.kaggle\kaggle.json" /inheritance:r /grant:r "%USERNAME%:F"
```

**Linux/Mac:**
```bash
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### Шаг 3️⃣: Загрузить датасеты

**Вариант А - Автоматическая загрузка (рекомендуется):**
```powershell
cd c:\drgreen\agroscan-ai\backend
.\venv\Scripts\activate
python download_datasets.py
```

**Вариант Б - Ручная загрузка:**
```powershell
# PlantVillage датасет
kaggle datasets download -d emmarex/plantdisease -p .\data\

# PlantDoc датасет
kaggle datasets download -d pratikkayal/plantdoc-dataset -p .\data\

# Распаковать (PowerShell)
cd .\data\
Expand-Archive -Path *.zip -DestinationPath .
Remove-Item -Path *.zip
```

---

## ✅ Проверка установки

После загрузки проверьте состояние датасетов:

```powershell
cd c:\drgreen\agroscan-ai\backend
.\venv\Scripts\activate
python verify_datasets.py
```

### Ожидаемый вывод:
```
📊 Статус датасетов AgroScan AI
════════════════════════════════════════════════════

✅ PlantVillage (emmarex/plantdisease)
   📁 Расположение: ./data/plantvillage
   📦 Статус: Загружен
   🖼️  Изображений: 54,306
   🏷️  Классов: 38
   📊 Размер: 7.2 ГБ

✅ PlantDoc (pratikkayal/plantdoc-dataset)  
   📁 Расположение: ./data/plantdoc
   📦 Статус: Загружен
   🖼️  Изображений: 2,598
   🏷️  Классов: 30
   📊 Размер: 1.8 ГБ

════════════════════════════════════════════════════
✅ Все датасеты готовы к использованию!
```

---

## 📁 Структура после загрузки

```
backend/
├── data/
│   ├── agroscan.db              # Ваша БД (будет сохранена)
│   ├── plantvillage/            # PlantVillage датасет (7-10 ГБ)
│   │   ├── Tomato___Bacterial_spot/
│   │   ├── Tomato___Late_blight/
│   │   ├── Tomato___Leaf_Mold/
│   │   ├── Tomato___Septoria_leaf_spot/
│   │   ├── Tomato___Spider_mites_Two-spotted_spider_mite/
│   │   ├── Tomato___Target_Spot/
│   │   ├── Tomato___Tomato_YellowLeaf_Curl_Virus/
│   │   ├── Tomato___Tomato_mosaic_virus/
│   │   ├── Tomato___healthy/
│   │   ├── Potato___ Early_blight/
│   │   ├── Potato___Late_blight/
│   │   ├── Potato___healthy/
│   │   ├── Pepper,_bell___Bacterial_spot/
│   │   ├── Pepper,_bell___healthy/
│   │   ├── Apple___Apple_scab/
│   │   ├── Apple___Black_rot/
│   │   ├── Apple___Cedar_apple_rust/
│   │   ├── Apple___healthy/
│   │   └── ... (еще 20+ папок с классами)
│   │
│   └── plantdoc/                # PlantDoc датасет (1-2 ГБ)
│       ├── train/
│       │   ├── Apple_blotch/
│       │   ├── Apple_scab/
│       │   ├── Banana_Black_leaf_streak/
│       │   ├── Banana_Sigatoka/
│       │   ├── Lemon_bacterial_spot/
│       │   ├── Lemon_canker/
│       │   ├── Mango_powdery_mildew/
│       │   ├── Mango_sooty_mould/
│       │   ├── Grape_Black_rot/
│       │   ├── Grape_Esca/
│       │   ├── Grape_Isariopsis_Leaf_Spot/
│       │   └── ... (еще 18+ папок)
│       ├── test/
│       └── val/
```