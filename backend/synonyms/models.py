from django.db import models


NAME_MAX_LENGTH = 255
COLOR_MAX_LENGTH = 8


class SynonymGroup(models.Model):
    """Группа синонимов."""

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            unique=True,
                            verbose_name="Название группы")
    is_completed = models.BooleanField(default=False,
                                       verbose_name="Завершена")

    def __str__(self):
        return self.name

    class Meta:
        """Настройка."""

        ordering = ['name']
        verbose_name = "Группа синонимов"
        verbose_name_plural = "Группы синонимов"
    

class Synonym(models.Model):
    """Синоним."""

    name = models.CharField(max_length=NAME_MAX_LENGTH,
                            unique=True,
                            verbose_name="Слово")
    group = models.ForeignKey(SynonymGroup,
                              on_delete=models.CASCADE,
                              related_name='synonyms')
    is_changed = models.BooleanField(default=False,
                                     null=True,
                                     verbose_name="Удалено")
    st_id = models.ForeignKey(
                'SynonymStatus',
                on_delete=models.SET_NULL,
                null=True,
                blank=True,
                related_name='synonyms',
                verbose_name='Тип синонима'
            )

    def __str__(self):
        return self.name

    class Meta:
        """Настройка."""

        ordering = ['name']
        verbose_name = "Синоним"
        verbose_name_plural = "Синонимы"


class SynonymStatus(models.Model):
    """Статус синонима."""

    st_name = models.CharField(max_length=NAME_MAX_LENGTH,
                               unique=True,
                               verbose_name='название статуса синонима')
    st_code = models.CharField(max_length=COLOR_MAX_LENGTH,
                               verbose_name='цвет статуса')

    def __str__(self):
        return self.st_name

    class Meta:
        """Настройка."""

        ordering = ['st_name']
        verbose_name = 'Статус синонима'
        verbose_name_plural = 'Статусы синонимов'
