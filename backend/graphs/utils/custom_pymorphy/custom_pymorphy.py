import json
import re

from pymorphy3 import MorphAnalyzer
from django.conf import settings


LEMM_PATH = (f"{settings.BASE_DIR}"
             "\\graphs\\utils\\custom_pymorphy\\custom_lemma_dict.json")


def normalize_text(text):
    # Удаляем лишние пробелы и символы
    text = re.sub(r' +\,', ',', text)
    text = re.sub(r' +\.', '.', text)
    text = re.sub(r' +\:', ':', text)
    text = re.sub(r' +\;', ';', text)
    text = re.sub(r' -', '-', text)
    text = re.sub(r'- ', '-', text)
    text = re.sub(r' \+ ', '+', text)
    text = re.sub(r' +\)', ')', text)
    text = re.sub(r'\( +', '(', text)
    text = re.sub(r'\,\.', '.', text)
    text = re.sub(r'\n\n+', '\n', text)

    # Дополнительная обработка
    text = re.sub(r'\[\s+', '[', text)
    text = re.sub(r'\s+\]', ']', text)
    text = re.sub(r'«\s+', '«', text)
    text = re.sub(r'\s+»', '»', text)
    text = re.sub(r'\s*/\s*', '/', text)

    text = re.sub(r'≤ +', '≤', text)
    text = re.sub(r'≤ +', '≤', text)

    return text


HTML_ENTITIES = {
    "&gt;": "__GT__",
    "&lt;": "__LT__",
    "&amp;": "__AMP__",
    "&quot;": "__QUOT__",
    "&apos;": "__APOS__"
}

REVERSE_HTML_ENTITIES = {v: k for k, v in HTML_ENTITIES.items()}

def protect_html_entities(text):
    for k, v in HTML_ENTITIES.items():
        if text:
            text = text.replace(k, v)
    return text

def restore_html_entities(text):
    for k, v in REVERSE_HTML_ENTITIES.items():
        if text:
            text = text.replace(k, v)
    return text

class EnhancedMorphAnalyzer:
    def __init__(self, corrections_path=LEMM_PATH):
        self.morph = MorphAnalyzer()
        # Загружаем словарь исправлений
        with open(corrections_path, "r", encoding="utf-8") as file:
            self.corrections = json.load(file)

    def parse(self, word):
        """
        Анализирует слово с помощью pymorphy3 и применяет исправления.
        Возвращает список объектов, как pymorphy3, но с учётом исправлений.
        Также записывает в файл слова с подозрительными леммами.
        """
        parsed_results = self.morph.parse(word)
        enhanced_results = []

        # Сортируем результаты по убыванию вероятности
        sorted_parsed_results = sorted(parsed_results, key=lambda p: p.score, reverse=True)

        # Получаем наиболее вероятную лемму
        most_probable_parse = sorted_parsed_results[0]
        lemma = most_probable_parse.normal_form
        corrected_lemma = self.corrections.get(lemma, lemma)  # Исправляем, если есть в словаре

        enhanced_parse = EnhancedParse(
            word=word,
            normal_form=corrected_lemma,
            tag=most_probable_parse.tag,
            methods_stack=most_probable_parse.methods_stack,
        )
        
        enhanced_results.append(enhanced_parse)

        return enhanced_results
    
    def lemmatize_string(self, text):
        """Лемматизирует текст с сохранением html-сущностей."""
        text = protect_html_entities(text)  # Сначала прячем &gt;, &amp; и т.п.

        if text:
            words = re.findall(r'\w+|[^\w\s]', text)
            lemmatized = [self.parse(word)[0].normal_form for word in words]
            result = normalize_text(' '.join(lemmatized))

            result = restore_html_entities(result)  # Возвращаем сущности обратно
        else:
            return text
        return result

class EnhancedParse:
    """
    Расширенный объект результата анализа слова, совместимый с pymorphy3.Parse.
    """
    def __init__(self, word, normal_form, tag, methods_stack):
        self.word = word
        self.normal_form = normal_form
        self.tag = tag
        self.methods_stack = methods_stack

    def __repr__(self):
        return f"<Parse: {self.word} -> {self.normal_form}, {self.tag}>"

    def __getitem__(self, item):
        return self.methods_stack[item]

if __name__ == "__main__":
    custom_morph = EnhancedMorphAnalyzer()

    # Тест
    print(custom_morph.parse("Каптоприлом")[0].normal_form)  # Пользовательский результат
    print(custom_morph.parse("Каптоприла")[0].normal_form)
    print(custom_morph.parse("Каптоприлу")[0].normal_form)  # Результат pymorphy3