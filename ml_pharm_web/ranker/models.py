from django.db import models


MAX_LENGTH = 255


class DrugCHF(models.Model):
    """Класс ЛС ХСН."""

    index = models.IntegerField(unique=True)
    name = models.CharField(max_length=MAX_LENGTH)

    def __str__(self):
        """Строковое представление."""
        return self.name


class DiseaseCHF(models.Model):
    """Класс болезни ХСН."""

    index = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=MAX_LENGTH)
    value = models.FloatField()

    def __str__(self):
        """Строковое представление."""
        return f"{self.index} - {self.name} ({self.value})"
