#!/usr/bin/env python3
"""
Скрипт для применения миграции add_entities_field.sql
"""

import asyncio
import asyncpg
from config import config

async def apply_migration():
    """Применяет миграцию для добавления поля entities"""
    try:
        # Подключаемся к БД
        conn = await asyncpg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        
        print("✅ Подключение к БД установлено")
        
        # Читаем файл миграции
        with open('deploy/migrations/add_entities_field.sql', 'r', encoding='utf-8') as f:
            migration_sql = f.read()
        
        print("📄 Файл миграции прочитан")
        
        # Выполняем миграцию
        await conn.execute(migration_sql)
        
        print("✅ Миграция успешно применена!")
        print("   - Добавлено поле entities в таблицу posts")
        print("   - Создан индекс для быстрого поиска")
        
        # Проверяем, что поле добавлено
        result = await conn.fetch("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'posts' AND column_name = 'entities'
        """)
        
        if result:
            print(f"✅ Поле entities найдено: {result[0]['data_type']}")
        else:
            print("❌ Поле entities не найдено!")
        
        await conn.close()
        print("🔌 Соединение с БД закрыто")
        
    except Exception as e:
        print(f"❌ Ошибка применения миграции: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Применение миграции add_entities_field.sql")
    print("=" * 50)
    
    success = asyncio.run(apply_migration())
    
    if success:
        print("\n🎉 Миграция применена успешно!")
        print("Теперь можно перезапускать бота.")
    else:
        print("\n❌ Ошибка применения миграции!")
        print("Проверьте настройки БД в config.py")
