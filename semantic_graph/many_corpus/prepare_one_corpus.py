import os

# Путь к папке с текстовыми файлами
input_folder = 'many_corpus\\corpus_keys'

# Имя файла для обучающих данных
train_data_file = 'many_corpus\\train_data.txt'

with open(train_data_file, 'w', encoding='utf-8') as outfile:
    for filename in os.listdir(input_folder):
        if filename.endswith('.txt'):
            label = f"__label__{os.path.splitext(filename)[0]}"
            filepath = os.path.join(input_folder, filename)
            with open(filepath, 'r', encoding='utf-8') as infile:
                for line in infile:
                    outfile.write(f"{label} {line.strip()}\n")