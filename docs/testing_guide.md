# 🧪 Testing Guide

## Пираміда тестов
- Unit: `services/*`, чистая логика (моки БД/AI)
- Интеграционные: взаимодействие handlers ↔ services ↔ БД (тестовая БД)
- e2e: сценарий создания и публикации поста (test token + test channel)

## Инструменты
- pytest, pytest-asyncio
- factory-boy/fixtures для мок-данных
