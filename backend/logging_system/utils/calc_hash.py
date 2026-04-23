# logging_system/utils/calc_hash.py
import hashlib

def calculate_file_hash(file_obj):
    """Вычисляет MD5 хеш для любого файлового объекта (UploadedFile или обычный файл)."""
    md5 = hashlib.md5()
    file_obj.seek(0)
    # Проверяем, есть ли метод .chunks() (для UploadedFile)
    if hasattr(file_obj, 'chunks'):
        for chunk in file_obj.chunks():
            md5.update(chunk)
    else:
        for chunk in iter(lambda: file_obj.read(8192), b''):
            md5.update(chunk)
    file_obj.seek(0)
    return md5.hexdigest()