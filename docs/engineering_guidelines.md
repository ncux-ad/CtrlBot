# ⚙️ Engineering Guidelines

## Стиль кода
- Python 3.10+
- PEP8
- Ruff (линтер)
- Black (форматирование)
- Mypy (статическая типизация)

## Коммиты
- Conventional Commits
  - `feat:` новая фича
  - `fix:` исправление
  - `chore:` рутинные задачи

## Логирование
- Все логи → `/var/log/post_bot.log`
- Ошибки → `/var/log/post_bot.err`
- logrotate: хранение 14 дней

## Безопасность
- Все ключи и токены → `.env`
- Никогда не коммитить `.env`
- Использовать минимум прав для PostgreSQL

## Тестирование
- pytest
- покрытие: `services/*` и `handlers/*`

## CI/CD
- Deploy: `git pull && systemctl restart controllerbot`
- Unit-тесты перед мёрджем в main


---
## 🔐 GitHub Secrets (CI/CD)

### Как добавить
1. Перейти: **GitHub → Settings → Secrets and variables → Actions → New repository secret**
2. Добавить секреты из таблицы ниже.

### Основные секреты

| Secret             | Что хранит                      | Пример |
|--------------------|---------------------------------|--------|
| DOCKER_USERNAME    | Логин от DockerHub              | andrey_danilin |
| DOCKER_PASSWORD    | Access token DockerHub          | ghp_xxxxxxxx |
| BOT_TOKEN          | Telegram Bot API токен          | 123456:ABC-DEF1234 |
| DB_HOST            | Хост базы данных                | db |
| DB_USER            | Пользователь PostgreSQL         | controllerbot |
| DB_PASS            | Пароль PostgreSQL               | supersecret |
| DB_NAME            | Имя базы                        | controllerbot_db |
| YANDEX_API_KEY     | API-ключ Яндекс GPT             | AQVNxxx... |
| YANDEX_FOLDER_ID   | ID каталога в Yandex Cloud      | b1gXXXXXX |

### Использование в workflow
```yaml
env:
  BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
  DB_PASS: ${{ secrets.DB_PASS }}
  YANDEX_API_KEY: ${{ secrets.YANDEX_API_KEY }}
```

### Для локальной разработки
- Копируем `.env.example` → `.env`
- Заполняем значениями из secrets
- `.env` не коммитим!


---
## 🚀 Деплой на VPS

### Требования
- systemd
- Python 3.10+ (или Docker)
- PostgreSQL

### Workflow GitHub Actions (deploy-vps.yml)
1. Загружает код на сервер через `rsync`.
2. Выполняет `systemctl restart controllerbot`.

### Secrets для деплоя
- `VPS_HOST` → IP/DNS сервера
- `VPS_USER` → пользователь (обычно `deploy`)
- `VPS_SSH_KEY` → приватный SSH-ключ (base64 или обычный)

---
## 🐳 Docker
- `Dockerfile` и `docker-compose.yml` для запуска бота + PostgreSQL.
- Volume `pgdata` для сохранения данных.

---
## 🔧 Systemd unit с .env

Пример: `deploy/controllerbot.service`

```ini
[Service]
EnvironmentFile=/opt/controllerbot_lite/.env
ExecStart=/usr/bin/python3 bot.py
Restart=always
```

Файл `.env` загружается автоматически, токены не хардкодятся в сервис.
