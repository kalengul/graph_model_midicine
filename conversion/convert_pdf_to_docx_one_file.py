import os


from tqdm import tqdm
from pdf2docx import Converter
import checking_pdf


def convert_pdf_to_docx(pdf_file, docx_file):

    # Создание объекта Converter
    cv = Converter(pdf_file)

    # Конвертация указанной страницы PDF в docx
    cv.convert(docx_file, start=0, end=None)
    cv.close()


def main():
    #PDF_DIR = 'C:\\for the job\\Интсрукции ГРЛС\\Амлодипин.pdf'
    print('введите путь к файлу')
    path_pdf = input('>')
    DOCX_DIR = 'инструкции ГРЛС в docx'     #\\Амлодипин.docx
    if checking_pdf.check_pdf_with_fitz(path_pdf):
        # Конвертация PDF в файл Docx
        file_name = path_pdf.split('\\')[-1].replace('pdf', 'docx')
        path_docx = os.path.join(DOCX_DIR, file_name)
        print('path_docx ', path_docx)
        convert_pdf_to_docx(path_pdf, path_docx)
    print('Работа программы успешно завершена!')


if __name__ == '__main__':
    main()
