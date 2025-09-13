#!/usr/bin/env python3
"""
Тест подключения к базе данных
"""

import asyncio
import asyncpg
from config import config

async def test_connection():
    """Тестирует подключение к БД"""
    try:
        print(f"🔍 Тестируем подключение к БД...")
        print(f"   Host: {config.DB_HOST}")
        print(f"   Port: {config.DB_PORT}")
        print(f"   User: {config.DB_USER}")
        print(f"   Database: {config.DB_NAME}")
        print(f"   Password: {'*' * len(config.DB_PASSWORD)}")
        
        # Подключаемся к БД
        conn = await asyncpg.connect(
            host=config.DB_HOST,
            port=config.DB_PORT,
            user=config.DB_USER,
            password=config.DB_PASSWORD,
            database=config.DB_NAME
        )
        
        print("✅ Подключение успешно!")
        
        # Проверяем, что можем выполнить запрос
        result = await conn.fetchval("SELECT 1")
        print(f"✅ Запрос выполнен: {result}")
        
        # Проверяем таблицу posts
        result = await conn.fetchval("SELECT COUNT(*) FROM posts")
        print(f"✅ Таблица posts: {result} записей")
        
        # Проверяем поле entities
        result = await conn.fetchval("SELECT column_name FROM information_schema.columns WHERE table_name = 'posts' AND column_name = 'entities'")
        if result:
            print("✅ Поле entities найдено!")
        else:
            print("❌ Поле entities не найдено!")
        
        await conn.close()
        print("✅ Соединение закрыто")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Тест подключения к базе данных CtrlBot")
    print("=" * 50)
    
    success = asyncio.run(test_connection())
    
    if success:
        print("\n🎉 Подключение к БД работает!")
    else:
        print("\n❌ Проблема с подключением к БД!")
