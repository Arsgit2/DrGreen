import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { ArrowLeft, Download, Share2, AlertTriangle, CheckCircle, Info, FileText } from 'lucide-react'
import { pdfService } from '../lib/pdfService'
import { useAuth } from '../contexts/AuthContext'

interface ScanResult {
  success: boolean
  scan_id: number
  disease: string
  confidence: number
  is_healthy: boolean
  description: string
  treatment: string
  symptoms: string
  all_probabilities: Record<string, number>
  image_path: string
  created_at: string
}

export function Results() {
  const [result, setResult] = useState<ScanResult | null>(null)
  const [isExporting, setIsExporting] = useState(false)
  const navigate = useNavigate()
  const { user } = useAuth()

  useEffect(() => {
    const savedResult = localStorage.getItem('scanResult')
    if (savedResult) {
      setResult(JSON.parse(savedResult))
    } else {
      navigate('/scanner')
    }
  }, [navigate])

  const handleExportPDF = async () => {
    if (!result || !user) return
    
    setIsExporting(true)
    try {
      const exportResult = await pdfService.generateReport(result, user.name)
      if (exportResult.success) {
        alert(`Отчет сохранен как ${exportResult.fileName}`)
      } else {
        alert(`Ошибка экспорта: ${exportResult.error}`)
      }
    } catch (error) {
      console.error('Ошибка экспорта PDF:', error)
      alert('Ошибка при экспорте отчета. Убедитесь, что библиотеки jspdf и html2canvas установлены.')
    } finally {
      setIsExporting(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getConfidenceLabel = (confidence: number) => {
    if (confidence >= 0.8) return 'Высокая'
    if (confidence >= 0.6) return 'Средняя'
    return 'Низкая'
  }

  const getDiseaseIcon = (isHealthy: boolean) => {
    if (isHealthy) {
      return <CheckCircle className="w-8 h-8 text-green-600" />
    }
    return <AlertTriangle className="w-8 h-8 text-red-600" />
  }

  const handleNewScan = () => {
    localStorage.removeItem('scanResult')
    navigate('/scanner')
  }

  const handleShare = async () => {
    if (navigator.share && result) {
      try {
        await navigator.share({
          title: 'Результат диагностики DrGreen AI',
          text: `Диагноз: ${result.disease} (уверенность: ${Math.round(result.confidence * 100)}%)`,
        })
      } catch (err) {
        console.log('Ошибка при попытке поделиться')
      }
    }
  }

  if (!result) {
    return (
      <div className="max-w-2xl mx-auto">
        <Card>
          <CardContent className="p-8 text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p>Загрузка результатов...</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Заголовок */}
      <div className="flex items-center justify-between">
        <Button
          variant="ghost"
          onClick={() => navigate('/scanner')}
          className="flex items-center"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          Назад к сканеру
        </Button>
        
        <div className="flex gap-2">
          <Button variant="outline" onClick={handleShare}>
            <Share2 className="w-4 h-4 mr-2" />
            Поделиться
          </Button>
          <Button 
            variant="outline" 
            onClick={handleExportPDF}
            disabled={isExporting}
            className="bg-green-50 hover:bg-green-100 border-green-200 text-green-700"
          >
            {isExporting ? (
              <>
                <div className="w-4 h-4 mr-2 animate-spin rounded-full border-2 border-green-600 border-t-transparent"></div>
                Экспорт...
              </>
            ) : (
              <>
                <FileText className="w-4 h-4 mr-2" />
                Экспорт PDF
              </>
            )}
          </Button>
        </div>
      </div>

      {/* Изображение */}
      {result.image_path && (
        <Card>
          <CardContent className="p-4">
            <img
              src={`http://localhost:8000/${result.image_path}`}
              alt="Сканированное изображение"
              className="w-full h-auto max-h-96 object-contain rounded-lg"
            />
          </CardContent>
        </Card>
      )}

      {/* Основной результат */}
      <Card className="overflow-hidden">
        <CardHeader className="bg-gradient-to-r from-green-50 to-blue-50">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              {getDiseaseIcon(result.is_healthy)}
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  {result.disease}
                </h1>
                <p className="text-gray-600">
                  Уверенность: <span className={getConfidenceColor(result.confidence)}>
                    {getConfidenceLabel(result.confidence)} ({Math.round(result.confidence * 100)}%)
                  </span>
                </p>
              </div>
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="p-6 space-y-6">
          {/* Описание */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center">
              <Info className="w-5 h-5 mr-2" />
              Описание
            </h3>
            <p className="text-gray-700 leading-relaxed">
              {result.description}
            </p>
          </div>

          {/* Симптомы */}
          {result.symptoms && !result.is_healthy && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2 text-orange-600" />
                Симптомы
              </h3>
              <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                <p className="text-orange-800 leading-relaxed">
                  {result.symptoms}
                </p>
              </div>
            </div>
          )}

          {/* Рекомендации по лечению */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center">
              <AlertTriangle className="w-5 h-5 mr-2" />
              Рекомендации по лечению
            </h3>
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-blue-800 leading-relaxed">
                {result.treatment}
              </p>
            </div>
          </div>

          {/* Все вероятности */}
          {result.all_probabilities && Object.keys(result.all_probabilities).length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Детальный анализ</h3>
              <div className="space-y-2">
                {Object.entries(result.all_probabilities)
                  .sort(([, a], [, b]) => b - a)
                  .map(([disease, prob]) => (
                    <div key={disease} className="flex items-center justify-between">
                      <span className="text-gray-700">{disease}</span>
                      <div className="flex items-center gap-3">
                        <div className="w-32 bg-gray-200 rounded-full h-2">
                          <div
                            className="bg-green-600 h-2 rounded-full"
                            style={{ width: `${Math.round(prob * 100)}%` }}
                          />
                        </div>
                        <span className="text-gray-600 text-sm font-mono w-12 text-right">
                          {Math.round(prob * 100)}%
                        </span>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Дополнительная информация */}
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900">ID сканирования</h4>
              <p className="text-gray-600 font-mono">#{result.scan_id}</p>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900">Время анализа</h4>
              <p className="text-gray-600">{new Date(result.created_at).toLocaleString('ru-RU')}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Дополнительные рекомендации */}
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Общие рекомендации</h3>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-6">
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900">Профилактика</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Регулярно осматривайте растения</li>
                <li>• Поддерживайте оптимальную влажность</li>
                <li>• Обеспечьте хорошую вентиляцию</li>
                <li>• Используйте качественные удобрения</li>
              </ul>
            </div>
            
            <div className="space-y-2">
              <h4 className="font-semibold text-gray-900">Мониторинг</h4>
              <ul className="text-sm text-gray-600 space-y-1">
                <li>• Проверяйте растения каждые 2-3 дня</li>
                <li>• Фотографируйте изменения</li>
                <li>• Ведите дневник ухода</li>
                <li>• Обращайтесь к специалистам при необходимости</li>
              </ul>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Действия */}
      <div className="flex flex-col sm:flex-row gap-4 justify-center">
        <Button onClick={handleNewScan} size="lg">
          Новое сканирование
        </Button>
        <Button 
          variant="outline" 
          onClick={() => navigate('/history')}
          size="lg"
        >
          История сканов
        </Button>
        <Button 
          variant="outline" 
          onClick={() => navigate('/diseases')}
          size="lg"
        >
          Справочник болезней
        </Button>
      </div>
    </div>
  )
}

