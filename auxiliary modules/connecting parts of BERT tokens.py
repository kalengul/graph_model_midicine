from transformers import BertTokenizer

def merge_tokens(tokens, labels):
    """
    Функция для объединения подслов в исходные слова и сохранения меток.

    tokens: Список токенов (токенизированные слова).
    labels: Список меток для каждого токена.

    Возвращает список слов с соответствующими метками.
    """
    merged_tokens = []
    merged_labels = []
    
    current_token = ""
    current_label = labels[0]
    
    for token, label in zip(tokens, labels):
        if token.startswith("##"):
            current_token += token[2:]  # Убираем префикс '##' и добавляем к текущему слову
        else:
            if current_token:  # Если есть собранное слово, добавляем его в результат
                merged_tokens.append(current_token)
                merged_labels.append(current_label)
            current_token = token  # Начинаем новое слово
            current_label = label
    
    # Добавляем последний токен
    if current_token:
        merged_tokens.append(current_token)
        merged_labels.append(current_label)
    
    return merged_tokens, merged_labels

# Пример использования
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Пример исходного текста
text = "The quick brown fox jumps over the lazy dog."

# Токенизация текста
tokens = tokenizer.tokenize(text)

# Пример меток (для задачи NER или другой задачи)
labels = ["O", "B-ADJ", "I-ADJ", "B-NOUN", "O", "O", "O", "B-ADJ", "B-NOUN"]

# Объединение токенов и меток
merged_tokens, merged_labels = merge_tokens(tokens, labels)

print("Tokens:", merged_tokens)
print("Labels:", merged_labels)
