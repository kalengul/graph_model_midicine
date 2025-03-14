import re
import json

from razdel import sentenize

# import spacy
# from spacy.tokenizer import Tokenizer
# from spacy.tokens import Span
# from spacy.tokens import Doc

from itertools import combinations

from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MyToken:
    text: str
    start: int
    end: int

@dataclass
class MySpan:
    id: Optional[int] = None
    doc: Optional["MyDoc"] = None   # Устанавливается после инициализации doc
    start: int = 0                  # Начало в символах
    end: int = 0                    # Конец в символах
    label: str = ""                 # Метка
    tokens: List[MyToken] = field(default_factory=list)  # Список токенов
    _text: str = ""  # Текст Span, который будет извлечён позже из токенов

    def __post_init__(self):
        if self.doc:
            # Инициализируем tokens после того, как doc уже проинициализирован
            self.tokens = self.tokens_in_range
            # Сохраняем текст как срез из doc.text
            self._text = self.doc.text[self.start:self.end]

    @property
    def tokens_in_range(self) -> List[MyToken]:
        if not self.doc:
            raise ValueError("Span is not associated with any document.")
        
        # Получаем токены, которые пересекаются с диапазоном [start, end)
        tokens_in_range = [
            token for token in self.doc.tokens
            if token.start >= self.start and token.end <= self.end
        ]
        
        # Обновляем start и end для корректности
        if tokens_in_range:
            self.start = tokens_in_range[0].start       # Начало первого токена
            self.end = tokens_in_range[-1].end     # Конец последнего токена
        return tokens_in_range

    @property
    def text(self) -> str:
        # Возвращаем текст как срез из doc.text, вычисленный по диапазону start и end
        return self._text

@dataclass
class MyDoc:
    text: str
    tokens: List[MyToken] = field(init=False)
    ents: List[MySpan] = field(default_factory=list)
    offset: int = 0

    def __post_init__(self):
        # Создаём токены из текста
        self.tokens = [
            MyToken(match.group(), match.start()+self.offset, match.end()+self.offset)
            for match in re.finditer(r'\w+|[^\w\s]', self.text)
        ]

    def add_span(self, start: int, end: int, label: str = "", id: int = None) -> MySpan:
        # Создаём Span и добавляем его в документ
        span = MySpan(doc=self, id = id, start=start, end=end, label=label)
        self.ents.append(span)
        return span


# Регистрируем пользовательские атрибуты
# Span.set_extension("id", default=None, force=True)     # Расширение для ID

