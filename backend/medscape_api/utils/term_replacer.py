"""Модуль заместителя классов совместимости."""

import json
from pathlib import Path


class TermReplace:
    """Заменитель классов совместимости."""

    _MAPPING_FILE = 'term_mapping.json'
    _MAPPING_DIR = 'mappings'
    _DEFAULT_MAPPING_PATH  = (Path(__file__).resolve().parent.parent / 
                              _MAPPING_DIR / _MAPPING_FILE)

    def __init__(self, mapping_file_path=None):
        """Создание заменителя."""
        path = (Path(mapping_file_path) if mapping_file_path
                else self._DEFAULT_MAPPING_PATH)

        if not path.exists():
            raise FileNotFoundError('Файл для замещения классов совместимости'
                                    f' {path} не найден')

        with path.open('r', encoding='utf-8') as file:
            self.mapping = json.load(file)

    def replace(self, term):
        """Метод замещения."""
        return self.mapping.get(term, term)
