# 🚀 БЫСТРЫЙ СТАРТ: Установка датасетов

## ✅ Текущее состояние

- **Kaggle API:** ✅ Установлена (v1.8.2)
- **Датасеты:** ❌ Не загружены (папка `data/` пуста, только БД)
- **Свободное место:** ℹ️ Убедитесь, что есть 10+ ГБ свободного места

---

## 📝 Инструкция за 3 шага

### 1️⃣ Получить API ключи Kaggle

```
1. Откройте https://www.kaggle.com/settings/account
2. Прокрутите вниз до "API"
3. Нажмите "Create New Token"
4. Загрузится kaggle.json
5. ВАЖНО: Сохраните его в безопасном месте!
```

### 2️⃣ Разместить kaggle.json на компьютере

**Windows (PowerShell):**
```powershell
# Создать папку
mkdir $env:USERPROFILE\.kaggle

# Скопировать файл (замените ПУТЬ на тот, где вы загрузили kaggle.json)
Copy-Item "ПУТЬ\kaggle.json" "$env:USERPROFILE\.kaggle\"

# Установить разрешения
icacls "$env:USERPROFILE\.kaggle\kaggle.json" /inheritance:r /grant:r "%USERNAME%:F"
```

**Linux/Mac:**
```bash
mkdir -p ~/.kaggle
cp ~/Downloads/kaggle.json ~/.kaggle/
chmod 600 ~/.kaggle/kaggle.json
```

### 3️⃣ Загрузить датасеты

```powershell
cd c:\drgreen\agroscan-ai\backend
.\venv\Scripts\activate
python download_datasets.py
```

**Ожидаемое время:** 30-60 минут (в зависимости от интернета)

---

## 🎯 Варианты загрузки

```powershell
# Загрузить ОБА датасета (PlantVillage + PlantDoc)
python download_datasets.py

# Только PlantVillage (7-10 ГБ, 54k изображений)
python download_datasets.py --plantvillage

# Только PlantDoc (1-2 ГБ, 2.5k изображений)
python download_datasets.py --plantdoc
```

---

## ✔️ Проверка статуса

**Во время загрузки:**
```powershell
# Открыть новый PowerShell и выполнить
cd c:\drgreen\agroscan-ai\backend
.\venv\Scripts\activate
python verify_datasets.py
```

**После загрузки:**
```powershell
python verify_datasets.py --stats
```

**Ожидаемый результат:**
```
✅ PlantVillage (emmarex/plantdisease)
   🖼️  Изображений: 54,306
   🏷️  Классов: 38
   📊 Размер: 7.2 ГБ

✅ PlantDoc (pratikkayal/plantdoc-dataset)
   🖼️  Изображений: 2,598
   🏷️  Классов: 30
   📊 Размер: 1.8 ГБ

✅ Все датасеты готовы к использованию!
```

---

## 📊 Информация о датасетах

| Датасет | Размер | Изображений | Классов | Растения |
|---------|--------|-------------|---------|----------|
| **PlantVillage** | 7-10 ГБ | 54,306 | 38 | Овощи, фрукты (помидоры, картофель, перец, яблоки, виноград, кукуруза и др.) |
| **PlantDoc** | 1-2 ГБ | 2,598 | 30+ | Реальные фото листьев деревьев, кустарников, овощей |

---

## 🆘 Если что-то не работает

| Проблема | Решение |
|----------|---------|
| "kaggle.json not found" | Проверьте путь: `$env:USERPROFILE\.kaggle\kaggle.json` |
| "401 Unauthorized" | API ключ неверный или устарел. Создайте новый на Kaggle |
| "Dataset not found" | Проверьте спелл в названии датасета (регистр важен) |
| "Out of disk space" | Удалите .zip файлы после распаковки или используйте внешний диск |
| Долгая загрузка | Это нормально! 7+ ГБ может загружаться 1+ час |

---

## 📚 Дополнительная информация

- **Полное руководство:** `README_DATASETS.md`
- **Автоматическая загрузка:** `download_datasets.py`
- **Проверка статуса:** `verify_datasets.py`

---

**Вопросы?** Начните с полного `README_DATASETS.md`!
