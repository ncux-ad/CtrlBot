# 📚 Data Model (PostgreSQL)

## Таблицы

### channels
- id (PK, bigint)
- tg_channel_id (bigint, unique) — ID канала в Telegram
- title (text)
- timezone (text, default 'Europe/Moscow')
- created_at (timestamptz, default now())

### posts
- id (PK, bigint)
- channel_id (FK -> channels.id, index)
- title (text, nullable)
- body_md (text) — Markdown-текст
- status (enum: draft|scheduled|published|deleted, default 'draft', index)
- scheduled_at (timestamptz, nullable, index)
- published_at (timestamptz, nullable, index)
- message_id (bigint, nullable) — id сообщения в канале после публикации
- series_id (FK -> series.id, nullable, index)
- tags_cache (text[]) — денормализованный кеш тегов
- created_at (timestamptz, default now())
- updated_at (timestamptz, default now())

### series
- id (PK, bigint)
- channel_id (FK -> channels.id, index)
- code (text, unique per channel) — машинное имя серии
- title (text)
- next_number (int, default 1) — для авто-нумерации
- created_at (timestamptz, default now())

### tags
- id (PK, bigint)
- channel_id (FK -> channels.id, index)
- name (text)
- kind (enum: regular|system|mood, default 'regular')
- UNIQUE(channel_id, name)

### post_tags (link)
- post_id (FK -> posts.id, index, on delete cascade)
- tag_id  (FK -> tags.id,  index, on delete cascade)
- PK(post_id, tag_id)

### reminders
- id (PK, bigint)
- channel_id (FK -> channels.id, index)
- kind (enum: soft_morning|evening_slot|custom)
- schedule_cron (text) — CRON-выражение или ISO time
- enabled (bool, default true)
- created_at (timestamptz, default now())

### digests
- id (PK, bigint)
- channel_id (FK -> channels.id, index)
- period_start (date)
- period_end (date)
- kind (enum: weekly|monthly)
- status (enum: scheduled|sent|failed, default 'scheduled')
- export_path (text, nullable)
- created_at (timestamptz, default now())

## Индексы и ограничения
- posts(status, scheduled_at) — ускорение выборки на публикацию.
- posts(channel_id, created_at desc) — лента.
- post_tags по обоим полям — для join.
- tags unique по (channel_id, name) — запрет дублей.

## Политика данных
- Удаление постов — мягкое (status=deleted).
- Денормализация: tags_cache в posts для быстрой фильтрации.
