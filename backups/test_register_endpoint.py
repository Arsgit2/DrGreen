#!/usr/bin/env python3
"""
Тестовый скрипт для проверки эндпоинта /auth/register
"""
import requests
import json

def test_register_endpoint():
    """Тестирует эндпоинт регистрации"""
    
    url = "http://localhost:8000/auth/register"
    
    # Тестовые данные
    test_data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    print("🧪 Тестируем эндпоинт /auth/register")
    print(f"📡 URL: {url}")
    print(f"📦 Данные: {test_data}")
    print(f"📋 Заголовки: {headers}")
    
    try:
        response = requests.post(url, json=test_data, headers=headers)
        
        print(f"\n📊 Результат:")
        print(f"Статус: {response.status_code}")
        print(f"Заголовки ответа: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Данные ответа: {response_data}")
        except:
            print(f"Текст ответа: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Ошибка подключения. Убедитесь, что сервер запущен на localhost:8000")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    test_register_endpoint()
