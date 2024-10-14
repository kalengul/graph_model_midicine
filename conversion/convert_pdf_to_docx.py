"""Модуль конвертирования pdf-файлов в docx-файлы."""
import os
from typing import Final


from tqdm import tqdm
from pdf2docx import Converter
import checking_pdf


PDF_DIR: Final[str] = 'C:\\for the job\\Интсрукции ГРЛС'
DOCX_DIR: Final[str] = 'инструкции ГРЛС в docx'


def convert_pdf_to_docx(pdf_file: str, docx_file: str) -> None:
    """Функция ковертирования pdf-файлов в docx-файлы."""
    # Создание объекта Converter
    cv = Converter(pdf_file)

    # Конвертация указанной страницы PDF в docx
    cv.convert(docx_file, start=0, end=None)
    cv.close()


def main() -> None:
    """Тело программы."""
    pdf_files = os.listdir(PDF_DIR)
    for pdf_file in tqdm(pdf_files, ncols=80):
        docx_file: str = os.path.join(DOCX_DIR, pdf_file.replace('.pdf',
                                                                 '.docx'))
        pdf_full_file_name: str = os.path.join(PDF_DIR, pdf_file)
        if checking_pdf.check_pdf_with_fitz(pdf_full_file_name):
            # Конвертация PDF в файл Docx
            convert_pdf_to_docx(pdf_full_file_name, docx_file)
    print('Работа программы успешно завершена!')


if __name__ == '__main__':
    main()
