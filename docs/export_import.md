# API для экспорта данных о рангах из БД
## Назначение
Экспорт данных о рангах из БД

## URL
```GET api/v1/export_from_db/```<br/>

## Аутентификация
Требуемый статус: `admin`

## Вход
Нет параметров

## Выход
Скачиваемый файл формата `.xlsx`, содержащий данные из БД

### HTTP-заголовки
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=data_from_db.xlsx

### Тело ответа
данные Excel-файла бинарном формате

### Замечание 
FileResponse автоматически пробразуется в двоичный формат для поддержки arraybuffer

### Статусы ответа  
- `200` — файл успешно найден и передан
- `404` — файл не найден на сервере  

### Вывод при успешном импорте
```
{
  "result": {
    "status": 400,
    "message": "Эксель-файл не обнаружен"
  },
  "data": {}
}
```


# API для импорта дааных о рангах в БД
## Назначение
Импорта данных о рангах в БД

## URL
```POST api/v1/import_to_db/```<br/>

## Аутентификация
Требуемый статус: `admin`

## Вход
На входе в теле запроса передаётся файл

| **Параметр** | **Тип данных** | **Обязательность** | **Описание** |
|--------------|----------------|---------------------|---------------|
| file         | file (.xlsx)   | да                  | Excel-файл с корректной структурой |

### HTTP-заголовки
Content-Type: multipart/form-data
Content-Disposition: form-data; name="file"; filename="какое-то название.xlsx"

### HTTP-запрос
POST api/v1/import_to_db/ HTTP/<какая-то версия>
Host: <example.com>
Authorization: Bearer <токен>
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...

------WebKitFormBoundary...
Content-Disposition: form-data; name="file"; filename="<your_data.xlsx>"
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet

<содержимое файла Excel>

------WebKitFormBoundary...

### Пример входных данных
```
{
  'file': 'сам файл'
}
```
```
{
  'file': [<InMemoryUploadedFile: Список побочных эффектов sqrt5_2.xlsx (application/vnd.openxmlformats-officedocument.spreadsheetml.sheet)>]
}
```


## Выход
### Статусы ответа  
- `200` — файл успешно найден и передан
- `400` — файл должен быть .xlsx
- `400` — в <имя файла> некоррекнтые листы или таблицы
- `500` — внутренная ошибка сервера

### Вывод при успешном импорте
```
{
  "result": {
    "status": 200,
    "message": "Данные в БД импортированы успешно"
  },
  "data": {}
}
```

### Вывод при импорте из файла некорректного формата
```
{
  "result": {
    "status": 400,
    "message": "Файл должен быть .xlsx"
  },
  "data": {}
}
```

### Вывод при некорректности содержания excel-файла
```
{
  "result": {
    "status": 400,
    "message": "В <имя файла> некорректные листы или таблицы"
  },
  "data": {}
}
```

### Вывод при обработке файла excel-файла
```
{
  "result": {
    "status": 500,
    "message": "Импорт данные. Ошибка при обработке файла"
  },
  "data": {}
}
```
