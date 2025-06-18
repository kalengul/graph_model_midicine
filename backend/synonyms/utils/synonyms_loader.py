"""Модуль абстрактного загрузчика синонимов."""

from abc import ABC, abstractmethod


class SynonymLoader(ABC):
    """Абструктный загрузчик синонимов."""

    @abstractmethod
    def import_synonyms(self, clusters_data):
        """Импорт синонимов."""

    @abstractmethod
    def export_synonyms(self):
        """Экспорт синонимов."""
