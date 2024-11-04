# функция сшивания  токенов BERT разорваных слов 
def merge_BERT_tokens(tokens, labels):
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