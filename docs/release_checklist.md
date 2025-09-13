# 🚀 Release Checklist

## 🔧 Подготовка
- [ ] Все задачи из sprint board (Must) закрыты
- [ ] Обновлён CHANGELOG.md с новой версией
- [ ] Версия в `pyproject.toml` или setup.cfg обновлена
- [ ] Тесты зелёные (pytest -v)
- [ ] Линтеры пройдены (ruff, black)

## 🗄️ База данных
- [ ] Все миграции Alembic применены (`alembic upgrade head`)
- [ ] Проверено соответствие схемы `deploy/schema.sql`
- [ ] Тестовые данные очищены, прод готов к данным пользователей

## 🛠 DevOps
- [ ] `.env` заполнен и проверен (BOT_TOKEN, DB_*, YANDEX_*)
- [ ] systemd unit активирован (`systemctl status controllerbot`)
- [ ] logrotate работает (`logrotate -d /etc/logrotate.d/post_bot_logrotate.conf`)
- [ ] Бэкапы PostgreSQL создаются (проверен `cron`)

## 🧪 Стейджинг
- [ ] Деплой протестирован на staging VPS
- [ ] Тестовый канал в Telegram подключён, пост опубликован и экспортирован
- [ ] Напоминания сработали в тестовом режиме (форс-триггер)

## 🚀 Продакшен
- [ ] CI/CD прошёл без ошибок
- [ ] Docker-образ запушен в DockerHub (если используется)
- [ ] Деплой на VPS завершён (deploy-vps.yml)
- [ ] Бот отвечает на /ping
- [ ] Админы получили уведомление о рестарте

## 📣 Пост-релиз
- [ ] Объявление в Telegram-канале (release notes)
- [ ] Создана GitHub release с changelog и бинарниками (если нужно)
- [ ] Мониторинг ошибок включён
