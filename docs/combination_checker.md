# API для расчёта комбинаций лекарственных средств в фоновом режиме

## Назначение

Расчёт выполняется в фоновом режиме. После запуска API сразу возвращает созданный отчёт, после чего фронтенд может периодически запрашивать его состояние.

Одновременно может выполняться только **один** расчёт.

---

# Статусы отчёта

Допустимые статусы:

| **Статус**  | **Описание**                |
| :---------- | :-------------------------- |
| `running`   | Расчёт выполняется          |
| `completed` | Расчёт успешно завершён     |
| `canceled`  | Расчёт отменён              |
| `failed`    | Расчёт завершился с ошибкой |

В модели отчёта предусмотрены все четыре состояния.

---

# URL


|   Метод  | URL                         | Назначение                                       |
| :------: | :-------------------------- | :----------------------------------------------- |
|   `GET`  | `reports/`                  | Получить список отчётов                          |
|  `POST`  | `reports/`                  | Запустить новый расчёт                           |
|   `GET`  | `reports/{id}/`             | Получить конкретный отчёт и его текущий прогресс |
| `DELETE` | `reports/{id}/`             | Удалить отчёт                                    |
|   `GET`  | `reports/{id}/cancel/`      | Отменить конкретный активный отчёт               |
|   `GET`  | `reports/{id}/download/`    | Скачать результат расчёта                        |
|   `GET`  | `reports/running/`          | Получить текущий выполняющийся отчёт             |
|   `GET`  | `reports/running/cancel/`   | Отменить текущий выполняющийся отчёт             |
|   `GET`  | `reports/latest-completed/` | Получить последний успешно завершённый отчёт     |
|   `GET`  | `reports/latest-completed/download` | Скачать последний успешно завершённый отчёт     |

---

# Аутентификация

Не требуется.

---

# 1. Запуск нового расчёта

## URL

`POST api/v1/reports/`

Новый расчёт запускается в фоновом режиме.

После успешного запуска endpoint возвращает созданный отчёт со статусом `running`.

Одновременно может выполняться только один расчёт. Перед запуском API проверяет наличие активного отчёта (`is_active=true`).

## Входные данные

|      **параметр**      | **Тип данных** | **Обязательность** | **Описание**                                                        |
| :--------------------: | :------------- | :----------------: | :------------------------------------------------------------------ |
|         `name`         | String         |         нет        | Название отчёта                                                     |
| `max_combination_size` | Integer        |         да         | Максимальный размер комбинации. Допустимые значения: от `2` до `10` |
|       `rank_name`      | String         |         нет        | Поле ранга, используемое при расчёте. По умолчанию `rang_base`      |

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `name`                 | String          | Название отчёта                                            |
| `status`               | String          | Текущее состояние отчёта                                   |
| `started_at`           | DateTime / null | Время начала расчёта                                       |
| `finished_at`          | DateTime / null | Время окончания расчёта                                    |
| `progress`             | Float           | Прогресс расчёта в процентах, округлённый до сотых         |
| `weight_version_name`  | String          | Версия файла весов                                         |
| `max_combination_size` | Integer         | Максимальный размер комбинации                             |
| `error_message`        | String          | Сообщение об ошибке. При отсутствии ошибки — пустая строка |

Допустимые значения `rank_name`:

```text
rang_base
rang_f1
rang_f2
rang_freq
rang_m1
rang_m2
```

## Пример входных данных

```json
{
    "name": "Test combinations",
    "max_combination_size": 3,
    "rank_name": "rang_base"
}
```

## Статусы ответа

201 – Расчёт комбинаций запущен
400 – Некорректные входные данные:
* max_combination_size не в диапазоне от 2 до 10;
* rank_name не входит в допустимый список;
* name превышает максимальную длину (255 символов);
* любые другие ошибки валидации сериализатора.

