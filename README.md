# CtrlBot - Микро-CMS для Telegram каналов

Современный Telegram-бот для управления контентом каналов с поддержкой медиа, отложенной публикации и продвинутой аналитики.

## 🚀 Основные возможности

### 📝 Создание контента
- **Мультимедиа посты**: фото, видео, документы, голосовые сообщения, аудио
- **Markdown форматирование**: жирный текст, курсив, код, ссылки
- **Предпросмотр**: полный предпросмотр перед публикацией
- **Валидация**: проверка корректности контента

### ⏰ Планирование публикаций
- **Отложенная публикация**: планирование постов на любое время
- **Управление расписанием**: изменение времени, отмена постов
- **Автоматическая публикация**: фоновый планировщик

### 📊 Управление контентом
- **Карточки постов**: современный интерфейс с превью
- **Фильтрация**: по дате, статусу, типу контента
- **Сортировка**: по дате создания, публикации
- **Массовые операции**: удаление, редактирование

### 📈 Аналитика и статистика
- **Еженедельные отчеты**: автоматическая отправка статистики
- **Детальная аналитика**: просмотры, взаимодействия
- **Экспорт данных**: Excel, Markdown

### 🏷️ Организация контента
- **Теги**: категоризация постов
- **Серии**: группировка связанного контента
- **Дайджесты**: сборники лучших постов

## 🛠 Технический стек

- **Backend**: Python 3.11, aiogram 3.x
- **База данных**: PostgreSQL 15
- **Планировщик**: APScheduler
- **Контейнеризация**: Docker, Docker Compose
- **Форматирование**: MarkdownV2

## 📦 Установка и запуск

### Docker (рекомендуется)

```bash
# Клонирование репозитория
git clone https://github.com/your-org/ctrlbot.git
cd ctrlbot

# Настройка окружения
cp .env.example .env
# Отредактируйте .env файл

# Запуск через Docker Compose
docker-compose up -d --build
```

### Локальная установка

```bash
# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows

# Установка зависимостей
pip install -r requirements.txt

# Настройка базы данных
# Создайте PostgreSQL базу и выполните schema.sql

# Запуск бота
python bot.py
```

## ⚙️ Конфигурация

Создайте файл `.env`:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token
ADMIN_IDS=123456789,987654321

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ctrlbot_db
DB_USER=ctrlbot
DB_PASSWORD=your_password

# AI Integration (опционально)
YANDEX_API_KEY=your_yandex_key
YANDEX_FOLDER_ID=your_folder_id

# Logging
LOG_LEVEL=INFO
TIMEZONE=Europe/Moscow
```

## 🎯 Использование

### Основные команды

- `/start` - Запуск бота и главное меню
- `/admin` - Админ-панель
- `/my_posts` - Мои посты
- `/help` - Справка

### Создание поста

1. Отправьте `/admin` → "Создать пост"
2. Отправьте текст, фото, видео или другой контент
3. Просмотрите предпросмотр
4. Выберите: "Опубликовать сейчас" или "Запланировать"

### Управление постами

- **Просмотр**: карточки с превью и метаданными
- **Фильтрация**: по дате, статусу, типу
- **Редактирование**: изменение времени публикации
- **Удаление**: из канала с сохранением в БД

## 🏗 Архитектура

```
CtrlBot/
├── handlers/          # Обработчики Telegram событий
├── services/          # Бизнес-логика
├── utils/            # Утилиты и вспомогательные функции
├── database/         # Работа с БД
├── deploy/           # Деплой и миграции
└── docs/            # Документация
```

### Ключевые компоненты

- **PostService**: CRUD операции с постами
- **PostPublisher**: Публикация в Telegram каналы
- **PostScheduler**: Планировщик отложенных постов
- **PostCardRenderer**: Рендеринг карточек постов
- **PostFilters**: Фильтрация и сортировка

## 🔧 Разработка

### Структура проекта

```
handlers/
├── admin.py          # Админ-панель
├── post_handlers.py  # Создание и управление постами
└── posts.py         # Просмотр постов

services/
├── post_service.py   # Бизнес-логика постов
├── publisher.py     # Публикация в каналы
└── post_scheduler.py # Планировщик

utils/
├── states.py        # FSM состояния
├── pagination.py    # Пагинация
├── post_card.py     # Карточки постов
└── post_filters.py  # Фильтры
```

### Добавление новых функций

1. Создайте обработчик в `handlers/`
2. Добавьте бизнес-логику в `services/`
3. Обновите FSM состояния в `utils/states.py`
4. Добавьте тесты

## 📊 Мониторинг

### Логи

```bash
# Просмотр логов Docker контейнера
docker logs ctrlbot -f

# Логи базы данных
docker logs ctrlbot_postgres -f
```

### Health Check

```bash
# Проверка состояния бота
curl http://localhost:8000/health
```

## 🚀 Деплой

### Production

1. Настройте переменные окружения
2. Обновите `docker-compose.yml` для production
3. Запустите: `docker-compose -f docker-compose.prod.yml up -d`

### CI/CD

- Автоматическая сборка при push в main
- Тестирование кода
- Деплой на production сервер

## 📚 Документация

- [Архитектура](docs/architecture.md)
- [API Reference](docs/api.md)
- [Changelog](docs/changelog.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Вклад в проект

1. Fork репозитория
2. Создайте feature branch
3. Внесите изменения
4. Добавьте тесты
5. Создайте Pull Request

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 🆘 Поддержка

- GitHub Issues: [Создать issue](https://github.com/your-org/ctrlbot/issues)
- Telegram: @your_support_bot
- Email: support@yourdomain.com

---

**CtrlBot** - современное решение для управления Telegram каналами! 🚀
