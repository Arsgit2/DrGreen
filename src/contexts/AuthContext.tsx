import React, { createContext, useContext, useState, useEffect } from 'react'
import { api } from '../lib/api'

interface User {
  id: number
  name: string
  email: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (email: string, password: string) => Promise<void>
  register: (name: string, email: string, password: string) => Promise<void>
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const savedToken = localStorage.getItem('token')
    const savedUser = localStorage.getItem('user')
    
    if (savedToken && savedUser) {
      try {
        setToken(savedToken)
        setUser(JSON.parse(savedUser))
      } catch (error) {
        console.error('Ошибка парсинга пользователя из localStorage:', error)
        // Очищаем поврежденные данные
        localStorage.removeItem('token')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
          password: password
        })
      })
      
      const data = await response.json()
      
      if (!response.ok) {
        // Если ошибка, показываем detail из ответа
        const errorMessage = data.detail || 'Ошибка входа в систему'
        alert(errorMessage)
        throw new Error(errorMessage)
      }
      
      // Показываем успешное сообщение
      alert(data.message)
      
      // Сохраняем токен и данные пользователя
      const accessToken = data.access_token
      const userData = { 
        id: data.user.id, 
        email: data.user.email, 
        name: data.user.email 
      }
      
      setToken(accessToken)
      setUser(userData)
      localStorage.setItem('token', accessToken)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error: any) {
      // Выводим alert с текстом ошибки
      const errorMessage = error.message || 'Ошибка входа в систему'
      alert(errorMessage)
      throw new Error(errorMessage)
    }
  }

  const register = async (name: string, email: string, password: string) => {
    try {
      const requestBody = {
        email: email,
        password: password
      }
      
      console.log('Отправляем данные:', requestBody)
      
      // Отправляем только email и password, как ожидает бэкенд
      const response = await fetch('http://localhost:8000/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestBody)
      })
      
      console.log('Статус ответа:', response.status)
      
      const data = await response.json()
      console.log('Данные ответа:', data)
      
      if (!response.ok) {
        // Если ошибка, показываем detail из ответа
        let errorMessage = 'Ошибка регистрации'
        
        if (data.detail && Array.isArray(data.detail)) {
          // Обрабатываем массив ошибок валидации
          const validationErrors = data.detail.map((err: any) => {
            return `${err.loc ? err.loc.join('.') : 'field'}: ${err.msg}`
          }).join(', ')
          errorMessage = `Ошибка валидации: ${validationErrors}`
        } else if (data.detail) {
          errorMessage = data.detail
        } else if (data.message) {
          errorMessage = data.message
        }
        
        console.error('Ошибка регистрации:', errorMessage)
        alert(`Ошибка ${response.status}: ${errorMessage}`)
        throw new Error(errorMessage)
      }
      
      // Показываем успешное сообщение
      alert(data.message)
      
      // Сохраняем токен и данные пользователя
      const accessToken = data.access_token
      const userData = { 
        id: data.user.id, 
        email: data.user.email, 
        name: data.user.email 
      }
      
      setToken(accessToken)
      setUser(userData)
      localStorage.setItem('token', accessToken)
      localStorage.setItem('user', JSON.stringify(userData))
    } catch (error: any) {
      // Выводим alert с текстом ошибки
      console.error('Ошибка в register:', error)
      const errorMessage = error.message || 'Ошибка регистрации'
      alert(errorMessage)
      throw new Error(errorMessage)
    }
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // Показываем загрузку, пока контекст не готов
  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 bg-green-500 rounded-full animate-pulse mx-auto mb-4"></div>
          <p className="text-gray-600">Загрузка...</p>
        </div>
      </div>
    )
  }

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