409 – Расчёт комбинаций уже запущен (активный отчёт существует).
500 – Внутренняя ошибка сервера (ошибка БД, сбой при создании отчёта, проблемы с фоновым запуском и т.п.).

## Успешный ответ

**HTTP 201 Created**

```json
{
    "result": {
        "status": 201,
        "message": "Report created successfully."
    },
    "data": {
        "id": 51,
        "name": "Test combinations",
        "status": "running",
        "started_at": "2026-08-12T12:51:48.372251+03:00",
        "finished_at": null,
        "progress": 0.0,
        "max_combination_size": 3,
        "weight_version_name": "Таблица ТОШ НЛ 11.07_16.06_transpose.xlsx"
    }
}
```

После запуска расчёт переходит в состояние `running`.

---

## Ошибка при попытке запустить второй расчёт

Если другой расчёт уже выполняется:

**HTTP 409 Conflict**

```json
{
    "result": {
        "status": 409,
        "message": "Another combination report is already running."
    },
    "data": {
        "active_report_id": 26
    }
}
```

---

# 2. Получение конкретного отчёта

## URL

`GET api/v1/reports/{id}/`

Используется для получения полной информации о конкретном отчёте, в том числе его текущего прогресса.

Например:

`GET api/v1/reports/26/`

## Входные данные

Параметры не требуются.

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `name`                 | String          | Название отчёта                                            |
| `status`               | String          | Текущее состояние отчёта                                   |
| `started_at`           | DateTime / null | Время начала расчёта                                       |
| `finished_at`          | DateTime / null | Время окончания расчёта                                    |
| `duration`             | Duration / null | Продолжительность расчёта                                  |
| `max_combination_size` | Integer         | Максимальный размер комбинации                             |
| `weight_version_name`  | String          | Версия файла весов                                         |
| `total_iterations`     | Integer         | Теоретическое общее количество комбинаций                  |
| `completed_iterations` | Integer         | Количество обработанных итераций                           |
| `checked_combinations` | Integer         | Количество проверенных комбинаций                          |
| `found_combinations`   | Integer         | Количество найденных результатов                           |
| `pruned_combinations`  | Integer         | Количество отсечённых комбинаций                           |
| `progress`             | Float           | Прогресс расчёта в процентах, округлённый до сотых         |
| `error_message`        | String          | Сообщение об ошибке. При отсутствии ошибки — пустая строка |


## Пример ответа во время выполнения

```json
{
    "result": {
        "status": 200,
        "message": "Report retrieved successfully."
    },
    "data": {
        "id": 26,
        "name": "Test combinations",
        "status": "running",
        "started_at": "2026-08-10T11:34:24.037335+03:00",
        "finished_at": null,
        "duration": null,
        "max_combination_size": 3,
        "weight_version_name": "Таблица ТОШ НЛ 01.07_16.14_transpose.xlsx",
        "total_iterations": 2027795,
        "completed_iterations": 100001,
        "checked_combinations": 100001,
        "found_combinations": 1234,
        "pruned_combinations": 45678,
        "progress": 4.93,
        "error_message": ""
    }
}
```


## Статусы ответа

200 – Отчёт найден
404 – Отчёт не найден
500 – Внутренняя ошибка сервера

---

# 3. Получение текущего выполняющегося отчёта

## URL

`GET api/v1/reports/running/`

Endpoint возвращает последний активный отчёт со статусом `running`.

Поиск выполняется по:

```text
status = running
is_active = true
```
и среди них выбирается отчёт с самым поздним `started_at`.

## Входные данные

