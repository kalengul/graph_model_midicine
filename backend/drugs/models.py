from django.db import models
from django.utils.text import slugify
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator)


MAX_LENGTH = 255


class DrugGroup(models.Model):
    """Класс группы ЛС."""

    dg_name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name="Название группы",
        unique=True
    )

    def __str__(self):
        return self.dg_name

    class Meta:
        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['dg_name']


class Nosology(models.Model):
    """Нозология ЛС"""
    id = models.AutoField(primary_key=True, editable=False)
    name = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name="Название подгруппы",
        unique=True
    )
    
    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Подгруппа ЛС'
        verbose_name_plural = 'Подгруппы ЛС'
        ordering = ['name']


class Drug(models.Model):
    """Класс ЛС."""

    id = models.AutoField(primary_key=True, editable=False)
    drug_name = models.CharField(max_length=MAX_LENGTH,
                                 verbose_name='Название ЛС',
                                 unique=True)
    
    drug_groups = models.ManyToManyField(
        DrugGroup,
        related_name='drugs',
        verbose_name='Фармакологические группы',
        blank=True
    )

    nosology = models.ForeignKey(
        Nosology,
        on_delete=models.SET_NULL,
        related_name='drugs',
        verbose_name='Нозология',
        null=True
    )

    side_effects = models.ManyToManyField('SideEffect',
                                          through='DrugSideEffect',
                                          related_name='drugs')
    contraindications = models.ManyToManyField(
        'contraindications.Contraindication',
        related_name='drugs')

    def __str__(self):
        return self.drug_name

    class Meta:
        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['drug_name']


class SideEffect(models.Model):
    """Класс ПД."""

    index = models.PositiveIntegerField(editable=False)
    se_name = models.CharField(max_length=MAX_LENGTH,
                               verbose_name="Побочный эффект",
                               unique=True)
    se_name_en = models.CharField(max_length=MAX_LENGTH,
                                  verbose_name='Side effect',
                                  unique=True,
                                  blank=True,
                                  null=True)
    weight = models.FloatField(default=0.0,
                               verbose_name='Вес побочки',
                               validators=[
                                    MinValueValidator(0.0),
                                    MaxValueValidator(1.0)
                               ])

    def __str__(self):
        """Строковое представление."""
        return self.se_name

    def save(self, *args, **kwargs):
        """Сохранение ПД."""
        if not self.pk:
            max_index = (
                SideEffect.objects.aggregate(models.Max('index'))['index__max']
                or 0)
            self.index = max_index + 1
        super().save(*args, **kwargs)

    class Meta:
        """Настройка модели ПД."""

        verbose_name = 'ПД'
        verbose_name_plural = 'ПД'
        ordering = ['se_name']


class DrugSideEffect(models.Model):
    """
    Класс для связи ЛС и ПД.

    Содержит связь с ЛС и ПД,
    а также ранги (веса или вероятности).
    """

    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    side_effect = models.ForeignKey(SideEffect, on_delete=models.CASCADE)
    probability = models.FloatField(default=0.0,
                                    verbose_name="Коэффициент появления",
                                    validators=[
                                        MinValueValidator(0.0),
                                        MaxValueValidator(1.0)
                                    ])
    rang_base = models.FloatField(default=0.0,
                                  verbose_name='Основной рангах',
                                  validators=[
                                      MinValueValidator(0.0),
                                      MaxValueValidator(1.0)
                                  ])
    rang_f1 = models.FloatField(default=0.0,
                                verbose_name='Ранг для женщин до 65 лет',
                                validators=[
                                    MinValueValidator(0.0),
                                    MaxValueValidator(2.0)
                                ])
    rang_f2 = models.FloatField(default=0.0,
                                verbose_name='Ранг для женщин после 65 лет',
                                validators=[
                                    MinValueValidator(0.0),
                                    MaxValueValidator(2.0)
                                ])
    rang_freq = models.FloatField(default=0.0,
                                  verbose_name='Ранг частоты.',
                                  validators=[
                                      MinValueValidator(0.0),
                                      MaxValueValidator(1.0)
                                  ])
    rang_m1 = models.FloatField(default=0.0,
                                verbose_name='Ранг для мужчин до 65 лет',
                                validators=[
                                    MinValueValidator(0.0),
                                    MaxValueValidator(2.0)
                                ])
    rang_m2 = models.FloatField(default=0.0,
                                verbose_name='Ранг для мужчин после 65 лет',
                                validators=[
                                    MinValueValidator(0.0),
                                    MaxValueValidator(2.0)
                                ])

    def __str__(self):
        """Строковое представление."""
        return (f"{self.drug.drug_name} - {self.side_effect.se_name}:"
                f"{self.probability}")

    class Meta:
        """Настройка модели."""

        ordering = ['drug__id', 'side_effect__id']
        unique_together = ('drug', 'side_effect')
        verbose_name = "Показатель побочного эффекта"
        verbose_name_plural = "Показатели побочных эффектов"


class BannedDrugPair(models.Model):
    """Пара ЛС."""

    first_drug = models.CharField(max_length=MAX_LENGTH,
                                  verbose_name='Первое ЛС')
    second_drug = models.CharField(max_length=MAX_LENGTH,
                                   verbose_name='Второе ЛС')
    comment = models.TextField(null=True,
                               blank=True,
                               verbose_name='Комментарий')

    def __str__(self):
        """Вывод информации о паре ЛС."""
        return f'Пара ЛС: {self.first_drug} и {self.second_drug}'

    class Meta:
        """Настройка."""

        ordering = ['first_drug', 'second_drug']
        unique_together = ['first_drug', 'second_drug']
