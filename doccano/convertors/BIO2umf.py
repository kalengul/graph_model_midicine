from convertors.normalize_text import normalize_text

import json

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

def BIO2umf_tt(tokens, tags):
    entity_list = []

    # Нормализация и завершение сущности
    def terminate_entity(func_list, text, tag):
        text = text.strip()
        if text:
            func_list.append((normalize_text(text), tag))
        return func_list, ""

    # for sent in data:
    current_tag = None      # Инициализация тега    сущности
    current_text = ""       # Инициализация текста  сущности

    for token, tag in zip(tokens, tags):

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

def BIO2umf_d(data):
    entity_list = []
    for sent in data:
        # Список кортежей сущнотей (сущность, тег)
        entity_list.extend(BIO2umf_tt(sent['tokens'], sent['tags']))
    return entity_list

def BIO2ent_sent(data):
    entity_sent_list = []
    for sent in data:
        # Список кортежей сущнотей (сущность, тег)
        entities = BIO2umf_tt(sent['tokens'], sent['tags'])
        # Восстанавливаются пробелы
        prepare_sent = normalize_text(" ".join(sent['tokens']))
        # Список кортежей ((сущность, тег), предложение)
        entity_sent_list.extend([(entity, prepare_sent) for entity in entities if entity[-1]])

    return entity_sent_list

if __name__ == "__main__":

    with open("data_bio\\data_bio_4.1.json", 'r', encoding='utf-8') as file:
        data = json.load(file)

    entity_sent = BIO2ent_sent(data)


    with open(f"data\\test.txt", 'w', encoding='utf-8') as file_rel:
        for tpl in entity_sent:
            file_rel.write(f"{tpl[0][0]}\t{tpl[1]}\n")
