from django.db import models


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


class TradeName(models.Model):
    """Торговое название ЛС."""
    
    name = models.CharField(max_length=MAX_LENGTH, unique=True, verbose_name='Торговое название')
    drug = models.ForeignKey('Drug', on_delete=models.CASCADE, related_name='trade_names')

    def __str__(self):
        return f'{self.name} ({self.drug})'


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

    side_effects = models.ManyToManyField('side_effects.SideEffect',
                                          through='side_effects.DrugSideEffect',
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


class DrugsAgeContraindications(models.Model):
    RESTRICTION_TYPES = [
        ('prohibited', 'Противопоказано'),
        ('caution', 'С осторожностью'),
    ]

    drug = models.ForeignKey(Drug, on_delete=models.CASCADE, related_name='age_restrictions')
    age_from = models.PositiveIntegerField(null=True, blank=True, verbose_name='Возраст от')
    age_to = models.PositiveIntegerField(null=True, blank=True, verbose_name='Возраст до')
    restriction_type = models.CharField(max_length=MAX_LENGTH, choices=RESTRICTION_TYPES, default='prohibited', verbose_name='Тип противопоказания')

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(age_from__isnull=True) | 
                    models.Q(age_to__isnull=True) | 
                    models.Q(age_from__lte=models.F('age_to'))
                ),
                name='valid_age_range'
            )
        ]

    def __str__(self):
        if self.age_from and self.age_to:
            return f'{self.drug.drug_name}: {self.age_from}-{self.age_to} лет'
        elif self.age_from:
            return f'{self.drug.drug_name}: от {self.age_from} лет'
        elif self.age_to:
            return f'{self.drug.drug_name}: до {self.age_to} лет'
        return f'{self.drug.drug_name}: возрастное ограничение'

