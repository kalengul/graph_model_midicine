import glob
import pandas as pd
import tabula

# def extract_adverse_effects(pdf_path):
#     # Открываем PDF-документ
#     document = fitz.open(pdf_path)
#     adverse_text = ""
#     collecting = False
#     tables_found = False
#     table_rows = []

#     # Регулярные выражения для поиска заголовков
#     adverse_effects_pattern = re.compile(r'(?i)\bпобочное действие\b')
#     overdose_pattern = re.compile(r'(?i)\bпередозировка\b')

#     # Список ключевых строк для таблицы
#     table_headers = ["Класс систем органов", "Частота", "Нежелательные явления"]
    
#     # Проходим по всем страницам
#     for page_num in range(len(document)):
#         page = document.load_page(page_num)
#         page_text = page.get_text("text")

#         # Проверяем, содержит ли страница текст
#         if not page_text.strip():
#             continue

#         # Ищем начало раздела "Побочное действие"
#         if adverse_effects_pattern.search(page_text):
#             collecting = True

#         # Если мы находимся в нужном разделе, собираем текст
#         if collecting:
#             adverse_text += page_text

#             # Ищем таблицы на текущей странице
#             blocks = page.get_text("dict")["blocks"]
#             for block in blocks:
#                 if block["type"] == 0:  # Текстовый блок
#                     lines = block["lines"]
#                     if len(lines) > 1:  # Предполагаем, что таблица имеет более одной строки
#                         # print(lines)
#                         # Составляем список строк для текущего блока
#                         block_lines = []
#                         for line in lines:
#                             row = [span["text"] for span in line["spans"]]  # Собираем текст из всех ячеек строки
#                             print(row) 
#                             block_lines.append(row)

#                         # Проверка, есть ли в строках заголовки таблицы
#                         block_text = " ".join([text for line in block_lines for text in line])
#                         if all(header in block_text for header in table_headers):
#                             tables_found = True
                            
#                             # Строим строки таблицы
#                             for line in block_lines:
#                                 table_rows.append(line)

#         # Проверяем конец раздела "Побочное действие"
#         if overdose_pattern.search(page_text):
#             break

#     if not adverse_text:
#         return "Раздел 'Побочное действие' не найден."

#     result = f"Текст раздела 'Побочное действие':\n{adverse_text.strip()}\n\n"
    
#     # Выводим таблицу, если она найдена
#     if tables_found:
#         result += "В разделе найдена таблица:\n"
#         for row in table_rows:
#             result += " | ".join(row) + "\n"
#     else:
#         result += "В разделе таблицы не найдены."
    
#     return result



def extract_and_combine_tables(pdf_path):
    # Извлекаем таблицы с использованием обоих режимов: lattice и stream.
    tables = tabula.read_pdf(pdf_path, pages="all", multiple_tables=True)  # Используем lattice

    # Если таблицы все равно не извлечены, возвращаем None
    if not tables:
        return None

    # Список для хранения подходящих таблиц
    filtered_tables = []

    indx = 0
    searched_columns = ["Класс систем органов", "Частота", "Нежелательные явления"]

    # Проходим по всем таблицам
    for idx, table in enumerate(tables):
        if isinstance(table, pd.DataFrame) and len(table.columns) == 3 :
            # Сохраняем заголовки в переменную
            columns = table.columns.tolist()
            
            # Добавляем таблицу в список отфильтрованных таблиц
            if all(col in columns for col in searched_columns):
                filtered_tables.append(table)
                indx = idx
                break

    # Если таблица с нужными колонками не найдена, возвращаем None
    if not filtered_tables:
        return None
    
    # # Извлекаем заголовки из первой найденной таблицы
    # column_names = filtered_tables[0].columns

    for table in tables[indx + 1:]:
        if isinstance(table, pd.DataFrame) and len(table.columns) == 3:


            columns = table.columns.tolist()
            table.loc[-1] = columns                 # Добавляем старые заголовки как строку данных
            table = table.sort_index()              # Сортируем по индексу, чтобы первая строка была на первом месте


            table.columns = searched_columns
            filtered_tables.append(table)
        else:
            break

    
    # Объединяем все найденные таблицы в одну
    # combined_table = pd.concat(filtered_tables, ignore_index=True)

    # combined_table = pd.DataFrame()
    # for table in filtered_tables:
    #     combined_table = pd.concat([combined_table, table])


    import numpy as np

    for table in filtered_tables:
        # Переименовываем все столбцы, начинающиеся с "Unnamed"
        table.iloc[0] = [
            cell if isinstance(cell, str) and not cell.startswith('Unnamed') else np.nan
            for cell in table.iloc[0]
        ]

    combined_table = pd.concat(filtered_tables, ignore_index=True)
    # print(combined_table)
    return combined_table

# if __name__ == "__main__":

#     # Пример использования
#     pdf_path = "data\\Инструкции ГРЛС\\Эсциталопрам.pdf"
#     combined_table = extract_and_combine_tables(pdf_path)

#     # Если таблица найдена, выводим ее
#     if combined_table is not None:
#         print("Объединенная таблица с нужными колонками:")
#         print(combined_table)
#     else:
#         print("Таблицы с нужными колонками не найдены в файле.")
    


if __name__ == "__main__":

    # Пример использования
    pdf_path = "data\\Инструкции ГРЛС\\Эсциталопрам.pdf"
    combined_table = extract_and_combine_tables(pdf_path)

    print(combined_table)

    # if isinstance(combined_table, pd.DataFrame):
    #     if not combined_table.empty:
    #         for idx, table in enumerate(combined_table):
    #             print(f"Таблица {idx + 1}:")
    #             print(table)
    #             print("\n" + "-"*50 + "\n")

    # if isinstance(combined_table, list):
    #     if combined_table:
    #         for idx, table in enumerate(combined_table):
    #             print(f"Таблица {idx + 1}:")
    #             print(table)
    #             print("\n" + "-"*50 + "\n")

    # # Если таблица найдена, выводим ее
    # if combined_table is not None:
    #     print("Объединенная таблица с нужными колонками:")
    #     print(combined_table)
    # else:
    #     print("Таблицы с нужными колонками не найдены в файле.")
