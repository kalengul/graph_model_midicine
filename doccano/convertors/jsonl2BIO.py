import re
import json

from razdel import sentenize

import spacy
from spacy.tokenizer import Tokenizer
from spacy.tokens import Span

from itertools import combinations

# Регистрируем пользовательские атрибуты
Span.set_extension("id", default=None, force=True)     # Расширение для ID

test_jsonl = {"id":1696,"text":"Возможные на фоне терапии ацетазоламидом распределены по рекомендациям ВОЗ: (>1\/10); (>1\/100, <1\/10); (>1\/1000, <1\/100); (>1\/10000, <1\/1000); (<1\/10000),(не мож ет быть определена на основании доступных данных); – апластическая анемия, тромбоцитопения, агранулоцитоз, лейкопения, тромбоцитопеническая пурпура, миелосупрессия, панцитопения; – анафилактические реакции; – снижение аппетита, нарушения вкуса, метаболический ацидоз, метаболический ацидоз и электролитные нарушения (это обычно может быть скорректировано назначением бикарбоната); – жажда; – глюкозурия;– гипокалиемия, гипонатриемия; нечаст о – депрессия, раздражительность;– возбуждение, спутанность сознания, дезориентация; – головокружение, парестезия, в частности ощущение покалывания в конечностях; – приливы, головная боль; – сонливость, периферический парез, судороги;– атаксия; – транзиторная миопия (это состояние полностью исчезало при снижении дозы либо отмене препарата);– хориоидальный выпот, отслойка сосудистой оболочки глаза; – нарушения слуха и звон в ушах; – тошнота, рвота, диарея, мелена;– сухость во рту, дисгевзия; – фульминантный некроз печени, нарушения функции печени, гепатит, холестатическая желтуха;– печеночная недостаточность, печеночная колика; – фотосенсибилизация;– кожный зуд, кожная сыпь, многоформная эритема, синдром Стивенса6 Джонсона, токсический эпидермальный некролиз, крапивница, острый генерализ ованный экзантематозный пустулёз; – артралгия; – образование конкрементов в почках, кристаллурия, почечная и мочеточниковая колики и поражение почек, полиурия, гематурия, почечная недостаточность; – снижение либидо; – усталость; – лихорадка, слабость.","entities":[{"id":917,"label":"prepare","start_offset":26,"end_offset":40},{"id":918,"label":"side_e","start_offset":214,"end_offset":234},{"id":919,"label":"side_e","start_offset":236,"end_offset":251},{"id":920,"label":"side_e","start_offset":253,"end_offset":266},{"id":921,"label":"side_e","start_offset":268,"end_offset":279},{"id":922,"label":"side_e","start_offset":280,"end_offset":308},{"id":923,"label":"side_e","start_offset":310,"end_offset":324},{"id":924,"label":"side_e","start_offset":326,"end_offset":338},{"id":925,"label":"side_e","start_offset":342,"end_offset":366},{"id":926,"label":"side_e","start_offset":370,"end_offset":387},{"id":927,"label":"side_e","start_offset":389,"end_offset":404},{"id":928,"label":"side_e","start_offset":406,"end_offset":427},{"id":929,"label":"side_e","start_offset":429,"end_offset":450},{"id":930,"label":"side_e","start_offset":453,"end_offset":476},{"id":931,"label":"side_e","start_offset":544,"end_offset":549},{"id":932,"label":"side_e","start_offset":553,"end_offset":563},{"id":933,"label":"side_e","start_offset":566,"end_offset":578},{"id":934,"label":"side_e","start_offset":580,"end_offset":593},{"id":935,"label":"side_e","start_offset":606,"end_offset":615},{"id":936,"label":"side_e","start_offset":617,"end_offset":634},{"id":937,"label":"side_e","start_offset":637,"end_offset":648},{"id":938,"label":"side_e","start_offset":650,"end_offset":670},{"id":939,"label":"side_e","start_offset":672,"end_offset":685},{"id":940,"label":"side_e","start_offset":689,"end_offset":703},{"id":941,"label":"side_e","start_offset":705,"end_offset":715},{"id":942,"label":"side_e","start_offset":729,"end_offset":763},{"id":943,"label":"side_e","start_offset":767,"end_offset":774},{"id":944,"label":"side_e","start_offset":776,"end_offset":789},{"id":945,"label":"side_e","start_offset":793,"end_offset":803},{"id":946,"label":"side_e","start_offset":805,"end_offset":825},{"id":947,"label":"side_e","start_offset":827,"end_offset":835},{"id":948,"label":"side_e","start_offset":838,"end_offset":845},{"id":949,"label":"side_e","start_offset":849,"end_offset":868},{"id":950,"label":"side_e","start_offset":946,"end_offset":965},{"id":951,"label":"side_e","start_offset":967,"end_offset":1001},{"id":952,"label":"side_e","start_offset":1005,"end_offset":1020},{"id":953,"label":"side_e","start_offset":1023,"end_offset":1034},{"id":954,"label":"side_e","start_offset":1038,"end_offset":1045},{"id":955,"label":"side_e","start_offset":1047,"end_offset":1052},{"id":956,"label":"side_e","start_offset":1054,"end_offset":1060},{"id":957,"label":"side_e","start_offset":1062,"end_offset":1068},{"id":958,"label":"side_e","start_offset":1071,"end_offset":1085},{"id":959,"label":"side_e","start_offset":1087,"end_offset":1096},{"id":960,"label":"side_e","start_offset":1100,"end_offset":1127},{"id":961,"label":"side_e","start_offset":1129,"end_offset":1153},{"id":962,"label":"side_e","start_offset":1155,"end_offset":1162},{"id":963,"label":"side_e","start_offset":1164,"end_offset":1187},{"id":964,"label":"side_e","start_offset":1190,"end_offset":1216},{"id":965,"label":"side_e","start_offset":1218,"end_offset":1235},{"id":966,"label":"side_e","start_offset":1239,"end_offset":1257},{"id":967,"label":"side_e","start_offset":1260,"end_offset":1270},{"id":968,"label":"side_e","start_offset":1272,"end_offset":1283},{"id":969,"label":"side_e","start_offset":1285,"end_offset":1305},{"id":970,"label":"side_e","start_offset":1307,"end_offset":1333},{"id":971,"label":"side_e","start_offset":1335,"end_offset":1369},{"id":972,"label":"side_e","start_offset":1371,"end_offset":1381},{"id":973,"label":"side_e","start_offset":1383,"end_offset":1432},{"id":974,"label":"side_e","start_offset":1436,"end_offset":1445},{"id":975,"label":"side_e","start_offset":1450,"end_offset":1482},{"id":976,"label":"side_e","start_offset":1484,"end_offset":1496},{"id":979,"label":"side_e","start_offset":1498,"end_offset":1530},{"id":980,"label":"side_e","start_offset":1533,"end_offset":1548},{"id":981,"label":"side_e","start_offset":1550,"end_offset":1558},{"id":982,"label":"side_e","start_offset":1560,"end_offset":1569},{"id":983,"label":"side_e","start_offset":1571,"end_offset":1595},{"id":984,"label":"side_e","start_offset":1599,"end_offset":1614},{"id":985,"label":"side_e","start_offset":1618,"end_offset":1627},{"id":986,"label":"side_e","start_offset":1631,"end_offset":1640},{"id":987,"label":"side_e","start_offset":1642,"end_offset":1650}],"relations":[],"Comments":[]}

