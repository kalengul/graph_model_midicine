# pHistory2se/views.py
import json
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

# Локальные импорты проекта
from .parsers import SimpleDocxParser
from .utils.extractors import SimpleMedicalExtractor
from .utils.normalize_contraindications import normalize_contraindications
from .model_loader import get_embedding_processor, get_synonym_dict, set_synonym_dict
from .utils.json_storage import read_synonym_dict, write_synonym_dict

# Импорты из другого приложения
from contraindications.models import Contraindication
from contraindications.serializers import ContraindicationListSerializer

logger = logging.getLogger('medical_history')

class MedicalHistoryToSideEffectsAPIView(APIView):
    """
    API для анализа медицинских .docx документов.
    Извлекает данные, нормализует противопоказания и сопоставляет их с БД.
    """
    SIMILARITY_THRESHOLD = 0.9 
    
    def post(self, request, *args, **kwargs):
        # 1. Валидация входного файла
        file_obj = request.FILES.get('file')
        if not file_obj:
            return self._error_response("Файл не прикреплён. Используйте поле 'file'.", 400)
        
        if not file_obj.name.lower().endswith('.docx'):
            return self._error_response("Поддерживаются только файлы .docx", 400)
        
        if file_obj.size > 10 * 1024 * 1024:
            return self._error_response("Файл слишком большой (> 10 МБ)", 413)
        
        try:
            # 2. Обработка документа
            file_obj.seek(0)
            text = SimpleDocxParser.extract_text(file_obj)
            extracted_data = SimpleMedicalExtractor.extract(text)
            
            # Извлекаем сырые названия противопоказаний
            raw_contraindications = SimpleMedicalExtractor.extract_contraindications(extracted_data)

            # 3. Нормализация через словарь синонимов и эмбеддинги
            processor = get_embedding_processor()
            synonym_dict = get_synonym_dict() # Читает из JSON файла
            
            normalized_names = normalize_contraindications(
                raw_contraindications,
                synonym_dict,
                processor,
                self.SIMILARITY_THRESHOLD
            )

            logger.info(f"Найдено противопоказаний из медкарты: {raw_contraindications}")
            logger.info(f"Нормализованы противопоказания: {normalized_names}")

            # 4. Маппинг в ID из базы данных
            # Оптимизация: используем values_list, если нужны только ID, но здесь нужен маппинг name->id
            db_data = ContraindicationListSerializer(
                                     Contraindication.objects.all(),
                                     many=True
                                    ).data
            logger.info(f"db_data: {db_data}")
            name2id = {item['cont_name']: item['cont_id'] for item in db_data}

            contraindications_id_list = []
            missing_contrs = []

            for name in normalized_names:
                contr_id = name2id.get(name)
                if contr_id:
                    contraindications_id_list.append(contr_id)
                else:
                    missing_contrs.append(name)

            if missing_contrs:
                logger.warning(f"Не найдены ID в БД для: {missing_contrs}")

            # 5. Формирование ответа
            response_data = {
                "age": extracted_data.get('age') if isinstance(extracted_data, dict) else None,
                "gender": extracted_data.get('gender') if isinstance(extracted_data, dict) else None,
                "cont_list": contraindications_id_list,
                # "missing_contrs": missing_contrs # Полезно добавить для отладки клиентом
            }

            return Response({
                "result": {"status": 200, "message": "Анализ успешно завершен"},
                "data": response_data
            }, status=status.HTTP_200_OK)
            
        except ValueError as e:
            logger.warning(f"Ошибка валидации данных документа: {e}")
            return self._error_response(str(e), 400)
        except Exception as e:
            logger.exception(f"Критическая ошибка обработки документа: {e}")
            return self._error_response(f"Ошибка обработки: {str(e)}", 500)
    
    def _error_response(self, message: str, status_code: int):
        """Хелпер для единого формата ошибок."""
        return Response({
            "result": {"status": status_code, "message": message},
            "data": {}
        }, status=status_code)
    

    def patch(self, request, *args, **kwargs):
        """
        Эндпоинт для изменения порога схожести (SIMILARITY_THRESHOLD).
        Метод: PATCH
        Body: { "threshold": 0.85 }
        """
        new_threshold = request.data.get('threshold')

        if new_threshold is None:
            return self._error_response("Поле 'threshold' обязательно.", 400)

        try:
            # Преобразуем в float
            new_threshold = float(new_threshold)
        except (TypeError, ValueError):
            return self._error_response("Значение 'threshold' должно быть числом (float).", 400)

        # Валидация диапазона (обычно от 0.0 до 1.0)
        if not (0.0 <= new_threshold <= 1.0):
            return self._error_response("Значение 'threshold' должно быть в диапазоне от 0.0 до 1.0.", 400)

        # Обновляем атрибут класса
        old_threshold = self.SIMILARITY_THRESHOLD
        self.SIMILARITY_THRESHOLD = new_threshold

        logger.info(f"Порог схожести изменен: {old_threshold} -> {new_threshold}")

        return Response({
            "result": {
                "status": 200,
                "message": f"Порог успешно обновлен"
            },
            "data": {
                "previous_threshold": old_threshold,
                "current_threshold": new_threshold
            }
        }, status=status.HTTP_200_OK)
    
class LoaderSynonymDictFileView(APIView):
    """
    Управление файлом словаря синонимов.
    GET: Чтение текущего состояния.
    POST: Полная перезапись файла новым JSON из загруженного файла.
    """

    def get(self, request, *args, **kwargs):
        data = read_synonym_dict()
        
        # Фильтрация по ключу
        search = request.query_params.get('search')
        if search:
            data = {
                k: v for k, v in data.items() 
                if search.lower() in k.lower()
            }

        return Response({
            "result": {"status": 200, "message": "Словарь загружен"},
            "data": data,
            "count": len(data)
        }, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({
                "result": {"status": 400, "message": "Файл не прикреплён. Используйте поле 'file'."},
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not file_obj.name.lower().endswith('.json'):
            return Response({
                "result": {"status": 400, "message": "Требуется файл с расширением .json"},
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            new_data = json.load(file_obj)
        except json.JSONDecodeError as e:
            return Response({
                "result": {"status": 400, "message": f"Невалидный JSON: {str(e)}"},
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception("Ошибка чтения файла")
            return Response({
                "result": {"status": 500, "message": f"Ошибка чтения: {str(e)}"},
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Валидация структуры
        if not isinstance(new_data, dict):
            return Response({
                "result": {"status": 400, "message": "JSON должен быть объектом (словарь)"},
                "data": {}
            }, status=status.HTTP_400_BAD_REQUEST)

        errors = []
        for key, value in new_data.items():
            if not isinstance(value, list):
                errors.append(f"Ключ '{key}': значение должно быть списком.")
            elif not all(isinstance(item, str) for item in value):
                errors.append(f"Ключ '{key}': список должен содержать только строки.")
        
        if errors:
            return Response({
                "result": {"status": 400, "message": "Ошибка структуры данных"},
                "data": {"errors": errors[:5]}
            }, status=status.HTTP_400_BAD_REQUEST)

        # Запись
        if write_synonym_dict(new_data):
            return Response({
                "result": {"status": 200, "message": "Словарь успешно обновлен"},
                "data": {"keys_count": len(new_data)}
            }, status=status.HTTP_200_OK)
            set_synonym_dict(new_data)
        else:
            return Response({
                "result": {"status": 500, "message": "Ошибка сохранения файла на сервере"},
                "data": {}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)