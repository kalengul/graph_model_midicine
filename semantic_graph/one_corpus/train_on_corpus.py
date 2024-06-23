import fasttext

# Путь к вашему текстовому файлу
input_file = 'corpus.txt'
output_model = 'model.bin'

# Параметры обучения модели
model_type = 'cbow'                 # Тип модели ('skipgram' или 'cbow')
learning_rate = 0.01                # Скорость обучения
vector_dim = 600                    # Размерность векторов слов
context_window = 15                 # Размер окна контекста
num_epochs = 3                      # Количество эпох обучения
min_word_count = 5                  # Минимальное количество появлений слова для его включения в словарь
num_negatives = 5                   # Количество негативных примеров для обучения
word_ngrams = 3                     # Максимальная длина n-граммы слов
num_buckets = 2000000               # Количество хеш-ячейок для подсловаря n-грамм
loss_function = 'softmax'           # Функция потерь ('ns', 'hs' или 'softmax')

# Обучение модели FastText
model = fasttext.train_unsupervised(
    input=input_file,               # Входной файл с текстом
    model=model_type,               # Тип модели
    lr=learning_rate,               # Скорость обучения
    dim=vector_dim,                 # Размерность векторов слов
    ws=context_window,              # Размер окна контекста
    epoch=num_epochs,               # Количество эпох обучения
    minCount=min_word_count,        # Минимальное количество появлений слова
    neg=num_negatives,              # Количество негативных примеров
    wordNgrams=word_ngrams,         # Максимальная длина n-граммы слов
    bucket=num_buckets,             # Количество хеш-ячейок для подсловаря n-грамм
    loss=loss_function              # Функция потерь
)

# Сохранение модели
model.save_model(output_model)
