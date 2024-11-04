import json
from razdel import sentenize

# example = {"id":1693,"text":"• Отечный синдром (слабой или умере нной выраженности, в сочетании с алкалозом); • Купирование острого приступа глаукомы, предоперационная подготовка больных, упорные случаи течения глаукомы (в комплексной терапии); • При эпилепсии в качестве дополнительной терапии к противоэпилептическим средствам; • Острая горная болезнь (препарат сокращает время акклиматизации); • Ликвородинамические нарушения, внутричерепная гипертензия (доброкачественная внутричерепная гипертензия, внутричерепная гипертензия после шунтирования желудочков мозга) в комплексной терапии.","entities":[{"id":637,"label":"illness","start_offset":2,"end_offset":17},{"id":638,"label":"illness","start_offset":112,"end_offset":120},{"id":639,"label":"illness","start_offset":182,"end_offset":190},{"id":640,"label":"illness","start_offset":268,"end_offset":300},{"id":641,"label":"illness","start_offset":304,"end_offset":325},{"id":642,"label":"illness","start_offset":371,"end_offset":400},{"id":643,"label":"illness","start_offset":402,"end_offset":428}],"relations":[],"Comments":[]}

base = 10000
counts = 0

# text = example['text']
# entities = example['entities']
file_path = "jsons\\data_1.jsonl"
file_path_res = "jsons\\data_edit_1.jsonl"
file_path_log = "jsons\\data_log_1.jsonl"

# Очистить файл
with open(file_path_res, 'w', encoding='utf-8') as file_res:
    file_res.write("")

with open(file_path_log, 'w', encoding='utf-8') as file_log:
    file_log.write("")

def write_add(file, text):
    with open(file, 'a', encoding='utf-8') as file:
        file.write(text)

with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

    for line in lines:
        data = json.loads(line)

        text        = data['text']
        entities    = data['entities']

        # Заменяем "\/" на "\"
        text = text.replace(r"\/", "\\")

        for ent in entities:
            id = ent['id']
            label = ent['label']
            start = ent['start_offset']
            end = ent['end_offset']
            # Удаляем пробелы в конце
            while end > start and (text[end-1].isspace() or text[end-1] in (',', '.', ';', ':')):
                end -= 1

            # Удаляем пробелы в начале
            while end > start and (text[start].isspace() or text[start] in (',', '.', ';', ':')):
                start += 1

            ent['start_offset'] = start
            ent['end_offset'] = end

        text = str(text)               
        sents = list(sentenize(text))

        items = []

        # Выводим каждое предложение
        offset = 0
        for sent in sents:
            counts += 1

            write_add(file_path_log, f"{sent.text}\n")
            write_add(file_path_log, f"{offset}-{offset + len(sent.text)} '{text[offset:offset + len(sent.text)]}'\n")

            current_ent = []
            for ent in entities:
                id = ent['id']
                label = ent['label']
                start = ent['start_offset']
                end = ent['end_offset']

                write_add(file_path_log, f"start: {start}, end: {end} text '{text[start:end]}'\n")

                if start >= offset and end <= (offset + len(sent.text)):
                    write_add(file_path_log,f"-- {text[start:end]} {start - offset}:{end - offset}\n")
                    current_ent.append({"id":id, "label":label, "start_offset": start - offset, "end_offset": end - offset})

            
            items.append({"id":base + counts, "text": sent.text, "entities": current_ent})

            entities = [ent for ent in entities if ent not in current_ent]

            offset += len(sent.text) + 1

            write_add(file_path_log, "\n")
            
        with open(file_path_res, 'a', encoding='utf-8') as file_res:
            for item in items:
                json.dump(item, file_res, ensure_ascii=False)
                file_res.write('\n')  # Перевод строки после каждой записи

