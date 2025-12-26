import { Link } from 'react-router-dom'
import { Card, CardContent } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Camera, Brain, BookOpen, History, ArrowRight, Leaf, Shield, Zap } from 'lucide-react'

export function Home() {
  const features = [
    {
      icon: Camera,
      title: 'Мгновенная диагностика',
      description: 'Сделайте фото листа и получите диагноз за секунды с помощью ИИ'
    },
    {
      icon: Brain,
      title: 'Точность 95%',
      description: 'Наша нейросеть обучена на тысячах изображений болезней растений'
    },
    {
      icon: BookOpen,
      title: 'Справочник болезней',
      description: 'Подробная информация о болезнях и методах лечения'
    },
    {
      icon: History,
      title: 'История сканов',
      description: 'Сохраняйте и отслеживайте все ваши диагностики'
    }
  ]

  const stats = [
    { label: 'Диагностированных растений', value: '10,000+' },
    { label: 'Точность диагностики', value: '95%' },
    { label: 'Поддерживаемых болезней', value: '50+' },
    { label: 'Довольных пользователей', value: '2,500+' }
  ]

  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="text-center space-y-8">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-6xl font-bold text-gray-900">
            Диагностика болезней растений
            <span className="block text-green-600">с помощью ИИ</span>
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            DrGreen AI использует передовые технологии машинного обучения для мгновенной диагностики болезней растений по фотографии листа
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/scanner">
            <Button size="lg" className="bg-green-600 hover:bg-green-700">
              <Camera className="w-5 h-5 mr-2" />
              Начать сканирование
            </Button>
          </Link>
          <Link to="/diseases">
            <Button variant="outline" size="lg">
              <BookOpen className="w-5 h-5 mr-2" />
              Справочник болезней
            </Button>
          </Link>
        </div>
      </section>

      {/* Stats */}
      <section className="grid grid-cols-2 md:grid-cols-4 gap-8">
        {stats.map((stat, index) => (
          <div key={index} className="text-center space-y-2">
            <div className="text-3xl font-bold text-green-600">{stat.value}</div>
            <div className="text-sm text-gray-600">{stat.label}</div>
          </div>
        ))}
      </section>

      {/* Features */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-gray-900">Возможности DrGreen AI</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Современные технологии для защиты ваших растений
          </p>
        </div>
        
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {features.map((feature, index) => {
            const Icon = feature.icon
            return (
              <Card key={index} className="hover:shadow-lg transition-shadow duration-300">
                <CardContent className="p-6 space-y-4">
                  <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
                    <Icon className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-gray-900">{feature.title}</h3>
                    <p className="text-sm text-gray-600">{feature.description}</p>
                  </div>
                </CardContent>
              </Card>
            )
          })}
        </div>
      </section>

      {/* How it works */}
      <section className="space-y-8">
        <div className="text-center space-y-4">
          <h2 className="text-3xl font-bold text-gray-900">Как это работает</h2>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Простой процесс диагностики в три шага
          </p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
              1
            </div>
            <h3 className="text-xl font-semibold">Сделайте фото</h3>
            <p className="text-gray-600">
              Сфотографируйте лист растения с помощью камеры или загрузите изображение
            </p>
          </div>
          
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
              2
            </div>
            <h3 className="text-xl font-semibold">ИИ анализирует</h3>
            <p className="text-gray-600">
              Наша нейросеть анализирует изображение и определяет возможные болезни
            </p>
          </div>
          
          <div className="text-center space-y-4">
            <div className="w-16 h-16 bg-green-600 text-white rounded-full flex items-center justify-center text-2xl font-bold mx-auto">
              3
            </div>
            <h3 className="text-xl font-semibold">Получите результат</h3>
            <p className="text-gray-600">
              Получите диагноз, рекомендации по лечению и профилактике
            </p>
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="bg-gradient-to-r from-green-600 to-green-700 rounded-2xl p-8 md:p-12 text-white text-center space-y-6">
        <div className="space-y-4">
          <h2 className="text-3xl md:text-4xl font-bold">
            Готовы защитить свои растения?
          </h2>
          <p className="text-xl opacity-90 max-w-2xl mx-auto">
            Присоединяйтесь к тысячам садоводов, которые уже используют DrGreen AI
          </p>
        </div>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/scanner">
            <Button size="lg" variant="secondary" className="bg-white text-green-600 hover:bg-gray-100">
              <Camera className="w-5 h-5 mr-2" />
              Начать диагностику
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>
    </div>
  )
}

