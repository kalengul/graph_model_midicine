import fasttext

# Путь к файлу с обучающими данными для классификации
train_data = 'many_corpus\\train_data.txt'

# Задайте параметры
learning_rate = 0.1          # Скорость обучения
vector_dim = 300             # Размерность векторов слов
context_window = 10          # Размер окна контекста
num_epochs = 25              # Количество эпох обучения
min_word_count = 1           # Минимальное количество появлений слова
num_negatives = 5            # Количество негативных примеров (если используется ns или neg)
word_ngrams = 2              # Максимальная длина n-граммы слов
num_buckets = 2000000        # Количество хеш-ячейок для подсловаря n-грамм
loss_function = 'softmax'    # Функция потерь

# Обучение модели классификации с дополнительными параметрами
model = fasttext.train_supervised(
    input=train_data,               
    lr=learning_rate,               
    dim=vector_dim,                 
    ws=context_window,              
    epoch=num_epochs,               
    minCount=min_word_count,        
    neg=num_negatives,              
    wordNgrams=word_ngrams,         
    bucket=num_buckets,             
    loss=loss_function              
)

# Сохранение модели
model.save_model("classifier_model.bin")
