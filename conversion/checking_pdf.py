"""Модуль для проверки pdf-файлов на наличие распознанных текстов."""
import PyPDF2
import pdfplumber
import fitz  # PyMuPDF


def check_pdf_for_text(file_path: str) -> bool:
    """Функция проверки с использованием библиотеки PyPDF2."""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text and text.strip():  # Проверяем, есть ли текст на странице
                return True
        return False


def check_pdf_with_pdfplumber(file_path: str) -> bool:
    """Функция проверки с использованием библиотеки pdfplumber."""
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text and text.strip():  # Если текст есть на странице
                return True
        return False


def check_pdf_with_fitz(file_path: str) -> bool:
    """Функция проверки с использованием библиотеки fitz."""
    doc = fitz.open(file_path)
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        if text.strip():
            return True
    return False


def main() -> None:
    """Тело программы. Нужно для текстирования и отладки."""
    pdf_path: str = 'Амиодарон.pdf'
    # pdf_path = 'Амлодипин.pdf'
    result: bool = check_pdf_for_text(pdf_path)
    print(result)
    result = check_pdf_with_pdfplumber(pdf_path)
    print(result)
    result = check_pdf_with_fitz(pdf_path)
    print(result)


if __name__ == '__main__':
    main()
