from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


MAX_LENGTH = 255
MAX_LENGTH_K = 10000
USER = 'Пользователь'


class NameDrugsMedScape(models.Model):
    """Модели ЛС из MedScape."""

    name_en = models.CharField(max_length=MAX_LENGTH,
                               verbose_name='Name Drug')
    name_ru = models.CharField(max_length=MAX_LENGTH,
                               verbose_name='Название ЛС')
    # Связь много ко многим с типом лекарственного средства
    group_type = models.ManyToManyField('TypeDrugsMedScape')

    def __str__(self):
        """Строковое представление."""
        return self.name_en

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Name_Drugs_MedScape',
                       kwargs={'Name_Drugs_MedScape_slug': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'МНН ЛС MedScape'
        ordering = ['name_en']


class TypeDrugsMedScape(models.Model):
    """Модель типа ЛС."""

    type_en = models.CharField(max_length=MAX_LENGTH, verbose_name='Type Drug')
    type_ru = models.CharField(max_length=MAX_LENGTH, verbose_name='Тип ЛС')

    def __str__(self):
        """Строковое представление."""
        return self.type_en

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Type_Drugs_MedScape',
                       kwargs={'Type_Drugs_MedScape_slug': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Тип ЛС MedScape'
        ordering = ['type_en']


class SourceDrugsMedScape(models.Model):
    """Источника MedScape."""

    source = models.CharField(max_length=MAX_LENGTH_K, verbose_name='Источник')

    def __str__(self):
        """Строковое представление."""
        return self.source

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Source_Drugs_MedScape',
                       kwargs={'Source_Drugs_MedScape': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Источник информации о ЛС MedScape'
        ordering = ['source']


class WarningsMedScape(models.Model):
    """Модель опасности."""

    warnings_name_en = models.CharField(max_length=MAX_LENGTH_K,
                                        verbose_name='Warnings')
    warnings_name_ru = models.CharField(max_length=MAX_LENGTH_K,
                                        verbose_name='Опасность')
    warnings_type = models.CharField(max_length=MAX_LENGTH_K,
                                     verbose_name='Тип опасности')

    def __str__(self):
        """Строковое представление."""
        return self.warnings_type

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Warnings_MedScape',
                       kwargs={'Warnings_MedScape': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Опасность применения ЛС MedScape'
        ordering = ['warnings_type']


class AdverseEffectsMedScape(models.Model):
    """Побочное действие."""

    adverse_effects_name_en = models.CharField(max_length=MAX_LENGTH_K,
                                               verbose_name='Adverse Effects')
    adverse_effects_name_ru = models.CharField(max_length=MAX_LENGTH_K,
                                               verbose_name='Побочное действие')
    adverse_effects_percent = models.CharField(max_length=MAX_LENGTH_K,
                                               verbose_name='Процент')

    def __str__(self):
        """Строковое представление."""
        return self.adverse_effects_name_en

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Adverse_Effects_MedScape',
                       kwargs={'Adverse_Effects_MedScape': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Побочные эффекты ЛС MedScape'
        ordering = ['adverse_effects_percent']


class PregnancyAndLactationMedScape(models.Model):
    """Рекомендации для беременности и лактации."""

    pregnancy_common_en = models.CharField(max_length=MAX_LENGTH_K,
                                           verbose_name='Pregnancy_common')
    pregnancy_specific_en = models.CharField(max_length=MAX_LENGTH_K,
                                             verbose_name='Pregnancy_specific')
    lactation_common_en = models.CharField(max_length=MAX_LENGTH_K,
                                           verbose_name='Lactation_common')
    lactation_specific_en = models.CharField(max_length=MAX_LENGTH_K,
                                             verbose_name='Lactation_specific')
    pregnancy_common_ru = models.CharField(max_length=MAX_LENGTH_K,
                                           verbose_name='Беременность')
    pregnancy_specific_ru = models.CharField(
        max_length=MAX_LENGTH_K,
        verbose_name='Конкретные рекомендации для беременных')
    lactation_common_ru = models.CharField(
        max_length=MAX_LENGTH_K,
        verbose_name='Грудное вскармливание')
    lactation_specific_ru = models.CharField(
        max_length=MAX_LENGTH_K,
        verbose_name='Конкретные рекомендации для грудного вскармливания')

    def __str__(self):
        """Строковое представление."""
        return self.pregnancy_common_en

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Pregnancy_and_lactation_MedScape',
                       kwargs={'Pregnancy_and_lactation_MedScape': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Лактация ЛС MedScape'


class InteractionMedScape(models.Model):
    """Взаимодействия ЛС."""

    interaction_with = models.ForeignKey('NameDrugsMedScape',
                                         on_delete=models.DO_NOTHING)
    classification_type_en = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Classification Interaction')
    classification_type_ru = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Классификация взаимодействия')
    description_en = models.CharField(max_length=MAX_LENGTH_K,
                                      verbose_name='Description')
    description_ru = models.CharField(max_length=MAX_LENGTH_K,
                                      verbose_name='Описание')

    def __str__(self):
        """Строковое представление."""
        return self.classification_type_en

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Interaction_MedScape',
                       kwargs={'Interaction_MedScape': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Взаимодействие ЛС MedScape'
        ordering = ['classification_type_en']


class DrugsInformationMedScape(models.Model):
    """Модели для хранения информации о ЛС MedScape."""

    name_file = models.CharField(
        max_length=MAX_LENGTH,
        verbose_name='Название файла с загруженной информацией')
    comment_en = models.CharField(max_length=MAX_LENGTH,
                                  verbose_name='Comment')
    comment_ru = models.CharField(max_length=MAX_LENGTH,
                                  verbose_name='Коментарий')
    name_drug = models.ManyToManyField('NameDrugsMedScape')
    source_drugs = models.ForeignKey('SourceDrugsMedScape',
                                     on_delete=models.DO_NOTHING,
                                     null=True)
    warnings = models.ManyToManyField('WarningsMedScape')
    adverse_effects = models.ManyToManyField('AdverseEffectsMedScape')
    pregnancy_and_lactation = models.ForeignKey(
        'PregnancyAndLactationMedScape',
        on_delete=models.DO_NOTHING,
        null=True)
    interaction = models.ManyToManyField('InteractionMedScape')

    def __str__(self):
        """Строковое представление."""
        return self.name_file

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Drugs_information_MedScape',
                       kwargs={'Drugs_information_MedScape_slug': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Информация о ЛС MedScape'
        ordering = ['name_file']


class DrugGroup(models.Model):
    """Группа ЛС."""

    title = models.CharField(max_length=MAX_LENGTH,
                             verbose_name="Название группы")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User,
                             verbose_name=USER,
                             on_delete=models.CASCADE)
    slug = models.SlugField(max_length=MAX_LENGTH,
                            unique=True,
                            db_index=True,
                            verbose_name="URL")

    def __str__(self):
        """Строковое представление."""
        return self.title

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('DrugGroup', kwargs={'DrugGroup_slug': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Группа ЛС'
        verbose_name_plural = 'Группы ЛС'
        ordering = ['title']


class Drug(models.Model):
    """ЛС."""

    name = models.CharField(max_length=MAX_LENGTH,
                            verbose_name='Название лекарственного средства')
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    pg = models.ForeignKey('DrugGroup',
                           null=True,
                           on_delete=models.CASCADE,
                           verbose_name='Группа лекарственных средств')
    user = models.ForeignKey(User, verbose_name=USER, on_delete=models.CASCADE)
    slug = models.SlugField(max_length=MAX_LENGTH,
                            unique=True,
                            db_index=True,
                            verbose_name="URL")

    def __str__(self):
        """Строковое представление."""
        return self.name

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('Drug', kwargs={'Drug_slug': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'ЛС'
        verbose_name_plural = 'ЛС'
        ordering = ['name']


class DrugInteractionTable(models.Model):
    """Таблица взаимодействий ЛС."""

    drug_one = models.ForeignKey('Drug',
                                 null=True,
                                 on_delete=models.CASCADE,
                                 verbose_name='ЛС №1',
                                 related_name='druginteractions_one')
    drug_two = models.ForeignKey('Drug',
                                 null=True,
                                 on_delete=models.CASCADE,
                                 verbose_name='ЛС №2',
                                 related_name='druginteractions_two')
    interaction = models.TextField(verbose_name="Взаимодействие")
    time_create = models.DateTimeField(auto_now_add=True)
    time_update = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, verbose_name=USER, on_delete=models.CASCADE)

    def __str__(self):
        """Строковое представление."""
        return self.interaction

    def get_absolute_url(self):
        """Получение URL."""
        return reverse('DrugInteractionTable',
                       kwargs={'DrugInteractionTable_slug': self.slug})

    class Meta:
        """Настройка модели."""

        verbose_name = 'Взаимодействие ЛС (Таблица)'
        verbose_name_plural = 'Взаимодействие ЛС (Таблица)'
        ordering = ['drug_one']
