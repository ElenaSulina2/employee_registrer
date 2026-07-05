# Реестр сотрудников

Веб-приложение для ведения списка сотрудников с возможностью добавления, редактирования, удаления, поиска и фильтрации. Реализовано на **FastAPI** с использованием **SQLAlchemy**, **PostgreSQL**, **Jinja2** и **Tailwind CSS**.

## Основные возможности ✅

- Просмотр списка сотрудников с пагинацией
- Добавление нового сотрудника (ФИО, дата рождения, пол, телефон, фото)
- Редактирование данных сотрудника
- Удаление сотрудника (с удалением фото)
- Поиск по ФИО
- Фильтрация по полу и возрасту
- Загрузка фотографий (форматы JPG, PNG, размер до 200 КБ)
- Автоматическое вычисление возраста
- Адаптивный интерфейс на Tailwind CSS

## Стек технологий 🔧

- **Python 3.12**
- **FastAPI** – веб-фреймворк
- **SQLAlchemy** – ORM
- **PostgreSQL** (SQLite для тестирования)
- **Alembic** – миграции
- **Jinja2** – шаблонизатор
- **Tailwind CSS** – стилизация
- **Docker** + **Docker Compose** – контейнеризация
- **Pytest** – тестирование
- **Pydantic** – валидация данных

## Установка и запуск 🚀

### Локальный запуск (без Docker)

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/your-username/employee-registry.git
   cd employee-registry

2. Создайте и активируйте виртуальное окружение:

    ```bash
    python -m venv venv
    source venv/bin/activate   # Linux/macOS
    venv\Scripts\activate      # Windows


3. Установите зависимости:

    ```bash
    pip install -r requirements.txt

4. Создайте файл .env в корне проекта:
    ```bash
    env
    DATABASE_URL=postgresql://user:password@localhost:5432/employee_db
    MAX_PHOTO_SIZE_KB=200

5. Примените миграции Alembic:
    ```bash
    alembic upgrade head

6. Запустите приложение:

    ```bash
    uvicorn app.main:app --reload
    Откройте в браузере: http://localhost:8000

### Запуск через Docker (рекомендуемый способ):

1. Убедитесь, что установлены Docker и Docker Compose.

2. Соберите и запустите контейнеры:

    ```bash
    docker-compose up --build
    Приложение будет доступно по адресу: http://localhost:8000

3. Для остановки:

    ```bash
    docker-compose down

4. Для полной очистки (удаление томов с БД и загруженными фото):
    ```bash
    docker-compose down -v

## Тестирование 🧪

### Запуск тестов с покрытием:
    `bash pytest -v --cov=app`

## Структура проекта 📌

```
employee-registry/
├── app/
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── dependencies.py
│   ├── template_engine.py
│   ├── routers/
│   │   └── employees.py
│   ├── services/
│   │   └── employee_service.py
│   ├── utils/
│   │   ├── helpers.py
│   │   ├── validators.py
│   │   ├── filters.py
│   │   ├── constants.py
│   │   └── template_utils.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   └── add_edit.html
│   └── static/
│       └── uploads/
├── migrations/       
├── tests/
│   ├── conftest.py
│   ├── test_employees.py
│   └── test_utils.py
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```


## Примечания по разработке ℹ️

- В проекте все эндпоинты и бизнес-логика осознанно реализованы с использованием синхронных функций выбрана в пользу надежности. При развитии проекта возможен переход на асинхонный вариант.

- Для изменения шаблонов используйте Tailwind CSS (подключён через CDN для простоты разрабоки).

- Для работы с PostgreSQL в Docker том с данными сохраняется между запусками.

## Возможные улучшения 💡

* Добавить логирование.

* Расширенная валидация (телефон, email).

* Кеширование с помощью Redis.

Лицензия
MIT License 📄