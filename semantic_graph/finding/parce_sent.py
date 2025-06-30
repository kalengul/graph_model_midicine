import re

def find_sentences_around_period(text):
    
    abbreviations_entr = {
    "ммрт.ст.", "рт.ст.", "ст.", "т.д.", "т.е.", "т.п.", "т.н.", "др.", "т.к.",
    }

    abbreviations_no_entr = {"т.ч."}

    # Регулярное выражение для поиска сокращения перед точкой и слова после точки
    # pattern = r'(\b\w+\.?\w*)\.\s+(\w+)'
    # pattern = r'(?<=\s|\n)(\S+)\.\s+(\S+)(?=\s|\n|$)'
    # pattern = r'(\b\w+)\.\s+(\S+)(?=\s|\n|$)'
    # pattern = r'(?<=\b)(\S+)\.\s+(\S+)(?=\s|\n|$)'
    # pattern = r'(?<=\b|\s)(\S+)\.\s+(\S+)'
    # pattern = r'(\S+)\.\s+(\S+)'
    # pattern = r'(\S+)\.\s+(\S+)(?=\s|\n|$)'
    # pattern = r'(\S+)\.\s+(\S+)(?=\s|\.|$)'
    # pattern = r'(\S+)\.\s*(\S+)(?=\s|\.|$)'
    # pattern = r'(\S+)\.\s*([^\s.]+)'


    # pattern = r'(\S+)\.\s*([^.\s]+)'
    pattern = r'\b(\S+)\.\s*([^\s.]+)'

    # Регулярное выражение для поиска ')\. '
    pattern_closing = r'\)\.\s+'

    # Замена всех случаев ')\. ' на ')\.\n'
    text = re.sub(pattern_closing, ')\n', text)

    # Находим все совпадения по регулярному выражению
    matches = list(re.finditer(pattern, text))  # Преобразуем в список для безопасного изменения текста

    if not matches:
        return text  # Если нет совпадений, возвращаем оригинальный текст
    
    modified_text = text  # Копия текста для внесения изменений

    for match in matches:
        sentence_before, sentence_after = match.groups()

        # Убираем пробелы по краям и восстанавливаем точку
        sentence_before = sentence_before.strip() + '.'
        sentence_after = sentence_after.strip()
        print(sentence_before, sentence_after)
       
        first_word_after = sentence_after.split()[0]
        # Проверка, начинается ли слово после точки с заглавной буквы
        if first_word_after[0].isupper():
            # Если после заглавной буквы идёт ещё одна заглавная или цифра, то это аббревиатура
            if len(first_word_after) > 1 and (first_word_after[1].isupper() or first_word_after[1].isdigit()):
                # Если сокращение и аббревиатура, то проверяем наличие в списке сокращений
                if sentence_before in abbreviations_entr:
                    # Запрашиваем у пользователя, ставить ли \n
                    response = input(f"Предложение после '{sentence_before} {first_word_after}'. Хотите поставить '\\n'? (да/нет): ").strip().lower()
                    if response in ('да', 'д', 'y', 'yes'):
                        modified_text = modified_text.replace(f"{sentence_before} {sentence_after}", f"{sentence_before}\n{sentence_after}", 1)
                
                # В этом случае не ставится \n
                elif sentence_before in abbreviations_no_entr:
                    pass
                else:
                    # Если это не сокращение, но аббревиатура, ставить \n
                    modified_text = modified_text.replace(f"{sentence_before} {sentence_after}", f"{sentence_before}\n{sentence_after}", 1)

            else:
                # Если после заглавной буквы идёт маленькая буква, то ставим \n
                modified_text = modified_text.replace(f"{sentence_before} {sentence_after}", f"{sentence_before}\n{sentence_after}", 1)

        else:
            # После точки слово начинается с маленькой буквы
            pass  # Ничего не делаем




        # Находим все совпадения по регулярному выражению
        matches = list(re.finditer(pattern, modified_text))

    # Возвращаем измененный текст
    return modified_text

# Пример использования функции
# text = (
#     "После повышения на 19 ммрт.ст. ЖКТ увеличилось втрое. Обратите внимание на документацию и т.д. Пять новых правил т.у. Р2Д2 изучает биологию. Это его любимый предмет. У нас есть план т.е. НУжно начать работу. Мы подготовили все документы. Уголь. Рассмотрим пример: т.д. все это важно для нас. Текст содержит примеры как т.Д. и г. и прочее. Пример для тестирования: Слово-через. Тестирование 123 456. Тестирование (а, б и др.). Привет, как дела?"
# )

text = (
    "Р2Д2 изучает биологию. Уголь. Рассмотрим пример: т.д. все это важно для нас. Текст содержит примеры как т.Д. и г. и прочее. Пример для тестирования: Слово-через. Тестирование 123 456. Тестирование (а, б и др.). Привет, как дела?"
)

# # Чтение текстового файла
# with open('one_corpus\\corpus_full.txt', 'r', encoding='utf-8') as file:
#     text = file.read()

# Вызов функции и вывод результата
result_text = find_sentences_around_period(text)

print(result_text)

# # Сохранение измененного текста в новый файл
# with open('one_corpus\\corpus_modified_3.txt', 'w', encoding='utf-8') as file:
#     file.write(result_text)

