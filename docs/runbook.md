# 🧭 Runbook (продакшен)

## Перед запуском
- Проверить .env (BOT_TOKEN, DB_*, YANDEX_*)
- Прогнать `make install && make test`
- Применить схему БД (`deploy/schema.sql`) или Alembic миграцию
- Настроить systemd и logrotate

## Дежурство
- Проверка `/ping`
- Лог-уровни: INFO для бота, WARNING для ошибок API
- Ежедневный бэкап в 03:00 (cron → `backup_postgres.sh`)

## Инциденты
- Бот не отвечает → `systemctl status controllerbot` → логи
- Публикация не прошла → проверить статус поста, Telegram ограничения
- AI не отвечает → переключить на fallback и уведомить владельца
