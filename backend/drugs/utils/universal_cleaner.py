from abc import ABC, abstractmethod
from django.db import connection

class BaseCleaner(ABC):
    """Абстрактный очиститель таблиц."""
    @abstractmethod
    def clear_table(self):
        """Очистка таблиц."""
        pass


class SQLiteCleaner(BaseCleaner):
    """Очиститель для SQLite (принимает списки таблиц и моделей)."""
    def __init__(self, table_names, model_classes):
        self.table_names = table_names
        self.model_classes = model_classes

    def clear_table(self):
        for model in self.model_classes:
            model.objects.all().delete()
        with connection.cursor() as cursor:
            for table in self.table_names:
                cursor.execute("DELETE FROM sqlite_sequence WHERE name = %s", [table])


class PostgresCleaner(BaseCleaner):
    """Очиститель для PostgreSQL (принимает списки таблиц и моделей)."""
    def __init__(self, table_names, model_classes):
        self.table_names = table_names
        self.model_classes = model_classes

    def clear_table(self):
        with connection.cursor() as cursor:
            quoted_tables = [f'"{table}"' for table in self.table_names]
            cursor.execute(f"TRUNCATE TABLE {', '.join(quoted_tables)} RESTART IDENTITY CASCADE;")


def universal_cleaner(table_names, model_classes):
    """Фабрика, возвращающая подходящий чистильщик для текущей БД."""
    engine = connection.settings_dict['ENGINE']
    if 'sqlite3' in engine:
        return SQLiteCleaner(table_names, model_classes)
    elif 'postgresql' in engine:
        return PostgresCleaner(table_names, model_classes)
    else:
        raise NotImplementedError(f"Неизвестный движок БД: {engine}")
