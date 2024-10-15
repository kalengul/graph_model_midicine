from tokenizers import (
    Tokenizer, 
    decoders, 
    models, 
    normalizers, 
    pre_tokenizers, 
    processors, 
    trainers
)
from tokenizers.normalizers import NFD, Lowercase, StripAccents, Sequence

# Инициализация модели WordPiece
tokenizer = Tokenizer(models.WordPiece(unk_token="[UNK]"))

# Определение нормализации текста. Последовательное применение правил
tokenizer.normalizer = Sequence([
    NFD(),                                  # Декомпозиция символов "é" -> "e'"
    Lowercase(),                            # Понижение регистра
    StripAccents()                          # Замена диакритических знаков "é" -> "e"
])

# Правило деления на токены
tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
    pre_tokenizers.Whitespace(),            # Деление на пробелах
    pre_tokenizers.Punctuation(),           # Отдельная токенизация пунктуации
])

# Определение тренера
trainer = trainers.WordPieceTrainer(
    vocab_size=30000,
    min_frequency=2,
    special_tokens=["[UNK]", "[PAD]", "[CLS]", "[SEP]", "[MASK]"]
)

# Обучение токенизатора WordPiece на корпусе текста
tokenizer.train(["one_corpus/corpus_modified_2.txt"], trainer=trainer)

# Определение постпроцессора
tokenizer.post_processor = processors.TemplateProcessing(
    single=f"[CLS]:0 $A:0 [SEP]:0",
    pair=f"[CLS]:0 $A:0 [SEP]:0 $B:1 [SEP]:1",
    special_tokens=[
        ("[CLS]", tokenizer.token_to_id("[CLS]")),
        ("[SEP]", tokenizer.token_to_id("[SEP]")),
        ("[PAD]", tokenizer.token_to_id("[PAD]"))   # Установка ID токена паддинга
    ]  
)

# Настройка токена паддинга
tokenizer.enable_padding(pad_id=tokenizer.token_to_id("[PAD]"), pad_token="[PAD]")

# Определение декодера
tokenizer.decoder = decoders.WordPiece(prefix="##")

# Добавление своих символов
new_tokens = ["т.ч.", "т.н.", "т.е.", "т.п.", "т.к.", "т.д.", "др.", "в/в", "в/м", "п/к"]
tokenizer.add_tokens(new_tokens)

# Пример токенизации текста
encoding = tokenizer.encode("Симпатолитическая активность и блокада калиевых и кальциевых каналов уменьшают потребность миокарда в кислороде, приводят к т.н. отрицательному дромотропному эффекту: замедляется проводимость и удлиняется рефрактерный период в синусном и AV узлах. Обладая свойством вазодилататора, может снижать и др. сопротивление коронарных сосудов.")
print(encoding.tokens)

# Проверка
print(tokenizer.decode(encoding.ids))

# Сохранение обученного токенизатора
tokenizer.save("my_tokenizer_zero.json")

# # Загрузка токенизатора из файла JSON
# import json
# from transformers import PreTrainedTokenizerFast
# with open("my_tokenizer_zero.json", 'r', encoding='utf-8-sig') as f:
#     tokenizer_dict = json.load(f)
# tokenizer = PreTrainedTokenizerFast(tokenizer_object=tokenizer_dict)


