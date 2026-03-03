"""Модуль строителя для текста."""

import unicodedata


class TextBuilder:
    """Строитель для текста."""

    def __init__(self, text: str):
        """Создание конструктора."""
        self._text = text or ""

    def lower(self):
        """Приведение в нижний регистр."""
        self._text = self._text.lower()
        return self

    def strip(self):
        """Удаление непечатных символов."""
        self._text = self._text.strip()
        return self

    def replace_yo(self):
        """Замена ё на е."""
        self._text = self._text.replace("ё", "е")
        return self

    def remove_extra_spaces(self):
        """удаление лишних пробелов."""
        self._text = " ".join(self._text.split())
        return self

    def normalize(self):
        """Нормализация."""
        self._text = unicodedata.normalize('NFC', self._text)
        return self

    @property
    def text(self):
        """Получение обработанного текста."""
        return self._text