Параметры не требуются.

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `name`                 | String          | Название отчёта                                            |
| `status`               | String          | Текущее состояние отчёта                                   |
| `started_at`           | DateTime / null | Время начала расчёта                                       |
| `finished_at`          | DateTime / null | Время окончания расчёта                                    |
| `duration`             | Duration / null | Продолжительность расчёта                                  |
| `max_combination_size` | Integer         | Максимальный размер комбинации                             |
| `weight_version_name`  | String          | Версия файла весов                                         |
| `total_iterations`     | Integer         | Теоретическое общее количество комбинаций                  |
| `completed_iterations` | Integer         | Количество обработанных итераций                           |
| `checked_combinations` | Integer         | Количество проверенных комбинаций                          |
| `found_combinations`   | Integer         | Количество найденных результатов                           |
| `pruned_combinations`  | Integer         | Количество отсечённых комбинаций                           |
| `progress`             | Float           | Прогресс расчёта в процентах, округлённый до сотых         |
| `error_message`        | String          | Сообщение об ошибке. При отсутствии ошибки — пустая строка |


## Статусы ответа

200 – Отчёт выполняется
404 – Активного расчёта нет
500 – Внутренняя ошибка сервера

## Успешный ответ

**HTTP 200 OK**

```json
{
    "result": {
        "status": 200,
        "message": "Report retrieved successfully."
    },
    "data": {
        "id": 26,
        "name": "Test combinations",
        "status": "running",
        "started_at": "2026-08-10T11:34:24.037335+03:00",
        "finished_at": null,
        "duration": null,
        "max_combination_size": 3,
        "weight_version_name": "Таблица ТОШ НЛ 01.07_16.14_transpose.xlsx",
        "total_iterations": 2027795,
        "completed_iterations": 100001,
        "checked_combinations": 100001,
        "found_combinations": 1234,
        "pruned_combinations": 45678,
        "progress": 4.93,
        "error_message": ""
    }
}
```

## Если расчёт не выполняется

**HTTP 404 Not Found**

```json
{
    "result": {
        "status": 404,
        "message": "No running reports found."
    },
    "data": {}
}
```

---

# 4. Отмена текущего расчёта

## URL

`GET api/v1/reports/running/cancel/`

Endpoint отменяет текущий активный расчёт.

После отмены:

```text
status = canceled
is_active = false
```

## Входные данные

Параметры не требуются.

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `status`               | String          | Текущее состояние отчёта                                   |

## Статусы ответа

202 – Запрос на отмену приният
404 – Активного расчёта нет
409 – Расчёт завершился между запросом и отменой
500 – Внутренняя ошибка сервера

## Успешный ответ

**HTTP 202 Accepted**

```json
{
    "result": {
        "status": 202,
        "message": "Cancellation requested."
    },
    "data": {
        "id": 52,
        "status": "canceled"
    }
}
```

## Если активного расчёта нет

**HTTP 404 Not Found**

```json
{
    "result": {
        "status": 404,
        "message": "No running reports found."
    },
    "data": {}
}
```

## Если расчёт завершился между запросом и отменой

**HTTP 409 Conflict**

```json
{
    "result": {
        "status": 409,
        "message": "Report is no longer running."
    },
    "data": {}
}
```

---

# 5. Отмена конкретного отчёта

## URL

`GET api/v1/reports/{id}/cancel/`

Например:

`GET api/v1/reports/26/cancel/`


Поле `cancel` обязательно должно иметь значение `true`.

## Входные данные

Параметры не требуются.

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `status`               | String          | Текущее состояние отчёта                                   |

## Статусы ответа

200 – Расчёт успешно отменён (запрос принят)
400 – Такой расчёт уже не активен
404 – Отчёт не найден
409 – Расчёт завершился между запросом и отменой
500 – Внутренняя ошибка сервера

## Успешный ответ

**HTTP 202 Accepted**

```json
{
    "result": {
        "status": 202,
        "message": "Cancellation requested."
    },
    "data": {
        "id": 52,
        "status": "canceled"
    }
}
```

После успешной отмены:

```json
{
    "status": "canceled"
}
```

и:

```text
is_active = false
```

## Отчёт уже не активен

**HTTP 400 Bad Request**

