test_umf = [('средства, действующие на ренин-ангиотензиновую систему', 'group'), (';', None), ('ингибиторы ангиотензинпревращающего фермента (', 'mechanism'), ('АПФ)', 'group'), (', комбинации;', None), ('ингибиторы АПФ и блокаторы кальциевых каналов', 'group'), ('.', None), ('Фармакодинамика', None), ('Амлодипин', 'prepare'), ('Механизм действия', None), ('Амлодипин', 'prepare'), ('-', None), ('БМКК, производное дигидропиридина', 'group'), ('.', None), ('Антигипертензивное действие', 'mechanism'), ('амлодипина', 'prepare'), ('обусловлено', None), ('прямым расслабляющим воздействием', 'mechanism'), ('на', 'prepare'), ('гладкомышечные клетки сосудистой стенки', 'mechanism'), ('.', None)]

def umf2jsonl(data):

    result = {'text': '', 'label': []}  # Словарь результата
    curr_len = 0                        # Счётчик текущей длина

    for text, tag in data:
        # Добавление пробела перед текстом,
        # если это не начальная часть строки
        # и текст не начинается с пунктуации
        if (result['text'] and not result['text'][-1].isspace()
        and text[0]             not in (',', '.', ';', ':', ')', "\"", "»")
        and result['text'][-1]  not in ('(', "\"", "«")):
            result['text'] += " "
            curr_len += 1

        # Добавление текста
        start = curr_len
        result['text'] += text
        end = curr_len + len(text)

        # Добавление метки, если есть тег
        if tag:
            result['label'].append([start, end, tag])

        curr_len = end

    return result


if __name__ == "__main__":
    print(umf2jsonl(test_umf))