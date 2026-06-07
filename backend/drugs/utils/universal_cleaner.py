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
        import threading
        print(f"THREAD={threading.get_ident()} START CLEAR")

        for model in self.model_classes:
            print(f"THREAD={threading.get_ident()} DELETE {model.__name__}")
            model.objects.all().delete()

        print(f"THREAD={threading.get_ident()} END CLEAR")
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

def universal_cleaner(model_classes, table_names=None):
    """Фабрика, возвращающая подходящий чистильщик для текущей БД.
    
    Args:
        model_classes: список классов моделей Django (опционально)
        table_names: список имен таблиц (опционально)
    
    Returns:
        Экземпляр очистителя для соответствующей БД
    """
    if model_classes and not table_names:
        table_names = [model._meta.db_table for model in model_classes]
    elif not table_names:
        raise ValueError("Необходимо передать model_classes или table_names")
    
    engine = connection.settings_dict['ENGINE']
    if 'sqlite3' in engine:
        return SQLiteCleaner(table_names, model_classes or [])
    elif 'postgresql' in engine:
        return PostgresCleaner(table_names, model_classes or [])
    else:
        raise NotImplementedError(f"Неизвестный движок БД: {engine}")