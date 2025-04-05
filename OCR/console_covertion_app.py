"""Консольное приложение для преобразование сканов в json."""

from pathlib import Path
import sys
from typing import Optional

from ocr_converter import OCRConverter
from dedoc_converter import DedocConverter
from saver import Saver
from json_saver import JSONSaver
from extractor import Extractor
from text_extrator import TextExtractor


class ScanConverter:
    """Класс приложения преобразованияю"""

    INPUT_PATH = 1
    OUTPUT_PATH = 2

    def __init__(self,
                 converter: OCRConverter,
                 saver: Saver,
                 extractor: Optional[Extractor] = None):
        self.converter = converter
        self.saver = saver
        self.extractor = extractor

        if len(sys.argv) > 3:
            raise ValueError("Ошибка: слишком много аргуметов!")
        elif len(sys.argv) < 2:
            raise ValueError('Ошибка: не введёно название файла!')
        else:
            self.input_path = Path(sys.argv[self.INPUT_PATH])

            if len(sys.argv) == 3:
                print('Есть второй аргумент!')
                self.output_path = Path(sys.argv[self.OUTPUT_PATH])
            else:
                self.output_path = self.input_path.with_suffix('.json')

    def convert_scan(self):
        """Метод конвертирования сканов."""
        try:
            if self.extractor:
                self.saver.save(
                    data=self.extractor.extract(
                        self.converter.convert(self.input_path)),
                    path=self.output_path)
            else:
                self.saver.save(data=self.converter.convert(self.input_path),
                                path=self.output_path)
            print('Скана успешно преобразован!')
        except Exception as error:
            print(f'Проблема преобразования: {error}')


def main():
    """Точка входа в программу."""
    try:
        scan_converter = ScanConverter(DedocConverter(),
                                       JSONSaver(),
                                       TextExtractor())
        scan_converter.convert_scan()
    except Exception as error:
        print(f'Ошибка: {error}')


if __name__ == '__main__':
    main()
