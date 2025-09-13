#!/usr/bin/env python3
"""
Тестовая версия CtrlBot без подключения к БД
Для проверки базовой функциональности
"""

import asyncio
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.filters import Command

from config import config
from utils.logging import setup_logging, get_logger
from utils.filters import IsConfigAdminFilter

# Настройка логирования
setup_logging(
    log_file_path=config.LOG_FILE,
    error_file_path=config.LOG_ERROR_FILE,
    log_level=config.LOG_LEVEL
)
logger = get_logger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Простые обработчики для тестирования
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "🚀 <b>CtrlBot запущен!</b>\n\n"
        "Это тестовая версия без подключения к БД.\n"
        "Основные функции будут доступны после настройки PostgreSQL."
    )

@dp.message(Command("ping"))
async def cmd_ping(message: Message):
    """Обработчик команды /ping"""
    await message.answer("🏓 Pong! Бот работает.")

@dp.message(Command("admin"))
async def cmd_admin(message: Message):
    """Обработчик команды /admin (только для админов)"""
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            f"👑 <b>Админ панель</b>\n\n"
            f"ID: {message.from_user.id}\n"
            f"Имя: {message.from_user.first_name}\n"
            f"Админов в системе: {len(config.ADMIN_IDS)}"
        )
    else:
        await message.answer("❌ У вас нет прав администратора.")

@dp.message(Command("config"))
async def cmd_config(message: Message):
    """Обработчик команды /config (только для админов)"""
    if message.from_user.id in config.ADMIN_IDS:
        await message.answer(
            f"⚙️ <b>Конфигурация</b>\n\n"
            f"Логирование: {config.LOG_LEVEL}\n"
            f"Макс. длина поста: {config.MAX_POST_LENGTH}\n"
            f"Мин. тегов: {config.MIN_TAGS_REQUIRED}\n"
            f"Часовой пояс: {config.TIMEZONE}\n"
            f"AI настроен: {'Да' if config.YANDEX_API_KEY else 'Нет'}"
        )
    else:
        await message.answer("❌ У вас нет прав администратора.")

@dp.message()
async def handle_text(message: Message):
    """Обработчик текстовых сообщений"""
    if message.text:
        await message.answer(
            f"📝 <b>Получено сообщение:</b>\n\n"
            f"Длина: {len(message.text)} символов\n"
            f"От: {message.from_user.first_name}\n"
            f"ID: {message.from_user.id}"
        )

async def on_startup():
    """Инициализация при запуске"""
    try:
        # Валидация конфигурации
        config.validate()
        logger.info("Configuration validated")
        
        logger.info("Test bot startup completed (no database)")
        
    except Exception as e:
        logger.error("Startup failed: %s", e)
        raise

async def on_shutdown():
    """Очистка при завершении"""
    logger.info("Test bot shutdown completed")

async def main():
    """Главная функция"""
    try:
        # Обработчики сигналов для graceful shutdown
        def signal_handler(signum, _frame):
            logger.info("Received signal %s, shutting down...", signum)
            asyncio.create_task(on_shutdown())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Инициализация
        await on_startup()
        
        # Запуск бота
        logger.info("Starting test bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error("Bot error: %s", e)
        raise
    finally:
        await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error("Fatal error: %s", e)
        sys.exit(1)