# test_jsonl = {"id":1696,"text":"Возможные на фоне терапии ацетазоламидом распределены по рекомендациям ВОЗ: (>1\/10); (>1\/100, <1\/10); (>1\/1000, <1\/100); (>1\/10000, <1\/1000); (<1\/10000),(не мож ет быть определена на основании доступных данных); – апластическая анемия, тромбоцитопения, агранулоцитоз, лейкопения, тромбоцитопеническая пурпура, миелосупрессия, панцитопения; – анафилактические реакции; – снижение аппетита, нарушения вкуса, метаболический ацидоз, метаболический ацидоз и электролитные нарушения (это обычно может быть скорректировано назначением бикарбоната); – жажда; – глюкозурия;– гипокалиемия, гипонатриемия; нечаст о – депрессия, раздражительность;– возбуждение, спутанность сознания, дезориентация; – головокружение, парестезия, в частности ощущение покалывания в конечностях; – приливы, головная боль; – сонливость, периферический парез, судороги;– атаксия; – транзиторная миопия (это состояние полностью исчезало при снижении дозы либо отмене препарата);– хориоидальный выпот, отслойка сосудистой оболочки глаза; – нарушения слуха и звон в ушах; – тошнота, рвота, диарея, мелена;– сухость во рту, дисгевзия; – фульминантный некроз печени, нарушения функции печени, гепатит, холестатическая желтуха;– печеночная недостаточность, печеночная колика; – фотосенсибилизация;– кожный зуд, кожная сыпь, многоформная эритема, синдром Стивенса6 Джонсона, токсический эпидермальный некролиз, крапивница, острый генерализ ованный экзантематозный пустулёз; – артралгия; – образование конкрементов в почках, кристаллурия, почечная и мочеточниковая колики и поражение почек, полиурия, гематурия, почечная недостаточность; – снижение либидо; – усталость; – лихорадка, слабость.","entities":[{"id":917,"label":"prepare","start_offset":26,"end_offset":40},{"id":918,"label":"side_e","start_offset":214,"end_offset":234},{"id":919,"label":"side_e","start_offset":236,"end_offset":251},{"id":920,"label":"side_e","start_offset":253,"end_offset":266},{"id":921,"label":"side_e","start_offset":268,"end_offset":279},{"id":922,"label":"side_e","start_offset":280,"end_offset":308},{"id":923,"label":"side_e","start_offset":310,"end_offset":324},{"id":924,"label":"side_e","start_offset":326,"end_offset":338},{"id":925,"label":"side_e","start_offset":342,"end_offset":366},{"id":926,"label":"side_e","start_offset":370,"end_offset":387},{"id":927,"label":"side_e","start_offset":389,"end_offset":404},{"id":928,"label":"side_e","start_offset":406,"end_offset":427},{"id":929,"label":"side_e","start_offset":429,"end_offset":450},{"id":930,"label":"side_e","start_offset":453,"end_offset":476},{"id":931,"label":"side_e","start_offset":544,"end_offset":549},{"id":932,"label":"side_e","start_offset":553,"end_offset":563},{"id":933,"label":"side_e","start_offset":566,"end_offset":578},{"id":934,"label":"side_e","start_offset":580,"end_offset":593},{"id":935,"label":"side_e","start_offset":606,"end_offset":615},{"id":936,"label":"side_e","start_offset":617,"end_offset":634},{"id":937,"label":"side_e","start_offset":637,"end_offset":648},{"id":938,"label":"side_e","start_offset":650,"end_offset":670},{"id":939,"label":"side_e","start_offset":672,"end_offset":685},{"id":940,"label":"side_e","start_offset":689,"end_offset":703},{"id":941,"label":"side_e","start_offset":705,"end_offset":715},{"id":942,"label":"side_e","start_offset":729,"end_offset":763},{"id":943,"label":"side_e","start_offset":767,"end_offset":774},{"id":944,"label":"side_e","start_offset":776,"end_offset":789},{"id":945,"label":"side_e","start_offset":793,"end_offset":803},{"id":946,"label":"side_e","start_offset":805,"end_offset":825},{"id":947,"label":"side_e","start_offset":827,"end_offset":835},{"id":948,"label":"side_e","start_offset":838,"end_offset":845},{"id":949,"label":"side_e","start_offset":849,"end_offset":868},{"id":950,"label":"side_e","start_offset":946,"end_offset":965},{"id":951,"label":"side_e","start_offset":967,"end_offset":1001},{"id":952,"label":"side_e","start_offset":1005,"end_offset":1020},{"id":953,"label":"side_e","start_offset":1023,"end_offset":1034},{"id":954,"label":"side_e","start_offset":1038,"end_offset":1045},{"id":955,"label":"side_e","start_offset":1047,"end_offset":1052},{"id":956,"label":"side_e","start_offset":1054,"end_offset":1060},{"id":957,"label":"side_e","start_offset":1062,"end_offset":1068},{"id":958,"label":"side_e","start_offset":1071,"end_offset":1085},{"id":959,"label":"side_e","start_offset":1087,"end_offset":1096},{"id":960,"label":"side_e","start_offset":1100,"end_offset":1127},{"id":961,"label":"side_e","start_offset":1129,"end_offset":1153},{"id":962,"label":"side_e","start_offset":1155,"end_offset":1162},{"id":963,"label":"side_e","start_offset":1164,"end_offset":1187},{"id":964,"label":"side_e","start_offset":1190,"end_offset":1216},{"id":965,"label":"side_e","start_offset":1218,"end_offset":1235},{"id":966,"label":"side_e","start_offset":1239,"end_offset":1257},{"id":967,"label":"side_e","start_offset":1260,"end_offset":1270},{"id":968,"label":"side_e","start_offset":1272,"end_offset":1283},{"id":969,"label":"side_e","start_offset":1285,"end_offset":1305},{"id":970,"label":"side_e","start_offset":1307,"end_offset":1333},{"id":971,"label":"side_e","start_offset":1335,"end_offset":1369},{"id":972,"label":"side_e","start_offset":1371,"end_offset":1381},{"id":973,"label":"side_e","start_offset":1383,"end_offset":1432},{"id":974,"label":"side_e","start_offset":1436,"end_offset":1445},{"id":975,"label":"side_e","start_offset":1450,"end_offset":1482},{"id":976,"label":"side_e","start_offset":1484,"end_offset":1496},{"id":979,"label":"side_e","start_offset":1498,"end_offset":1530},{"id":980,"label":"side_e","start_offset":1533,"end_offset":1548},{"id":981,"label":"side_e","start_offset":1550,"end_offset":1558},{"id":982,"label":"side_e","start_offset":1560,"end_offset":1569},{"id":983,"label":"side_e","start_offset":1571,"end_offset":1595},{"id":984,"label":"side_e","start_offset":1599,"end_offset":1614},{"id":985,"label":"side_e","start_offset":1618,"end_offset":1627},{"id":986,"label":"side_e","start_offset":1631,"end_offset":1640},{"id":987,"label":"side_e","start_offset":1642,"end_offset":1650}],"relations":[],"Comments":[]}

