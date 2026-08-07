"""
logging_system\models.py
"""

from django.db import models
from logging_system.utils.get_current_commit_hash import get_current_commit_hash

class SystemState(models.Model):
    """Хранит состояние системы: версии загруженных файлов и настройки логирования."""
    
    # Настройки логирования
    logging_enabled = models.BooleanField(default=True, verbose_name="Логирование включено")
    
    # Информация о файле препаратов
    drugs_file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя файла препаратов")
    drugs_file_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name="Хеш файла препаратов")
    drugs_file_uploaded_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата загрузки файла препаратов")
    
    # Информация о файле весов
    weights_file_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Имя файла весов")
    weights_file_hash = models.CharField(max_length=64, blank=True, null=True, verbose_name="Хеш файла весов")
    weights_file_uploaded_at = models.DateTimeField(blank=True, null=True, verbose_name="Дата загрузки файла весов")
    
    # Время последнего обновления состояния
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Последнее обновление")

    # Версия проекта
    commit_hash = models.CharField(max_length=40, blank=True, null=True, verbose_name="Хэш коммита")
    
    class Meta:
        verbose_name = "Состояние системы"
        verbose_name_plural = "Состояния системы"
    
    def __str__(self):
        return f"Состояние от {self.updated_at}"
    
    @classmethod
    def get_current_state(cls):
        """Возвращает текущее состояние (создаёт, если не существует), обновляя хэш коммита."""
        state, _ = cls.objects.get_or_create(id=1)
        # Обновляем хэш коммита, если он изменился
        current_commit = get_current_commit_hash()
        if current_commit and state.commit_hash != current_commit:
            state.commit_hash = current_commit
            state.save(update_fields=['commit_hash'])
        return state