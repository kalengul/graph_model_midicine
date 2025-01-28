from normalize_text import normalize_text

import sys
sys.path.append("")


test_BIO_format = [
    {
        "tokens": [
            "средства",
            ",",
            "действующие",
            "на",
            "ренин",
            "-",
            "ангиотензиновую",
            "систему",
            ";",
            "ингибиторы",
            "ангиотензинпревращающего",
            "фермента",
            "(",
            "АПФ",
            ")",
            ",",
            "комбинации",
            ";",
            "ингибиторы",
            "АПФ",
            "и",
            "блокаторы",
            "кальциевых",
            "каналов",
            "."
        ],
        "tags": [
            "B-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "O",
            "B-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "O",
            "O",
            "O",
            "B-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "I-group",
            "O"
        ]
    },
    {
        "tokens": [
            "Фармакодинамика",
            "Амлодипин",
            "Механизм",
            "действия",
            "Амлодипин",
            "-",
            "БМКК",
            ",",
            "производное",
            "дигидропиридина",
            "."
        ],
        "tags": [
            "O",
            "B-prepare",
            "O",
            "O",
            "B-prepare",
            "O",
            "B-group",
            "I-group",
            "I-group",
            "I-group",
            "O"
        ]
    },
    {
        "tokens": [
            "Антигипертензивное",
            "действие",
            "амлодипина",
            "обусловлено",
            "прямым",
            "расслабляющим",
            "воздействием",
            "на",
            "гладкомышечные",
            "клетки",
            "сосудистой",
            "стенки",
            "."
        ],
        "tags": [
            "B-mechanism",
            "I-mechanism",
            "B-prepare",
            "O",
            "B-mechanism",
            "I-mechanism",
            "I-mechanism",
            "B-prepare",
            "B-mechanism",
            "I-mechanism",
            "I-mechanism",
            "I-mechanism",
            "O"
        ]
    },
]

def BIO2umf(data):
    entity_list = []

    # Нормализация и завершение сущности
    def terminate_entity(func_list, text, tag):
        text = text.strip()
        if text:
            func_list.append((normalize_text(text), tag))
        return func_list, ""

    for entry in data:
        current_tag = None      # Инициализация тега    сущности
        current_text = ""       # Инициализация текста  сущности

        for token, tag in zip(entry['tokens'], entry['tags']):

            # Начало сущности
            if tag.startswith('B-'):

                # Завершение текущей сущности в любом случае, кроме первого раза
                entity_list, current_text = terminate_entity(entity_list, current_text, current_tag)

                # Присвоение тега
                current_tag = tag[2:]
                current_text += f'{token} '

            # Продолжение текущей сущности с тем же тегом
            elif tag.startswith('I-') and current_tag == tag[2:]:
                current_text += f'{token} '

            # Токен под "O"
            # ИЛИ
            # Внезапно начался кусок другой сущности
            # Добавление текста без тега
            else:
                # Завершение сущности и обнуление тега
                if current_tag:
                    entity_list, current_text = terminate_entity(entity_list, current_text, current_tag)
                    current_tag = None
                    
                # Добавляем токен без сущности
                current_text += f'{token} '

        # Завершение последней сущности
        entity_list, current_text = terminate_entity(entity_list, current_text, current_tag)

    return entity_list

if __name__ == "__main__":
    print(BIO2umf(test_BIO_format))
