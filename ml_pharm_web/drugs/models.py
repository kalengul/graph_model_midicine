from django.db import models
from django.utils.text import slugify
from django.core.validators import (MinValueValidator,
                                    MaxValueValidator)


MAX_LENGTH = 255


class DrugGroup(models.Model):
    """Класс группы ЛС."""

    dg_name = models.CharField(max_length=MAX_LENGTH,
                               verbose_name="Название группы",
                               unique=True)
    slug = models.SlugField(max_length=MAX_LENGTH,
                            null=True,
                            unique=True,
                            db_index=True,
                            verbose_name="URL")

    def save(self, *args, **kwargs):
        """Сохранение группы ЛС."""
        if not self.slug:
            base_slug = slugify(self.dg_name)
            unique_slug = base_slug
            counter = 1

            while DrugGroup.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        """Строковое представление."""
        return self.dg_name

    class Meta:
        """Настройка модели."""

        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['dg_name']


class Drug(models.Model):
    """Класс ЛС."""

    drug_name = models.CharField(max_length=MAX_LENGTH,
                                 verbose_name='Название ЛС')
    slug = models.SlugField(max_length=MAX_LENGTH,
                            null=True,
                            unique=True,
                            db_index=True,
                            verbose_name="URL")
    drug_group = models.ForeignKey(DrugGroup,
                                   on_delete=models.CASCADE,
                                   related_name='drugs',
                                   verbose_name='Группа ЛС',
                                   default=1,
                                   null=True)
    side_effects = models.ManyToManyField('SideEffect',
                                          through='DrugSideEffect',
                                          related_name='drugs')

    def save(self, *args, **kwargs):
        """Сохранение группы ЛС."""
        if not self.slug:
            base_slug = slugify(self.drug_name)
            unique_slug = base_slug
            counter = 1

            while Drug.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1

            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        """Строковое представление."""
        return self.drug_name

    class Meta:
        """Настройка модели."""

        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['drug_name']


class SideEffect(models.Model):
    """Класс ПД."""

    se_name = models.CharField(max_length=MAX_LENGTH,
                               verbose_name="Побочный эффект")
    weight = models.FloatField(default=0.0,
                               verbose_name='Вес побочки',
                               validators=[
                                    MinValueValidator(0.0),
                                    MaxValueValidator(1.0)
                               ])

    def __str__(self):
        """Строковое представление."""
        return self.se_name


class DrugSideEffect(models.Model):
    """
    Класс для связи ЛС и ПД.

    Содержит связ с ЛС и ПД,
    а также ранги (веса или вероятности).
    """

    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    side_effect = models.ForeignKey(SideEffect, on_delete=models.CASCADE)
    # rang_s
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
    # в текущей версии веростностью
    # комент потом наверное можно убрать)))
    # rang_s = models.FloatField(
    #     validators=[
    #         MinValueValidator(0.0),
    #         MaxValueValidator(1.0)
    #     ]
    # )

    def __str__(self):
        """Строковое представление."""
        return (f"{self.drug.drug_name} - {self.side_effect.se_name}:"
                f"{self.probability}")

    class Meta:
        """Настройка модели."""

        unique_together = ('drug', 'side_effect')
        verbose_name = "Показатель побочного эффекта"
        verbose_name_plural = "Показатели побочных эффектов"
