# 🏗 Архитектура

## Технологии
- Python 3.10+
- aiogram 3.x
- PostgreSQL
- APScheduler
- YandexGPT (API)

## Структура
- `handlers/` — обработчики событий Telegram
- `services/` — бизнес-логика (посты, теги, дайджесты, AI)
- `utils/` — вспомогательные утилиты (логирование, фильтры, клавиатуры, FSM)
- `scheduler/` — задачи планировщика (напоминания, дайджесты)
- `database/` — подключение к PostgreSQL
- `docs/` — документация
- `tests/` — тесты

## Архитектурный подход
- MVP: модульная структура (быстро, просто).
- SaaS: переход к Dependency Injection через middleware.