# nlp = spacy.load("ru_core_news_lg")

# Функция для кастомного токенайзера
# def custom_tokenizer(nlp):
#     # Регулярное выражение для разделителей внутри текста, включая '/'
#     infix_re = re.compile(r'''[.\,;\:\!\?\…\-\)\(\/"«»]''')

#     # Создаем токенайзер с кастомными правилами
#     return Tokenizer(
#         nlp.vocab,
#         prefix_search=nlp.tokenizer.prefix_search,
#         suffix_search=nlp.tokenizer.suffix_search,
#         infix_finditer=infix_re.finditer,  # Используем кастомное регулярное выражение
#         token_match=None,  # Оставляем стандартный `token_match`
#     )


# def custom_tokenize_with_spaces(text):
#     """
#     Разделяет текст на токены с сохранением пробелов и позиций токенов в тексте.
#     """
#     tokens = []
#     # Регулярное выражение для выделения слов и спецсимволов, исключая пробелы
#     for match in re.finditer(r'\w+|[^\w\s]', text):
#         tokens.append(MyToken(match.group(), match.start(), match.end() - 1))
#     return tokens
    
    # # Определение пробелов: если токен — пробел, следующий токен не будет иметь пробела
    # words = []
    # spaces = []
    # for token in tokens:
    #     if token.isspace():     # Если это пробел
    #         if words:           # Если уже есть слова, добавить пробел к последнему
    #             spaces[-1] = True
    #     else:
    #         words.append(token)
    #         spaces.append(False)
    
    # # Последний токен всегда без пробела
    # if spaces:
    #     spaces[-1] = False
    
    # return words, spaces

def write_add(file, text):
    with open(file, 'a', encoding='utf-8') as file:
        file.write(text)

def check_correct_token(doc, text, ent):
    """Проверка на целостность токена и корректировка границ токена с учётом символов пунктуации и открывающих/закрывающих символов."""

    # Разделение переданных данных
    id, start_const, end_const, label = ent
    start, end = start_const, end_const  # Используем start_const и end_const для изначальных границ

    # Символы, которые нужно проверить (открывающие и закрывающие)
    open_symbols = '("«'  # Открывающие символы
    close_symbols = ')"»'  # Закрывающие символы
    punct_symbols = ',.;:-'  # Пунктуация для удаления

    # Подсчёт количества открывающих и закрывающих символов в пределах токена
    open_count = sum(text[start:end].count(symbol) for symbol in open_symbols)
    close_count = sum(text[start:end].count(symbol) for symbol in close_symbols)

    # Печать отладочной информации (можно убрать позже)
    # print(f"text: '{text[start:end]}', open_count: {open_count}, close_count: {close_count}")
    
    # Определяем количество символов, которые нужно удалить с каждой стороны
    count_del_start = open_count - close_count
    count_del_end = close_count - open_count

    # Удаляем лишние пробелы и пунктуацию с конца и с начала
    while end > start and (text[end-1].isspace() or text[end-1] in punct_symbols):
        end -= 1
    while end > start and (text[start].isspace() or text[start] in punct_symbols):
        start += 1

    # Убрать лишние открывающие/закрывающие символы с учётом баланса
    if end > start and text[start] in open_symbols and count_del_start > 0:
        start += 1
    if end > start and text[end-1] in close_symbols and count_del_end > 0:
        end -= 1

    # Откатываем start и end, если перед ним есть буквы (нужно для целостности слова)
    while start > 0 and text[start-1].isalpha():
        start -= 1
    while end < len(text) and text[end].isalpha():
        end += 1

    # Создание Span с обновлёнными границами
    span = doc.add_span(start, end, label=label, id=id)

    # Если Span не был создан, выводим информацию о "браке"
    if not span:
        print(f"Брак: '{text[start_const:end_const]}' -> '{text[start:end]}'")

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

