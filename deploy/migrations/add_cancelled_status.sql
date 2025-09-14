-- Добавляем статус 'cancelled' в enum post_status
-- Миграция: add_cancelled_status.sql

-- Добавляем новый статус в enum
ALTER TYPE post_status ADD VALUE IF NOT EXISTS 'cancelled';

-- Добавляем комментарий
COMMENT ON TYPE post_status IS 'Статусы постов: draft, scheduled, published, deleted, cancelled, failed';
