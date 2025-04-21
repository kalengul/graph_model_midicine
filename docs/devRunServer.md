# Запуск сервера во время разрабоки
|**Команда**|**Описание**|
|:-----:|:--------|
|`python manage.py custom_clear`|Очистка тестовых данных БД|
|`python manage.py clean_medscape`|Очистка БД Medscape|
|`python manage.py migrate`|Миграции|
|`python manage.py import_data`|Заполнение БД тестовыми данными|
|`python manage.py load_medscape_data`|Заполнение БД Medscape|
|`python manage.py runserver`|Запуск сервера|
|`python manage.py test_initialization_with_sqlite`|Инициализация тестовыми данными с SQLite|
|`python manage.py test_initialization_with_postgres`|Инициализация тестовыми данными с Postgres|