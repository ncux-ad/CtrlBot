# ControllerBot-лайт 2.0

Лёгкий Telegram-бот для администрирования каналов.

## 🚀 Возможности
- Автоматизация подготовки и публикации постов.
- Структура: теги, серии, дайджесты.
- Напоминания админу (12:00, 21:00).
- Экспорт (Excel, Markdown).
- Интеграция с AI (YandexGPT).
- Работа на слабом VPS без Docker.

## 📦 Установка
```bash
git clone https://github.com/your-org/controllerbot_lite.git
cd controllerbot_lite
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Создайте `.env` и настройте PostgreSQL.

## ▶️ Запуск
```bash
python bot.py
```
или через systemd:
```bash
sudo cp deploy/controllerbot.service /etc/systemd/system/
sudo systemctl enable controllerbot
sudo systemctl start controllerbot
```

## 📄 Документация
- [Roadmap](docs/roadmap.md)
- [Architecture](docs/architecture.md)
- [Changelog](docs/changelog.md)
- [Task Tracker](docs/tasktracker.md)
- [Engineering Guidelines](docs/engineering_guidelines.md)


---
## 🐳 Docker-развёртывание

```bash
docker-compose up -d --build
```

Сервисы:
- `bot` — Telegram-бот
- `db` — PostgreSQL

---
## ⚙️ CI/CD

- GitHub Actions: сборка, тесты, линтеры.
- Автобилд Docker-образа и пуш в DockerHub.
- Автодеплой на VPS через SSH.

---
## 🔐 Secrets

Секреты GitHub для CI/CD:
- `DOCKER_USERNAME`, `DOCKER_PASSWORD`
- `BOT_TOKEN`, `YANDEX_API_KEY`, `YANDEX_FOLDER_ID`
- `VPS_HOST`, `VPS_USER`, `VPS_SSH_KEY`

Подробнее см. [Engineering Guidelines](engineering_guidelines.md).


---
## 📚 Доп. материалы
- [Data Model](data_model.md)
- [ERD (Mermaid)](erd_mermaid.md)
- [FSM постов](fsm_posts.md)
- [Планировщик задач](scheduler_jobs.md)
- [Роли и права](permissions.md)
- [AI Spec](ai_spec.md)
- [Runbook](runbook.md)
- [Privacy & Security](privacy_security.md)
- [API Contracts](api_contracts.md)
- [Alebmic Setup](alembic_setup.md)
- SQL схема: `deploy/schema.sql`
- Шаблон экспорта: `deploy/export_template.xlsx`
