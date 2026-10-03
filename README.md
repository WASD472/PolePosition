# PolePosition

Сайт про Формулу-1: календарь сезона, расписание сессий, результаты гонок и зачёты.

## Функционал

- **Главная** — ближайший Гран-при с таймером до первой сессии (время в МСК)
- **Календарь** — все Гран-при сезона с раскрытием сессий (практики, квалификация, спринт, гонка) и результатами гонок
- **Трассы** — список трасс
- **Пилоты** — список пилотов с победами и подиумами за сезон, сортировка по победам/подиумам
- **Команды** — список команд
- **Зачёты** — личный зачёт пилотов и кубок конструкторов с подсветкой топ-3

## Стек

**Backend:**

- Python 3.13
- FastAPI
- SQLAlchemy 2.x
- PostgreSQL
- Docker / Docker Compose
- httpx (для запросов к внешнему API)

**Frontend:**

- HTML
- CSS
- JavaScript (vanilla)

## Источник данных

Данные предоставлены **[Jolpica F1 API](https://api.jolpi.ca/)** — открытый API для Формулы-1, преемник Ergast API.

Jolpica распространяется по лицензии **[CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)** (Attribution-NonCommercial-ShareAlike). Проект использует данные в некоммерческих целях.

## Как запустить

1. Требования
   Docker и Docker Compose

2. Клонировать репозиторий

```bash
git clone https://github.com/WASD472/PolePosition.git
cd PolePosition/backend
```

### 3. Создать .env

```
DATABASE_URL=postgresql://postgres:secret@db:5432/poleposition
POSTGRES_USER=postgres
POSTGRES_PASSWORD=secret
POSTGRES_DB=poleposition
```

### 4. Запустить

```bash
docker compose up -d
API будет доступно на http://localhost:8000, Swagger — на http://localhost:8000/docs.

```

### 5. Загрузить данные

```bash
Данные загружаются из Jolpica вручную, отдельным скриптом (см. backend/app/services/jolpica.py). Базовая последовательность:

load_season(2026, db) — календарь, трассы, сессии

load_drivers(2026, db) — пилоты

load_driver_standings(2026, db) — зачёт пилотов

load_constructors(2026, db) — команды

load_constructor_standings(2026, db) — зачёт команд

load_results(2026, db) — результаты гонок
```

6. Фронтенд
   Открыть frontend/index.html через локальный сервер (например, Live Server в VS Code).
