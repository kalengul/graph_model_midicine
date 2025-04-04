"""Модулья экстрактора текстов."""

from extractor import Extractor


class TextExtractor(Extractor):
    """Экстрактор текста."""

    CONTENT = 'content'
    STRUCTURE = 'structure'
    SUBPARAGS = 'subparagraphs'
    TEXT = 'text'

    @classmethod
    def extract(cls, inputs):
        """
        Метод извлечения текст в список словарей.

        Результат список словарей,
        ключ которого - 'text',
        значение - извлечённый текст.
        """
        extracted_texts = []

        def extract_texts(data):
            """Функция рекурсивного извлечения текстов."""
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "text":
                        extracted_texts.append(value.strip())
                    else:
                        extract_texts(value)
            elif isinstance(data, list):
                for item in data:
                    extract_texts(item)

        # for subparag in inputs[cls.CONTENT][cls.STRUCTURE][cls.SUBPARAGS]:
        #     extracted_texts.append({cls.TEXT: subparag[cls.TEXT]})
        #     if subparag[cls.SUBPARAGS]:
        #         for item in subparag[cls.SUBPARAGS]:
        #             extracted_texts.append({cls.TEXT: item[cls.TEXT]})

        extract_texts(inputs)
        return [{cls.TEXT: text} for text in extracted_texts]

    @classmethod
    def extract_to_list(cls, inputs):
        """
        Метод извлечения текст в список словарей.

        Результат список извлечённый текст.
        """
        extracted_texts = []

        def extract_texts(data):
            """Функция рекурсивного извлечения текстов."""
            if isinstance(data, dict):
                for key, value in data.items():
                    if key == "text":
                        extracted_texts.append(value.strip())
                    else:
                        extract_texts(value)
            elif isinstance(data, list):
                for item in data:
                    extract_texts(item)

        extract_texts(inputs)
        # for subparag in inputs[cls.CONTENT][cls.STRUCTURE][cls.SUBPARAGS]:
        #     extracted_texts.append({cls.TEXT: subparag[cls.TEXT]})
        #     if subparag[cls.SUBPARAGS]:
        #         for item in subparag[cls.SUBPARAGS]:
        #             extracted_texts.append({cls.TEXT: item[cls.TEXT]})

        return extracted_texts
