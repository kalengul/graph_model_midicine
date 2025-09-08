from django.db import models


class Graph(models.Model):
    """Модель графа."""

    name = models.CharField(max_length=100)
    graph_json = models.JSONField()
    graph_xml = models.TextField(null=True)

    def __str__(self):
        return self.name
