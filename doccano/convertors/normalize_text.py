import re

def normalize_text(text):

    # Удаляем лишние пробелы и символы
    text = re.sub(r' +\,', ',', text)
    text = re.sub(r' +\.', '.', text)
    text = re.sub(r' +\:', ':', text)
    text = re.sub(r' +\;', ';', text)
    text = re.sub(r' - ', '-', text)
    text = re.sub(r' +\)', ')', text)
    text = re.sub(r'\( +', '(', text)
    text = re.sub(r'\,\.', '.', text)
    text = re.sub(r'\n\n+', '\n', text)

    # Дополнительная обработка
    text = re.sub(r'\[\s+', '[', text)
    text = re.sub(r'\s+\]', ']', text)
    text = re.sub(r'«\s+', '«', text)
    text = re.sub(r'\s+»', '»', text)
    text = re.sub(r'\s*/\s*', '/', text)
    text = re.sub(r'T\s+1/2', 'T1/2', text)
    text = re.sub(r'Т\s+1/2', 'T1/2', text)
    text = re.sub(r'C\s+max', 'Cmax', text)
    text = re.sub(r'С\s+max', 'Cmax', text)

    return text