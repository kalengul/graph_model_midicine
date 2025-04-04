"""Модуль абстрактного распознователя."""

from abc import (ABC,
                 abstractmethod)


class OCRConverter(ABC):
    """Абстрактный конвертер."""

    @abstractmethod
    def convert(self, path):
        'Метод преобразования сканов.'