# def generate_bio_tags(doc, sent_start, sent_end):
#     """Генерирует BIO-теги для токенов в пределах предложения."""
#     return [
#         (token.text, f'{token.ent_iob_}-{token.ent_type_}'
#          if token.ent_iob_ != 'O' else 'O')
#         for token in doc
#         if sent_start <= token.idx < sent_end
#     ]

def generate_bio_tags(doc, sent_start, sent_end):
    """Генерирует BIO-теги для токенов в пределах предложения."""

    # for ent in doc.ents: 
    #     print(ent.text)

    bio_tags = []

    token_tag_dict = {"tokens":[], "tags":[]}
    # tokens = []
    # tags = []

    # Пройдем по всем токенам в документе
    for token in doc.tokens:

        # Найдем спаны, которые пересекаются с данным токеном
        token_bio = "O"  # По умолчанию токен помечается как 'Outside'
        for span in doc.ents:
            # Если токен попадает в диапазон спана
            if token.start >= span.start and token.end <= span.end:
                # Если это первый токен в спане, то это 'B' (beginning)
                if token.start == span.start:
                    token_bio = f"B-{span.label}"
                # Если это токен внутри спана, то это 'I' (inside)
                elif token.start > span.start and token.end <= span.end:
                    token_bio = f"I-{span.label}"
                break  # Если нашли хотя бы один спан, больше не проверяем

        bio_tags.append((token.text, token_bio))

        token_tag_dict["tokens"].append(token.text)
        token_tag_dict["tags"].append(token_bio)
        # tokens.append(token.text)
        # tags.append(token.text)

    return bio_tags, token_tag_dict


