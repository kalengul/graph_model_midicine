from django.db import models


class Graph(models.Model):
    """Модель графа."""

    name = models.CharField(max_length=100,
                            verbose_name='Название семантического графа')
    graph_json = models.JSONField(
        verbose_name='Семантический граф в формате JSON')
    graph_xml = models.TextField(
        null=True,
        verbose_name='Семантический граф в формате XML')

    def __str__(self):
        """Вывод информации от семантическом графе."""
        return self.name

    class Meta:
        """Настройка графов."""

        ordering = ['name']
