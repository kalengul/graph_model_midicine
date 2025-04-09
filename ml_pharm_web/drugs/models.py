from django.db import models


MAX_LENGTH = 255


class DrugGroup(models.Model):
    title = models.CharField(max_length=MAX_LENGTH, verbose_name="Название группы")
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['title']


class Drug(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, verbose_name='Название лекарственного средства')
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True, db_index=True, verbose_name="URL")
    drug_group = models.ForeignKey('DrugGroup', null=True, on_delete=models.CASCADE,
                           verbose_name='Группа лекарственных средств')
    side_effects = models.ManyToManyField('SideEffect', through='DrugSideEffect', related_name='drugs')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['name']


class SideEffect(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, verbose_name="Побочный эффект")

    def __str__(self):
        return self.name


class DrugSideEffect(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    side_effect = models.ForeignKey(SideEffect, on_delete=models.CASCADE)
    probability = models.FloatField(default=0.0, verbose_name="Коэффициент появления")

    class Meta:
        unique_together = ('drug', 'side_effect')
        verbose_name = "Показатель побочного эффекта"
        verbose_name_plural = "Показатели побочных эффектов"

    def __str__(self):
        return f"{self.drug.name} - {self.side_effect.name}: {self.probability}"
