"""Модуль манипулятора таблицей графов в БД."""

class GraphManipulator:
    """Манипулятор графом."""

    def __init__(self, cleaner, loader):
        """Конструктор."""
        self.cleaner = cleaner
        self.loader = loader

    def perform(self, count=None):
        """Выполнение."""
        self.cleaner.clean()
        self.loader.load(count=count)
