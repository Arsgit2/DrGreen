import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Camera, Upload, X, Loader2 } from 'lucide-react'
import { api } from '../lib/api'
import { useAuth } from '../contexts/AuthContext'

export function Scanner() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [preview, setPreview] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [showCamera, setShowCamera] = useState(false)
  const navigate = useNavigate()
  const { user } = useAuth()

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedFile(file)
      setError(null)
      
      // Создаем превью
      const reader = new FileReader()
      reader.onload = (e) => {
        setPreview(e.target?.result as string)
      }
      reader.readAsDataURL(file)
    }
  }

  const startCamera = async () => {
    try {
      setError(null)
      
      // Простой запрос камеры
      console.log('🎥 Запрос доступа к камере...')
      const mediaStream = await navigator.mediaDevices.getUserMedia({ 
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      })
      
      console.log('✅ Поток камеры получен:', mediaStream.getVideoTracks())
      
      // Сразу устанавливаем состояние
      setStream(mediaStream)
      setShowCamera(true)
      
      // Ждем следующего рендера
      setTimeout(() => {
        if (videoRef.current) {
          console.log('📹 Устанавливаем поток в видео элемент')
          videoRef.current.srcObject = mediaStream
          
          // Пытаемся запустить сразу
          videoRef.current.play()
            .then(() => {
              console.log('✅ Видео успешно запущено!')
            })
            .catch(err => {
              console.error('❌ Ошибка запуска видео:', err)
              
              // Пробуем через обработчик метаданных
              videoRef.current!.onloadedmetadata = () => {
                console.log('✅ Метаданные загружены, пробуем запустить снова')
                videoRef.current!.play()
                  .then(() => console.log('✅ Видео запущено через onloadedmetadata'))
                  .catch(e => console.error('❌ Все равно не запускается:', e))
              }
            })
        } else {
          console.error('❌ videoRef.current не найден!')
        }
      }, 100)
      
    } catch (err: any) {
      console.error('❌ Ошибка доступа к камере:', err)
      setError(`Не удалось получить доступ к камере: ${err.message || 'Проверьте разрешения браузера'}`)
      setShowCamera(false)
      setStream(null)
    }
  }

  const stopCamera = () => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
      setShowCamera(false)
    }
  }

  const capturePhoto = () => {
    if (videoRef.current && canvasRef.current) {
      const canvas = canvasRef.current
      const video = videoRef.current
      const context = canvas.getContext('2d')
      
      if (context) {
        console.log('📸 Захват фото, размер видео:', video.videoWidth, 'x', video.videoHeight)
        
        canvas.width = video.videoWidth
        canvas.height = video.videoHeight
        
        // Рисуем видео на canvas
        context.drawImage(video, 0, 0, canvas.width, canvas.height)
        
        console.log('✅ Фото отрисовано на canvas')
        
        canvas.toBlob((blob) => {
          if (blob) {
            console.log('✅ Blob создан, размер:', (blob.size / 1024).toFixed(2), 'KB')
            const file = new File([blob], 'camera-capture.jpg', { type: 'image/jpeg' })
            setSelectedFile(file)
            setPreview(URL.createObjectURL(blob))
            stopCamera()
          }
        }, 'image/jpeg', 0.95)
      }
    }
  }

  const handleSubmit = async () => {
    if (!selectedFile || !user) {
      setError('Пожалуйста, выберите изображение и войдите в систему')
      return
    }

    setLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', selectedFile)

      const response = await api.post('/api/predict', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      })

      // Сохраняем результат в localStorage для страницы результатов
      localStorage.setItem('scanResult', JSON.stringify(response.data))
      navigate('/results')
    } catch (err) {
      setError('Ошибка при анализе изображения. Попробуйте еще раз.')
    } finally {
      setLoading(false)
    }
  }

  const clearSelection = () => {
    setSelectedFile(null)
    setPreview(null)
    setError(null)
    if (fileInputRef.current) {
      fileInputRef.current.value = ''
    }
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
              Для использования сканера необходимо войти в систему
            </p>
            <div className="flex gap-4 justify-center">
              <Button onClick={() => navigate('/login')}>
                Войти
              </Button>
              <Button variant="outline" onClick={() => navigate('/register')}>
                Регистрация
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      <div className="text-center space-y-4">
        <h1 className="text-3xl font-bold text-gray-900">Сканер болезней растений</h1>
        <p className="text-lg text-gray-600">
          Сделайте фото листа или загрузите изображение для диагностики
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Загрузка файла */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold flex items-center">
              <Upload className="w-5 h-5 mr-2" />
              Загрузить изображение
            </h2>
          </CardHeader>
          <CardContent className="space-y-4">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            <Button
              onClick={() => fileInputRef.current?.click()}
              variant="outline"
              className="w-full"
            >
              <Upload className="w-4 h-4 mr-2" />
              Выбрать файл
            </Button>
            
            {preview && (
              <div className="space-y-4">
                <div className="relative">
                  <img
                    src={preview}
                    alt="Preview"
                    className="w-full h-64 object-cover rounded-lg"
                  />
                  <button
                    onClick={clearSelection}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Камера */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold flex items-center">
              <Camera className="w-5 h-5 mr-2" />
              Сделать фото
            </h2>
          </CardHeader>
          <CardContent className="space-y-4">
            {!showCamera ? (
              <Button
                onClick={startCamera}
                className="w-full"
              >
                <Camera className="w-4 h-4 mr-2" />
                Открыть камеру
              </Button>
            ) : (
              <div className="space-y-4">
                <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ minHeight: '256px' }}>
                  <video
                    ref={videoRef}
                    autoPlay
                    playsInline
                    muted
                    className="w-full h-64 object-cover"
                    style={{ 
                      display: 'block',
                      backgroundColor: '#000'
                    }}
                  />
                  <canvas ref={canvasRef} className="hidden" />
                  <div className="absolute bottom-2 left-2 bg-green-500 text-white text-xs px-2 py-1 rounded flex items-center gap-1">
                    <span className="inline-block w-2 h-2 bg-white rounded-full animate-pulse"></span>
                    Камера активна
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <Button
                    onClick={capturePhoto}
                    className="flex-1 bg-green-600 hover:bg-green-700"
                  >
                    <Camera className="w-4 h-4 mr-2" />
                    Сделать фото
                  </Button>
                  <Button
                    onClick={stopCamera}
                    variant="outline"
                  >
                    Отмена
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Результат */}
      {selectedFile && (
        <Card>
          <CardContent className="p-6">
            <div className="space-y-4">
              <h3 className="text-lg font-semibold">Готово к анализу</h3>
              <p className="text-gray-600">
                Файл: {selectedFile.name} ({(selectedFile.size / 1024 / 1024).toFixed(2)} MB)
              </p>
              
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <p className="text-red-600">{error}</p>
                </div>
              )}
              
              <Button
                onClick={handleSubmit}
                disabled={loading}
                className="w-full"
                size="lg"
              >
                {loading ? (
                  <>
                    <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                    Анализируем лист...
                  </>
                ) : (
                  'Начать диагностику'
                )}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Инструкции */}
      <Card>
        <CardContent className="p-6">
          <h3 className="text-lg font-semibold mb-4">Рекомендации для лучшего результата</h3>
          <ul className="space-y-2 text-gray-600">
            <li>• Сделайте фото при хорошем освещении</li>
            <li>• Лист должен занимать большую часть кадра</li>
            <li>• Избегайте размытых или слишком темных изображений</li>
            <li>• Фотографируйте пораженные участки крупным планом</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

