"""Модуль основных моделей."""

from django.contrib.auth.models import User
from django.db import models

# Create your models here.
# Импорт модуля models из библиотеки Django
from django.db import models
from django.urls import reverse

class DrugGroup(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название группы")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('DrugGroup', kwargs={'DrugGroup_slug': self.slug})

    class Meta:
        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['title']

class Drug(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название лекарственного средства')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    pg = models.ForeignKey('DrugGroup', null=True, on_delete=models.CASCADE,
                           verbose_name='Группа лекарственных средств')
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('Drug', kwargs={'Drug_slug': self.slug})

    class Meta:
        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['name']


class UserGroupAll(models.Model):
    group_name = models.CharField(max_length=255)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.group_name

    def get_absolute_url(self):
        return reverse('UserGroupAll', kwargs={'UserGroupAll_slug': self.slug})


class UserInGroup(models.Model):
    user_group = models.ForeignKey('UserGroupAll', null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")

    def __str__(self):
        return self.id

    def get_absolute_url(self):
        return reverse('UserInGroup', kwargs={'UserInGroup_slug': self.slug})


class ml_model(models.Model):
    name_model = models.CharField(max_length=255, verbose_name="Название модели")
    description = models.TextField(verbose_name="Описание модели")
    autor = models.CharField(max_length=255, verbose_name="Автор")
    user_group = models.ForeignKey('UserGroupAll', null=True, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=255, unique=True, db_index=True, verbose_name="URL")
    New_name= models.CharField(max_length=255)
    is_visible = models.BooleanField(default=True)  # Добавляем поле is_visible

    def __str__(self):
        return self.name_model

    def get_absolute_url(self):
        return reverse('show_model', kwargs={'ml_model_slug': self.slug})

    class Meta:
        verbose_name = 'Модель'
        verbose_name_plural = 'Модели'
        ordering = ['time_update']


class DrugInteractionTable(models.Model):
    DrugOne = models.ForeignKey('Drug', null=True, on_delete=models.CASCADE, verbose_name='ЛС №1',
                                related_name='druginteractions_one')
    DrugTwo = models.ForeignKey('Drug', null=True, on_delete=models.CASCADE, verbose_name='ЛС №2',
                                related_name='druginteractions_two')
    Interaction = models.TextField(verbose_name="Взаимодействие")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.Interaction

    def get_absolute_url(self):
        return reverse('DrugInteractionTable', kwargs={'DrugInteractionTable_slug': self.slug})

    class Meta:
        verbose_name = 'Взаимодействие ЛС (Таблица)'
        verbose_name_plural = 'Взаимодействие ЛС (Таблица)'
        ordering = ['DrugOne']



class Type_Drugs_MedScape(models.Model):
    Type_en = models.CharField(max_length=255, verbose_name='Type Drug')
    Type_ru = models.CharField(max_length=255, verbose_name='Тип ЛС')

    def __str__(self):
        return self.Type_en

    def get_absolute_url(self):
        return reverse('Type_Drugs_MedScape', kwargs={'Type_Drugs_MedScape_slug': self.slug})

    class Meta:
        verbose_name = 'Тип ЛС MedScape'
        ordering = ['Type_en']


class Name_Drugs_MedScape(models.Model):
    Name_en = models.CharField(max_length=255, verbose_name='Name Drug')
    Name_ru = models.CharField(max_length=255, verbose_name='Название ЛС')
    Group_Type = models.ManyToManyField('Type_Drugs_MedScape')  # Связь много ко многим с типом лекарственного средства

    def __str__(self):
        return self.Name_en

    def get_absolute_url(self):
        return reverse('Name_Drugs_MedScape', kwargs={'Name_Drugs_MedScape_slug': self.slug})

    class Meta:
        verbose_name = 'МНН ЛС MedScape'
        ordering = ['Name_en']


class Source_Drugs_MedScape(models.Model):
    Source = models.CharField(max_length=10000, verbose_name='Источник')

    def __str__(self):
        return self.Source

    def get_absolute_url(self):
        return reverse('Source_Drugs_MedScape', kwargs={'Source_Drugs_MedScape': self.slug})

    class Meta:
        verbose_name = 'Источник информации о ЛС MedScape'
        ordering = ['Source']


class Warnings_MedScape(models.Model):
    warnings_name_en = models.CharField(max_length=10000, verbose_name='Warnings')
    warnings_name_ru = models.CharField(max_length=10000, verbose_name='Опасность')
    warnings_type = models.CharField(max_length=10000, verbose_name='Тип опасности')

    def __str__(self):
        return self.warnings_type

    def get_absolute_url(self):
        return reverse('Warnings_MedScape', kwargs={'Warnings_MedScape': self.slug})

    class Meta:
        verbose_name = 'Опасность применения  ЛС MedScape'
        ordering = ['warnings_type']


class Adverse_Effects_MedScape(models.Model):
    adverse_effects_name_en = models.CharField(max_length=10000, verbose_name='Adverse Effects')
    adverse_effects_name_ru = models.CharField(max_length=10000, verbose_name='Побочное действие')
    adverse_effects_percent = models.CharField(max_length=10000, verbose_name='Процент')

    def __str__(self):
        return self.adverse_effects_name_en

    def get_absolute_url(self):
        return reverse('Adverse_Effects_MedScape', kwargs={'Adverse_Effects_MedScape': self.slug})

    class Meta:
        verbose_name = 'Побочные эффекты ЛС MedScape'
        ordering = ['adverse_effects_percent']


class Pregnancy_and_lactation_MedScape(models.Model):
    Pregnancy_common_en = models.CharField(max_length=10000, verbose_name='Pregnancy_common')
    Pregnancy_specific_en = models.CharField(max_length=10000, verbose_name='Pregnancy_specific')
    Lactation_common_en = models.CharField(max_length=10000, verbose_name='Lactation_common')
    Lactation_specific_en = models.CharField(max_length=10000, verbose_name='Lactation_specific')
    Pregnancy_common_ru = models.CharField(max_length=10000, verbose_name='Беременность')
    Pregnancy_specific_ru = models.CharField(max_length=10000, verbose_name='Конкретные рекомендации для беременных')
    Lactation_common_ru = models.CharField(max_length=10000, verbose_name='Грудное вскармливание')
    Lactation_specific_ru = models.CharField(max_length=10000,
                                             verbose_name='Конкретные рекомендации для грудного вскармливания')

    def __str__(self):
        return self.Pregnancy_common_en

    def get_absolute_url(self):
        return reverse('Pregnancy_and_lactation_MedScape', kwargs={'Pregnancy_and_lactation_MedScape': self.slug})

    class Meta:
        verbose_name = 'Лактация ЛС MedScape'


class Interaction_MedScape(models.Model):
    interaction_with = models.ForeignKey('Name_Drugs_MedScape', on_delete=models.DO_NOTHING)
    classification_type_en = models.CharField(max_length=255, verbose_name='Classification Interaction')
    classification_type_ru = models.CharField(max_length=255, verbose_name='Классификация взаимодействия')
    description_en = models.CharField(max_length=10000, verbose_name='Description')
    description_ru = models.CharField(max_length=10000, verbose_name='Описание')

    def __str__(self):
        return self.classification_type_en

    def get_absolute_url(self):
        return reverse('Interaction_MedScape', kwargs={'Interaction_MedScape': self.slug})

    class Meta:
        verbose_name = 'Взаимодействие ЛС MedScape'
        ordering = ['classification_type_en']


class Drugs_information_MedScape(models.Model):
    Name_File = models.CharField(max_length=255, verbose_name='Название файла с загруженной информацией')
    Comment_en = models.CharField(max_length=255, verbose_name='Comment')
    Comment_ru = models.CharField(max_length=255, verbose_name='Коментарий')
    Name_Drug = models.ManyToManyField('Name_Drugs_MedScape')
    Source_Drugs = models.ForeignKey('Source_Drugs_MedScape', on_delete=models.DO_NOTHING, null=True)
    Warnings = models.ManyToManyField('Warnings_MedScape')
    Adverse_Effects = models.ManyToManyField('Adverse_Effects_MedScape')
    Pregnancy_and_lactation = models.ForeignKey('Pregnancy_and_lactation_MedScape', on_delete=models.DO_NOTHING, null=True)
    Interaction = models.ManyToManyField('Interaction_MedScape')


    def __str__(self):
        return self.Name_File

    def get_absolute_url(self):
        return reverse('Drugs_information_MedScape', kwargs={'Drugs_information_MedScape_slug': self.slug})

    class Meta:
        verbose_name = 'Информация о ЛС MedScape'
        ordering = ['Name_File']

class drugs_chf(models.Model):
    index = models.IntegerField(unique=True)
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class disease_chf(models.Model):
    index = models.PositiveIntegerField(unique=True)
    name = models.CharField(max_length=255)
    value = models.FloatField()

    def __str__(self):
        return f"{self.index} - {self.name} ({self.value})"