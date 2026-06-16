from django.db import models


MAX_LENGTH = 1024


class Contraindication(models.Model):
    """Противопоказания."""

    name = models.CharField(max_length=MAX_LENGTH,
                            unique=True,
                            verbose_name='Название противопоказания')
    weight = models.FloatField(default=0.0,
                               verbose_name='Вес противопоказания')
    node_target = models.CharField(max_length=MAX_LENGTH,
                                   null=True,
                                   blank=True,
                                   verbose_name='Соседняя вершина')

    def __str__(self):
        """Вывод информации о противопоказании."""
        return f'{self.name} - {self.weight}'

    class Meta:
        """Настройка противопоказаний."""

        ordering = ['name']

class OriginalContraindication(models.Model):
    """Оригинальное название противопоказания (синоним)."""
    
    name = models.CharField(max_length=MAX_LENGTH,
                            unique=True,
                            verbose_name='Оригинальное название')
    standard = models.ForeignKey(Contraindication,
                                 on_delete=models.CASCADE,
                                 related_name='original_names',
                                 verbose_name='Соответствует стандартному названию')

    def __str__(self):
        return f'{self.name} -> {self.standard.name}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Оригинальное название'
        verbose_name_plural = 'Оригинальные названия'
