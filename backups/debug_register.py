#!/usr/bin/env python3
"""
Отладочный скрипт для проверки эндпоинта регистрации
"""
import requests
import json

def debug_register():
    """Отлаживает эндпоинт регистрации"""
    
    url = "http://localhost:8000/auth/register"
    
    # Тестовые данные - точно такие же, как отправляет фронтенд
    test_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("Отладка эндпоинта /auth/register")
    print(f"URL: {url}")
    print(f"Данные: {json.dumps(test_data, indent=2)}")
    print(f"Заголовки: {headers}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\n📊 Результат:")
        print(f"Статус: {response.status_code}")
        print(f"Заголовки: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"JSON ответ: {json.dumps(response_data, indent=2)}")
        except:
            print(f"Текст ответа: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print(" Ошибка подключения. Запустите сервер: uvicorn app.main:app --reload")
    except Exception as e:
        print(f" Ошибка: {e}")

if __name__ == "__main__":
    debug_register()