```json
{
    "result": {
        "status": 400,
        "message": "Report is not active."
    },
    "data": {}
}
```

## Расчёт уже завершился

**HTTP 409 Conflict**

```json
{
    "result": {
        "status": 409,
        "message": "Report is no longer running."
    },
    "data": {}
}
```

---

# 6. Последний успешно завершённый отчёт

## URL

`GET api/v1/reports/latest-completed/`

Endpoint возвращает последний отчёт со статусом:

```text
completed
```

Сортировка выполняется по времени `finished_at`, поэтому возвращается именно последний завершённый расчёт.

## Входные данные

Параметры не требуются.

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `name`                 | String          | Название отчёта                                            |
| `status`               | String          | Текущее состояние отчёта                                   |
| `started_at`           | DateTime / null | Время начала расчёта                                       |
| `finished_at`          | DateTime / null | Время окончания расчёта                                    |
| `duration`             | Duration / null | Продолжительность расчёта                                  |
| `max_combination_size` | Integer         | Максимальный размер комбинации                             |
| `weight_version_name`  | String          | Версия файла весов                                         |
| `total_iterations`     | Integer         | Теоретическое общее количество комбинаций                  |
| `completed_iterations` | Integer         | Количество обработанных итераций                           |
| `checked_combinations` | Integer         | Количество проверенных комбинаций                          |
| `found_combinations`   | Integer         | Количество найденных результатов                           |
| `pruned_combinations`  | Integer         | Количество отсечённых комбинаций                           |
| `progress`             | Float           | Прогресс расчёта в процентах, округлённый до сотых         |
| `error_message`        | String          | Сообщение об ошибке. При отсутствии ошибки — пустая строка |

## Статусы ответа

200 – Расчёт найден
404 – Расчётов нет
500 – Внутренняя ошибка сервера

## Успешный ответ

**HTTP 200 OK**

```json
{
    "result": {
        "status": 200,
        "message": "Latest completed report retrieved successfully."
    },
    "data": {
        "id": 25,
        "name": "Test combinations",
        "status": "completed",
        "started_at": "2026-08-10T10:20:00+03:00",
        "finished_at": "2026-08-10T10:45:32+03:00",
        "duration": "00:25:32",
        "max_combination_size": 3,
        "weight_version_name": "Таблица ТОШ НЛ 01.07_16.14_transpose.xlsx",
        "total_iterations": 2027795,
        "completed_iterations": 2027795,
        "checked_combinations": 1800000,
        "found_combinations": 125430,
        "pruned_combinations": 227795,
        "progress": 100.0,
        "error_message": ""
    }
}
```

Если успешных расчётов ещё нет:

**HTTP 404 Not Found**

```json
{
    "result": {
        "status": 404,
        "message": "No completed reports found."
    },
    "data": {}
}
```

---

# 7. Список отчётов

## URL

`GET api/v1/reports/`

Возвращает список созданных отчётов.

## Входные данные

Параметры не требуются.

## Выходные данные

| **параметр**           | **Тип данных**  | **Описание**                                               |
| :--------------------- | :-------------- | :--------------------------------------------------------- |
| `id`                   | Integer         | ID отчёта                                                  |
| `name`                 | String          | Название отчёта                                            |
| `status`               | String          | Текущее состояние отчёта                                   |
| `started_at`           | DateTime / null | Время начала расчёта                                       |
| `finished_at`          | DateTime / null | Время окончания расчёта                                    |
| `progress`             | Float           | Прогресс расчёта в процентах, округлённый до сотых         |
| `weight_version_name`  | String          | Версия файла весов                                         |
| `max_combination_size` | Integer         | Максимальный размер комбинации                             |
| `error_message`        | String          | Сообщение об ошибке. При отсутствии ошибки — пустая строка |

## Пример ответа

