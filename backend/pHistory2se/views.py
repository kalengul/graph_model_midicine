# pHistory2se/views.py
import json
import logging
from pathlib import Path

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings

# Локальные импорты проекта
from .parsers import SimpleDocxParser
from .utils.extractors import SimpleMedicalExtractor
from .utils.normalize_contraindications import normalize_contraindications
# from .model_loader import get_embedding_processor, get_synonym_dict, set_synonym_dict
# from .utils.json_storage import read_synonym_dict, write_synonym_dict

# Синглтоны
from .utils.ModelService import model_service
from .utils.DictionaryService import dictionary_service

# Импорты из другого приложения
from contraindications.models import Contraindication
from contraindications.serializers import ContraindicationListSerializer


logger = logging.getLogger('medical_history')

class MedicalHistoryToSideEffectsAPIView(APIView):
    """
    API для анализа медицинских .docx документов.
    Извлекает данные, нормализует противопоказания и сопоставляет их с БД.
    """
    
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

            # Получаем словарь синонимов из dictionary_service
            synonym_dict = dictionary_service.get_dictionary()

            # Получаем процессор из model_service
            processor = model_service.get_processor()
            
            normalized_names = normalize_contraindications(
                raw_contraindications,
                synonym_dict,
                processor
            )

            logger.info(f"Найдено противопоказаний из медкарты: {raw_contraindications}")
            logger.info(f"Нормализованы противопоказания: {normalized_names}")

            # 4. Маппинг в ID из базы данных
            # Оптимизация: используем values_list, если нужны только ID, но здесь нужен маппинг name->id
            db_data = ContraindicationListSerializer(
                                     Contraindication.objects.all(),
                                     many=True
                                    ).data
            # logger.debug(f"db_data: {db_data}")
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

        

