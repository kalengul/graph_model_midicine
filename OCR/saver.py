"""Модуль абструктного сохранения."""

from abc import (ABC,
                 abstractmethod)


class Saver(ABC):
    """Абстрактный класс сохранения."""

    def save(self, data, path):
        """Метод сохранения данных в файл."""
