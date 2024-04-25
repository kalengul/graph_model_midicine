import os
import json
import datetime

from loader_app.models  import *

'''
Метод разделения заголовков и содержания под заголовками.
Входной параметр метода istructionRow - строка, представляющая инструкцию.
Инструкция (теоретически) является структурированным текстом - состоит из загаловков
и содержания под загаловком.
Текств считается заголовко если оснсовпадает со списком заголовков 
или написан заглавными буква (проще говоря, капсом).
Если по критериям заголовка не соотвествует, это текст содержания под заголовком.
Результатом метода является словарь:
    ключи - заголовки (строка),
    значения - содержания по заголовками (строка).
'''
def separater_headline_and_content(istructionRow: str) -> dict[str, str]:
    headlineList = [
        'ИНСТРУКЦИЯ',
        'СОСТАВ',
        'ФАРМАКОТЕРАПЕВТИЧЕСКАЯ ГРУППА',
        'ОПИСАНИЕ',
        'ЛЕКАРСТВЕННАЯ ФОРМА',
        'ДЕЙСТВУЮЩЕЕ ВЕЩЕСТВО',
        'ФАРМАКОЛОГИЧЕСКИЕ СВОЙСТВА',
        'ПОКАЗАНИЯ К ПРИМЕНЕНИЮ',
        'ПРОТИВОПОКАЗАНИЯ',
        #'ПРИМЕНЕНИЕ ПРИ БЕРЕМЕННОСТИ В ПЕРИОД ГРУДНОГО ВСКАРМЛИВАНИЯ, ВЛИЯНИЕ НА ФЕРТИЛЬНОСТЬ, РЕКОМЕНДАЦИИ ДЛЯ ПАЦИЕНТОВ ДЕТОРОДНОГО ВОЗРАСТО',
        #'ПРИМЕНЕНИЕ ПРИ БЕРЕМЕННОСТИ В ПЕРИОД ГРУДНОГО ВСКАРМЛИВАНИЯ, ВЛИЯНИЕ НА ФЕРТИЛЬНОСТЬ, РЕКОМЕНДАЦИИ ДЛЯ ПАЦИЕНТОВ С РЕПРОДУКТИВНЫМ ПОТЕНЦИАЛОМ',
        'СПОСОБ ПРИМЕНЕНИЯ И ДОЗЫ',
        'СПОСОБ ВВЕДЕНИЯ',
        'ПОБОЧНЫЕ ЭФФЕКТЫ',
        'ПОБОЧНЫЕ ДЕЙСТВИЯ',
        'ПЕРЕДОЗИРОВКА',
        'ВЗАИМОДЕЙСТВИЕ С ДРУГИМИ ЛЕКАРСТВЕННЫМИ ПРЕПАРАТАМИ И ДРУГИЕ ФОРМЫ ВЗАИМОДЕЙСТВИЯ',
        'ВЗАИМОДЕЙСТВИЕ С ДРУГИМИ ЛЕКАРСТВЕННЫМИ  СРЕДСТВАМИ',
        'ВЗАИМОДЕЙСТВИЕ С ПИЩЕЙ',
        'КОРРЕКЦИЯ ДОЗЫ',
        'ОСОБЫЕ УКАЗАНИЯ',
        'ФОРМА ВЫПУСКА',
        'УСЛОВИЯ ХРАНЕНИЯ',
        'СРОК ГОДНОСТИ',
        'УСЛОВИЯ ОТПУСКА ИЗ АПТЕК',
        'УСЛОВИЯ ОТПУСКА',
        'РЕЗУЛЬТАТЫ КЛИНИЧЕСКИХ ИСПЫТАНИЙ',
        'ЮРИДИЧЕСКОЕ ЛИЦО НА ИМЯ КОТОРОГО ВЫДАНО РЕГИСТРАЦИОННОЕ УДОСТОВЕРЕНИЕ',
        'ПРОИЗВОДИТЕЛЬ',
        'ПРЕТЕНЗИИ ПОТРЕБИТЕЛЕЙ НАПРАВЛЯТЬ ПО АДРЕСУ'
    ]

    headline_content_dict = dict()

    istructionRow = istructionRow.replace('\n\n', '\n')
    istructionRow = istructionRow.replace('POCCHH', 'РОССИИ')
    istructionRow = istructionRow.replace('ИНСТРУКНИЯ', 'ИНСТРУКЦИЯ')
    istructionRow = istructionRow.replace('инстгукция', 'ИНСТРУКЦИЯ')

    rows = istructionRow.split('\n')
    rows = [row.strip() for row in rows]

    lv = False
    lv2 = False
    headline = 'Пустой заголовок'
    char_list = ['\\', '+', '*', '>', '<', '!']
    for row in rows:
        if row == '':
            continue
        if row.isupper() and (lv == False)  and (len(row) != 1) and (True not in [r in char_list for r in row]):
            headline = row
            lv = True
        elif row.isupper() and lv and (len(row) != 1) and (True not in [r in char_list for r in row]):
            row = ' ' + row
            headline += row
        elif (not row.isupper()) and any(row.upper() in r for r in headlineList) and (len(row) != 1) and (True not in [r in char_list for r in row]):
            headline = row.upper()
            lv2 = True
        else: 
            if lv or lv2:
                lv = False
                lv2 = False
                headline_content_dict[headline] = row    
            else:
                if len(headline_content_dict) == 0:
                    headline_content_dict[headline] = row
                else:
                    row = ' ' + row
                    headline_content_dict[headline] += row

    return headline_content_dict

