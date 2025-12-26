#!/usr/bin/env python3
"""
Test script for authentication endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    url = f"{BASE_URL}/auth/register"
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    print("🧪 Testing registration...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 201
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_login():
    """Test user login"""
    url = f"{BASE_URL}/auth/login"
    data = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    print("\n🧪 Testing login...")
    print(f"URL: {url}")
    print(f"Data: {data}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_health():
    """Test health endpoint"""
    url = f"{BASE_URL}/health"
    
    print("\n🧪 Testing health check...")
    print(f"URL: {url}")
    
    try:
        response = requests.get(url)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Testing DrGreen AI API")
    print("=" * 50)
    
    # Test health first
    health_ok = test_health()
    
    if health_ok:
        # Test registration
        register_ok = test_register()
        
        if register_ok:
            # Test login
            login_ok = test_login()
            
            print("\n" + "=" * 50)
            print("📊 Results:")
            print(f"Health: {'✅' if health_ok else '❌'}")
            print(f"Register: {'✅' if register_ok else '❌'}")
            print(f"Login: {'✅' if login_ok else '❌'}")
        else:
            print("\n❌ Registration failed, skipping login test")
    else:
        print("\n❌ Health check failed, server not running")
