#!/usr/bin/env python3
"""Проверка статусов в БД"""

import asyncio
from database import db

async def main():
    try:
        # Подключаемся к БД
        await db.connect()
        print("✅ Подключение к БД установлено")
        
        # Проверяем статусы
        result = await db.fetch_all("SELECT unnest(enum_range(NULL::post_status)) as status")
        statuses = [row['status'] for row in result]
        print("📊 Статусы в БД:", statuses)
        
        # Закрываем соединение
        await db.close()
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())
