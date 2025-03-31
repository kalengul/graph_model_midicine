import os
import json
import re
import sqlite3
from CustomPymorphy.CustomPymorphy import EnhancedMorphAnalyzer
from normalize_text import normalize_text

class DatabaseManager:
    """
    Класс для управления базой данных SQLite, создания таблиц и загрузки данных.
    """
    def __init__(self, db_name="orlov_side_effects_dataset.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()
        self._insert_frequency_ranges()

    def _create_tables(self):
        """Создает таблицы в базе данных."""
        
        # Таблица лекарств
        self.cursor.execute("DROP TABLE IF EXISTS drugs")
        self.cursor.execute('''
            CREATE TABLE drugs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                drug TEXT UNIQUE NOT NULL
            )
        ''')

        # Таблица побочных эффектов
        self.cursor.execute("DROP TABLE IF EXISTS side_effects")
        self.cursor.execute('''
            CREATE TABLE side_effects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                effect TEXT UNIQUE NOT NULL
            )
        ''')

        # Таблица связи ЛС и побочных эффектов
        self.cursor.execute("DROP TABLE IF EXISTS drug_side_effects")
        self.cursor.execute('''
            CREATE TABLE drug_side_effects (
                drug_id INTEGER NOT NULL,
                side_effect_id INTEGER NOT NULL,
                frequency TEXT NOT NULL,
                PRIMARY KEY (drug_id, side_effect_id),
                FOREIGN KEY (drug_id) REFERENCES drugs(id) ON DELETE CASCADE,
                FOREIGN KEY (side_effect_id) REFERENCES side_effects(id) ON DELETE CASCADE
            )
        ''')
        # Таблица частот
        self.cursor.execute("DROP TABLE IF EXISTS frequency_ranges")
        self.cursor.execute('''
            CREATE TABLE frequency_ranges (
                category TEXT PRIMARY KEY,
                min_probability REAL,
                max_probability REAL
            )
        ''')

        # self.conn.commit()

    def _insert_frequency_ranges(self):
        """Заполняет таблицу диапазонов частот значениями по умолчанию."""
        frequency_data = [
            ("Очень часто", 0.1, 1),
            ("Часто", 0.01, 0.1),
            ("Нечасто", 0.001, 0.01),
            ("Редко", 0.0001, 0.001),
            ("Очень редко", 0.0, 0.0001),
            ("Частота неизвестна", None, None),
            ("Данные о частоте, собранные после продажи", None, None)
        ]
        self.cursor.executemany(
            "INSERT INTO frequency_ranges (category, min_probability, max_probability) VALUES (?, ?, ?)",
            frequency_data
        )
        self.conn.commit()

    def insert_drug(self, drug_name):
        """Добавляет лекарство в базу или получает его ID."""
        self.cursor.execute("INSERT INTO drugs (drug) VALUES (?) ON CONFLICT(drug) DO NOTHING", (drug_name,))
        self.cursor.execute("SELECT id FROM drugs WHERE drug = ?", (drug_name,))
        return self.cursor.fetchone()[0]

    def insert_side_effect(self, effect):
        """Добавляет побочный эффект в базу или получает его ID."""
        self.cursor.execute("INSERT INTO side_effects (effect) VALUES (?) ON CONFLICT(effect) DO NOTHING", (effect,))
        self.cursor.execute("SELECT id FROM side_effects WHERE effect = ?", (effect,))
        return self.cursor.fetchone()[0]

    def insert_drug_side_effect(self, drug_id, side_effect_id, frequency):
        """Создает связь между лекарством и побочным эффектом."""
        self.cursor.execute(
            "INSERT INTO drug_side_effects (drug_id, side_effect_id, frequency) VALUES (?, ?, ?) ON CONFLICT DO NOTHING",
            (drug_id, side_effect_id, frequency)
        )

    def commit_and_close(self):
        """Сохраняет изменения и закрывает соединение с базой данных."""
        self.conn.commit()
        self.conn.close()


class DataProcessor:
    """
    Класс для обработки JSON-файлов и их загрузки в базу данных.
    """
    def __init__(self, folder_path, db_manager):
        self.folder_path = folder_path
        self.db_manager = db_manager
        self.morph_analyzer = EnhancedMorphAnalyzer()
        self.side_effects_set = set()
        self.drugs_set = set()

    def _lemmatize_text(self, text):
        """Лемматизирует текст с использованием морфологического анализатора."""
        words = re.findall(r'\w+|[^\w\s]', text)
        lemmatized = [self.morph_analyzer.parse(word)[0].normal_form for word in words]
        return normalize_text(' '.join(lemmatized))

    def process_files(self):
        """Обрабатывает JSON-файлы в указанной директории и загружает их в базу данных."""
        for filename in os.listdir(self.folder_path):
            if filename.endswith(".json"):
                self._process_file(os.path.join(self.folder_path, filename))

    def _process_file(self, filepath):
        """Обрабатывает один JSON-файл и заносит данные в базу."""
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        drug_name = data.get("Название ЛС")
        if not drug_name:
            return
        
        drug_id = self.db_manager.insert_drug(drug_name.lower())

        count_side_e = 0
        for category, effects in data.get("Побочные действия", {}).items():
            for frequency, effect_list in effects.items():
                if frequency == "Данные о частоте, собранные после продажи":
                    continue
                count_side_e+=len(effect_list)
                for effect in effect_list:
                    normalized_effect = self._lemmatize_text(effect.lower())
                    effect_id = self.db_manager.insert_side_effect(normalized_effect)
                    self.db_manager.insert_drug_side_effect(drug_id, effect_id, frequency)

        print(f"drug_{drug_name}: {count_side_e}")
                    # self.db_manager.insert_side_effect(drug_name, normalized_effect, frequency)


if __name__ == "__main__":
    folder_path = "orlov_dataset"  # Укажите путь к папке с JSON-файлами
    db_manager = DatabaseManager()
    processor = DataProcessor(folder_path, db_manager)
    processor.process_files()
    db_manager.commit_and_close()
    print("Данные успешно загружены в SQLite.")
