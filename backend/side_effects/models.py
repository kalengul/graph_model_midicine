from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from drugs.models import Drug

MAX_LENGTH = 255


class SideEffect(models.Model):
    """Класс ПД."""

    id = models.PositiveIntegerField(primary_key=True, editable=False)
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
    is_life_threatening = models.BooleanField(default=True,
                                              verbose_name='Жизнеугрожающий'
                                              )

    def __str__(self):
        """Строковое представление."""
        return self.se_name

    def save(self, *args, **kwargs):
        """Сохранение ПД."""
        if not self.pk:
            max_id = (
                SideEffect.objects.aggregate(models.Max('id'))['id__max']
                or 0)
            self.id = max_id + 1
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


class SideEffectsGender(models.Model):
    GENDER_CHOICES = [
        ('woman', 'женщина'),
        ('man', 'мужчина'),
    ]

    side_effect = models.ForeignKey(SideEffect, on_delete=models.CASCADE, related_name='se_gender')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, verbose_name='пол')

    class Meta:
        unique_together = [['side_effect', 'gender']]

    def __str__(self) -> str:
        return f'{self.side_effect.se_name} - {self.gender}'

