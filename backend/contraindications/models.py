from django.db import models


MAX_LENGTH = 255


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
