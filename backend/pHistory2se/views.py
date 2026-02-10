from django.shortcuts import render

# Create your views here.
# pHistory2se/views.py
import json
from rest_framework.views import APIView
from rest_framework import status
from django.http import HttpResponse

from .parsers import SimpleDocxParser
from .extractors import SimpleMedicalExtractor


class MedicalHistoryToSideEffectsAPIView(APIView):
    """
    API для анализа медицинских .docx документов
    Публичный эндпоинт без авторизации
    """
    
    def post(self, request, *args, **kwargs):
        # Проверка наличия файла
        if 'file' not in request.FILES:
            return self._error_response("Файл не прикреплён. Используйте поле 'file'.", 400)
        
        file_obj = request.FILES['file']
        
        # Проверка расширения
        if not file_obj.name.lower().endswith('.docx'):
            return self._error_response("Поддерживаются только файлы .docx", 400)
        
        # Проверка размера (10 МБ)
        if file_obj.size > 10 * 1024 * 1024:
            return self._error_response("Файл слишком большой (> 10 МБ)", 413)
        
        try:
            # Сбрасываем позицию файла перед чтением
            file_obj.seek(0)
            
            # Извлекаем текст
            text = SimpleDocxParser.extract_text(file_obj)
            
            # Извлекаем структурированные данные
            data = SimpleMedicalExtractor.extract(text)
            
            # Формируем ответ
            response = {
                "status": "success",
                "filename": file_obj.name,
                "contraindications": data,
                "total_contraindications": len(data)
            }
            
            return HttpResponse(
                json.dumps(response, ensure_ascii=False, indent=2),
                content_type='application/json',
                status=status.HTTP_200_OK
            )
            
        except ValueError as e:
            return self._error_response(str(e), 400)
        except Exception as e:
            # Логируем ошибку (можно добавить логирование в прод)
            return self._error_response(f"Ошибка обработки: {str(e)}", 500)
    
    def _error_response(self, message: str, status_code: int):
        """Создание ответа с ошибкой."""
        return HttpResponse(
            json.dumps({"error": message}, ensure_ascii=False),
            content_type='application/json',
            status=status_code
        )