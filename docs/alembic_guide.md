# 🔄 Руководство по миграциям Alembic

Alembic — это инструмент для управления миграциями базы данных в CtrlBot. Он автоматически отслеживает изменения в схеме БД и применяет их безопасно.

## 📋 Основные команды

### 🐳 В Docker контейнере (рекомендуется)

```bash
# Создать новую миграцию
docker exec ctrlbot alembic revision --autogenerate -m "Описание изменений"

# Применить все миграции
docker exec ctrlbot alembic upgrade head

# Откатить одну миграцию
docker exec ctrlbot alembic downgrade -1

# Посмотреть текущую версию БД
docker exec ctrlbot alembic current

# Посмотреть историю миграций
docker exec ctrlbot alembic history

# Посмотреть информацию о миграции
docker exec ctrlbot alembic show <revision_id>
```

### 🛠️ Альтернативный скрипт

Используйте удобный скрипт `docker-migrate.sh`:

```bash
# Сделать файл исполняемым (Linux/macOS)
chmod +x docker-migrate.sh

# Создать новую миграцию
./docker-migrate.sh revision "Добавить новое поле"

# Применить миграции
./docker-migrate.sh upgrade

# Откатить миграцию
./docker-migrate.sh downgrade

# Посмотреть текущую версию
./docker-migrate.sh current

# Посмотреть историю
./docker-migrate.sh history
```

## 🔧 Рабочий процесс

### 1. Изменение схемы БД

1. Отредактируйте файлы с моделями SQLAlchemy (если используете ORM)
2. Или подготовьте SQL-скрипты для изменений

### 2. Создание миграции

```bash
# Автогенерация на основе изменений в моделях
docker exec ctrlbot alembic revision --autogenerate -m "Добавить таблицу пользователей"

# Ручная миграция (пустой шаблон)
docker exec ctrlbot alembic revision -m "Кастомные изменения"
```

### 3. Проверка миграции

1. Откройте созданный файл в `migrations/versions/`
2. Проверьте корректность сгенерированного кода
3. При необходимости отредактируйте вручную

### 4. Применение миграции

```bash
# В тестовой среде
docker exec ctrlbot alembic upgrade head

# В продакшене (с осторожностью!)
docker exec ctrlbot alembic upgrade head
```

## 📁 Структура файлов

```
migrations/
├── env.py              # Конфигурация окружения
├── script.py.mako      # Шаблон для новых миграций
└── versions/           # Файлы миграций
    ├── 9dc5ad2d2802_initial_migration_with_models.py
    └── ...
```

## ⚠️ Важные правила

### ✅ Рекомендации

- **Всегда проверяйте** сгенерированные миграции перед применением
- **Тестируйте** миграции на копии продакшн-данных
- **Делайте бэкапы** перед применением в продакшене
- **Используйте описательные** названия для миграций
- **Не редактируйте** уже применённые миграции

### ❌ Чего избегать

- Не удаляйте файлы миграций после их применения
- Не изменяйте порядок миграций
- Не применяйте миграции на продакшене без тестирования
- Не игнорируйте ошибки при применении миграций

## 🔄 Типичные сценарии

### Добавление нового поля

```python
# В upgrade():
op.add_column('posts', sa.Column('priority', sa.Integer(), nullable=True))

# В downgrade():
op.drop_column('posts', 'priority')
```

### Изменение типа поля

```python
# В upgrade():
op.alter_column('posts', 'status',
                existing_type=sa.VARCHAR(20),
                type_=sa.VARCHAR(50),
                existing_nullable=False)

# В downgrade():
op.alter_column('posts', 'status',
                existing_type=sa.VARCHAR(50),
                type_=sa.VARCHAR(20),
                existing_nullable=False)
```

### Добавление индекса

```python
# В upgrade():
op.create_index('idx_posts_priority', 'posts', ['priority'])

# В downgrade():
op.drop_index('idx_posts_priority', 'posts')
```

## 🚨 Восстановление после ошибок

### Откат миграции

```bash
# Откатить к конкретной версии
docker exec ctrlbot alembic downgrade <revision_id>

# Откатить на одну версию назад
docker exec ctrlbot alembic downgrade -1
```

### Ручное исправление

```bash
# Пометить текущее состояние как определённую версию
docker exec ctrlbot alembic stamp <revision_id>

# Применить миграцию без выполнения SQL
docker exec ctrlbot alembic stamp head
```

## 🔍 Отладка

### Просмотр SQL без выполнения

```bash
# Показать SQL для применения миграций
docker exec ctrlbot alembic upgrade head --sql

# Показать SQL для отката
docker exec ctrlbot alembic downgrade -1 --sql
```

### Логирование

Для включения подробного логирования отредактируйте `alembic.ini`:

```ini
# В секции [logger_alembic]
level = DEBUG
```

## 🎯 Лучшие практики

1. **Регулярное создание миграций** после изменений в схеме
2. **Тестирование миграций** на копии данных
3. **Резервное копирование** перед критическими изменениями
4. **Документирование** сложных миграций
5. **Использование транзакций** для атомарности операций

## 📞 Поддержка

При возникновении проблем с миграциями:

1. Проверьте логи: `docker logs ctrlbot`
2. Убедитесь в корректности миграций
3. Проверьте состояние БД: `docker exec ctrlbot alembic current`
4. При необходимости откатитесь к стабильной версии
