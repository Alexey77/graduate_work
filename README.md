# «AI ассистент онлайн кинотеатра» 
__Дипломная работа на курсе Яндекс Практикум "Расширенный курс мидл Python-разработчик" (11 месяцев)__

__Такой программы больше нет. Есть программа на 6 месяцев ["Расширенный курс мидл Python-разработчик"](https://practicum.yandex.ru/middle-python/)__

[_Ссылка на этот репозиторий_](https://github.com/Alexey77/graduate_work)

[![Cover](cover.png)](https://github.com/Alexey77/graduate_work/raw/main/cover.png)

## Общая схема

[![Scheme](scheme.png)](https://github.com/Alexey77/graduate_work/raw/main/cover.png)

## Сервисы созданные в рамках дипломного проекта

### [Auth service](https://github.com/Alexey77/graduate_work/tree/main/auth-service)

Сервис аутентификацией и авторизацией пользователей.

**Реализация**: FastAPI + JWT + Postgresql + SQLAlchemy + Alembic 

### [Assistant service](https://github.com/Alexey77/graduate_work/tree/main/assistant_service)

Сервис "AI-Ассистент" - единая точка входа для пользователей по всем вопросам онлайн кинотеатра.

**Реализация**: FastAPI + MongoDB + client gRPC

### [Text Vector Service](https://github.com/Alexey77/graduate_work/tree/main/text_vector_service)

GPRC сервис для преобразования текста в векторное представление и поиска по векторной базе данных

**Реализация**: server gRPC, Qdrant, TextEncoder

При первом старте идёт скачивание модели [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small)

### [LLM Service](https://github.com/Alexey77/graduate_work/tree/main/llm_service)

GPRC сервис для взаимодействия с LLM

**Реализация**: server gRPC, aiohttp, (можно доделать до локальной LLM модели)

Для работы с API OpenAI использовался сервис [proxyAPI.ru](proxyapi.ru)

### [Wiki crawler](https://github.com/Alexey77/graduate_work/tree/main/wiki-scrapy-api-crawler)

Парсер API Wiki [eng](https://www.mediawiki.org/wiki/API) | [rus](https://www.mediawiki.org/wiki/API/ru)

**Реализация**: scrapy, SQLite, ETL из [SQLite в Qdrant](https://github.com/Alexey77/graduate_work/blob/main/text_vector_service/src/etl_wiki/run_etl_wiki.py), ETL из [Wikipedia dump в SQLite](https://github.com/Alexey77/graduate_work/blob/main/text_vector_service/src/etl_wiki/from_dump_to_sqlite.py)  

### Docker

Все сервисы завернуты в Docker


### Run project

1. Для запуска проекта в следующих директориях на основании `.env.example` файла нужно создать `.env` файл:

- assistant_service
- auth-service
- llm_service
- text_vector_service

2. Загрузить [dump Qdrant 0.9 Gb](https://storage.yandexcloud.net/yandex-practicum/docs-206350992826913-2024-11-17-17-31-15.7z), (не обязательно [dump SQlite 0.26 Gb](https://storage.yandexcloud.net/yandex-practicum/wiki_pages.7z)) 
3. Выполнить `docker-compose up -d --build`
4. Создать нового пользователя
   ```
   curl -L -X POST 'http://localhost:81/api/v1/auth/register' \
    -H 'Content-Type: application/json' \
    --data-raw '{
        "email": "test@example.com",
        "password": "1234qwerty",
        "first_name": "Test",
        "last_name": "User"
    }'
   ```
   
5. Получить `access_token`
    ```
    curl -L -X POST 'http://localhost:81/api/v1/auth/login' \
    -H 'Content-Type: application/json' \
    --data-raw '{
        "email": "test@example.com",
        "password": "1234qwerty"
    }'
    ```
6. Полученный токен использовать при запросе к ai-ассистенту
    ```
   curl -X 'POST' \
      'http://localhost/api/v1/assistant/chat' \
      -H 'accept: application/json' \
      -H 'Authorization: Bearer ••••••' \
      -H 'Content-Type: application/json' \
      -d '{
      "role": "user",
      "content": "Какие фильмы сняты по сказкам Пушкина?"
    }'
    ```

### Other

Реализован Github Actions для [линтера Ruff](https://github.com/Alexey77/graduate_work/blob/main/.github/workflows/lint.yml) и [pre-commit-config](https://github.com/Alexey77/graduate_work/blob/main/.pre-commit-config.yaml)  

### Примеры ответов AI-Ассистента по RAG запросам:

1. «кто главные герои мультфильма Ну погоди»

```
Главными героями мультфильма «Ну, погоди!» являются Волк и Заяц.

Based on:
- "Волк, Клара Румянова — Заяц"
- "Анатолий Папанов — Волк, Клара Румянова — Заяц"
```


2. «Когда вышел фильм Мимино и кто его режиссер»

```
Фильм «Мимино» вышел на всесоюзный экран 27 марта 1978 года. Его режиссёром был Георгий Данелия.

Based on: 
- "Выход картины на всесоюзный экран состоялся 27 марта 1978 года."
- "советский художественный фильм, снятый в 1977 году режиссёром Георгием Данелией"
```


3. «какой акетор играл Чапаева» (опечатка)

```
В роли Чапаева в телесериале «Страсти по Чапаю» снялся Сергей Стрельников. В фильме «Чапаев» роль Чапаева исполнил Борис Бабочкин.

Based on:
- "В ролях Сергей Стрельников — Василий Чапаев"
- "В ролях Борис Бабочкин — Василий Иванович Чапаев"
```


4. «в каком фильме 31 декабря ходят в баню»

```
В фильме «Ирония судьбы, или С лёгким паром!» 31 декабря герои по традиции ходят в баню.  
  
Based on:  
- "Заголовок страницы: Ирония судьбы, или С лёгким паром!. Начало фрагмента: Фильм начинается... куда по традиции они ходят дружеской компанией каждый год 31 декабря."  
```

5. «когда вышел мультфильм про домовенка кузю»

```
Мультфильм про Домовёнка Кузю начал выходить в 1984 году. Первая серия по сюжету была названа «Дом для Кузьки». Далее вышли серии: «Приключения домовёнка» в 1985 году, «Сказка для Наташи» в 1986 году и «Возвращение домовёнка» в 1987 году.

Based on:
- "Важно отметить, что серия «Дом для Кузьки», вышедшая первой по времени, по сюжету оказалась всего лишь второй. Между тем первая часть оригинальной трилогии Татьяны Александровой заканчивается тем..."
- "Продолжение не заставило себя долго ждать, и в 1985 году вышла вторая серия «Приключения домовёнка», сценарий для которой был написан..."
- "В этом же году вышла третья серия мультфильма — «Сказка для Наташи», а через год и последняя — «Возвращение домовёнка»."
```

6. «Как называется фильм, где главного героя играет Том Круз и он пилот?»

```
Фильм, в котором Том Круз играет главного героя-пилота, называется «Топ Ган: Мэверик». Также ведется работа над продолжением этого фильма под названием «Топ Ган 3».

Based on:
1. "Известно, что в будущем фильме появятся те же персонажи, что и в предыдущих частях франшизы. Главный герой — легендарный пилот, капитан ВМС США Питер «Мэверик» Митчелл."
2. "В 2022 году Круз снялся и продюсировал сиквел боевика «Топ Ган: Мэверик», который собрал более 1,4 миллиарда долларов и стал его самым кассовым фильмом."
3. "Топ Ган 3» — будущий американский драматический боевик Джозефа Косински с Томом Крузом в главной роли, продолжение фильма «Топ Ган: Мэверик»."
```

7. почему Никулин отказался сниматься у Феллини в Сладкой жизни

```
"В предоставленной информации нет сведений о том, что Юрий Никулин отказывался сниматься у Федерико Феллини в фильме «Сладкая жизнь». Если вы имеете в виду другую ситуацию, относящуюся к «Сладкой жизни», уточните, пожалуйста."
```

[полные json ответы](https://github.com/Alexey77/graduate_work/blob/main/docs/response/)

### Участники команды:

* [Alexey77](https://github.com/Alexey77)
* [anjadvr](https://github.com/anjadvr)
* [itsuppartem](https://github.com/itsuppartem)