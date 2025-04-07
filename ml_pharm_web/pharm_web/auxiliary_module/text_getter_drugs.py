"""Модуль получения названия ЛС из текстового файла."""


class TextGetterDrugs:
    """Класс получения названий ЛС."""

    def __init__(self, path):
        """Конструктор геттера ЛС из текстового класса."""
        self.path = path

    def get_drug_names(self):
        """Метод получения ЛС из текстового класса."""
        with open(self.path, 'r', encoding='utf-8') as file:
            return [name.strip().split('\t')[1] for name in file
                    if name != '\n']
