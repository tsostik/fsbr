# Добавление игрока с другого сервера

`POST /api/addplayer/` принимает JSON без браузерной сессии и возвращает
`201 {"id": 123}`. Используется тот же механизм добавления, что в `/players/add/`.

В источнике параметров приложения Flask:

```text
PLAYER_API_TOKEN=<случайный секрет>
```

Автор передаётся в обязательном поле JSON `author_id` — положительный целочисленный
ФСБР ID — и записывается при добавлении игрока. Вызывающий сервер с корректным
токеном выбирает автора. Без настройки токена API возвращает 503.
После настройки перезапустите процесс.
Секрет можно сгенерировать командой `python -c "import secrets; print(secrets.token_urlsafe(32))"`.
Храните его в секретах окружения на обоих серверах, отдельно от Flask `SECRET_KEY`;
не добавляйте в репозиторий, URL, клиентский JavaScript или логи. Для ротации замените
его на обоих серверах и перезапустите приложение. Передавайте запросы по HTTPS.

Пример Python на вызывающем сервере:

```python
import os
import requests

response = requests.post(
    'https://db.bridgesport.ru/api/addplayer/',
    headers={'Authorization': 'Bearer ' + os.environ['PLAYER_API_TOKEN']},
    json={
        'author_id': 42,
        'lastname': 'Иванов',
        'firstname': 'Иван',
        'fathername': 'Иванович',
        'sex': '1',
        'city': '16',
        'birthdate': '2000/01/02',
        'is_sputnik': False,
        'notes': 'Регистрация с соседнего сервера',
    },
    timeout=15,
)
response.raise_for_status()
player_id = response.json()['id']
```

Пример curl на вызывающем сервере (Bash; `PLAYER_API_TOKEN` уже задан в окружении):

```bash
curl --fail-with-body --max-time 15 \
  'https://your-host/api/addplayer/' \
  --header "Authorization: Bearer ${PLAYER_API_TOKEN}" \
  --header 'Content-Type: application/json' \
  --data-raw '{
    "author_id": 42,
    "lastname": "Иванов",
    "firstname": "Иван",
    "fathername": "Иванович",
    "sex": "1",
    "city": "16",
    "birthdate": "2000/01/02",
    "is_sputnik": false,
    "notes": "Регистрация с соседнего сервера"
  }'
```

Замените `https://your-host` на адрес сервера Flask. Параметр `--data-raw`
задаёт метод POST; при успехе ответ содержит JSON с ID созданного игрока.

Тело JSON должно быть закодировано в **UTF-8**. Windows-1251 не поддерживается:
сервер вернёт `400` с `error: invalid_encoding`. Заголовок `charset=utf-8`
сам по себе не перекодирует отправляемые байты.

Для вызова из Windows сохраните JSON из примера в файл `player.json` в UTF-8
и передайте файл через `curl.exe` (PowerShell):

```powershell
curl.exe --fail-with-body --max-time 15 `
  'https://your-host/api/addplayer/' `
  --header "Authorization: Bearer $env:PLAYER_API_TOKEN" `
  --header 'Content-Type: application/json' `
  --data-binary '@player.json'
```

Пример Python с `requests.post(..., json=...)` выше также корректно передаёт кириллицу.

Обязательны `author_id`, `lastname`, `firstname`, `city`. Остальные поля необязательны:
`fathername`, `sex` (строка `1` — мужчина, `0` — женщина, по умолчанию `1`),
`birthdate`, `is_sputnik` (JSON boolean, по умолчанию false), `sputnik_first`,
`notes` (до 233 символов). Даты — `YYYY/MM/DD` или пустая строка.
`author_id` передаётся целым JSON-числом, `is_sputnik` — boolean, остальные поля —
строками. Коды городов из текущей формы:
20 — Екатеринбург, 16 — Москва, 22 — Новосибирск, 29 — Пермь,
18 — С.-Петербург, 21 — Челябинск, 25 — другой.

Ошибки возвращаются в JSON с полем `error`: 400 — неверные данные
(ошибки полей в `fields`), 401 — неверный/отсутствующий Bearer,
415 — требуется JSON, 503 — API не настроен или база заблокирована,
500 — не удалось добавить игрока. Проверки секрета выполняются до обращения к БД.
CSRF отключён только для этой формы API; браузерный маршрут сохраняет авторизацию
и CSRF. CORS для межсерверного вызова не требуется.

Каждый успешный запрос создаёт новую запись, как браузерная форма. Если ответ
потерялся после записи, перед повторной отправкой проверьте наличие игрока:
автоматическая защита от повторов здесь не предусмотрена.


## ????? ??????

????? ?? ??????? ???????? ????? ?????????:

```http
GET /api/findplayer/?surname=Smith&newonly=true
GET /api/findplayer/Smith?newonly=true
POST /api/findplayer/
Content-Type: application/json

{"surname": "Smith", "newonly": true}
```

`newonly` ???????????? ? ?? ????????? ????? `false`. ? ?????????? GET
??????????? `true`, `false`, `1`, `0` (??? ????? ????????); ???????? `newonly`
??? ???????? ????? ???????? ??????. ? JSON POST
????? ???????? boolean, ? ????? ?? ?? ????????? ???????? ??? ????? 1 ? 0.
??? ?????????? ??????? ???????????? ?????? ????? ??????. ??? ???????
?????????? ????? ? JSON-?????? ? ?????? 201; ??? ?????????? ? ?????? 404
? `null` ??? ?????? ????????. ??? POST ????????? JSON-??????; ????????
?????? ??? ??? ????????? ?????????? 400, ?????????? JSON Content-Type ? 415.
