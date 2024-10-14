import subprocess


# Применение OCRmyPDF
subprocess.run(['ocrmypdf',
                '-l', 'rus+eng',  # Используем русский и английский язык
                '--output-type', 'pdfa-2',  # Тип выходного файла
                '--deskew',  # Исправление наклона
                '--rotate-pages',  # Автоматическое вращение страниц
                '--tesseract-oem', '1',  # Используем LSTM OCR Engine для более точного распознавания
                '--image-dpi', '350',  # Устанавливаем разрешение изображения в 300 DPI
                #'--optimize', '2',
                #'--pdfa-image-compression', 'lossless',
                'C:\\for the job\\Интсрукции ГРЛС\\Добутамин.pdf',
                'C:\\for the job\\Интсрукции ГРЛС\\Добутамин_ocr.pdf'])
print('Работа программы успешно завершина!')
