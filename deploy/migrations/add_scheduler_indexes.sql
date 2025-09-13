-- Миграция для оптимизации PostScheduler
-- Добавляем индексы для эффективной работы с отложенными постами

-- Индекс для быстрого поиска постов по статусу и времени публикации
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_status_time 
ON posts (status, scheduled_at) 
WHERE status = 'scheduled';

-- Индекс для быстрого поиска постов по времени публикации (для случаев без фильтра по статусу)
CREATE INDEX IF NOT EXISTS idx_posts_scheduled_at 
ON posts (scheduled_at) 
WHERE scheduled_at IS NOT NULL;

-- Индекс для быстрого поиска постов по каналу и статусу
CREATE INDEX IF NOT EXISTS idx_posts_channel_status 
ON posts (channel_id, status);

-- Комментарии к индексам
COMMENT ON INDEX idx_posts_scheduled_status_time IS 'Индекс для быстрого поиска отложенных постов по статусу и времени';
COMMENT ON INDEX idx_posts_scheduled_at IS 'Индекс для быстрого поиска постов по времени публикации';
COMMENT ON INDEX idx_posts_channel_status IS 'Индекс для быстрого поиска постов по каналу и статусу';
