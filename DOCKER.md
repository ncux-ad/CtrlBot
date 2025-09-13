# 🐳 CtrlBot Docker Setup

## Быстрый старт

### 1. Настройка переменных окружения
Скопируйте `.env.example` в `.env` и заполните:
```bash
cp .env.example .env
```

### 2. Запуск бота
```bash
# Запуск через менеджер
.\docker_manager.bat

# Или напрямую
docker-compose up --build -d
```

### 3. Проверка статуса
```bash
# Статус контейнеров
docker-compose ps

# Логи бота
docker-compose logs -f ctrlbot

# Логи БД
docker-compose logs -f postgres
```

## Управление

### Основные команды
```bash
# Запуск
docker-compose up -d

# Остановка
docker-compose down

# Перезапуск
docker-compose restart ctrlbot

# Пересборка
docker-compose up --build -d
```

### Скрипты
- `docker_manager.bat` - Полное меню управления
- `restart_docker.bat` - Быстрый перезапуск

## Мониторинг

### Healthcheck
Бот автоматически проверяет свое здоровье каждые 30 секунд:
- Конфигурация
- Подключение к БД
- Планировщик

### Логи
```bash
# Все логи
docker-compose logs

# Только бот
docker-compose logs ctrlbot

# Следить за логами
docker-compose logs -f ctrlbot
```

## База данных

### pgAdmin (опционально)
```bash
# Запуск с pgAdmin
docker-compose --profile admin up -d

# Доступ: http://localhost:8080
# Email: admin@ctrlbot.local
# Password: admin
```

### Прямое подключение
```bash
# Войти в контейнер БД
docker-compose exec postgres psql -U ctrlbot -d ctrlbot_db
```

## Разработка

### Вход в контейнер
```bash
docker-compose exec ctrlbot /bin/bash
```

### Обновление кода
```bash
# Пересборка после изменений
docker-compose up --build -d
```

## Очистка

### Остановка и удаление
```bash
# Остановить и удалить контейнеры
docker-compose down

# Удалить все (включая данные!)
docker-compose down -v
docker system prune -f
```

## Troubleshooting

### Бот не запускается
1. Проверьте `.env` файл
2. Проверьте логи: `docker-compose logs ctrlbot`
3. Проверьте БД: `docker-compose logs postgres`

### Проблемы с БД
1. Убедитесь, что БД запущена: `docker-compose ps`
2. Проверьте подключение: `docker-compose exec postgres pg_isready`

### Проблемы с форматированием
- Используйте **копирование** вместо пересылки
- Проверьте логи на наличие entities
