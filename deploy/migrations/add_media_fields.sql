-- Миграция: добавление полей для медиа-файлов
-- Дата: 2025-09-13

-- Добавляем поля для медиа
ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_type text;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_file_id text;
ALTER TABLE posts ADD COLUMN IF NOT EXISTS media_data jsonb;

-- Добавляем комментарии
COMMENT ON COLUMN posts.media_type IS 'Тип медиа: photo, video, document, voice, audio, video_note';
COMMENT ON COLUMN posts.media_file_id IS 'Telegram file_id медиа-файла';
COMMENT ON COLUMN posts.media_data IS 'Дополнительные данные медиа (размеры, длительность, MIME-тип и т.д.)';

-- Создаем индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_posts_media_type ON posts (media_type);
CREATE INDEX IF NOT EXISTS idx_posts_media_file_id ON posts (media_file_id);
CREATE INDEX IF NOT EXISTS idx_posts_media_data ON posts USING GIN (media_data);
