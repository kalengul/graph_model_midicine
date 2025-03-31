import json
import re
from pymorphy3 import MorphAnalyzer

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


class EnhancedMorphAnalyzer:
    def __init__(self,
                 corrections_path="CustomPymorphy\\custom_lemma_dict.json",
                 log_file="CustomPymorphy\\suspicious_lemmas.json",
                 threshold=0.26):
        self.morph = MorphAnalyzer()
        # Загружаем словарь исправлений
        with open(corrections_path, "r", encoding="utf-8") as file:
            self.corrections = json.load(file)
        # Файл для записи подозрительных лемм
        self.log_file = log_file
        # Порог вероятности
        self.threshold = threshold
        with open(self.log_file, "w", encoding="utf-8") as file:
            pass

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
        score = most_probable_parse.score  # Вероятность самой вероятной леммы
        corrected_lemma = self.corrections.get(lemma, lemma)  # Исправляем, если есть в словаре

        enhanced_parse = EnhancedParse(
            word=word,
            normal_form=corrected_lemma,
            tag=most_probable_parse.tag,
            methods_stack=most_probable_parse.methods_stack,
        )
        
        # Проверка вероятности и запись, если ниже порога
        if score < self.threshold and corrected_lemma == lemma:
            self._log_suspicious_lemma(word, corrected_lemma, score)

        enhanced_results.append(enhanced_parse)

        return enhanced_results
    
    def lemmatize_string(self, text):
        """Лемматизирует текст с использованием морфологического анализатора."""
        words = re.findall(r'\w+|[^\w\s]', text)
        lemmatized = [self.parse(word)[0].normal_form for word in words]
        return normalize_text(' '.join(lemmatized))

    def _log_suspicious_lemma(self, word, corrected_lemma, score):
        """
        Логирует наиболее вероятную лемму в файл, если вероятность меньше порога.
        """
        suspicious_data = {
            'word': word,
            'corrected_lemma': corrected_lemma,
            'score': score
        }
        
        # Записываем данные в файл
        try:
            with open(self.log_file, "a", encoding="utf-8") as file:
                json.dump(suspicious_data, file, ensure_ascii=False)
                file.write("\n")  # Для разделения записей
        except Exception as e:
            print(f"Ошибка записи в файл: {e}")

            


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