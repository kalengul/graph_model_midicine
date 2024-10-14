import PyPDF2


def check_struture(file_name):
    with open(file_name, 'rb') as file:  # Открытие PDF файла в режиме чтения байтов
        reader = PyPDF2.PdfReader(file)  # Создание объекта для чтения PDF
        num_pages = len(reader.pages)    # Получение количества страниц
        print(f"Количество страниц: {num_pages}")  # Вывод количества страниц

    
def main():
    print('введите путь к файлу')
    file_name = input('>')
    check_struture(file_name)
    print('Работы программы успешно завершена!')


if __name__ == '__main__':
    main()