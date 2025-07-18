import ufal.udpipe

# Загружаем модель spaCy для русского языка
import spacy
nlp = spacy.load("ru_core_news_lg")

# Функция для загрузки модели
def load_model(model_path):
    model = ufal.udpipe.Model.load(model_path)
    if not model:
        raise Exception(f"Невозможно загрузить модель из {model_path}")
    return model

def process_text_udpipe(model, text):
    tokenizer = model.newTokenizer(ufal.udpipe.Model.DEFAULT)
    tokenizer.setText(text)
    
    sentence = ufal.udpipe.Sentence()
    sentences = []
    
    while tokenizer.nextSentence(sentence):        
        # Теггирование и парсинг
        model.tag(sentence, model.DEFAULT)
        model.parse(sentence, model.DEFAULT)
        
        # Собираем информацию о токенах
        parsed_sentence = []
        for word in sentence.words[1:]:  # Пропускаем <root>
            parsed_sentence.append({
                "id": word.id,
                "form": word.form,
                "lemma": word.lemma,
                "upostag": word.upostag,
                "head": word.head,
                "deprel": word.deprel
            })

        sentences.append(parsed_sentence)  # Добавляем разобранное предложение
    
    return sentences

def process_text_spacy(text):
    # Применяем модель spaCy к тексту
    doc = nlp(text)
    
    sentences = []
    
    for sent in doc.sents:  # Проходим по предложениям
        parsed_sentence = []
        
        for token in sent:  # Проходим по токенам в предложении
            parsed_sentence.append({
                "id": token.i + 1,  # Нумерация с 1 (индекс в spaCy начинается с 0)
                "form": token.text,
                "lemma": token.lemma_,
                "upostag": token.pos_,
                "head": token.head.i + 1,  # Индекс родительского токена
                "deprel": token.dep_
            })
        
        sentences.append(parsed_sentence)
    
    return sentences

def print_conllu(sentences):
    offset = 20
    # Используем f-строки для задания ширины столбцов
    print(f"{'id':<5}{'form':<{offset}}{'lemma':<{offset}}{'upostag':<{10}}{'head':<{5}}{'deprel':<{offset}}")
    
    for sentence in sentences:
        for word in sentence:
            print(f"{word['id']:<5}{word['form']:<{offset}}{word['lemma']:<{offset}}{word['upostag']:<{10}}{word['head']:<{5}}{word['deprel']:<{offset}}")
    print()


# Путь к модели
model_path = 'full_pipeline\\model_udpipe\\russian-syntagrus-ud-2.0-170801.udpipe'
model = load_model(model_path)

# Пример
text = "Ингибирует циклооксигеназу (ЦОГ-1 и ЦОГ-2) и необратимо тормозит циклооксигеназный путь метаболизма арахидоновой кислоты."

# Пример данных
sentences_example = [
    [
        {"id": 1, "form": "Ингибирует", "lemma": "ингибировать", "upostag": "VERB", "head": 0, "deprel": "root"},
        {"id": 2, "form": "циклооксигеназу", "lemma": "циклооксигеназа", "upostag": "NOUN", "head": 3, "deprel": "obj"},
        {"id": 3, "form": "(", "lemma": "(", "upostag": "PUNCT", "head": 4, "deprel": "punct"},
        {"id": 4, "form": "ЦОГ-1", "lemma": "ЦОГ-1", "upostag": "PROPN", "head": 3, "deprel": "appos"},
        {"id": 5, "form": "и", "lemma": "и", "upostag": "CCONJ", "head": 3, "deprel": "cc"},
        {"id": 6, "form": "ЦОГ-2", "lemma": "ЦОГ-2", "upostag": "PROPN", "head": 3, "deprel": "appos"},
        {"id": 7, "form": ")", "lemma": ")", "upostag": "PUNCT", "head": 3, "deprel": "punct"},
        {"id": 8, "form": "и", "lemma": "и", "upostag": "CCONJ", "head": 9, "deprel": "cc"},
        {"id": 9, "form": "необратимо", "lemma": "необратимо", "upostag": "ADV", "head": 10, "deprel": "advmod"},
        {"id": 10, "form": "тормозит", "lemma": "тормозить", "upostag": "VERB", "head": 0, "deprel": "root"},
        {"id": 11, "form": "циклооксигеназный", "lemma": "циклооксигеназный", "upostag": "ADJ", "head": 12, "deprel": "amod"},
        {"id": 12, "form": "путь", "lemma": "путь", "upostag": "NOUN", "head": 10, "deprel": "obj"},
        {"id": 13, "form": "метаболизма", "lemma": "метаболизм", "upostag": "NOUN", "head": 12, "deprel": "nmod"},
        {"id": 14, "form": "арахидоновой", "lemma": "арахидоновый", "upostag": "ADJ", "head": 15, "deprel": "amod"},
        {"id": 15, "form": "кислоты", "lemma": "кислота", "upostag": "NOUN", "head": 13, "deprel": "nmod"},
        {"id": 16, "form": ".", "lemma": ".", "upostag": "PUNCT", "head": 10, "deprel": "punct"}
    ]
]

sentences_udpipe = process_text_udpipe(model, text)
sentences_spacy = process_text_spacy(text)

print("Размеченный вручную:")
print_conllu(sentences_example)

print("udpipe:")
print_conllu(sentences_udpipe)

print("spaCy:")
print_conllu(sentences_spacy)