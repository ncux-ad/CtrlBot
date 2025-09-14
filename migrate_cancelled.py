#!/usr/bin/env python3
"""Миграция: добавление статуса cancelled"""

import asyncio
from database import db

async def main():
    try:
        # Добавляем статус cancelled в enum
        await db.execute("ALTER TYPE post_status ADD VALUE IF NOT EXISTS 'cancelled'")
        print("✅ Статус 'cancelled' добавлен в enum post_status")
        
        # Закрываем соединение
        await db.close()
        print("✅ Миграция завершена")
        
    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")

if __name__ == "__main__":
    asyncio.run(main())
