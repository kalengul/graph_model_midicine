[Описание API](docs/API.md) <br/>
[Вспомогательные команды](docs/devRunServer.md) <br/>
[Статусы выполнения задач](docs/status.md) <br/>

# Issues
[^logs-perm]: **Исправление прав на volume `logs`.** Если контейнер `backend` не может писать в `/app/logs`
    (ошибка вида `Permission denied` при открытии лог-файла), значит volume `tosh_logs` был создан
    старым образом, когда `backend` запускался от `root`, и файлы в нём принадлежат `root`. Разово исправить
    можно командой:

    ```sh
    docker run --rm -v tosh_logs:/app/logs alpine chown -R 10001:10001 /app/logs
    ```
