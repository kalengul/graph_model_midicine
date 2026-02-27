import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from django.conf import settings

logger = logging.getLogger('medical_history')

class DictionaryService:
    """Синглтон для управления словарем"""

    SYNONYM_DICT_DIR = Path(settings.SYNONYM_PATH)
    DEFAULT_SYNONYM_DICT_NAME = "dict_synonym_contraindications.json"
    
    _instance = None
    _dictionary: Dict[str, List[str]] = {}
    _dictionary_filename: Optional[str] = None
    _is_loaded = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def load_dictionary(self, dictionary_filename: Optional[str] = None) -> bool:
        """
        Загрузка словаря из JSON файла
        """
        try:
            # Если путь не указан, используем дефолтный из настроек
            if dictionary_filename is None:
                dictionary_filename = self.DEFAULT_SYNONYM_DICT_NAME
            
            path = self.SYNONYM_DICT_DIR / dictionary_filename
            if not path.exists():
                logger.error(f"Файл словаря не найден: {path}")
                return False
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict):
                logger.error(f"Неверный формат словаря: ожидается dict, получен {type(data)}")
                return False
            
            # Загружаем словарь
            self._dictionary = {}
            for key, value in data.items():
                if isinstance(value, list):
                    string_list = [str(item).strip() for item in value if item and str(item).strip()]
                    if string_list:
                        self._dictionary[key] = string_list
                else:
                    logger.warning(f"Пропускаем ключ {key}: значение не является списком")
            
            self._dictionary_filename = dictionary_filename
            self._is_loaded = True
            
            total_strings = sum(len(v) for v in self._dictionary.values())
            logger.info(f"Словарь загружен из {path}: {len(self._dictionary)} ключей, {total_strings} строк")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка загрузки словаря: {e}")
            return False
    
    def get_dictionary(self) -> Dict[str, List[str]]:
        """
        Получение словаря. Если не загружен - загружает по умолчанию.
        
        Returns:
            Dict[str, List[str]]: Словарь синонимов
        """
        if not self._is_loaded or not self._dictionary:
            logger.info("Словарь не загружен, загружаем по умолчанию")
            self.load_dictionary()
        
        return self._dictionary.copy()
    
    def get_all_strings(self) -> List[str]:
        """Получение всех строк из словаря в виде плоского списка"""
        all_strings = []
        for strings in self._dictionary.values():
            all_strings.extend(strings)
        return all_strings
    
    def update_dictionary(self, new_dictionary: Dict[str, List[str]]) -> bool:
        """Обновление словаря в памяти"""
        self._dictionary = new_dictionary
        self._is_loaded = True
        logger.info("Словарь обновлен в памяти")
        return True
    
    def save_to_file(self, filename) -> bool:
        """Сохранение словаря в файл"""
        try:
            save_path = self.SYNONYM_DICT_DIR / filename
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self._dictionary, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Словарь перезаписан в {save_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка сохранения словаря: {e}")
            return False
    
    @property
    def is_loaded(self) -> bool:
        return self._is_loaded
    
    @property
    def dictionary_filename(self) -> Optional[str]:
        return self._dictionary_filename

# Глобальный экземпляр
dictionary_service = DictionaryService()