nlp = spacy.load("ru_core_news_lg")

# Функция для кастомного токенайзера
def custom_tokenizer(nlp):
    # Регулярное выражение, которое разделяет слова, точки и другие знаки отдельно
    infix_re = re.compile(r'''[.\,;\:\!\?\…\-\)\(]''')

    # Создаем токенайзер с кастомными правилами
    return Tokenizer(
        nlp.vocab,
        prefix_search=nlp.tokenizer.prefix_search,
        suffix_search=nlp.tokenizer.suffix_search,
        infix_finditer=infix_re.finditer,  # Используем наше регулярное выражение
        token_match=nlp.tokenizer.token_match,
    )


def write_add(file, text):
    with open(file, 'a', encoding='utf-8') as file:
        file.write(text)

def check_correct_token(doc, text, ent):
    """Проверка на целостность токена."""
    start_const, end_const, label = ent
    start, end, label = ent
    # Удаляем пробелы в конце
    while end > start and (text[end-1].isspace() or text[end-1] in (',', '.', ';', ':', ')', "\"", "»")):
        end -= 1
    # Удаляем пробелы в начале
    while end > start and (text[start].isspace() or text[start] in (',', '.', ';', ':', '(', "\"", "«")):
        start += 1

    # Создание Span
    span = doc.char_span(start, end, label = label)

    if not span:
        print("Брак:", text[start_const:end_const], "->", text[start:end])

    return span

