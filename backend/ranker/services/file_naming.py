"""Модуль наименования файлов."""

import os
import uuid

from django.utils.text import slugify


def generate_unique_filename(original_filename):
    """Генерация уникального названия для файла."""
    ext = os.path.splitext(original_filename)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    return unique_name
