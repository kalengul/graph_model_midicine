"""Модуль хранения графа."""

import json
from pathlib import Path

from django.conf import settings


class GraphStorage:
    """
    Класс для хранения графа.

    Граф храниться в директории graph_for_bayes.
    Помимо самого графа, а точнее мультиграфа
    в этой директории хранятся и вероятности
    для расчёта СБ.
    Оба графа в формате JSON.
    """

    GRAPH_FILE = 'multigraph.json'
    PROBABILITY_FILE = 'probability_opt.json'
    DIR_PATH = Path(settings.GRAPH_PATH)

    def __init__(self):
        """Создание хранилища графа."""
        self.DIR_PATH.mkdir(exist_ok=True)
        self.graph_path = self.DIR_PATH / self.GRAPH_FILE
        self.probability_path = self.DIR_PATH / self.PROBABILITY_FILE

        if not self.graph_path.exists():
            f = open(self.graph_path, 'w', encoding='utf-8')
            f.close()

        if not self.probability_path.exists():
            f = open(self.probability_path, 'w', encoding='utf-8')
            f.close()

    def save_graph(self, data: dict):
        """Сохранение графа."""
        with open(self.graph_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def download_graph(self):
        """Выгрузка графа."""
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_probability(self, data: dict):
        """Сохранение вероятностей."""
        with open(self.probability_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def download_probability(self):
        """Выгрузка вероятностей."""
        with open(self.graph_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    @property
    def size_of_graph_file(self):
        """Получение размера файла с графом."""
        return self.graph_path.stat().st_size

    @property
    def size_of_probability_file(self):
        """Получение размера файла с вероятностями."""
        return self.probability_path.stat().st_size