def span_filter(spans):
    """Удаление пересекающихся сущностей."""
    # Сортируем спаны: по индексу начала,
    sorted_spans = sorted(spans,
                          key=lambda span: (span.start))
    # Результирующий список без пересечений
    filtered_spans = []
    for span in sorted_spans:
        # Проверяем пересечения с последним добавленным в список спаном
        if filtered_spans and span.start < filtered_spans[-1].end:
            if len(filtered_spans[-1].text) < len(span.text):
                filtered_spans[-1] = span
        else:
            filtered_spans.append(span)
    return filtered_spans

def generate_bio_tags(doc, sent_start, sent_end):
    """Генерирует BIO-теги для токенов в пределах предложения."""
    return [
        (token.text, f'{token.ent_iob_}-{token.ent_type_}'
         if token.ent_iob_ != 'O' else 'O')
        for token in doc
        if sent_start <= token.idx < sent_end
    ]

def find_sentence_for_span(span, sentences):
    """Ищет предложение, в котором находится span."""
    for sentence in sentences:
        if  sentence.start <= span.start_char < sentence.stop:
            return sentence
    return None  # Если не найдено

def create_sentence_lookup(sentences):
    """Создаёт словарь для быстрого поиска предложения по диапазону символов."""
    sentence_lookup = {}
    for sentence in sentences:
        sentence_lookup[(sentence.start, sentence.end)] = sentence
    return sentence_lookup

def find_missing_relations(id_ent_list,
                           all_relations,
                           sentence_for_entity,
                           id2ent):
    """Ищет связи и связи, которых нет."""

    # Существующие связи
    existing_pairs = set(
        (item["from_id"], item["to_id"])
        for item in all_relations
        if item["from_id"] in id_ent_list
    )

    # Все возможные комбинации id сущностей
    all_combinations = combinations(id_ent_list, 2)

    # Поиск связей, относящихся к сущностям текущего предложения
    relations = [
        (
            id2ent[item["from_id"]].text,
            sentence_for_entity.get(item["from_id"]),
            item["type"],
            id2ent[item["to_id"]].text,
            sentence_for_entity.get(item["to_id"])
        )
        for item in all_relations
        if item["from_id"] in id_ent_list and item["to_id"] in id_ent_list
    ]

    # Находим комбинации, которых нет в sent_relations
    sent_missing_relations = [
        (
            id2ent[from_id].text,
            sentence_for_entity.get(from_id),
            "Not_link",
            id2ent[to_id].text,
            sentence_for_entity.get(to_id)
        )
        for from_id, to_id in all_combinations
        if (from_id, to_id) not in existing_pairs and (to_id, from_id) not in existing_pairs
    ]
    
    return relations, sent_missing_relations

