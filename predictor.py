"""
Простой wrapper-предсказатель с пост-обработкой (эвристика для
обнаружения мучнистой росы, чтобы корректировать ошибки "Черная пятнистость" -> "Мучнистая роса").

Правила (объяснимо и просто):
- Если модель предсказала "Черная пятнистость" с confidence > 0.85
- И на изображении есть светлые/белые участки (white_ratio) и низкая контрастность
- И отсутствуют чёткие чёрные округлые пятна (детекция контуров)
  => понижаем confidence, заменяем диагноз на "Мучнистая роса" и ставим flag `corrected_by_heuristic=True`.

Требования: работает офлайн, использует только OpenCV / NumPy, код читабелен для защиты диплома.
"""
from typing import Dict
import cv2
import numpy as np

# Используем глобальный предсказатель из приложения (не меняем веса модели)
try:
    from app.ml import predictor as base_predictor
except Exception:
    # fallback — если модуль недоступен при импорте в отдельном контексте
    base_predictor = None


def _image_powdery_checks(img: np.ndarray) -> Dict[str, float]:
    """Вычисляет простые метрики: white_ratio, contrast, black_round_count.

    Возвращает словарь с ключами `white_ratio`, `contrast`, `black_round_count`.
    """
    h, w = img.shape[:2]
    total = max(h * w, 1)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    v = hsv[:, :, 2]
    s = hsv[:, :, 1]

    # Белые/светлые пиксели: высокий V и низкая насыщенность
    white_mask = (v > 200) & (s < 40)
    white_ratio = int(np.count_nonzero(white_mask)) / total

    # Контраст: стандартное отклонение по серому
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    contrast = float(np.std(gray))

    # Обнаружим тёмные округлые пятна — считаем, что это признаки "Черной пятнистости"
    black_mask = (v < 60).astype('uint8') * 255
    # Убираем шум мелких пятен
    kernel = np.ones((5, 5), np.uint8)
    black_mask = cv2.morphologyEx(black_mask, cv2.MORPH_OPEN, kernel)

    contours, _ = cv2.findContours(black_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    black_round_count = 0
    for c in contours:
        area = cv2.contourArea(c)
        if area < 200:  # игнорируем очень мелкие объекты
            continue
        perimeter = cv2.arcLength(c, True)
        if perimeter <= 0:
            continue
        circularity = 4 * np.pi * area / (perimeter * perimeter)
        # круглая форма с достаточной площадью считается чётким пятном
        if circularity > 0.5 and area > 300:
            black_round_count += 1

    return {
        "white_ratio": white_ratio,
        "contrast": contrast,
        "black_round_count": black_round_count
    }


def predict(image_path: str) -> Dict:
    """Wrapper: вызывает базовый предсказатель и применяет эвристику.

    Возвращает словарь на основе результата базовой модели, дополненный
    полем `corrected_by_heuristic` (bool). Если эвристика применилась —
    `disease` и `confidence` могут быть скорректированы.
    """
    if base_predictor is None:
        raise RuntimeError("Base predictor (app.ml.predictor) is not available")

    # Получаем первичное предсказание (не меняем модель)
    result = base_predictor.predict(image_path)

    # По умолчанию — эвристика не применилась
    result = dict(result)  # копируем, чтобы не мутировать оригиналы
    result.setdefault('corrected_by_heuristic', False)

    try:
        disease = result.get('disease', '')
        confidence = float(result.get('confidence', 0.0))

        # Условие срабатывания: модель уверена в Черной пятнистости
        if disease == 'Черная пятнистость' and confidence > 0.85:
            img = cv2.imread(image_path)
            if img is not None:
                checks = _image_powdery_checks(img)

                white_ratio = checks['white_ratio']
                contrast = checks['contrast']
                black_round_count = checks['black_round_count']

                # Объяснимые пороги — легко описать на защите
                has_light_powdery = white_ratio > 0.12      # заметная доля светлых пикселей
                low_contrast = contrast < 30.0              # невысокая контрастность
                no_clear_black_spots = black_round_count == 0

                if has_light_powdery and low_contrast and no_clear_black_spots:
                    # Эвристика принята — корректируем
                    corrected_confidence = max(0.5, confidence * 0.6)

                    # Попробуем учесть вероятность для "Мучнистая роса" из всех вероятностей
                    all_probs = result.get('all_probabilities', {}) or {}
                    powder_prob = all_probs.get('Мучнистая роса')
                    if powder_prob:
                        # если модель уже ставила небольшую вероятность — усилим её немного
                        corrected_confidence = max(corrected_confidence, min(0.95, float(powder_prob) + 0.1))

                    result['disease'] = 'Мучнистая роса'
                    result['confidence'] = float(corrected_confidence)
                    result['corrected_by_heuristic'] = True

    except Exception:
        # Любые ошибки эвристики — не ломают основной результат
        result['corrected_by_heuristic'] = result.get('corrected_by_heuristic', False)

    return result


if __name__ == '__main__':
    # Простой локальный тест (не обязательно запускать в CI)
    import sys
    if len(sys.argv) > 1:
        print(predict(sys.argv[1]))