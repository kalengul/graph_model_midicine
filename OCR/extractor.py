"""Модуль абстрактоного экстрактора."""

from abc import (ABC,
                 abstractmethod)


class Extractor(ABC):
    """Абстрактный экстрактор."""

    @classmethod
    @abstractmethod
    def extract_to_dict(cls, inputs):
        """Метод извлечения в словарь."""

    @classmethod
    @abstractmethod
    def extract_to_list(cls, inputs):
        """Метод извлечения в список."""

    @classmethod
    @abstractmethod
    def extract(cls, inputs):
        """Метод извлечения."""
