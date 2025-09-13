# 🧱 Миграции БД (Alebmic)

## Инициализация
```bash
pip install alembic
alembic init migrations
```

## Настройка
- В `alembic.ini` указать строку подключения к БД
- В `env.py` использовать строку из `.env`

## Базовая миграция
```bash
alembic revision -m "init schema"
# заполнить upgrade() схемой из deploy/schema.sql
alembic upgrade head
```
