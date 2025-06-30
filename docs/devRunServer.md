# Запуск сервера во время разрабоки
|**Команда**|**Описание**|
|:-----:|:--------|
|`python manage.py custom_clear`|Очистка тестовых данных БД|
|`python manage.py clean_medscape`|Очистка БД Medscape|
|`python manage.py clear_synonyms`|Очистка БД синонимов|
|`python manage.py migrate`|Миграции|
|`python manage.py import_data`|Заполнение БД тестовыми данными из excel-файла по умолчанию|
|`python manage.py import_data --excel "имя файла"`|Заполнение БД тестовыми данными из указанного файла|
|`python manage.py import_data --txt`|Заполнение БД тестовыми данными из txt-файлов поумолчанию по умолчанию|
|`python manage.py export_data`|Выгрузка данных из БД в excel-файл по умолчению|
|`python manage.py export_data --excel "имя файла"`|Выгрузка данных из БД в указанный excel-файл|
|`python manage.py export_data --txt`|Выгрузка данных из БД в txt-файлов по умолчанию|
|`python manage.py load_medscape_data`|Заполнение БД Medscape|
|`python manage.py import_synonyms.py`|Заполнение БД синонимов|
|`python manage.py export_synonyms.py`|Выгрузка БД синонимов|
|`python manage.py full_load_data.py`|Полная загрузка данных (выполняет `custom_clear`, `clear_synonyms`, `migrate`, `import_data`, `import_synonyms`)|
|`python manage.py runserver`|Запуск сервера|
|`python manage.py test_initialization_with_sqlite`|Инициализация тестовыми данными с SQLite|

# Проверенные комбинации расчётов Medscape
|**Первое ЛС**|**Второе ЛС**|**ID первого ЛС**|**ID второго ЛС**|**URL-запроса**|
|--------|--------|:----------:|:----------:|----------------------|
|Амиодарон|Ацетазоламид|1|4|`/api/v1/iteraction_medscape/?drugs=[1, 4]`|
|Амиодарон|Бисопролол|1|6|`/api/v1/iteraction_medscape/?drugs=[1, 6]`|
|Амиодарон|Гидрохлоротиазид|1|9|`/api/v1/iteraction_medscape/?drugs=[1, 9]`|
|Амиодарон|Дигоксин|1|12|`/api/v1/iteraction_medscape/?drugs=[1, 12]`|

# Проверенные комбинации расчётов Fortran
|**Первое ЛС**|**Второе ЛС**|**ID первого ЛС**|**ID второго ЛС**|**URL-запроса**|
|--------|--------|:----------:|:----------:|----------------------|
|Амиодарон|Ацетазоламид|1|4|`/api/v1/polifarmakoterapiya-fortran/?drugs=[1, 4]&humanData={"age": ["rangbase.txt"]}`|
|Амиодарон|Бисопролол|1|6|`/api/v1/polifarmakoterapiya-fortran/?drugs=[1, 6]&humanData={"age": ["rangbase.txt"]}`|
|Амиодарон|Гидрохлоротиазид|1|9|`/api/v1/polifarmakoterapiya-fortran/?drugs=[1, 9]&humanData={"age": ["rangbase.txt"]}`|
|Амиодарон|Дигоксин|1|12|`/api/v1/polifarmakoterapiya-fortran/?drugs=[1, 12]&humanData={"age": ["rangbase.txt"]}`|