def find_sentence_for_span(span, sentences):
    """Ищет предложение, в котором находится span."""
    for sentence in sentences:
        if  sentence.start <= span.start < sentence.stop:
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
            id2ent[item["from_id"]].label,
            sentence_for_entity.get(item["from_id"]),
            item["type"],
            id2ent[item["to_id"]].text,
            id2ent[item["to_id"]].label,
            sentence_for_entity.get(item["to_id"])
        )
        for item in all_relations
        if item["from_id"] in id_ent_list
        and item["to_id"] in id_ent_list
    ]

    # Находим комбинации, которых нет в sent_relations
    sent_missing_relations = [
        (
            id2ent[from_id].text,
            id2ent[from_id].label,
            sentence_for_entity.get(from_id),
            "Not_link",
            id2ent[to_id].text,
            id2ent[to_id].label,
            sentence_for_entity.get(to_id)
        )
        for from_id, to_id in all_combinations
        if (from_id, to_id) not in existing_pairs and (to_id, from_id) not in existing_pairs
        and (id2ent[from_id].label != "side_e" and id2ent[to_id].label != "side_e")
        and (id2ent[from_id].label != "side_e" and id2ent[to_id].label != "prepare")
        and (id2ent[from_id].label != "side_e" and id2ent[to_id].label != "illness")
        and (id2ent[from_id].label != "group" and id2ent[to_id].label != "group")
        and id2ent[from_id].label != "illness"
        and id2ent[from_id].label != "condition"
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
    # text = text.replace("\\/", "/")

    doc = MyDoc(text=text)
    spans = []
    # Подготовка сущностей
    for entity in entities:
        spans.append(check_correct_token(doc,
                                         text,
                                         (entity['id'],
                                          entity['start_offset'],
                                          entity['end_offset'],
                                          entity['label'])
                                          )
                    )
        # if span:
        #     id2ent[entity['id']] = span

    # Отсеиваем пересекающиеся сущности
    correct_ents = span_filter(spans)

    id2ent = {span.id: span for span in correct_ents}

    for ent in correct_ents:
        write_add(file_path_log, f"{ent.id} -- {ent.text}\n")

    # Назначаем отфильтрованные сущности документу
    doc.ents = correct_ents

    # Разделение текста на предложения
    sentences = list(sentenize(text))

    # Список id сущностей по предложению
    sent2ents = {
        sentence: [entity.id for entity in correct_ents
                   if sentence.start <= entity.start < sentence.stop]
        for sentence in sentences
    }

    # Предложение по id сущности
    ent_id2sent = {
        ent_id: next((sentence.text for sentence in sentences
                      if sentence.start <= entity.start < sentence.stop), None)
        for ent_id, entity in id2ent.items()
    }

    info_sents = []
    
    # Обрабатываем предложения
    for sentence in sentences:
        sent_start, sent_end = sentence.start, sentence.stop

        # Извлекаем список ID сущностей для текущего предложения
        current_ents = sent2ents.get(sentence, [])

        # Формирование структур для предложения
        sent_doc = MyDoc(text=sentence.text, offset = sent_start)
        sent_doc.ents = [id2ent[id] for id in current_ents]

        # Поиск связей и отсутствующих связей
        sent_relations, sent_missing_relations = find_missing_relations(current_ents, relations, ent_id2sent, id2ent)


        # print("len relations:", total_rellen(relations))

        # Генерация BIO-тегов
        # bio_tags =""
        bio_tags,token_tag_dict = generate_bio_tags(sent_doc, sent_start, sent_end)

        # Добавляем информацию о текущем предложении
        info_sents.append({
            "text": (f"{sent_start}-{sent_end}", sentence.text),
            "tokens": bio_tags,
            "token_tag_dict":token_tag_dict,
            "entities_full": [(id, id2ent[id].text, f"{id2ent[id].start}-{id2ent[id].end}", id2ent[id].label) for id in current_ents],
            "entities": [(id2ent[id].text, id2ent[id].label) for id in current_ents],
            "relations": sent_relations,
            "missing_relations": sent_missing_relations,
        })

    return info_sents

def prepare_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    res_total = []

    for line in lines:
        data = json.loads(line)

        # if data['id'] in (1857, 1859):
            # Присвоение каждому предложению свои сущности и связи
        res_total.append(link_ent_sent(data))

    global total_rel
    for res_sent in res_total:
        for res in res_sent:
            total_rel += len(res["relations"])

    print(total_rel)

    return res_total

# Пути (непутю)
# Входные данные
file_path = "data\\data_4.jsonl"

# Выходные данные
file_path_relation = "data\\data_relations_4.csv"
file_path_bio = "data_bio\\data_bio_4.json"
file_path_log = "data\\data_log_4.txt"

total_rel = 0

with open(file_path_log, 'w', encoding='utf-8') as file_log:
    file_log.write("")

# file_path_log = "convertors\\test\\log.txt"

if __name__ == "__main__":
    result = prepare_file(file_path)

    # print(item["relations"])

    total_rel_1 = 0

    # Запись связей
    with open(file_path_relation, 'w', encoding='utf-8') as file_rel:
        # file_rel.write("from||label_from||sent_from||type||to||label_to||sent_to\n")
        file_rel.write("from$label_from$sent_from$type$to$label_to$sent_to\n")
        for sent_list in result:
            for item in sent_list:
                total_rel_1 += len(item["relations"])
                for relation in (item["relations"]+item["missing_relations"]):
                    entity_from, label_from, text_from, relation_type, entity_to, label_to, text_to = relation
                    write_line = f"{entity_from}||{label_from}||{text_from}||{relation_type}||{entity_to}||{label_to}||{text_to}\n"
                    write_line = write_line.replace("•", "*")
                    write_line = write_line.replace("( ", "(")
                    write_line = write_line.replace("||", "$")
                    file_rel.write(write_line)

                # for not_relation in (item["missing_relations"]):
                #     from_entity, from_text, relation_type, to_entity, to_text = not_relation
                #     write_line = f"{from_entity}||{from_text}||{relation_type}||{to_entity}||{to_text}\n"
                #     write_line = write_line.replace("( ", "(")
                #     file_rel.write(write_line)

        # print(total_rel_1)

    # Запись BIO
    with open(file_path_bio, 'w', encoding='utf-8') as file_bio:
        bio_list = []
        for sent in result:
            for item in sent:
                # bio_result = {
                #     "tokens": [],
                #     "tags": []
                # }
                # for token, tag in item['tokens']:
                #     bio_result['tokens'].append(token)  # Добавляем токен в список
                #     bio_result['tags'].append(tag)  # Добавляем тег в список
                
                bio_list.append(item["token_tag_dict"])

            # Записываем весь объект в файл
        json.dump(bio_list, file_bio, ensure_ascii=False, indent=4)
        
    # Логи
    with open(file_path_log, 'w', encoding='utf-8') as file_log:
        json.dump(result, file_log, ensure_ascii=False, indent=4)

    print(total_rel)

