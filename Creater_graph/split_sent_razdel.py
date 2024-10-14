from razdel import sentenize
import re

# # Чтение текстового файла
# with open('one_corpus\\corpus_full.txt', 'r', encoding='utf-8') as file:
#     text = file.read()

def split_format_text(text):

    text = re.sub(r'\(.*?\)', '', text)                                         # Удаление круглых скобок и их содержимого

    text = re.sub(r'^Таблица.*\d+$', '', text, flags=re.MULTILINE)              # "Таблица n"
    text = re.sub(r'^RxList\.com.*$', '', text, flags=re.MULTILINE)             # "RxList.com ..."
    text = re.sub(r',? показаны в таблице \d+', '', text)                       # ", показаны в таблице n"
    text = re.sub(r'представлен(?:а|о|ы)? в таблице \d+', '', text)             # "представлен(а)(о)(ы) в таблице n"
    text = re.sub(r'приведен(?:а|о|ы)? в таблице \d+', '', text)             # "представлен(а)(о)(ы) в таблице n"

    text = re.sub(r'Результаты представлены в таблице \d+.', '', text)          # "Результаты представлены в таблице n"

    # Разделение на предложения
    sentenses = [sentense.text for sentense in list(sentenize(text))]

    # Проставление \n
    text = '\n'.join(sentenses)

    # Удаление лишних пробелов
    text = re.sub(r' +\,', ',', text)
    text = re.sub(r' +\.', '.', text)
    text = re.sub(r' +\:', ':', text)
    text = re.sub(r' +\;', ';', text)
    text = re.sub(r'\,\.', '.', text)
    text = re.sub(r' +', ' ', text)

    # Доп разделение  
    text = text.replace(' ч. ', ' ч.\n')
    text = text.replace('/ч. ', '/ч.\n')
    text = text.replace(' тел. ', ' тел.\n')
    text = text.replace(' с. ', ' с.\n')

    text = text.replace('\n,', ',')

    text = re.sub(r'\n\n+', '\n', text)

    def filter_line(text):

        # Фильтрация строк, заканчивающихся не на ".", ";" или ":"
        lines = text.split('\n')

        # Функция для проверки, содержит ли строка только одно слово с точкой
        def is_single_word_with_period(line):
            words = line.split()
            return len(words) == 1 and words[0].endswith('.')

        # Фильтрация строк, которые заканчиваются на ".", ";", ":" и не являются одним словом с точкой
        filtered_lines = [
            line for line in lines
            if (line.endswith(('.', ';', ':')) and not is_single_word_with_period(line))
        ]

        text = '\n'.join(filtered_lines)

        return text

    text = filter_line(text)

    return text

# with open('one_corpus\\corpus_razdel.txt', 'w', encoding='utf-8') as file:
#     file.write(text)
