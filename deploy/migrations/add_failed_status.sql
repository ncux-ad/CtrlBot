-- Миграция для добавления статуса 'failed' в enum post_status
-- Это позволяет помечать посты, которые не удалось опубликовать

-- Добавляем новый статус в enum
ALTER TYPE post_status ADD VALUE IF NOT EXISTS 'failed';

-- Комментарий к новому статусу
COMMENT ON TYPE post_status IS 'Статусы постов: draft (черновик), scheduled (отложен), published (опубликован), deleted (удален), failed (не удалось опубликовать)';
