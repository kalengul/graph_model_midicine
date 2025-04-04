"""Модуль конвертера на основе dedoc."""

# from dedoc.api.dedoc_api import DedocAPI
from dedoc import DedocManager

from ocr_converter import OCRConverter


class DedocConverter(OCRConverter):
    """Конвертер на основе Dedoc."""

    # NEED_OCR = 'need_ocr'
    # OCR_LANG = 'ocr_language'

    def __init__(self):
        self.dedoc_manager = DedocManager()

    def convert(self, path, need_ocr='true', ocr_lang=None):
        """Метод преобразования содержания файла."""
        # parameters = {
        #     self.NEED_OCR: need_ocr
        # }
        # if ocr_lang:
        #     parameters[self.OCR_LANG] = ocr_lang

        try:
            return self.dedoc_manager.parse(path).to_api_schema().model_dump()
            # return self.convert_to_dict(self.dedoc_manager.parse(
            #     path,
            #     parameters=parameters))
        except FileNotFoundError:
            raise Exception(("Проблема открытия файла!"
                             "Убедитель в его наличии."))
        except ValueError as error:
            raise Exception((f"Ошибка фортама файла! {error}"
                             "Убедитель, что файл правильного формата."))
        except PermissionError:
            raise Exception(("Ошибка доступа!"
                             "Убедитель, что есть разрешение"
                             "на доступ к файлу."))
        except Exception as error:
            raise Exception(f"Не предвиденная ошибка! {error}")