class ModelConfigView(APIView):
    """
    Эндпоинт для управления конфигурацией модели
    GET: возвращает информацию о текущей модели
    POST: обновляет конфигурацию и перезагружает модель
    """
    
    def get(self, request):
        """
        Получение информации о текущей модели
        """
        try:
            model_info = model_service.get_model_info()
            
            return Response({
                "result": {
                    "status": 200, "message": "Информация о модели успешно получена"
                },
                "data": model_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Ошибка при GET запросе: {e}")
            return Response({
                "result": {
                    "status": 500, "message": "Внутренняя ошибка сервера"
                },
                "data": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """
        Обновление конфигурации модели и перезагрузка
        Ожидает JSON с полями:
        {
            "model_name": "model_name",
            "threshold": 0.85,
            "cache_size": 1000,
        }
        """
        try:
            # Валидация входных данных
            validated_data, errors = self._validate_request_data(request.data)
            
            # Если есть ошибки валидации
            if errors:
                return Response({
                    "result": {
                        "status": 400, "message": "Ошибка валидации данных"
                    },
                    "data": {"errors": errors[:5]}  # Возвращаем первые 5 ошибок
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Обновляем конфигурацию и загружаем модель
            logger.info(f"Обновление конфигурации модели: {validated_data}")
            success = model_service.update_config(**validated_data)
            
            if success:
                return Response({
                    "result": {
                        "status": 200, "message": "Модель успешно обновлена и загружена"
                    },
                    "data": model_service.get_model_info()
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "result": {
                        "status": 500, "message": "Не удалось загрузить модель с новой конфигурацией"
                    },
                    "data": {
                        "current_state": model_service.get_model_info(),
                        "attempted_config": validated_data
                    }
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Ошибка при POST запросе: {e}")
            return Response({
                "result": {
                    "status": 500, "message": "Внутренняя ошибка сервера"
                },
                "data": {"error": str(e)}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _validate_request_data(self, data):
        """Валидация входных данных"""
        validated = {}
        errors = []
        
        # Проверяем, что данные вообще есть
        if not data:
            errors.append("Нет данных для обработки")
            return validated, errors
        
        # Проверяем model_name (обязательное поле при первой загрузке)
        if 'model_name' in data:
            if not isinstance(data['model_name'], str):
                errors.append("model_name должен быть строкой")
            elif not data['model_name'].strip():
                errors.append("model_name не может быть пустым")
            else:
                validated['model_name'] = data['model_name'].strip()
        elif not model_service.is_loaded:
            # Если модель не загружена и не передан model_name
            errors.append("model_name обязателен при первой загрузке модели")
        
        # Проверяем threshold (опционально)
        if 'threshold' in data:
            try:
                threshold = float(data['threshold'])
                if threshold < 0 or threshold > 1:
                    errors.append("threshold должен быть в диапазоне от 0 до 1")
                else:
                    validated['threshold'] = threshold
            except (TypeError, ValueError):
                errors.append("threshold должен быть числом")
        
        # Проверяем cache_size (опционально)
        if 'cache_size' in data:
            try:
                cache_size = int(data['cache_size'])
                if cache_size < 1:
                    errors.append("cache_size должен быть положительным числом")
                else:
                    validated['cache_size'] = cache_size
            except (TypeError, ValueError):
                errors.append("cache_size должен быть целым числом")
                
        return validated, errors
    

class DictionaryView(APIView):
    """
    Эндпоинт для работы с конкретным словарем
    GET: получить текущий словарь
    POST: загрузить словарь из файла (с возможностью сохранения)
    """
    
    def get(self, request):
        """Получение текущего загруженного словаря"""
        try:
            if not dictionary_service.is_loaded:
                dictionary_service.load_dictionary()
            
            dictionary = dictionary_service.get_dictionary()
            
            return Response({
                "result": {"status": 200, "message": "Словарь успешно получен"},
                "data": {
                    "current_file": str(dictionary_service.dictionary_filename) if dictionary_service.dictionary_filename else None,
                    "total_keys": len(dictionary),
                    "total_strings": sum(len(v) for v in dictionary.values()),
                    "is_loaded": dictionary_service.is_loaded,
                    "dictionary": dictionary
                }
            })
            
        except Exception as e:
            return Response({
                "result": {"status": 500, "message": "Ошибка при получении словаря"},
                "data": {"error": str(e)}
            }, status=500)
    
    def post(self, request):
        """
        Загрузка словаря из файла
        Параметры:
            - file: путь к файлу (обязательно)
            - save: имя файла - сохранить загружаемый словарь
        """
        try:
            file_path = request.data.get('file')
            if not file_path:
                return Response({
                    "result": {"status": 400, "message": "Не указан путь к файлу"},
                    "data": {}
                }, status=400)
            
            # Сохраняем загруженный, если указан параметр save
            save_filename = request.query_params.get('save')
            if save_filename and dictionary_service.is_loaded:
                
                # Формируем путь для сохранения
                save_path = Path(settings.SYNONYM_PATH) / save_filename
                
                # Сохраняем текущий словарь
                dictionary_service.save_to_file(save_path)
                logger.info(f"Текущий словарь сохранен как: {save_path}")
            
            # Загружаем новый словарь
            success = dictionary_service.load_dictionary(save_filename)
            
            if success:
                return Response({
                    "result": {"status": 200, "message": "Словарь успешно загружен"},
                    "data": {
                        "path": str(dictionary_service.dictionary_path),
                        "total_keys": len(dictionary_service.get_dictionary()),
                        "dictionary": dictionary_service.get_dictionary()
                    }
                })
            else:
                return Response({
                    "result": {"status": 400, "message": "Ошибка загрузки словаря"},
                    "data": {}
                }, status=400)
                
        except Exception as e:
            logger.error(f"Ошибка: {e}")
            return Response({
                "result": {"status": 500, "message": "Внутренняя ошибка"},
                "data": {"error": str(e)}
            }, status=500)



class DictionaryDirectoryView(APIView):
    """
    Эндпоинт для работы с директорией словарей
    GET: получить список всех доступных словарей в папке
    POST: загрузить словарь по имени из директории
    """
    
    def get(self, request):
        """Получение списка всех словарей в директории"""
        try:
            # from django.conf import settings
            # from pathlib import Path
            # import os
            from datetime import datetime
            
            synonym_path = Path(settings.SYNONYM_PATH)
            dictionaries = []

            print()
            
            if synonym_path.exists():
                for file_path in synonym_path.glob('*.json'):
                    # print("file_path:", file_path.name)
                    # print("dictionary_service.dictionary_filename:", dictionary_service.dictionary_filename)
                    # print("file_path.name == dictionary_service.dictionary_filename", file_path.name == dictionary_service.dictionary_filename)
                    stats = file_path.stat()
                    mod_time = datetime.fromtimestamp(stats.st_mtime)
                    
                    dictionaries.append({
                        "name": file_path.name,
                        "size_kb": round(stats.st_size / 1024, 2),
                        "modified": mod_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "is_current": dictionary_service.dictionary_filename == file_path.name
                                        if dictionary_service.dictionary_filename else False
                    })
            
            # Сортируем по имени
            dictionaries.sort(key=lambda x: x['name'])
            
            return Response({
                "result": {"status": 200, "message": "Список словарей получен"},
                "data": {
                    "total_files": len(dictionaries),
                    "dictionaries": dictionaries,
                    "current_loaded": str(dictionary_service.dictionary_filename)
                                            if dictionary_service.dictionary_filename else None
                }
            })
            
        except Exception as e:
            return Response({
                "result": {"status": 500, "message": str(e)},
                "data": {}
            }, status=500)
    
    def post(self, request):
        """
        Загрузка словаря по имени из директории
        Параметры:
            - name: имя файла словаря (например: "dict_synonym_contraindications.json")
        """
        try:
            name = request.data.get('name')
            if not name:
                return Response({
                    "result": {"status": 400, "message": "Не указано имя файла"},
                    "data": {}
                }, status=400)
            
            file_path = Path(settings.SYNONYM_PATH) / name
            
            if not file_path.exists():
                return Response({
                    "result": {"status": 404, "message": f"Файл {name} не найден"},
                    "data": {}
                }, status=404)
            
            # Загружаем словарь
            success = dictionary_service.load_dictionary(str(file_path))
            
            if success:
                return Response({
                    "result": {"status": 200, "message": f"Словарь {name} загружен"},
                    "data": {
                        "name": name,
                        "total_keys": len(dictionary_service.get_dictionary())
                    }
                })
            else:
                return Response({
                    "result": {"status": 400, "message": "Ошибка загрузки словаря"},
                    "data": {}
                }, status=400)
                
        except Exception as e:
            return Response({
                "result": {"status": 500, "message": str(e)},
                "data": {}
            }, status=500)