## Входные и выходные данные расчётов Medscape
### Для Амиодарон и Ацетазоламид:
### Вход
```api/v1/iteraction_medscape/?drugs=[1, 4]```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по MedScape успешно расcчитана"
    },
    "data": [
        {
            "drugs": [
                "Амиодарон",
                "Ацетазоламид"
            ],
            "description": "ацетазоламид будет увеличивать уровень или эффект амиодарона, влияя на метаболизм печеночного/кишечного фермента CYP3A4. Незначительное/значение неизвестно.",
            "compatibility_medscape": "compatible"
        }
    ]
}
```
### Для Амиодарон и Бисопролол:
### Вход
```api/v1/iteraction_medscape/?drugs=[1, 6]```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по MedScape успешно расcчитана"
    },
    "data": [
        {
            "drugs": [
                "Амиодарон",
                "Бисопролол"
            ],
            "description": "амиодарон, бисопролол. Механизм: фармакодинамический синергизм. Используйте осторожность/монитор. Риск кардиотоксичности с брадикардией.",
            "compatibility_medscape": "caution"
        }
    ]
}
```
### Для Амиодарон и Гидрохлоротиазид:
### Вход
```api/v1/iteraction_medscape/?drugs=[1, 9]```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по MedScape успешно расcчитана"
    },
    "data": [
        {
            "drugs": [
                "Амиодарон",
                "Гидрохлоротиазид"
            ],
            "description": "амиодарон будет увеличивать уровень или эффект гидрохлоротиазида за счет конкуренции основных (катионных) препаратов за почечный канальцевый клиренс. Используйте осторожность/монитор.",
            "compatibility_medscape": "caution"
        }
    ]
}
```
### Для Амиодарон и Дигоксин:
### Вход
```api/v1/iteraction_medscape/?drugs=[1, 12]```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по MedScape успешно расcчитана"
    },
    "data": [
        {
            "drugs": [
                "Амиодарон",
                "Дигоксин"
            ],
            "description": "амиодарон будет увеличивать уровень или эффект дигоксина с помощью переносчика оттока P-гликопротеина (MDR1). Избегайте или используйте альтернативный препарат. Амиодарон повышает концентрацию дигоксина в сыворотке перорально на ~70% и дигоксина внутривенно на ~17%; измерить уровень дигоксина до начала приема амиодарона и снизить пероральную дозу дигоксина на 30-50%; уменьшить внутривенную дозу дигоксина на 15-30%",
            "compatibility_medscape": "incompatible"
        }
    ]
}
```
## Входные и выходные данные расчётов Fortran
### Для Амиодарон и Ацетазоламид:
### Вход
```api/v1/polifarmakoterapiya-fortran/?drugs=[1, 4]&humanData={'age': ['rangbase.txt']}```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по Fortran успешно расcчитана"
    },
    "data": {
        "rank_iteractions": 1.4,
        "сompatibility_fortran": "incompatible",
        "side_effects": [
            {
                "сompatibility": "incompatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "некроз",
                        "rank": 0.49
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.46
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.43
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.41
                    },
                    {
                        "se_name": "брадикардия",
                        "rank": 0.4
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.36
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "гипотензия",
                        "rank": 0.31
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.3
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.24
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.19
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.17
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.14
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.11
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.1
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.1
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.0
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.0
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.94
                    },
                    {
                        "se_name": "анафилактический шок",
                        "rank": 0.84
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.83
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    }
                ]
            },
            {
                "сompatibility": "compatible",
                "effects": [
                    {
                        "se_name": "гепатит",
                        "rank": 1.4
                    }
                ]
            }
        ],
        "combinations": [
            {
                "сompatibility": "compatible",
                "drugs": [
                    "Амиодарон",
                    "Ацетазоламид"
                ]
            },
            {
                "сompatibility": "caution",
                "drugs": []
            },
            {
                "сompatibility": "incompatible",
                "drugs": []
            }
        ],
        "compatibility_medscape": "compatible",
        "description": [
            "ацетазоламид будет увеличивать уровень или эффект амиодарона, влияя на метаболизм печеночного/кишечного фермента CYP3A4. Незначительное/значение неизвестно."
        ],
        "drugs": [
            "Амиодарон",
            "Ацетазоламид"
        ]
    }
}
```
### Для Амиодарон и Бисопролол:
### Вход
```api/v1/polifarmakoterapiya-fortran/?drugs=[1, 6]&humanData={'age': ['rangbase.txt']}```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по Fortran успешно расcчитана"
    },
    "data": {
        "rank_iteractions": 0.94,
        "сompatibility_fortran": "caution",
        "side_effects": [
            {
                "сompatibility": "incompatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "некроз",
                        "rank": 0.49
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.46
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.43
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "брадикардия",
                        "rank": 0.4
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.38
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.3
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.24
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.17
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.17
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.15
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.14
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.12
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.11
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.11
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.1
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.0
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.0
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "гипотензия",
                        "rank": 0.94
                    },
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.94
                    },
                    {
                        "se_name": "анафилактический шок",
                        "rank": 0.84
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.83
                    },
                    {
                        "se_name": "гепатит",
                        "rank": 0.7
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    }
                ]
            },
            {
                "сompatibility": "compatible",
                "effects": []
            }
        ],
        "combinations": [
            {
                "сompatibility": "compatible",
                "drugs": [
                    "Амиодарон",
                    "Бисопролол"
                ]
            },
            {
                "сompatibility": "caution",
                "drugs": []
            },
            {
                "сompatibility": "incompatible",
                "drugs": []
            }
        ],
        "compatibility_medscape": "caution",
        "description": [
            "амиодарон, бисопролол. Механизм: фармакодинамический синергизм. Используйте осторожность/монитор. Риск кардиотоксичности с брадикардией."
        ],
        "drugs": [
            "Амиодарон",
            "Бисопролол"
        ]
    }
}
```
### Для Амиодарон и Гидрохлоротиазид:
### Вход
```api/v1/polifarmakoterapiya-fortran/?drugs=[1, 9]&humanData={'age': ['rangbase.txt']}```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по Fortran успешно расcчитана"
    },
    "data": {
        "rank_iteractions": 1.68,
        "сompatibility_fortran": "incompatible",
        "side_effects": [
            {
                "сompatibility": "incompatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "некроз",
                        "rank": 0.49
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.43
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.41
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.38
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.18
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.17
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.17
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.15
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.15
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.15
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.12
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.11
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.11
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.1
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.94
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.92
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.86
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.83
                    },
                    {
                        "se_name": "брадикардия",
                        "rank": 0.8
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.68
                    },
                    {
                        "se_name": "гипотензия",
                        "rank": 0.63
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.55
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.53
                    }
                ]
            },
            {
                "сompatibility": "compatible",
                "effects": [
                    {
                        "se_name": "анафилактический шок",
                        "rank": 1.68
                    },
                    {
                        "se_name": "гепатит",
                        "rank": 1.4
                    }
                ]
            }
        ],
        "combinations": [
            {
                "сompatibility": "compatible",
                "drugs": [
                    "Амиодарон",
                    "Гидрохлоротиазид"
                ]
            },
            {
                "сompatibility": "caution",
                "drugs": []
            },
            {
                "сompatibility": "incompatible",
                "drugs": []
            }
        ],
        "compatibility_medscape": "caution",
        "description": [
            "амиодарон будет увеличивать уровень или эффект гидрохлоротиазида за счет конкуренции основных (катионных) препаратов за почечный канальцевый клиренс. Используйте осторожность/монитор."
        ],
        "drugs": [
            "Амиодарон",
            "Гидрохлоротиазид"
        ]
    }
}
```
### Для Амиодарон и Дигоксин:
### Вход
```api/v1/polifarmakoterapiya-fortran/?drugs=[1, 12]&humanData={'age': ['rangbase.txt']}```
### Выход
```
{
    "result": {
        "status": 200,
        "message": "Совместимость ЛС по Fortran успешно расcчитана"
    },
    "data": {
        "rank_iteractions": 1.2,
        "сompatibility_fortran": "incompatible",
        "side_effects": [
            {
                "сompatibility": "incompatible",
                "effects": [
                    {
                        "se_name": "отек Квинке",
                        "rank": 0.49
                    },
                    {
                        "se_name": "атриовентрикулярная блокада",
                        "rank": 0.49
                    },
                    {
                        "se_name": "агранулоцитоз",
                        "rank": 0.47
                    },
                    {
                        "se_name": "панкреатит",
                        "rank": 0.46
                    },
                    {
                        "se_name": "гипокалиемия",
                        "rank": 0.42
                    },
                    {
                        "se_name": "гипертиреоз",
                        "rank": 0.42
                    },
                    {
                        "se_name": "эозинофилия",
                        "rank": 0.39
                    },
                    {
                        "se_name": "фиброз",
                        "rank": 0.38
                    },
                    {
                        "se_name": "тошнота/рвота",
                        "rank": 0.38
                    },
                    {
                        "se_name": "флебит",
                        "rank": 0.35
                    },
                    {
                        "se_name": "гипотензия",
                        "rank": 0.31
                    },
                    {
                        "se_name": "экзема/крапивница",
                        "rank": 0.24
                    },
                    {
                        "se_name": "галлюцинации",
                        "rank": 0.24
                    },
                    {
                        "se_name": "парестезия",
                        "rank": 0.23
                    },
                    {
                        "se_name": "гинекомастия",
                        "rank": 0.2
                    },
                    {
                        "se_name": "головная боль",
                        "rank": 0.2
                    },
                    {
                        "se_name": "неврит/нейропатия",
                        "rank": 0.19
                    },
                    {
                        "se_name": "анорексия",
                        "rank": 0.18
                    },
                    {
                        "se_name": "обморок",
                        "rank": 0.18
                    },
                    {
                        "se_name": "диарея/запор",
                        "rank": 0.15
                    },
                    {
                        "se_name": "снижение либидо",
                        "rank": 0.15
                    },
                    {
                        "se_name": "инфаркт",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гангрена Фурнье",
                        "rank": 0.0
                    },
                    {
                        "se_name": "внутричерепное кровоизлияние",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперкалиемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "лейкопения",
                        "rank": 0.0
                    },
                    {
                        "se_name": "фибрилляция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипертензия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипогликемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "желудочно-кишечное кровотечение",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва пищевода",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кетоацидоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек легких",
                        "rank": 0.0
                    },
                    {
                        "se_name": "глаукома",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стенокардия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бронхиальная астма",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гематурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гиперурикемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоцитопения",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Стивенса-Джонсона",
                        "rank": 0.0
                    },
                    {
                        "se_name": "язва желудка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гипербилирубинемия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нефролитиаз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "почечная недостаточность",
                        "rank": 0.0
                    },
                    {
                        "se_name": "гастрит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "конъюнктивит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дисменорея",
                        "rank": 0.0
                    },
                    {
                        "se_name": "пневмония",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тромбоэмболия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "стоматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "синдром Рейно",
                        "rank": 0.0
                    },
                    {
                        "se_name": "ринорея/фарингит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "паранойя",
                        "rank": 0.0
                    },
                    {
                        "se_name": "кашель/ринит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "озноб/лихорадка",
                        "rank": 0.0
                    },
                    {
                        "se_name": "васкулит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "псориаз/алопеция",
                        "rank": 0.0
                    },
                    {
                        "se_name": "бессонница",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дизурия/полиурия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "дерматит",
                        "rank": 0.0
                    },
                    {
                        "se_name": "вертиго",
                        "rank": 0.0
                    },
                    {
                        "se_name": "артралгия",
                        "rank": 0.0
                    },
                    {
                        "se_name": "подагра",
                        "rank": 0.0
                    },
                    {
                        "se_name": "тремор",
                        "rank": 0.0
                    },
                    {
                        "se_name": "полипоз",
                        "rank": 0.0
                    },
                    {
                        "se_name": "миалгия/судороги",
                        "rank": 0.0
                    },
                    {
                        "se_name": "отек лица/конечностей",
                        "rank": 0.0
                    },
                    {
                        "se_name": "нарушение слуха/зрения/вкуса",
                        "rank": 0.0
                    },
                    {
                        "se_name": "припухлость суставов",
                        "rank": 0.0
                    },
                    {
                        "se_name": "астения/утомляемость",
                        "rank": 0.0
                    },
                    {
                        "se_name": "приливы",
                        "rank": 0.0
                    }
                ]
            },
            {
                "сompatibility": "caution",
                "effects": [
                    {
                        "se_name": "некроз",
                        "rank": 0.98
                    },
                    {
                        "se_name": "анафилактический шок",
                        "rank": 0.84
                    },
                    {
                        "se_name": "гепатит",
                        "rank": 0.7
                    },
                    {
                        "se_name": "желудочковая экстрасистолия",
                        "rank": 0.65
                    },
                    {
                        "se_name": "тахикардия",
                        "rank": 0.62
                    },
                    {
                        "se_name": "бронхоспазм",
                        "rank": 0.57
                    }
                ]
            },
            {
                "сompatibility": "compatible",
                "effects": [
                    {
                        "se_name": "брадикардия",
                        "rank": 1.2
                    }
                ]
            }
        ],
        "combinations": [
            {
                "сompatibility": "compatible",
                "drugs": [
                    "Амиодарон",
                    "Дигоксин"
                ]
            },
            {
                "сompatibility": "caution",
                "drugs": []
            },
            {
                "сompatibility": "incompatible",
                "drugs": []
            }
        ],
        "compatibility_medscape": "incompatible",
        "description": [
            "амиодарон будет увеличивать уровень или эффект дигоксина с помощью переносчика оттока P-гликопротеина (MDR1). Избегайте или используйте альтернативный препарат. Амиодарон повышает концентрацию дигоксина в сыворотке перорально на ~70% и дигоксина внутривенно на ~17%; измерить уровень дигоксина до начала приема амиодарона и снизить пероральную дозу дигоксина на 30-50%; уменьшить внутривенную дозу дигоксина на 15-30%"
        ],
        "drugs": [
            "Амиодарон",
            "Дигоксин"
        ]
    }
}
```