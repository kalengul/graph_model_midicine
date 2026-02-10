# pHistory2se/docx_parser.py
import docx
import io
from typing import List, Dict


class SimpleDocxParser:
    """Простой парсер .docx файлов."""
    
    @staticmethod
    def extract_text(file_obj: io.BytesIO) -> str:
        """Извлекает весь текст из .docx файла."""
        try:
            doc = docx.Document(file_obj)
            # Собираем текст из всех параграфов
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs)
        except Exception as e:
            raise ValueError(f"Ошибка чтения .docx файла: {str(e)}")