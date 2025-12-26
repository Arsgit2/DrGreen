import { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { BookOpen, Search, AlertTriangle, Shield, Lightbulb, Filter } from 'lucide-react'
import { api } from '../lib/api'

interface Disease {
  id: number
  name: string
  description: string
  treatment: string
  symptoms?: string
  prevention?: string
  image_url?: string
  created_at?: string
}

export function Diseases() {
  const [diseases, setDiseases] = useState<Disease[]>([])
  const [filteredDiseases, setFilteredDiseases] = useState<Disease[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedDisease, setSelectedDisease] = useState<Disease | null>(null)

  useEffect(() => {
    fetchDiseases()
  }, [])

  useEffect(() => {
    const filtered = diseases.filter(disease =>
      disease.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      disease.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
      disease.treatment.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredDiseases(filtered)
  }, [diseases, searchTerm])

  const fetchDiseases = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/diseases')
      setDiseases(response.data)
    } catch (err) {
      setError('Ошибка при загрузке справочника')
    } finally {
      setLoading(false)
    }
  }

  const getDiseaseIcon = (name: string) => {
    if (name === 'Здоровое растение') {
      return <Shield className="w-6 h-6 text-green-600" />
    }
    return <AlertTriangle className="w-6 h-6 text-red-600" />
  }

  const getDiseaseColor = (name: string) => {
    if (name === 'Здоровое растение') {
      return 'border-green-200 bg-green-50'
    }
    return 'border-red-200 bg-red-50'
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8">
      {/* Заголовок */}
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900 flex items-center justify-center">
          <BookOpen className="w-8 h-8 mr-3" />
          Справочник болезней растений
        </h1>
        <p className="text-lg text-gray-600">
          Подробная информация о болезнях и методах лечения
        </p>
      </div>

      {/* Поиск */}
      <Card>
        <CardContent className="p-6">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <Input
              placeholder="Поиск по названию, описанию или лечению..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
        </CardContent>
      </Card>

      {/* Загрузка */}
      {loading && (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p>Загрузка справочника...</p>
          </CardContent>
        </Card>
      )}

      {/* Ошибка */}
      {error && (
        <Card>
          <CardContent className="p-8 text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={fetchDiseases}>
              Попробовать снова
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Модальное окно с деталями */}
      {selectedDisease && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <Card className="max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <CardHeader className="flex items-center justify-between">
              <div className="flex items-center space-x-3">
                {getDiseaseIcon(selectedDisease.name)}
                <h2 className="text-xl font-semibold">{selectedDisease.name}</h2>
              </div>
              <Button
                variant="ghost"
                onClick={() => setSelectedDisease(null)}
              >
                ✕
              </Button>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <h3 className="font-semibold mb-2 flex items-center">
                  <BookOpen className="w-4 h-4 mr-2" />
                  Описание
                </h3>
                <p className="text-gray-700 leading-relaxed">
                  {selectedDisease.description}
                </p>
              </div>

              {selectedDisease.symptoms && (
                <div>
                  <h3 className="font-semibold mb-2 flex items-center">
                    <AlertTriangle className="w-4 h-4 mr-2 text-orange-600" />
                    Симптомы
                  </h3>
                  <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                    <p className="text-orange-800 leading-relaxed">
                      {selectedDisease.symptoms}
                    </p>
                  </div>
                </div>
              )}
              
              <div>
                <h3 className="font-semibold mb-2 flex items-center">
                  <Lightbulb className="w-4 h-4 mr-2" />
                  Лечение
                </h3>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  <p className="text-blue-800 leading-relaxed">
                    {selectedDisease.treatment}
                  </p>
                </div>
              </div>

              {selectedDisease.prevention && (
                <div>
                  <h3 className="font-semibold mb-2 flex items-center">
                    <Shield className="w-4 h-4 mr-2 text-green-600" />
                    Профилактика
                  </h3>
                  <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                    <p className="text-green-800 leading-relaxed">
                      {selectedDisease.prevention}
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      )}

      {/* Список болезней */}
      {!loading && !error && (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredDiseases.map((disease) => (
            <Card 
              key={disease.id} 
              className={`hover:shadow-lg transition-all duration-200 cursor-pointer ${getDiseaseColor(disease.name)}`}
              onClick={() => setSelectedDisease(disease)}
            >
              <CardContent className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    {getDiseaseIcon(disease.name)}
                    <h3 className="font-semibold text-gray-900">
                      {disease.name}
                    </h3>
                  </div>
                  
                  <p className="text-sm text-gray-600 line-clamp-3">
                    {disease.description}
                  </p>
                  
                  <div className="flex items-center text-sm text-blue-600">
                    <Lightbulb className="w-4 h-4 mr-1" />
                    Есть рекомендации по лечению
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Пустой результат поиска */}
      {!loading && !error && filteredDiseases.length === 0 && searchTerm && (
        <Card>
          <CardContent className="p-8 text-center space-y-4">
            <Search className="w-16 h-16 text-gray-400 mx-auto" />
            <h3 className="text-xl font-semibold text-gray-900">
              Ничего не найдено
            </h3>
            <p className="text-gray-600">
              Попробуйте изменить поисковый запрос
            </p>
            <Button onClick={() => setSearchTerm('')}>
              Очистить поиск
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Статистика */}
      {!loading && !error && diseases.length > 0 && (
        <Card>
          <CardHeader>
            <h3 className="text-lg font-semibold">Статистика справочника</h3>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center">
                <div className="text-2xl font-bold text-gray-900">
                  {diseases.length}
                </div>
                <div className="text-sm text-gray-600">Всего записей</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-red-600">
                  {diseases.filter(d => d.name !== 'Здоровое растение').length}
                </div>
                <div className="text-sm text-gray-600">Болезней</div>
              </div>
              
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">
                  {diseases.filter(d => d.name === 'Здоровое растение').length}
                </div>
                <div className="text-sm text-gray-600">Здоровых состояний</div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