'''
Метод загрузки данных в БД.
В метод выполнянется перебор и открытие всех json-файлов в хранилище.
Json-файлы содержат структурированые данных о ЛС.
Эти данные сопоставляются с классами из модуля models.py и сохраняются 
в БД как объект этих классов в соответсвии с технологией ORM.
'''
def loader():
    #DIR = 'D:\\The job\\loaderDB\\loaderDB\\loader_app\\input files'
    DIR = 'I:\\datasets\\datasets\\For the job'
    errors = 0
    file_count = 0

    for root, dirs, files in os.walk(DIR):
        for file in files:
            if file.endswith('.json'):
                file_count += 1
                if file_count % 1000 == 0:
                    print(f'обработано {file_count} файлов')
                path = os.path.join(root, file)
                path = path.replace('._', '')
                print(f'file number {file_count + 1} - {root}\{file}')
                f = open(path, 'r', encoding='utf-8')
                data = None
                try:
                    data = json.load(f)
                except:
                    errors += 1
                    continue
                source = Source.objects.create(source = data['Источник'])
                source.save()
                registrationNumber = RegistrationNumber.objects.create(registrationNumber = data['Регистрационный номер'])
                registrationNumber.save()
                for drug_item in data['Препараты']:
                    internationalName = InternationalName.objects.create(internationalName = drug_item['Международное непатентованное наименование или группировочное (химическое) наименование'],
                                                                        reg = registrationNumber,
                                                                        source = source)
                    internationalName.save()

                    tradeName = None
                    if ('Торговое наименование' in drug_item) and drug_item['Торговое наименование']:
                        tradeName = TradeName.objects.create(tradeName = drug_item['Торговое наименование'],
                                                            internationalName = internationalName)
                        tradeName.save()

                    if ('Текст инструкции' in drug_item) and drug_item['Текст инструкции']:
                        istructionRow = drug_item['Текст инструкции']
                        # метод разделения заголовков и содержания под заголовками.
                        textDict = separater_headline_and_content(istructionRow)
                        for headline, content in textDict.items():
                            instructionText = InstructionText(headline = headline, content = content, tradeName = tradeName)
                            instructionText.save()

                    holder = None
                    if 'Наименование держателя или владельца регистрационного удостоверения лекарственного препарата' in drug_item:
                        holder, _ = Holder.objects.get_or_create(holderName = drug_item['Наименование держателя или владельца регистрационного удостоверения лекарственного препарата'],
                                                            holderCountry = drug_item['Страна держателя или владельца регистрационного удостоверения лекарственного препарата'])
                        holder.save()
                    elif ('Производитель' in drug_item) and drug_item['Производитель']:
                        holder, _ = Holder.objects.get_or_create(holderName = drug_item['Производитель'], holderCountry = None)

                    ATC_obj = None
                    if 'Анатомо-терапевтическая химическая классификация' in drug_item:
                        if drug_item['Анатомо-терапевтическая химическая классификация']['Код АТХ'] or drug_item['Анатомо-терапевтическая химическая классификация']['АТХ']:
                            ATC_obj, _ = ATC_classification.objects.get_or_create(ATC_code = drug_item['Анатомо-терапевтическая химическая классификация']['Код АТХ'],
                                                                                ATC = drug_item['Анатомо-терапевтическая химическая классификация']['АТХ'])
                            ATC_obj.save()

                    pharmacotherapeuticGroup = None
                    if ('Фармако-терапевтическая группа' in drug_item) and drug_item['Фармако-терапевтическая группа']:
                        pharmacotherapeuticGroup, _ = PharmacotherapeuticGroup.objects.get_or_create(name = drug_item['Фармако-терапевтическая группа'])
                        pharmacotherapeuticGroup.save()


                    stateRegistrationDate = None
                    if ('Дата государственной регистрации' in drug_item) and drug_item['Дата государственной регистрации'] :
                        day, month, year = drug_item['Дата государственной регистрации'].split('.')
                        stateRegistrationDate = datetime.date(year=int(year), month=int(month), day=int(day))
                    elif ('Дата включения в реестр' in drug_item) and drug_item['Дата включения в реестр']:
                        day, month, year = drug_item['Дата включения в реестр'].split('.')
                        stateRegistrationDate = datetime.date(year=int(year), month=int(month), day=int(day))

                    registrationExpirationDate = None
                    if ('Дата окончания действ. рег. уд.' in drug_item) and drug_item['Дата окончания действ. рег. уд.']:
                        day, month, year = drug_item['Дата окончания действ. рег. уд.'].split('.')
                        registrationExpirationDate = datetime.date(year=int(year), month=int(month), day=int(day))
                    elif ('Дата исключения из реестра'in drug_item) and drug_item['Дата исключения из реестра']:
                        day, month, year = drug_item['Дата исключения из реестра'].split('.')
                        registrationExpirationDate = datetime.date(year=int(year), month=int(month), day=int(day))

                    renewalDate = None
                    if ('Дата переоформления РУ' in drug_item) and drug_item['Дата переоформления РУ']:
                        day, month, year = drug_item['Дата переоформления РУ'].split('.')
                        renewalDate = datetime.date(year=int(year), month=int(month), day=int(day))
                        
                    decisionDate = None
                    if ('Дата решения' in drug_item) and drug_item['Дата решения']:
                        day, month, year = drug_item['Дата решения'].split('.')
                        decisionDate = datetime.date(year=int(year), month=int(month), day=int(day))
                    
                    allowedUntil = None
                    if ('Разрешён ввод в гражданский оборот до' in drug_item) and drug_item['Разрешён ввод в гражданский оборот до']:
                        allowedUntil = drug_item['Разрешён ввод в гражданский оборот до']
                    
                    pharmaceuticalSubstanceName = None
                    if ('Наименование фармацевтической субстанции' in drug_item) and drug_item['Наименование фармацевтической субстанции']:
                        pharmaceuticalSubstanceName = drug_item['Наименование фармацевтической субстанции']


                    condition = None
                    if ('Состояние' in drug_item) and drug_item['Состояние']:
                        condition = drug_item['Состояние']

                    releaseForm = None
                    if ('Форма выпуска' in drug_item) and drug_item['Форма выпуска']:
                        releaseForm = drug_item['Форма выпуска']
                    
                    IName = None
                    if ('Международное непатентованное или группировочное или химическое наименование' in drug_item) and drug_item['Международное непатентованное или группировочное или химическое наименование']:
                        IName = drug_item['Международное непатентованное или группировочное или химическое наименование']
                    elif ('Международное непатентованное или группировочное (химическое) наименование' in drug_item) and drug_item['Международное непатентованное или группировочное (химическое) наименование']:
                        IName = drug_item['Международное непатентованное или группировочное (химическое) наименование']

                    drugInformation = DrugInformation.objects.create(releaseForm = releaseForm,
                                                                    stateRegistrationDate = stateRegistrationDate,
                                                                    registrationExpirationDate = registrationExpirationDate,
                                                                    renewalDate = renewalDate,
                                                                    condition = condition,
                                                                    decisionDate = decisionDate,
                                                                    IName = IName,
                                                                    allowedUntil = allowedUntil,
                                                                    internationalName = internationalName,
                                                                    pharmacotherapeuticGroup = pharmacotherapeuticGroup,
                                                                    ATCclassification = ATC_obj,
                                                                    holder = holder,
                                                                    pharmaceuticalSubstanceName = pharmaceuticalSubstanceName)
                    drugInformation.save()
                    if ('Сведения о стадиях производства' in drug_item) and drug_item['Сведения о стадиях производства']:
                        for item in drug_item['Сведения о стадиях производства']:
                            informationStage = InformationStage.objects.create(stage = item['Стадия производства'],
                                                                            manufacturer = item['Производитель'],
                                                                            address = item['Адрес производителя'],
                                                                            country = item['Страна'],
                                                                            drugInfo =  drugInformation)
                            informationStage.save()

                    if ('Фармацевтическая субстанция' in drug_item) and drug_item['Фармацевтическая субстанция']:
                        for item in drug_item['Фармацевтическая субстанция']:
                            pharmaceuticalSubstance = PharmaceuticalSubstance.objects.create(manufacturer = item['Производитель'],
                                                                                            address = item['Адрес'],
                                                                                            expirationDate = item['Срок годности'],
                                                                                            storageConditions = item['Условия хранения'],
                                                                                            INN = item['Международное непатентованное или группировочное или химическое наименование'],
                                                                                            drugCrazyBool = item['Входит в перечень нарк. средств, псих. веществ и их прекурсоров'],
                                                                                            pharmacopoeiArticle = item['Фармакоп. статья / Номер НД'],
                                                                                            drugInfo = drugInformation)
                            pharmaceuticalSubstance.save()

                    if ('Нормативная документация' in drug_item) and drug_item['Нормативная документация']:
                        for item in drug_item['Нормативная документация']:
                            if item['Год'] and (len(item['Год']) == 4):
                                year=datetime.date(year=int(item['Год']), month=1, day=1)
                                regulatoryDocumentation = RegulatoryDocumentation.objects.create(RDNumber = item['Номер НД'],
                                                                                                year = year,
                                                                                                productNumber = item['№ изм'],
                                                                                                name = item['Наименование'],
                                                                                                drugInfo = drugInformation)
                            else:
                                regulatoryDocumentation = RegulatoryDocumentation.objects.create(RDNumber = item['Номер НД'],
                                                                                                year = None,
                                                                                                productNumber = item['№ изм'],
                                                                                                name = item['Наименование'],
                                                                                                drugInfo = drugInformation)
                            regulatoryDocumentation.save()
                    
                    if 'Особые отметки' in drug_item:
                        if drug_item['Особые отметки'] != []:
                            for item in drug_item['Особые отметки']:
                                specialMark = SpecialMark.objects.create(content = item, 
                                                                        drugInfo = drugInformation)
                                specialMark.save()

                    if 'Инструкции по применению лекарственного препарата' in drug_item:
                        if drug_item['Инструкции по применению лекарственного препарата'] != [] or drug_item['Инструкции по применению лекарственного препарата'] != 'Инструкция отсутствует':
                            for item in drug_item['Инструкции по применению лекарственного препарата']:
                                drugInstruction = DrugInstruction.objects.create(URL = item,
                                                                                drugInfo = drugInformation)
                                drugInstruction.save()
                    if ('Формы выпуска' in drug_item) and drug_item['Формы выпуска']:
                        for item in drug_item['Формы выпуска']:
                            releaseForm = ReleaseForm.objects.create(dosageForm = item['Лекарственная форма'],
                                                                    dosage = item['Дозировка'],
                                                                    expirationDate = item['Срок годности'],
                                                                    storageConditions = item['Условия хранения'],
                                                                    drugInfo = drugInformation)
                            releaseForm.save()
                            
                            if ('Упаковки' in item) and item['Упаковки']:
                                for i in item['Упаковки']:
                                    package = Package.objects.create(packageDescription = i,
                                                                    releaseForm = releaseForm)
                                    package.save()
                f.close()

    print(f'json-файлов {file_count}')
    print(f'ошибок кодировки {errors}')
    return 'загрузчик отработал'