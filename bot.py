# Entry point

import asyncio
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from config import config
from database import db
from utils.logging import setup_logging, get_logger
from utils.states import PostCreationStates, AdminStates, DigestStates

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

# Регистрация состояний FSM
dp.include_router(PostCreationStates.router)
dp.include_router(AdminStates.router)
dp.include_router(DigestStates.router)

async def on_startup():
    """Инициализация при запуске"""
    try:
        # Валидация конфигурации
        config.validate()
        logger.info("Configuration validated")
        
        # Подключение к БД
        await db.connect()
        await db.init_schema()
        logger.info("Database connected and schema initialized")
        
        # Здесь будут регистрироваться обработчики
        # from handlers import posts, admin, reminders, digest
        # dp.include_router(posts.router)
        # dp.include_router(admin.router)
        # dp.include_router(reminders.router)
        # dp.include_router(digest.router)
        
        logger.info("Bot startup completed")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

async def on_shutdown():
    """Очистка при завершении"""
    try:
        await db.close()
        logger.info("Database connection closed")
        logger.info("Bot shutdown completed")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")

async def main():
    """Главная функция"""
    try:
        # Обработчики сигналов для graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, shutting down...")
            asyncio.create_task(on_shutdown())
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Инициализация
        await on_startup()
        
        # Запуск бота
        logger.info("Starting bot...")
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise
    finally:
        await on_shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
