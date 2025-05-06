"""Модуль загрузчика из файлов."""

import os
import logging

from django.db import connection

from ranker.models import DrugCHF, DiseaseCHF


logger = logging.getLogger('ranker')


class FileLoader:
    """Загрузчик из файлов."""

    _TABLE_NAMES = ['ranker_drugchf', 'ranker_diseasechf']
    _MODEL_CLASSES = [DrugCHF, DiseaseCHF]

    @classmethod
    def reset_tables(cls):
        """Удаляет все записи и сбрасывает автоинкремент."""
        with connection.cursor() as cursor:
            if connection.vendor == 'postgresql':
                logger.debug('Выбран PostgreSql')
                cursor.execute(f"""
                    TRUNCATE TABLE {', '.join(cls._TABLE_NAMES)}
                    RESTART IDENTITY CASCADE;
                """)
            if connection.vendor == 'sqlite':
                logger.debug('Выбран SQLite')
                for model in cls._MODEL_CLASSES:
                    model.objects.all().delete()
                with connection.cursor() as cursor:
                    for table in cls._TABLE_NAMES:
                        cursor.execute(
                            "DELETE FROM sqlite_sequence WHERE name=%s",
                            [table])
            else:
                raise NotImplementedError(
                    f'Выбранный тип СУБД не поддерживается: {connection.vendor}')

    @staticmethod
    def load_disease_chf_from_file(base_dir):
        """Метод загрузки ПД из файла в БД."""
        file_path = os.path.join(base_dir, 'txt_files_db', 'side_effects.txt')
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(';')
                if len(parts) == 2:
                    index_name = parts[0].strip().split(maxsplit=1)
                    if len(index_name) == 2:
                        index = int(index_name[0])
                        name = index_name[1].strip()
                        value = float(parts[1].replace(',', '.'))
                        DiseaseCHF.objects.update_or_create(
                            index=index,
                            defaults={'name': name, 'value': value})

    @staticmethod
    def load_drugs_from_file(base_dir):
        """Метод загрузки ЛС из файла в БД."""
        file_path = os.path.join(base_dir, 'txt_files_db', 'drugs_xcn.txt')
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            for line in file:
                parts = line.strip().split(maxsplit=1)
                if len(parts) == 2:
                    index = int(parts[0])
                    value = parts[1].strip()
                    DrugCHF.objects.update_or_create(index=index,
                                                     defaults={'name': value})
                    while len(data) <= index:
                        data.append(None)
                    data[index] = value
        return data

    @classmethod
    def load_all(cls, base_dir):
        """Метод для выполения всех действий."""
        cls.reset_tables()
        cls.load_disease_chf_from_file(base_dir)
        cls.load_drugs_from_file(base_dir)
