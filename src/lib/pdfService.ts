// Сервис для генерации PDF отчетов
// Требует установки: npm install jspdf html2canvas

export interface ScanResult {
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

export class PDFService {
  private async loadLibraries() {
    // Динамический импорт библиотек
    const jsPDF = (await import('jspdf')).jsPDF
    const html2canvas = (await import('html2canvas')).default
    return { jsPDF, html2canvas }
  }

  async generateReport(result: ScanResult, userName: string) {
    try {
      const { jsPDF, html2canvas } = await this.loadLibraries()
      
      // Создаем новый PDF документ
      const pdf = new jsPDF('p', 'mm', 'a4')
      const pageWidth = pdf.internal.pageSize.getWidth()
      const pageHeight = pdf.internal.pageSize.getHeight()
      
      // Добавляем поддержку кириллицы
      await this.addCyrillicSupport(pdf)
      
      // Настройки цветов
      const primaryColor = '#16a34a' // green-600
      const secondaryColor = '#f0f9ff' // blue-50
      const textColor = '#374151' // gray-700
      
      // Заголовок
      pdf.setFillColor(primaryColor)
      pdf.rect(0, 0, pageWidth, 40, 'F')
      
      pdf.setTextColor(255, 255, 255)
      pdf.setFontSize(24)
      pdf.setFont('helvetica', 'bold')
      pdf.text('DrGreen AI', 20, 20)
      pdf.text('Diagnostic Report', 20, 30)
      
      // Информация о пользователе и дате
      pdf.setTextColor(textColor)
      pdf.setFontSize(10)
      pdf.setFont('helvetica', 'normal')
      pdf.text(`User: ${userName}`, pageWidth - 80, 15)
      pdf.text(`Date: ${new Date(result.created_at).toLocaleDateString('en-US')}`, pageWidth - 80, 25)
      
      let yPosition = 60
      
      // Загружаем изображение
      try {
        const img = await this.loadImage(result.image_path)
        const imgWidth = 80
        const imgHeight = (img.height * imgWidth) / img.width
        
        pdf.addImage(img, 'JPEG', 20, yPosition, imgWidth, imgHeight)
        
        // Информация рядом с изображением
        pdf.setFontSize(16)
        pdf.setFont('helvetica', 'bold')
        pdf.text('Diagnostic Result:', 110, yPosition + 10)
        
        pdf.setFontSize(12)
        pdf.setFont('helvetica', 'normal')
        
        // Статус здоровья
        const healthStatus = result.is_healthy ? 'Healthy Plant' : 'Disease Detected'
        const statusColor = result.is_healthy ? [34, 197, 94] : [239, 68, 68] // green-500 : red-500
        
        pdf.setTextColor(statusColor[0], statusColor[1], statusColor[2])
        pdf.text(healthStatus, 110, yPosition + 20)
        
        if (!result.is_healthy) {
          pdf.setTextColor(textColor)
          const diseaseName = this.transliterate(result.disease)
          pdf.text(`Disease: ${diseaseName}`, 110, yPosition + 30)
          pdf.text(`Confidence: ${(result.confidence * 100).toFixed(1)}%`, 110, yPosition + 40)
        }
        
        yPosition += Math.max(imgHeight, 50) + 20
      } catch (error) {
        console.warn('Изображение не загружено, продолжаем без него:', error)
        
        // Показываем информацию без изображения
        pdf.setFontSize(16)
        pdf.setFont('helvetica', 'bold')
        pdf.text('Diagnostic Result:', 20, yPosition + 10)
        
        pdf.setFontSize(12)
        pdf.setFont('helvetica', 'normal')
        
        const healthStatus = result.is_healthy ? 'Healthy Plant' : 'Disease Detected'
        const statusColor = result.is_healthy ? [34, 197, 94] : [239, 68, 68]
        
        pdf.setTextColor(statusColor[0], statusColor[1], statusColor[2])
        pdf.text(healthStatus, 20, yPosition + 20)
        
        if (!result.is_healthy) {
          pdf.setTextColor(textColor)
          const diseaseName = this.transliterate(result.disease)
          pdf.text(`Disease: ${diseaseName}`, 20, yPosition + 30)
          pdf.text(`Confidence: ${(result.confidence * 100).toFixed(1)}%`, 20, yPosition + 40)
        }
        
        yPosition += 50
      }
      
      // Описание болезни (если есть)
      if (!result.is_healthy && result.description) {
        pdf.setFillColor(secondaryColor)
        pdf.rect(20, yPosition, pageWidth - 40, 30, 'F')
        
        pdf.setTextColor(textColor)
        pdf.setFontSize(14)
        pdf.setFont('helvetica', 'bold')
        pdf.text('Disease Description:', 25, yPosition + 10)
        
        pdf.setFontSize(10)
        pdf.setFont('helvetica', 'normal')
        const description = this.wrapText(this.transliterate(result.description), pageWidth - 50)
        pdf.text(description, 25, yPosition + 20)
        
        yPosition += 40
      }
      
      // Симптомы
      if (!result.is_healthy && result.symptoms) {
        pdf.setTextColor(textColor)
        pdf.setFontSize(14)
        pdf.setFont('helvetica', 'bold')
        pdf.text('Symptoms:', 20, yPosition)
        
        pdf.setFontSize(10)
        pdf.setFont('helvetica', 'normal')
        const symptoms = this.wrapText(this.transliterate(result.symptoms), pageWidth - 40)
        pdf.text(symptoms, 20, yPosition + 10)
        
        yPosition += 25
      }
      
      // Лечение
      if (!result.is_healthy && result.treatment) {
        pdf.setTextColor(textColor)
        pdf.setFontSize(14)
        pdf.setFont('helvetica', 'bold')
        pdf.text('Treatment Recommendations:', 20, yPosition)
        
        pdf.setFontSize(10)
        pdf.setFont('helvetica', 'normal')
        const treatment = this.wrapText(this.transliterate(result.treatment), pageWidth - 40)
        pdf.text(treatment, 20, yPosition + 10)
        
        yPosition += 25
      }
      
      // Все вероятности (если есть место)
      if (result.all_probabilities && yPosition < pageHeight - 50) {
        pdf.setTextColor(textColor)
        pdf.setFontSize(14)
        pdf.setFont('helvetica', 'bold')
        pdf.text('All Classes Analysis:', 20, yPosition)
        
        pdf.setFontSize(9)
        pdf.setFont('helvetica', 'normal')
        
        const probabilities = Object.entries(result.all_probabilities)
          .sort(([,a], [,b]) => b - a)
          .slice(0, 5) // Показываем только топ-5
        
        probabilities.forEach(([disease, probability], index) => {
          const y = yPosition + 10 + (index * 8)
          if (y < pageHeight - 20) {
            const diseaseName = this.transliterate(disease)
            pdf.text(`${diseaseName}: ${(probability * 100).toFixed(1)}%`, 25, y)
          }
        })
        
        yPosition += 10 + (probabilities.length * 8)
      }
      
      // Футер
      pdf.setFillColor(primaryColor)
      pdf.rect(0, pageHeight - 20, pageWidth, 20, 'F')
      
      pdf.setTextColor(255, 255, 255)
      pdf.setFontSize(8)
      pdf.setFont('helvetica', 'normal')
      pdf.text('DrGreen AI - Plant Disease Diagnosis with AI', 20, pageHeight - 10)
      pdf.text('www.drgreen-ai.com', pageWidth - 50, pageHeight - 10)
      
      // Сохраняем PDF
      const fileName = `drgreen-report-${result.scan_id}-${new Date().toISOString().split('T')[0]}.pdf`
      pdf.save(fileName)
      
      return { success: true, fileName }
      
    } catch (error) {
      console.error('Ошибка генерации PDF:', error)
      return { success: false, error: error.message }
    }
  }
  
