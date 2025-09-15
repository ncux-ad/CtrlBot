Андрей Данилин | Психиатр, нарколог Москва, [15.09.2025 04:31]
/add_channel

CtrlBot, [15.09.2025 04:31]
➕ *Добавление канала*

Для добавления канала:
1. Добавьте бота в канал как администратора
2. Отправьте команду /start в канале
3. Бот автоматически добавит канал в систему

Или используйте команду /add_channel в канале.

Андрей Данилин | Психиатр, нарколог Москва, [15.09.2025 04:46]
/add_channel

CtrlBot, [15.09.2025 04:46]
❓ *Неизвестная команда*

Используйте /help для просмотра доступных команд.#!/usr/bin/env python3
"""
Скрипт для применения оптимизации PostScheduler
"""
import asyncio
import logging
from database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def apply_scheduler_optimization():
    """Применяет оптимизацию PostScheduler"""
    try:
        logger.info("🚀 Применяем оптимизацию PostScheduler...")
        
        # Читаем миграцию
        with open('deploy/migrations/add_scheduler_indexes.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        # Применяем миграцию
        logger.info("📊 Создаем индексы для оптимизации...")
        await db.execute(migration_sql)
        
        logger.info("✅ Оптимизация PostScheduler применена успешно!")
        
        # Показываем статистику
        stats_query = """
            SELECT 
                schemaname,
                tablename,
                indexname,
                indexdef
            FROM pg_indexes 
            WHERE tablename = 'posts' 
            AND indexname LIKE 'idx_posts_%'
            ORDER BY indexname
        """
        results = await db.fetch_all(stats_query)
        
        logger.info("📈 Созданные индексы:")
        for row in results:
            logger.info(f"  - {row['indexname']}")
        
        # Показываем статистику по постам
        posts_stats = await db.fetch_all("""
            SELECT 
                status,
                COUNT(*) as count
            FROM posts 
            WHERE scheduled_at IS NOT NULL
            GROUP BY status
        """)
        
        logger.info("📊 Статистика постов:")
        for row in posts_stats:
            logger.info(f"  - {row['status']}: {row['count']}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка применения оптимизации: {e}")
        raise
    finally:
        await db.close()

if __name__ == "__main__":
    asyncio.run(apply_scheduler_optimization())
