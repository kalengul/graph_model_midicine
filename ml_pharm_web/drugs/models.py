from django.db import models
from django.utils.text import slugify


MAX_LENGTH = 255


class DrugGroup(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, verbose_name="Название группы")
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True, db_index=True, verbose_name="URL")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            
            while DrugGroup.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
                
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['name']


class Drug(models.Model):
    name = models.CharField(max_length=MAX_LENGTH, verbose_name='Название ЛС')
    slug = models.SlugField(max_length=MAX_LENGTH, unique=True, db_index=True, verbose_name="URL")
    drug_group = models.ForeignKey(DrugGroup, on_delete=models.CASCADE, 
                                  related_name='drugs', verbose_name='Группа ЛС')
    side_effects = models.ManyToManyField('SideEffect', through='DrugSideEffect', related_name='drugs')

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            unique_slug = base_slug
            counter = 1
            
            while Drug.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
                
            self.slug = unique_slug
        super().save(*args, **kwargs)

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