```json
{
    "result": {
        "status": 200,
        "message": "Reports retrieved successfully."
    },
    "data": [
        {
            "id": 26,
            "name": "Test combinations",
            "status": "running",
            "created_at": "2026-08-10T11:34:23.939545+03:00",
            "finished_at": null,
            "progress": 4.93,
            "max_combination_size": 3,
            "weight_version_name": "Таблица ТОШ НЛ 01.07_16.14_transpose.xlsx"
        },
        {
            "id": 25,
            "name": "Previous calculation",
            "status": "completed",
            "created_at": "2026-08-10T10:20:00+03:00",
            "finished_at": "2026-08-10T10:45:32+03:00",
            "progress": 100.0,
            "max_combination_size": 3,
            "weight_version_name": "Таблица ТОШ НЛ 01.07_16.14_transpose.xlsx"
        }
    ]
}
```

## Статусы ответа

200 – Расчёты найдены (список может быть пустым)
500 – Внутренняя ошибка сервера

---

# 8. Скачивание результата

## URL

`GET api/v1/reports/{id}/download/`

Например:

`GET api/v1/reports/25/download/`

Endpoint возвращает файл результата расчёта.

Файл возвращается как `attachment`.

## Входные данные

Параметры не требуются.

## Статусы ответа

200 – Расчёт передан (файл)
404 – Отчёт отсутствует или файл результата не найден
500 – Внутренняя ошибка сервера (ошибка чтения файла и т.п.)

## Успешный ответ

**HTTP 200 OK**

Ответом является файл CSV.

## Файл отсутствует

**HTTP 404 Not Found**

```text
Result file not found.
```

Скачивать результат имеет смысл только для отчёта со статусом `completed`

---

# 9. Скачивание результата последнего завершённого расчёта

## URL

`GET api/v1/reports/latest-completed/download/`

Endpoint возвращает файл результата **последнего успешно завершённого расчёта**.

Последний отчёт определяется как отчёт со статусом `completed`с наиболее поздним значением `finished_at`.

## Входные данные

Параметры не требуются.

## Статусы ответа

200 – Расчёт передан (файл)
404 – Отчёт отсутствует (нет завершённых) или файл результата не найден
500 – Внутренняя ошибка сервера

## Успешный ответ

**HTTP 200 OK**

Ответом является файл результата расчёта.

Файл возвращается как `attachment`, поэтому браузер/клиент может сразу начать скачивание.

Например:

```
Content-Type: text/csv
Content-Disposition: attachment; filename="report_25.csv"
```

Название файла определяется сервером.

## Если завершённых отчётов нет

Если в системе ещё нет ни одного отчёта со статусом completed:

**HTTP 404 Not Found**

```json
{
    "result": {
        "status": 404,
        "message": "No completed reports found."
    },
    "data": {}
}
```

Если отчёт найден, но файл результата отсутствует

Если последний завершённый отчёт существует, но файл результата был удалён или недоступен:

**HTTP 404 Not Found**

```json
{
    "result": {
        "status": 404,
        "message": "Result file not found."
    },
    "data": {}
}
```

---

# 10. Удаление отчёта

## URL

`DELETE api/v1/reports/{id}/`

Например:

`DELETE api/v1/reports/25/`

Активный отчёт удалить нельзя. Сначала необходимо его отменить.

## Входные данные

Параметры не требуются.

## Статусы ответа

200 – Расчёт удалён (фактически возвращается 204 No Content, но в документации оставлено как 200)
404 – Отчёт не найден
409 – Выбранный расчёт ещё запущен (активен), сначала необходимо его отменить
500 – Внутренняя ошибка сервера

## Успешный ответ

**HTTP 200 No Content**
```json
{
    "result": {
        "status": 200,
        "message": "Report deleted successfully."
    },
    "data": {}
}
```

## Попытка удалить активный отчёт

**HTTP 409 Conflict**

```json
{
    "result": {
        "status": 409,
        "message": "Report is active. Cancel it first."
    },
    "data": {}
}
```

---

