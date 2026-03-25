import logging
from typing import Optional, Any, Dict, List
from dataclasses import dataclass, asdict
from pathlib import Path
import json

from django.conf import settings

from stm_service.utils.SemanticEmbeddingProcessor import SemanticEmbeddingProcessor

logger = logging.getLogger('medical_history')

@dataclass
class ModelConfig:
    """Конфигурация модели"""
    model_name: str
    threshold: float = 0.85
    cache_size: int = 1000

class ModelService:
    """Сервис для управления Sentence Transformer модели с хранением состояния в полях"""

    ST_MODEL_DIR = Path(settings.ST_MODEL_PATH)
    DEFAULT_ST_MODEL_NAME = 'all-MiniLM-L6-v2'
    DEFAULT_THRESHOLD = 0.9
    DEFAULT_CACHE_SIZE = 1000
    
    def __init__(self):
        self._processor: Optional[Any] = None
        self._config: Optional[ModelConfig] = None
        self._is_loaded: bool = False
    
    @property
    def config(self) -> Optional[ModelConfig]:
        """Текущая конфигурация модели"""
        return self._config
    
    @property
    def is_loaded(self) -> bool:
        """Флаг загрузки модели"""
        return self._is_loaded
    
    def get_model_info(self) -> Dict:
        """Получение информации о текущей модели"""
        if not self._config:
            return {
                "status": "not_loaded",
                "message": "Модель не загружена"
            }
        
        return {
            "is_loaded": self._is_loaded,
            "config": asdict(self._config) if self._config else None
        }
    
    def get_processor(self) -> SemanticEmbeddingProcessor:
        """
        Получение процессора эмбеддингов с автоматической загрузкой
        
        Returns:
            SemanticEmbeddingProcessor
            
        Raises:
            RuntimeError: если не удалось загрузить модель
            ValueError: если путь к модели не существует
        """
        # Проверяем, загружена ли модель
        if self._is_loaded and self._processor:
            return self._processor
        
        # Логируем попытку загрузки
        logger.info("Модель не загружена, загружаем с настройками по умолчанию")
        
        # Создаем конфигурацию
        config = ModelConfig(
            model_name=self.DEFAULT_ST_MODEL_NAME, 
            threshold=self.DEFAULT_THRESHOLD,
            cache_size=self.DEFAULT_CACHE_SIZE,
        )
        
        # Загружаем модель
        success = self.load_model(config)
        if not success:
            error_msg = "Не удалось загрузить модель по умолчанию"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
        
        return self._processor
    
    def load_model(self, config: ModelConfig, dictionary_path = None) -> bool:
        """
        Загрузка модели и прогрев кэша
        
        Args:
            config: Конфигурация модели
            
        Returns:
            bool: Успешность загрузки
        """
        try:
            logger.info(f"Загрузка модели: {config.model_name}")
            
            # Логика загрузки модели
            model_path = str(self.ST_MODEL_DIR / config.model_name)
            logger.debug(f"model_path: {model_path}")
            self._processor = SemanticEmbeddingProcessor(
                                                    model_path = model_path,
                                                    # model_path = r'D:\Work\polypharmacy-nikita\train_synonim_model\data\synonym-model_4',
                                                    cache_size = config.cache_size,
                                                    threshold = config.threshold
                                                    )
            
            self._config = config
            self._is_loaded = True
                        
            # Прогрев кэша
            if dictionary_path:
                self._warmup_cache_from_dictionary(dictionary_path)
            
            logger.info(f"Модель '{config.model_name}' успешно загружена")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки модели: {e}")
            self._is_loaded = False
            return False
    
    def _warmup_cache_from_dictionary(self, dictionary_path):
        """Прогрев кэша из JSON словаря"""
        if not self._processor or not self._config:
            logger.warning("Невозможно прогреть кэш: модель не загружена")
            return
        
        # Определяем путь к словарю
        # dictionary_path = self.DEFAULT_DICTIONARY_PATH
        
        try:
            # Загружаем словарь из JSON
            strings_list = self._load_dictionary(dictionary_path)
            
            if not strings_list:
                logger.warning(f"Список строк {dictionary_path} пуст или не загружен")
                return
            
            logger.info(f"Начало прогрева кэша из словаря: {dictionary_path}")

            max_to_warm = min(self._config.cache_size, 1000)  # Ограничение
            self._processor.get_embeddings_batch(strings_list[:max_to_warm])                                    
            logger.info(f"Прогрев завершен. Прогрето {max_to_warm} элементов")
            
        except Exception as e:
            logger.error(f"Ошибка при прогреве кэша из словаря: {e}")


    def _load_dictionary(self, synonym_dict: str) -> List[str]:
        """
        Загрузка словаря из JSON файла
        
        Args:
            dictionary_path: Путь к JSON файлу
            
        Returns:
            Dict[str, List[str]]: Словарь в формате {ключ: [список строк]}
        """
        try:
            data = synonym_dict
            
            # Проверяем структуру данных
            if not isinstance(data, dict):
                logger.error(f"Неверный формат словаря: ожидается dict, получен {type(data)}")
                return []
            
            # Фильтруем только валидные записи
            all_strings  = []
            for key, value in data.items():
                if isinstance(value, list):
                    # Преобразуем все элементы в строки и фильтруем пустые
                    string_list = [str(item).strip() for item in value if item and str(item).strip()]
                    all_strings.extend(string_list)
                    logger.info(f"Ключ '{key}': добавлено {len(string_list)} строк")
                else:
                    logger.warning(f"Пропускаем ключ {key}: значение не является списком")
            
            logger.info(f"Загружен список: {len(all_strings)} элементов")
            return all_strings 
            
        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON: {e}")
            return []
        except Exception as e:
            logger.error(f"Ошибка загрузки словаря: {e}")
            return []
    
    def update_config(self, **kwargs) -> bool:
        """
        Обновление конфигурации и перезагрузка модели
        
        Args:
            **kwargs: Поля для обновления (model_name, threshold, cache_size)
            
        Returns:
            bool: Успешность обновления
        """
        if not self._config:
            new_config = ModelConfig(
                model_name=kwargs.get('model_name', self.DEFAULT_MODEL),
                threshold=kwargs.get('threshold', self.DEFAULT_THRESHOLD),
                cache_size=kwargs.get('cache_size', self.DEFAULT_CACHE_SIZE),
            )
        else:
            current_dict = asdict(self._config)
            current_dict.update(kwargs)
            new_config = ModelConfig(**current_dict)
        
        # Проверяем, изменилась ли конфигурация
        if self._config and asdict(self._config) == asdict(new_config):
            logger.info("Конфигурация не изменилась")
            return True
        
        # Перезагружаем модель с новой конфигурацией
        return self.load_model(new_config)

# Создаем глобальный экземпляр сервиса
model_service = ModelService()