"""Модуль сохранения в JSON-файл."""

import json

from saver import Saver


class JSONSaver(Saver):
    """Класс сохранения в json-файл."""

    def save(self, data, path):
        """Метод сохранения в json-файл."""
        with open(path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4, ensure_ascii=False)
