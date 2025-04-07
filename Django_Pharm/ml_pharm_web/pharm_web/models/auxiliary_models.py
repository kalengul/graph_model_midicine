"""Модуль вспомогательных данных из файлов."""

from django.db import models
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator)


MAX_LENGTH = 255


class Medication(models.Model):
    """Класс ЛС."""

    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name="Название ЛС")

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class SideEffect(models.Model):
    """Класс ПД."""

    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name='Название ПД')
    weight = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class MedicationSideEffect(models.Model):
    """Класс коэфециентов ПД ЛС."""

    medication = models.ForeignKey(Medication,
                                   on_delete=models.CASCADE,
                                   related_name='side_effrects')
    side_effect = models.ForeignKey(SideEffect,
                                    on_delete=models.CASCADE,
                                    related_name='medications')
    rang_base = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )
    rang_f1 = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(2.0)
        ]
    )
    rang_f2 = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(2.0)
        ]
    )
    rang_freq = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )
    rang_m1 = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(2.0)
        ]
    )
    rang_m2 = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(2.0)
        ]
    )
    rang_s = models.FloatField(
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ]
    )

    def __str__(self):
        return f'{self.medication} - {self.side_effect}'

    class Meta:
        unique_together = ('medication', 'side_effect')
