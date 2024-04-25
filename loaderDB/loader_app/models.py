from django.db import models


# источник
class Source(models.Model):
    source = models.URLField(max_length=255, verbose_name='источник')

    def __str__(self) -> str:
        return self.source
    
    class Meta:
        verbose_name = 'Источник'
        verbose_name_plural = 'Источники'
        ordering = ['source']


# регистрационный номер
class RegistrationNumber(models.Model):
    registrationNumber = models.CharField(max_length=40, verbose_name='регистрационный номер')

    def __str__(self) -> str:
        return self.registrationNumber
    
    class Meta:
        verbose_name = 'Регистрационный номер'
        verbose_name_plural = 'регистрационный номера'
        ordering = ['registrationNumber']


# международное наименование препарата
class InternationalName(models.Model):
    internationalName = models.CharField(max_length=255, verbose_name='международное наименование')

    reg = models.ForeignKey(RegistrationNumber, on_delete = models.CASCADE)
    source = models.ForeignKey(Source, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.internationalName
    
    class Meta:
        verbose_name = 'Международное наименование препарата'
        verbose_name_plural = 'Международные наименования препаратов'
        ordering = ['internationalName']


# торговое назавние препарата
class TradeName(models.Model):
    tradeName = models.TextField(verbose_name='торговое наименование')

    internationalName = models.OneToOneField(InternationalName, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.tradeName
    
    class Meta:
        verbose_name = 'Торговое наименование препарата'
        verbose_name_plural = 'Торговые наименования препаратов'
        ordering = ['tradeName']


# тексты инструкций
class InstructionText(models.Model):
    headline = models.TextField(null = True, verbose_name='заголовок в нструкции')
    content = models.TextField(null = True, verbose_name='содержание заголовока в нструкции')

    tradeName = models.ForeignKey(TradeName, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.headline + self.content
    
    class Meta:
        verbose_name = 'Текст инструкции'
        verbose_name_plural = 'Тексты инструкций'
        ordering = ['headline']


# Фармако-терапевтическая группа
class PharmacotherapeuticGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name='фармако-терапевтическая группа')

    def __str__(self) -> str:
        return self.name
    
    class Meta:
        verbose_name = 'Фармако-терапевтическая группа'
        verbose_name_plural = 'Фармако-терапевтические группы'
        ordering = ['name']


# Анатомо-терапевтическая химическая классификация
class ATC_classification(models.Model):
    ATC_code = models.CharField(max_length=20, verbose_name='Код АТХ')
    ATC = models.CharField(max_length=255, verbose_name='АТХ')

    def __str__(self) -> str:
        return self.ATC_code + self.ATC
    
    class Meta:
        verbose_name = 'Анатомо-терапевтическая химическая классификация'
        ordering = ['ATC_code']


# держатель препарата
class Holder(models.Model):
    holderName = models.CharField(max_length=1000, verbose_name='Наименование держателя или владельца регистрационного удостоверения лекарственного препарата')
    holderCountry = models.CharField(max_length=255, null=True, verbose_name='Страна держателя или владельца регистрационного удостоверения лекарственного препарата')

    def __str__(self) -> str:
        return self.holferName + self.holderCountry
    
    class Meta:
        verbose_name = 'Держатель препарата'
        verbose_name_plural = 'Держатели препарата'
        ordering = ['holderName']


# сведения о препарате
class DrugInformation(models.Model):
    releaseForm = models.TextField(null = True, verbose_name='Форма выпуска')
    stateRegistrationDate = models.DateField(null = True, verbose_name='Дата государственной регистрации')
    registrationExpirationDate = models.DateField(null = True, verbose_name='Дата окончания действ. рег. уд.')
    renewalDate = models.DateField(null = True, verbose_name='Дата переоформления РУ')
    condition = models.CharField(max_length=10, null = True, verbose_name='Состояние')
    decisionDate = models.DateField(null = True, verbose_name='Дата решения')
    IName = models.CharField(max_length=1000, null = True, verbose_name='Международное непатентованное или группировочное или химическое наименование')
    allowedUntil = models.CharField(max_length=255, null = True, verbose_name='Разрешён ввод в гражданский оборот до')
    pharmaceuticalSubstanceName = models.CharField(max_length=1000, null=True, verbose_name='Наименование фармацевтической субстанции')

    internationalName = models.OneToOneField(InternationalName, on_delete = models.CASCADE)
    pharmacotherapeuticGroup = models.ForeignKey(PharmacotherapeuticGroup, null=True, on_delete = models.SET_NULL)
    ATCclassification = models.ForeignKey(ATC_classification, null=True, on_delete = models.SET_NULL)
    holder = models.ForeignKey(Holder, null=True, on_delete = models.SET_NULL)

    def __str__(self) -> str:
        return self.IName
    
    class Meta:
        verbose_name = 'Сведения о препарате'
        verbose_name_plural = 'Сведения о препаратах'
        ordering = ['releaseForm']


# Сведения о стадиях производства
class InformationStage(models.Model):
    stage = models.CharField(max_length=500, verbose_name='Стадия производства')
    manufacturer = models.CharField(max_length=500, verbose_name='Производитель')
    address = models.CharField(max_length=500, verbose_name='Адрес производителя')
    country = models.CharField(max_length=60, verbose_name='Страна')

    drugInfo = models.ForeignKey(DrugInformation, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.stage
    
    class Meta:
        verbose_name = 'Сведения о стадиях производства'
        ordering = ['stage']


# Фармацевтическая субстанция
class PharmaceuticalSubstance(models.Model):
    manufacturer = models.CharField(max_length=500, null = True, verbose_name='Производитель')
    address = models.CharField(max_length=500, null = True, verbose_name='Адрес')
    expirationDate = models.CharField(max_length=500, null = True, verbose_name='Срок годности')
    storageConditions = models.CharField(max_length=500, null = True, verbose_name='Условия хранения')
    INN = models.CharField(max_length=500, verbose_name='Международное непатентованное или группировочное или химическое наименование')
    drugCrazyBool = models.CharField(max_length=500, null = True, verbose_name='Входит в перечень нарк. средств, псих. веществ и их прекурсоров')
    pharmacopoeiArticle = models.CharField(max_length=500, null = True, verbose_name='Фармакоп. статья / Номер НД')


    drugInfo = models.ForeignKey(DrugInformation, on_delete = models.CASCADE)

    def __str__(self) -> str: 
        return self.INN
    
    class Meta:
        verbose_name = 'Фармацевтическая субстанция'
        verbose_name_plural = 'Фармацевтические субстанции'
        ordering = ['INN']



# Нормативная документация
class RegulatoryDocumentation(models.Model):
    RDNumber = models.CharField(max_length=40, verbose_name='Номер НД')
    year =  models.DateField(null = True, verbose_name='Год')
    productNumber = models.CharField(max_length=40, null = True, verbose_name='№ изм')
    name = models.CharField(max_length=360, verbose_name='Наименование')

    drugInfo = models.ForeignKey(DrugInformation, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.RDNumber
    
    class Meta:
        verbose_name = 'Нормативный документ'
        verbose_name_plural = 'Нормативная документация'
        ordering = ['name']


# Особые отметки
class SpecialMark(models.Model):
    content = models.TextField(verbose_name='Содержание отметки')

    drugInfo = models.ForeignKey(DrugInformation, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.content
    
    class Meta:
        verbose_name = 'Особая отметка'
        verbose_name_plural = 'Особые отметки'
        ordering = ['content']



# Инструкции по применению лекарственного препарата
class DrugInstruction(models.Model):
    URL = models.URLField(verbose_name='URL инструкции')

    drugInfo = models.ForeignKey(DrugInformation, null=True, on_delete = models.SET_NULL)

    def __str__(self) -> str:
        return self.URL
    
    class Meta:
        verbose_name = 'Инструкция по применению лекарственного препарата'
        verbose_name_plural = 'Инструкции по применению лекарственного препарата'
        ordering = ['URL']


# Формы выпуска
class ReleaseForm(models.Model):
    dosageForm = models.CharField(max_length=255, verbose_name='Лекарственная форма')
    dosage = models.CharField(max_length=255, verbose_name='Дозировка')
    expirationDate = models.CharField(max_length=1000, verbose_name='Срок годности')
    storageConditions = models.CharField(max_length=255, verbose_name='Условия хранения')

    drugInfo = models.ForeignKey(DrugInformation, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.dosageForm
    
    class Meta:
        verbose_name = 'Форма выпуска'
        verbose_name_plural = 'Формы выпуска'
        ordering = ['dosageForm']



# Упаковки
class Package(models.Model):
    packageDescription = models.TextField(verbose_name='Упаковка')

    releaseForm = models.ForeignKey(ReleaseForm, on_delete = models.CASCADE)

    def __str__(self) -> str:
        return self.packageDescription
    
    class Meta:
        verbose_name = 'Упаковка'
        verbose_name_plural = 'Упаковки'
        ordering = ['packageDescription']
