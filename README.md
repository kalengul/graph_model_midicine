# Для чего нужно?
Программа для преобразования сканов текст
на основе библиотеки dedoc.
## Ссылки:
- [документация Dedoc](https://dedoc.readthedocs.io/en/latest/)
- [статья на Хабре](https://habr.com/ru/companies/isp_ras/articles/779390/)
# Установка
Создание виртуальной среды
```
python -m venv venv
```
Для Linux:
```
source venv/bin/activate
```
Windows:
```
.\venv\Scripts\activate
```
Установка зависимостей из requirements.txt
```
pip install -r requirements.txt
```
## ВАЖНО!!! 
Установить программу poppler.
Когда poppler будет установлена,
нужно путь до директории bin добавить
в системную переменную окружения PATH.