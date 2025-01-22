# asyncFastApi-BaseProject

Проект представляет собой демонстрационный сервис FastAPI, разработанный с использованием Clean Architecture.

## Быстрый старт

1. Создать переменные окружения:

```bash
cd ./backend/ 
cp .env.example ./app/.env
```

2. Запустить проект:

```bash
docker-compose up -d --build
```


## Доступ к пользовательскому интерфейсу:

Благодаря строгой типизации во фреймворке есть встроенная генерация OpenAPI-файла.
После запуска приложения вы получите готовую документацию для вашего API и интерфейс для её просмотра, например по адресу:

- Swagger UI: [http://127.0.0.1:8000/docs/](http://127.0.0.1:8000/docs/)
- ReDoc: [http://127.0.0.1:8000/redoc/](http://127.0.0.1:8000/redoc/)

Чтобы войти в систему, нажмите кнопку *Authorize* в правом верхнем углу и введите учетные данные пользователя, который находится внутри базы данных. Если их нет, зарегистрировать пользователя с промощью эндпоита `/signup`.

Затем вы сможете опробовать конечную точку `/me`. Который покажет вам данные авторизованного пользователя.

[Реализация](./docs/backend/authentication.md) авторизации сделана очень близко к [документации FastAPI](https://fastapi.tiangolo.com/tutorial/security/).

Конечная точка `/token` после введения логина и пароля сгенерирует JWT токены для этого пользователя, которые действительны в течение некоторого времени (указанного в настройках приложения).

# Общая архитектура системы

У FastAPI нет традиционной структуры проекта, чтобы сделать проект более модульным, масштабируемым и тестируемым используется Clean Architecture. Эта архитектура предпилагает разделяет приложение на несколько слоев, вложенный друг в круга.

Такая архитектура следует правилу, называемому <i>Правилом зависимости</i>, которое гласит, что поток между слоями должен двигаться к внутреннему слою. Это, в свою очередь, означает, что внутренний слой не должен беспокоиться о том, что происходит во внешнем слое, а внешний слой не будет иметь никакого влияния на внутренние слой.

Для достижения концепции «чистой архитектуры» разделим приложение на компоненты

```
├─📁 app --------------- # приложение
│ ├─📁 api ------------ # конечноые точки
│ ├─📁 core ----------- # основные настройки приложения
│ ├─📁 migrations ----- # Alembic миграции
│ ├─📁 model ---------- # Sqlalchemy2 модели
│ ├─📁 repositories --- # доступ к данным
│ ├─📁 schema --------- # схемы данных
│ └─📁 service -------- # бизнес логика
```

## Используемые технологии

### FastAPI

[FastAPI](https://fastapi.tiangolo.com/) - асинхронный фреймворк, на котором создан REST API для демонстрации возможностей. В основе FastAPI лежит веб-фреймворк Starlette, использующий asyncio, и библиотека для валидации данных Pydantic.

### Fastapi Middleware

Это способ глобальной обработки запросов до того, как они дойдут до ваших конечных точек. FastAPI предоставляет несколько встроенных вариантов Middleware, которые расширяют функциональность приложений.

Декоратор `@app.middleware("http")` предназначен для перехвата запросов и ответов, что позволяет выполнять код до и после обработки запроса путём выполнения операции. Изменить ответ перед его возвратом, полезно для добавления пользовательских заголовков или информации для ведения журнала. Пользовательские заголовки могут быть добавлены с помощью префикса "X-", `response.headers["X-Process-Time"] = ...`. 

Но если у вас есть пользовательские заголовки, которые вы хотите, чтобы клиент в браузере мог видеть, вам нужно добавить их в свои конфигурации CORS (совместное использование ресурсов разных источников), используя параметр "expose_headers", `app.add_middleware(expose_headers=["X-Process-Time"], ...)`.

### JWT Authentication

Реализация аутентификации [JSON Web Token](https://jwt.io/introduction) для безопасной аутентификации пользователей.

### Pydantic

[Pydantic](https://docs.pydantic.dev/latest/) - библиотека для проверки данных и управления настройками для Python, часто используемая с FastAPI.

### Sqlalchemy

[Sqlalchemy](https://docs.sqlalchemy.org/) - библиотека, которая позволяет работать с реляционными базами данных с помощью ORM (объектно-реляционного сопоставления).
С помощью Sqlalchemy был создан класс, который можем асинхронно взаимодействовать с базой данных.

### Alembic

[Alembic](https://alembic.sqlalchemy.org/en/latest/) — это легкий инструмент миграции базы данных для использования совместно с SQLAlchemy.

`alembic init -t async <change>` (это ассинхронный код для создания миграций, добавьте путь для расположения директории миграции)

`alembic revision --autogenerate -m "<change>"` (это сгенерит миграцию, добавьте название версии миграции)

`alembic upgrade head` (это обновляет/настраивает базу данных с использованием самой последней версии)

### Loguru

[Loguru](https://loguru.readthedocs.io/en/stable/) — простая библиотека для ведения журналов.

### Uvicorn

[Uvicorn](https://www.uvicorn.org/) - это веб-сервер поддерживающий протокол ASGI, обслуживающий приложения FastAPI.

### Docker Compose

[Docker Compose](https://docs.docker.com/compose/) - это инструмент для определения и запуска многоконтейнерных приложений. Это ключ к открытию оптимизированного и эффективного опыта разработки и развертывания.

### Хуки

Хуки - это запуска пользовательских скриптов в случае возникновения определённых событий.

pre-commit - это инструмент автоматизации проверок кода

`pre-commit install`(добавить прекоммит)

`pre-commit run --all-files`(запустить без коммита)

`git commit --no-verify`  (пропустить выполнение хука при коммите)

### Poetry

[Poetry](https://python-poetry.org/) — это виртуальная среда, подобная venv, с более разнообразными опциями конфигурации.
Вот несколько удобных команд:

`poetry shell` (старт виртуальной среды shell)

`poetry add <module>` (эквивалент установки pip, добавляет этот модуль и зависимости к нему)

`poetry update` (обновить/установить все зависимости)
