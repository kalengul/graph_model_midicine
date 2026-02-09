from django.shortcuts import render

# Create your views here.
import docx
import json
from rest_framework.views import APIView
from rest_framework import status
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from django.conf import settings


# КЛЮЧЕВЫЕ СЛОВА — МЕНЯТЬ ТОЛЬКО ЗДЕСЬ
TARGET_KEYWORDS = ["анализ", "диагноз", "рекомендация", "прогноз", "лечение"]


@method_decorator(csrf_exempt, name='dispatch')
class MedicalHistoryToSideEffectsAPIView(APIView):
    """
    API для анализа медицинских документов (.docx, в будущем .pdf)
    Публичный эндпоинт без авторизации
    """
    
    def post(self, request, *args, **kwargs):
        # Валидация наличия файла
        if 'file' not in request.FILES:
            return HttpResponse(
                '{"error": "Файл не прикреплён. Используйте поле \'file\'."}',
                content_type='application/json',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        file_obj = request.FILES['file']
        filename = file_obj.name.lower()
        
        # Проверка расширения файла
        if not (filename.endswith('.docx')):
            return HttpResponse(
                '{"error": "Поддерживаются только файлы .docx"}',
                content_type='application/json',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Проверка размера (10 МБ)
        if file_obj.size > 10 * 1024 * 1024:
            return HttpResponse(
                '{"error": "Файл слишком большой (> 10 МБ)"}',
                content_type='application/json',
                status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
            )
        
        # Обработка DOCX файла
        if filename.endswith('.docx'):
            return self._process_docx(file_obj)
        
        # На будущее: обработка PDF
        # elif filename.endswith('.pdf'):
        #     return self._process_pdf(file_obj)
        
        # Должен быть недостижим, но на всякий случай
        return HttpResponse(
            '{"error": "Неподдерживаемый формат файла"}',
            content_type='application/json',
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def _process_docx(self, file_obj):
        """Обработка DOCX файлов"""
        try:
            # Чтение DOCX из памяти
            doc = docx.Document(file_obj)
            
            # Извлекаем весь текст
            full_text = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    full_text.append(paragraph.text)
            
            text = " ".join(full_text).lower()
            
        except Exception as e:
            return HttpResponse(
                f'{{"error": "Ошибка чтения DOCX файла: {str(e)}"}}',
                content_type='application/json',
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Поиск ключевых слов
        results = []
        for keyword in TARGET_KEYWORDS:
            keyword_lower = keyword.lower()
            count = text.count(keyword_lower)
            if count > 0:
                results.append({
                    "keyword": keyword,
                    "count": count,
                    "positions": self._find_keyword_positions(text, keyword_lower)
                })
        
        # Формирование ответа
        response_data = {
            "status": "success",
            "filename": file_obj.name,
            "file_type": "docx",
            "keywords_found": results,
            "total_matches": sum(r["count"] for r in results),
            "keywords_searched": TARGET_KEYWORDS,
            "text_length": len(text),
            "note": "PDF support will be added in future updates"
        }
        response_data_moc= {
            "filename": file_obj.name,
            "contraindications": [ "Гипертоническая болезнь III стадии с поражением сердца",
                                  "Хроническая сердечная недостаточность I стадии, II функциональный класс (NYHA), с сохранённой фракцией выброса",
                                  "Фибрилляция предсердий, персистирующая форма, тахисистолический вариант (впервые выявлен-ная)"
            ]
        }
        
        return HttpResponse(
            json.dumps(response_data_moc, ensure_ascii=False, indent=2),
            content_type='application/json',
            status=status.HTTP_200_OK
        )
    
    def _find_keyword_positions(self, text, keyword):
        """Найти позиции ключевых слов в тексте (базовая реализация)"""
        positions = []
        start = 0
        while True:
            index = text.find(keyword, start)
            if index == -1:
                break
            positions.append(index)
            start = index + 1
        return positions[:10]  # Ограничиваем для JSON
    
    # На будущее: метод для PDF
    # def _process_pdf(self, file_obj):
    #     """Обработка PDF файлов (заглушка для будущей реализации)"""
    #     return HttpResponse(
    #         '{"error": "PDF support is under development"}',
    #         content_type='application/json',
    #         status=status.HTTP_501_NOT_IMPLEMENTED
    #     )