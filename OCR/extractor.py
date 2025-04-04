"""Модуль абстрактоного экстрактора."""

from abc import (ABC,
                 abstractmethod)


class Extractor(ABC):
    """Абстрактный экстрактор."""

    @classmethod
    @abstractmethod
    def extract(cls, inputs):
        """Метод извлечения."""
