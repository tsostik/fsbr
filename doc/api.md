# HTTP-интерфейс

Источник маршрутов — `src/start.py`. Пути чувствительны к регистру, в частности `/misc/ListXL/`. Ниже перечислены прикладные методы; стандартные HEAD и OPTIONS Flask не раскрываются. Большинство путей имеют завершающий `/`.

## Страницы и вход

| Метод | Путь | Результат / ограничения |
| --- | --- | --- |
| GET | `/` | Главная HTML-страница |
| GET, POST | `/players/` | Поиск; POST принимает поле `name` и перенаправляет на URL поиска |
| GET | `/players/<name>/` | HTML результатов поиска; SQL-поиск выполняется при длине строки от 3 символов |
| GET, POST | `/players/add/` | Форма и добавление; требуется вход, незаблокированная база и валидная форма |
| GET | `/authorize/<provider>/` | Начало входа; `provider`: `google`, `facebook`, `twitter`; необязательный query `next` |
| GET | `/callback/<provider>/` | Callback провайдера; параметры зависят от OAuth-протокола |
| GET | `/logout/` | Выход; необязательный query `next` |
| GET | `/toggle_lock_state` | Переключение флага `locked`; требуется вход, изменение только для роли `Admin`; query `next` |
| GET | `/misc/sirius/`, `/misc/sputnik/` | HTML списков учащихся |
| GET | `/misc/clubs/<int:club_id>/` | HTML списка игроков клуба |

Числовой `/players/<int:player_id>/` — карточка XML, а не поиск по строке. Право `AddPlayers` используется шаблонами для отображения формы и ссылки; отдельной проверки этой роли при обработке POST в `add_player` нет.

Форма добавления: обязательные `lastname`, `firstname`; необязательные `fathername`, `birthdate`, `sputnik_first`, `notes` (до 255 символов); `sex` (`1`/`0`), `city` (значение из списка), `is_sputnik` и CSRF-токен формы. Обе даты формы имеют формат `YYYY/MM/DD`. Успех возвращает перенаправление и flash-сообщение с новым ID, а не JSON.

## Данные игроков и турниров

| GET-путь | Формат / корневой XML-элемент |
| --- | --- |
| `/players/<int:player_id>/`, `/players/<int:player_id>/xml/` | XML `player` |
| `/players/<int:player_id>/info/` | JSON краткой карточки; CORS `Access-Control-Allow-Origin: *` |
| `/tourns/`, `/tourns/xml/` | XML `tournament_list` |
| `/tourns/<int:tournament_id>/`, `/tourns/<int:tournament_id>/xml/` | XML `tournament` |
| `/tourns/families/xml/` | XML `families`, все семьи |
| `/tourns/families/<int:family_id>/xml/` | XML `families`, выбранная семья |
| `/misc/clubs/`, `/misc/clubs/xml/` | XML `ClubStat` |

JSON-карточка содержит `id`, `name`, `city`, `razr`, `rate`, `categories`, если у объекта есть фамилия. `photo` добавляется при наличии проверенного файла фотографии; URL сформирован с фиксированным доменом `db.bridgesport.ru`. Отсутствующий игрок даёт `{}` в JSON или текст `Player not found` в XML; явный HTTP 404 для этого случая обработчиком не задан.

## Рейтинги и отчёты

| GET-путь | Результат |
| --- | --- |
| `/rate/fulllist/`, `/rate/fulllist/xml/` | XML `FullList`, полная классификация |
| `/rate/`, `/rate/xml/` | XML `rate`, запрос на первое число текущего месяца |
| `/rate/<rdate>/`, `/rate/<rdate>/xml/` | XML `rate`, запрос на дату `YYYY-MM-DD` |
| `/rate/forecast/`, `/rate/forecast/xml/` | XML `RateForecast` |
| `/misc/razrchange/`, `/misc/razrchange/xml/` | XML `RazrChange`, запрос на первое число месяца |
| `/misc/razrchange/<date>/`, `/misc/razrchange/<date>/xml/` | XML `RazrChange`, дата `YYYY-MM-DD` |
| `/misc/ListXL/` | Файл XLS с именем `players`, создаваемый Flask-Excel |

Рейтинговые турниры за год возвращают XML `tournaments`. Все восемь алиасов:

```text
/tourns/rate/                  /tourns/rate/xml/
/tourns/rate/<int:year>/       /tourns/rate/<int:year>/xml/
/rate/tourns/                 /rate/tourns/xml/
/rate/tourns/<int:year>/       /rate/tourns/<int:year>/xml/
```

При отсутствии года либо значении `0` выбирается текущий год, а в январе — предыдущий.

## Формат и поведение

XML сериализуется через lxml с декларацией UTF-8, форматированием и MIME `text/xml`. В корень XML обработчики добавляют `generated` — длительность формирования в секундах. Это не дата создания данных.

В URL рейтинга и изменения разрядов неверно записанная дата заменяется первым числом текущего месяца. Затем из истории выбирается последняя доступная дата не позже запрошенной; если запрос раньше всей истории, берётся самая ранняя. У `rate/@date` отражается выбранная дата; у `RazrChange/@date` остаётся дата запроса, хотя данные загружены для выбранной даты истории.

Структура вложенных элементов определяется свойствами сериализации в `interface.py`, `misc.py` и `RateTours.py`. Например, карточка игрока включает `info`, `sportlevel`, `stat` и при наличии данных `IDs`, `results`, `clubMbStatistics`, `administrative`, `directing`, `other`. Не следует считать необязательные элементы всегда присутствующими.

Единого JSON-формата ошибок, версии API и схем XSD/OpenAPI нет. Ошибки БД и сериализации обычно не перехватываются маршрутами; интеграции должны учитывать возможность ответа 500. Публичные маршруты чтения не требуют входа.

Примеры чтения после локального запуска:

```powershell
Invoke-WebRequest http://127.0.0.1:5000/tourns/xml/
Invoke-WebRequest http://127.0.0.1:5000/rate/2026-11-01/xml/
Invoke-RestMethod http://127.0.0.1:5000/players/1/info/
```

ID `1` приведён как пример и может отсутствовать в конкретной базе.
