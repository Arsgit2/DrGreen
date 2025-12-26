import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { History as HistoryIcon, Calendar, Eye, AlertTriangle, CheckCircle, Filter } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

interface ScanHistoryItem {
  id: number
  disease_name: string
  confidence: number
  is_healthy: string
  image_path: string
  created_at: string
}

export function History() {
  const [scans, setScans] = useState<ScanHistoryItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'diseases' | 'healthy'>('all')
  const { user } = useAuth()

  useEffect(() => {
    if (user) {
      fetchHistory()
    }
  }, [user])

  const fetchHistory = async () => {
    if (!user) return
    
    try {
      setLoading(true)
      const response = await api.get('/api/scans')
      setScans(response.data)
    } catch (err) {
      setError('Ошибка при загрузке истории')
    } finally {
      setLoading(false)
    }
  }

  const filteredScans = scans.filter(scan => {
    if (filter === 'diseases') return scan.is_healthy === 'disease'
    if (filter === 'healthy') return scan.is_healthy === 'healthy'
    return true
  })

  const getDiseaseIcon = (isHealthy: string) => {
    if (isHealthy === 'healthy') {
      return <CheckCircle className="w-5 h-5 text-green-600" />
    }
    return <AlertTriangle className="w-5 h-5 text-red-600" />
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  if (!user) {
    return (
      <div className="max-w-2xl mx-auto text-center space-y-6">
        <Card>
          <CardContent className="p-8">
            <h2 className="text-2xl font-bold text-gray-900 mb-4">
              Войдите в систему
            </h2>
            <p className="text-gray-600 mb-6">
              Для просмотра истории сканов необходимо войти в систему
            </p>
            <Button onClick={() => window.location.href = '/login'}>
              Войти
            </Button>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Заголовок */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center">
          <HistoryIcon className="w-8 h-8 mr-3" />
          История сканов
        </h1>
        <p className="text-lg text-gray-600">
          Все ваши диагностики растений
        </p>
      </div>

      {/* Фильтры */}
      <Card>
        <CardContent className="p-4">
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filter === 'all' ? 'default' : 'outline'}
              onClick={() => setFilter('all')}
              size="sm"
            >
              Все ({scans.length})
            </Button>
            <Button
              variant={filter === 'diseases' ? 'default' : 'outline'}
              onClick={() => setFilter('diseases')}
              size="sm"
            >
              <AlertTriangle className="w-4 h-4 mr-1" />
              Болезни ({scans.filter(s => s.is_healthy === 'disease').length})
            </Button>
            <Button
              variant={filter === 'healthy' ? 'default' : 'outline'}
              onClick={() => setFilter('healthy')}
              size="sm"
            >
              <CheckCircle className="w-4 h-4 mr-1" />
              Здоровые ({scans.filter(s => s.is_healthy === 'healthy').length})
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Загрузка */}
      {loading && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p>Загрузка истории...</p>
          </CardContent>
        </Card>
      )}

      {/* Ошибка */}
      {error && (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchHistory}>
              Попробовать снова
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Пустая история */}
      {!loading && !error && filteredScans.length === 0 && (
        <Card>
          <CardContent className="p-8 text-center space-y-4">
            <HistoryIcon className="w-16 h-16 text-gray-400 mx-auto" />
            <h3 className="text-xl font-semibold text-gray-900">
              История пуста
            </h3>
            <p className="text-gray-600">
              {filter === 'all' 
                ? 'У вас пока нет сканирований. Сделайте первое сканирование!'
                : 'Нет сканирований, соответствующих выбранному фильтру'
              }
            </p>
            <Button onClick={() => window.location.href = '/scanner'}>
              Сделать сканирование
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Список сканов */}
      {!loading && !error && filteredScans.length > 0 && (
        <div className="grid gap-6">
          {filteredScans.map((scan) => (
            <Card key={scan.id} className="hover:shadow-lg transition-shadow">
              <CardContent className="p-6">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start space-x-4 flex-1">
                    {/* Изображение */}
                    {scan.image_path && (
                      <div className="flex-shrink-0">
                        <img
                          src={`http://localhost:8000/${scan.image_path}`}
                          alt="Scan"
                          className="w-20 h-20 object-cover rounded-lg"
                        />
                      </div>
                    )}
                    
                    {/* Информация */}
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        {getDiseaseIcon(scan.is_healthy)}
                        <h3 className="text-lg font-semibold text-gray-900">
                          {scan.disease_name || 'Неизвестно'}
                        </h3>
                      </div>
                      
                      <div className="flex items-center gap-4">
                        <span className={`text-sm font-medium ${getConfidenceColor(scan.confidence)}`}>
                          Уверенность: {Math.round(scan.confidence * 100)}%
                        </span>
                        <div className="flex items-center text-sm text-gray-500">
                          <Calendar className="w-4 h-4 mr-1" />
                          {formatDate(scan.created_at)}
                        </div>
                      </div>
                      
                      <p className="text-sm text-gray-600">
                        ID сканирования: #{scan.id}
                      </p>
                    </div>
                  </div>
                  
                  {/* Действия */}
                  <div className="flex-shrink-0">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => {
                        // Переход к деталям скана (пока просто показываем изображение)
                        window.open(`http://localhost:8000/${scan.image_path}`, '_blank')
                      }}
                    >
                      <Eye className="w-4 h-4 mr-1" />
                      Просмотр
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Статистика */}
      {!loading && !error && scans.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Статистика</h3>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {scans.length}
                </div>
                <div className="text-sm text-gray-600">Всего сканов</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {scans.filter(s => s.is_healthy === 'disease').length}
                </div>
                <div className="text-sm text-gray-600">С болезнями</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {scans.filter(s => s.is_healthy === 'healthy').length}
                </div>
                <div className="text-sm text-gray-600">Здоровых</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

