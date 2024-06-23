import os

# Указываем путь к папке с файлами
# folder_path = "./side_effects_ru_txt"

# Получаем список всех файлов в папке
# files = os.listdir(folder_path)

files = ["Допереведённые\\aspirine.txt", "Допереведённые\\atenolol.txt"]

# Перебираем каждый файл
for file_name in files:
    # Полный путь к текущему файлу
    # file_path = os.path.join(folder_path, file_name)
    
    # Проверяем, является ли файл текстовым файлом
    if file_name.endswith('.txt'):
        # Открываем файл для чтения и записи
        with open(file_name, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Удаляем пустые строки
        lines = [line for line in lines if line.strip()]
        
        # Открываем файл для перезаписи
        with open(file_name, 'w', encoding='utf-8') as file:
            file.writelines(lines)

print("Пустые строки удалены.")
