from django.db import models


class SynonymGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название группы")
    is_completed = models.BooleanField(default=False, verbose_name="Завершена")

    def __str__(self):
        return self.name
    

class Synonym(models.Model):
    name = models.CharField(max_length=255, verbose_name="Слово")
    group = models.ForeignKey(SynonymGroup, on_delete=models.CASCADE, related_name='synonyms')
    is_changed = models.BooleanField(default=False, verbose_name="Удалено")

    def __str__(self):
        return self.name
    