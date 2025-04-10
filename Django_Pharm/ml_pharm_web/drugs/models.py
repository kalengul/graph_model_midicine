from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class DrugGroup(models.Model):
    """Модель группы ЛС."""
    title = models.CharField(max_length=255, verbose_name="Название группы")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255,
                            unique=True,
                            db_index=True,
                            verbose_name="URL")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('DrugGroup', kwargs={'DrugGroup_slug': self.slug})

    class Meta:
        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['title']


class Drug(models.Model):
    """Модель ЛС."""

    name = models.CharField(max_length=255,
                            verbose_name='Название лекарственного средства')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    pg = models.ForeignKey('DrugGroup', null=True, on_delete=models.CASCADE,
                           verbose_name='Группа лекарственных средств')
    user = models.ForeignKey(User,
                             verbose_name='Пользователь',
                             on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255,
                            unique=True,
                            db_index=True, verbose_name="URL")
    side_effects = models.ManyToManyField('SideEffect',
                                          through='DrugSideEffect',
                                          related_name='drugs')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Drug', kwargs={'Drug_slug': self.slug})

    class Meta:
        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['name']


class SideEffect(models.Model):
    """Модель ПД."""

    name = models.CharField(max_length=255, verbose_name="Побочный эффект")

    def __str__(self):
        return self.name


class DrugSideEffect(models.Model):
    """Модель для работы рангами (вероятностями)"""

    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    side_effect = models.ForeignKey(SideEffect, on_delete=models.CASCADE)
    probability = models.FloatField(default=0.0,
                                    verbose_name="Коэффициент появления")

    class Meta:
        unique_together = ('drug', 'side_effect')
        verbose_name = "Показатель побочного эффекта"
        verbose_name_plural = "Показатели побочных эффектов"

    def __str__(self):
        return f"{self.drug.name} - {self.side_effect.name}: {self.probability}"
