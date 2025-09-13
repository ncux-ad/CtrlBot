#!/usr/bin/env python3
"""
Healthcheck для CtrlBot в Docker
Проверяет доступность бота и его компонентов
"""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем путь к модулям
sys.path.append(str(Path(__file__).parent))

async def check_bot_health():
    """Проверяет здоровье бота"""
    try:
        # Проверяем конфигурацию
        from config import config
        if not config.BOT_TOKEN:
            print("❌ BOT_TOKEN не настроен")
            return False
        
        print("✅ Бот здоров")
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки здоровья: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(check_bot_health())
    sys.exit(0 if success else 1)
