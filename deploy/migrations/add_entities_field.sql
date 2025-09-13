-- Миграция: добавление поля entities в таблицу posts
-- Дата: 2025-01-27
-- Описание: Добавляет поле entities для хранения Telegram entities в формате JSON

-- Добавляем поле entities в таблицу posts
ALTER TABLE posts ADD COLUMN IF NOT EXISTS entities jsonb;

-- Добавляем комментарий к полю
COMMENT ON COLUMN posts.entities IS 'Telegram entities для сохранения форматирования в формате JSON';

-- Создаем индекс для быстрого поиска по entities (опционально)
CREATE INDEX IF NOT EXISTS idx_posts_entities ON posts USING GIN (entities);

-- Обновляем версию схемы (если есть таблица версий)
-- INSERT INTO schema_versions (version, applied_at) VALUES ('add_entities_field', NOW());
