"""Программа для экспериментов с библиотеками для преобразования pdf в docx."""
import pdfplumber
from docx import Document
import tabula


# Укажите путь к PDF-файлу с OCR-текстом и путь к выходному файлу DOCX
pdf_file = 'C:\\for the job\\Интсрукции ГРЛС\\Добутамин_ocr.pdf'
docx_file = 'Добутамин_ocr.docx'

# Создаем новый документ DOCX
doc = Document()

# Открываем PDF и извлекаем текст
try:
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:  # Если текст распознан
                doc.add_paragraph(text)
            # Извлечение таблиц на текущей странице

    # Сохраняем документ
    doc.save(docx_file)
    print(f'PDF успешно конвертирован в {docx_file}')
    # Извлечение таблиц из PDF
    tables = tabula.read_pdf(pdf_file, pages='all', multiple_tables=True)
    # Сохранение всех таблиц в CSV
    if tables:
        for i, table in enumerate(tables):
            table.to_csv(f'output_table_{i + 1}.csv', index=False)
        print(f"{len(tables)} таблиц(ы) успешно сохранены.")
    else:
        print("Таблицы не найдены.")
except Exception as e:
    print(f'Ошибка при извлечении текста: {e}')
