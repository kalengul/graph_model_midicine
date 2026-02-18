import os
import json
import logging
from django.conf import settings

logger = logging.getLogger('pHistory2se.storage')

# Конфигурация пути
DATA_FILE_NAME = 'dict_synonym_contraindications.json'
DATA_FILE_PATH = os.path.join(
    settings.BASE_DIR, 
    'data', 
    'dictionaries', 
    DATA_FILE_NAME
)

def get_json_storage_path():
    return DATA_FILE_PATH

def read_synonym_dict():
    """
    Безопасное чтение словаря синонимов.
    Возвращает dict. Если файла нет или он битый — пустой dict.
    """
    if not os.path.exists(DATA_FILE_PATH):
        logger.warning(f"Файл словаря не найден: {DATA_FILE_PATH}")
        return {}
    
    try:
        with open(DATA_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not isinstance(data, dict):
                logger.error("Файл словаря содержит не JSON объект. Возвращаем пустой словарь.")
                return {}
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Ошибка парсинга JSON словаря: {e}")
        return {}
    except Exception as e:
        logger.error(f"Критическая ошибка чтения словаря: {e}")
        return {}

def write_synonym_dict(data: dict) -> bool:
    """
    Полная перезапись файла словаря.
    Возвращает True при успехе, False при ошибке.
    """
    if not isinstance(data, dict):
        logger.error("Попытка записать в словарь не dict объект")
        return False

    try:
        os.makedirs(os.path.dirname(DATA_FILE_PATH), exist_ok=True)
        
        with open(DATA_FILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        
        logger.info(f"Словарь успешно сохранен: {len(data)} ключей")
        return True
    except Exception as e:
        logger.error(f"Ошибка записи словаря: {e}")
        return False