def link_ent_sent(data):
    """Разделение текста на предложения,"""
    """Назначение сущностей каждому предложению"""
    """Назначение связей    каждому предложению"""

    text        = data['text']
    entities    = data['entities']
    relations   = data['relations']
    
    info_sents = []

    # Заменяем "\/" на "\"
    text = text.replace("\\/", "/")

    # Парсинг текста в spaCy Doc
    doc = nlp.make_doc(text)

    # for token in doc:
    #     write_add(file_path_log, f"'{token.text}' ")
    
    # Подготовка сущностей
    id2ent = {}
    for entity in entities:
        span = check_correct_token(doc, text, (entity['start_offset'],
                                               entity['end_offset'],
                                               entity['label']))
        if span:
            span._.id = entity['id']
            id2ent[entity['id']] = span

    # Отсеиваем пересекающиеся сущности
    correct_ents = span_filter(list(id2ent.values()))

    # Назначаем отфильтрованные сущности документу
    doc.ents = correct_ents

    # Разделение текста на предложения
    sentences = list(sentenize(text))

    # Список id сущностей по предложению
    id_ent_dict_by_sentence = {
        sentence: [entity._.id for entity in correct_ents
                   if sentence.start <= entity.start_char < sentence.stop]
        for sentence in sentences
    }

    # Предложение по id
    sentence_for_entity = {
        ent_id: next((sentence.text for sentence in sentences
                      if sentence.start <= entity.start_char < sentence.stop), None)
        for ent_id, entity in id2ent.items()
    }

    info_sents = []
    
    # Обрабатываем предложения
    for sentence in sentences:
        sent_start, sent_end = sentence.start, sentence.stop

        # Извлекаем ID сущностей для текущего предложения
        id_ent_list_for_sentence = id_ent_dict_by_sentence.get(sentence, [])

        # Поиск связей и отсутствующих связей
        sent_relations, sent_missing_relations = find_missing_relations(id_ent_list_for_sentence, relations, sentence_for_entity, id2ent)

        # Генерация BIO-тегов
        bio_tags = generate_bio_tags(doc, sent_start, sent_end)

        # Добавляем информацию о текущем предложении
        info_sents.append({
            "text": (f"{sent_start}-{sent_end}", sentence.text),
            "tokens": bio_tags,
            "entities": [(id, id2ent[id].text, f"{id2ent[id].start_char}-{id2ent[id].end_char}") for id in id_ent_list_for_sentence],
            "relations": sent_relations,
            "missing_relations": sent_missing_relations,
        })

    return info_sents

def prepare_file(file):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    for line in lines:
        data = json.loads(line)

        # Присвоение для каждому предложению свои сущности и связи
        res = link_ent_sent(data)
    
    return res

# Пути (непутю)
# Входные данные
file_path = "convertors\\test\\data_3.jsonl"

# Выходные данные
file_path_relation = "convertors\\test\\data_relations.csv"
file_path_bio = "convertors\\test\\data_bio.json"
file_path_log = "convertors\\test\\data_log.json"

# file_path_log = "convertors\\test\\log.txt"

if __name__ == "__main__":
    result = prepare_file(file_path)

    # Запись связей
    with open(file_path_relation, 'w', encoding='utf-8') as file_rel:
        file_rel.write("from||sent_from||type||to||sent_to\n")
        for item in result:
            for relation in (item["relations"] + item["missing_relations"]):
                from_entity, from_text, relation_type, to_entity, to_text = relation
                file_rel.write(f"{from_entity}||{from_text}||{relation_type}||{to_entity}||{to_text}\n")

    # Запись BIO
    with open(file_path_bio, 'w', encoding='utf-8') as file_bio:
        bio_list = []
        for item in result:
            bio_result = {
                "tokens": [],
                "tags": []
            }
            for token, tag in item['tokens']:
                bio_result['tokens'].append(token)  # Добавляем токен в список
                bio_result['tags'].append(tag)  # Добавляем тег в список
            
            bio_list.append(bio_result)

        # Записываем весь объект в файл
        json.dump(bio_list, file_bio, ensure_ascii=False, indent=4)

    # Логи
    with open(file_path_log, 'w', encoding='utf-8') as file_res:
        json.dump(result, file_res, ensure_ascii=False, indent=4)