  private async loadImage(imagePath: string): Promise<HTMLImageElement> {
    return new Promise((resolve, reject) => {
      const img = new Image()
      img.crossOrigin = 'anonymous'
      img.onload = () => resolve(img)
      img.onerror = reject
      
      // Исправляем URL - изображения хранятся на backend
      const fullImageUrl = imagePath.startsWith('http') 
        ? imagePath 
        : `http://localhost:8000/${imagePath}`
      
      img.src = fullImageUrl
    })
  }
  
  private async addCyrillicSupport(pdf: any) {
    try {
      // Используем встроенный шрифт Times с лучшей поддержкой символов
      pdf.setFont('times')
      return pdf
    } catch (error) {
      console.warn('Не удалось установить шрифт:', error)
      return pdf
    }
  }
  
  private transliterate(text: string): string {
    if (!text) return text
    
    // Таблица транслитерации русских символов
    const translitMap: Record<string, string> = {
      'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
      'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
      'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
      'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
      'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
      'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
      'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
      'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
      'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
      'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }
    
    // Специальные замены для медицинских терминов
    const specialReplacements: Record<string, string> = {
      'Фитофтороз': 'Phytophthora',
      'Мучнистая роса': 'Powdery mildew',
      'Черная пятнистость': 'Black spot',
      'Антракноз': 'Anthracnose',
      'Ржавчина': 'Rust',
      'Септориоз': 'Septoria',
      'Фузариоз': 'Fusarium',
      'Вертициллез': 'Verticillium',
      'Бактериальный ожог': 'Bacterial blight',
      'Мозаика': 'Mosaic',
      'Курчавость листьев': 'Leaf curl',
      'Парша': 'Scab',
      'Серая гниль': 'Gray rot',
      'Корневая гниль': 'Root rot',
      'Белая пятнистость': 'White spot',
      'Альтернариоз': 'Alternaria',
      'Кила': 'Clubroot',
      'Фитофтороз картофеля': 'Potato blight',
      'Мучнистая роса огурцов': 'Cucumber powdery mildew',
      'Грибковое заболевание': 'Fungal disease',
      'Бактериальное заболевание': 'Bacterial disease',
      'Вирусное заболевание': 'Viral disease',
      'Обработка фунгицидами': 'Fungicide treatment',
      'Удаление пораженных частей': 'Remove affected parts',
      'Профилактические обработки': 'Preventive treatments',
      'Севооборот': 'Crop rotation',
      'Устойчивые сорта': 'Resistant varieties',
      'Правильный полив': 'Proper watering',
      'Улучшение вентиляции': 'Improve ventilation'
    }
    
    let result = text
    
    // Сначала применяем специальные замены
    for (const [russian, english] of Object.entries(specialReplacements)) {
      result = result.replace(new RegExp(russian, 'gi'), english)
    }
    
    // Затем транслитерируем оставшиеся русские символы
    result = result.split('').map(char => translitMap[char] || char).join('')
    
    return result
  }
  
  private wrapText(text: string, maxWidth: number): string[] {
    const words = text.split(' ')
    const lines: string[] = []
    let currentLine = ''
    
    for (const word of words) {
      const testLine = currentLine + (currentLine ? ' ' : '') + word
      // Примерная ширина текста (можно улучшить)
      const testWidth = testLine.length * 1.5
      
      if (testWidth > maxWidth && currentLine) {
        lines.push(currentLine)
        currentLine = word
      } else {
        currentLine = testLine
      }
    }
    
    if (currentLine) {
      lines.push(currentLine)
    }
    
    return lines
  }
}

// Экспортируем singleton
export const pdfService = new PDFService()
