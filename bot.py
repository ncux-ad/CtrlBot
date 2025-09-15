# Entry point

import asyncio
import signal
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
# ParseMode больше не нужен глобально

from config import config
from database import db
from utils.logging import setup_logging, get_logger
# States импортируются автоматически при использовании

# Настройка логирования
setup_logging(log_level=config.LOG_LEVEL)
logger = get_logger(__name__)

# Инициализация бота и диспетчера
bot = Bot(
    token=config.BOT_TOKEN,
    default=DefaultBotProperties()  # Убираем глобальный parse_mode
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Регистрация состояний FSM (состояния регистрируются автоматически при использовании)

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
        
        # Регистрация обработчиков (только для админов)
        from handlers import post_handlers, admin, reminder_handlers, digest_handlers, ai_handlers, post_deletion_handlers
        dp.include_router(admin.router)
        dp.include_router(post_handlers.router)
        dp.include_router(post_deletion_handlers.router)
        dp.include_router(reminder_handlers.router)
        dp.include_router(digest_handlers.router)
        dp.include_router(ai_handlers.router)
        
        # Импорт и регистрация роутера для опросов
        from handlers import poll_handlers
        dp.include_router(poll_handlers.router)
        
        # Глобальный обработчик для не-админов (должен быть последним)
        from aiogram import Router
        from aiogram.types import Message, CallbackQuery
        
        non_admin_router = Router()
        
        @non_admin_router.message()
        async def handle_non_admin_messages(message: Message):
            """Обработчик для всех сообщений от не-админов"""
            if message.from_user and message.from_user.id not in config.ADMIN_IDS:
                # НЕ ОТВЕЧАЕМ - просто игнорируем
                return
        
        @non_admin_router.callback_query()
        async def handle_non_admin_callbacks(callback: CallbackQuery):
            """Обработчик для всех callback'ов от не-админов"""
            if callback.from_user and callback.from_user.id not in config.ADMIN_IDS:
                # НЕ ОТВЕЧАЕМ - просто игнорируем
                return
        
        dp.include_router(non_admin_router)
        
        # Инициализация планировщика напоминаний
        from services.reminder_service import reminder_service
        reminder_service.set_bot(bot)
        await reminder_service.start_scheduler()
        
        # Инициализация планировщика постов
        from services.post_scheduler import post_scheduler
        post_scheduler.set_bot(bot)
        await post_scheduler.start_scheduler()
        
        # Инициализация PostPublisher
        from services.publisher import init_publisher
        init_publisher(bot)
        
        logger.info("Bot startup completed")
        
    except Exception as e:
        logger.error("Startup failed: %s", e)
        raise

async def on_shutdown():
    """Очистка при завершении"""
    try:
        # Остановка планировщика напоминаний
        from services.reminder_service import reminder_service
        await reminder_service.stop_scheduler()
        
        # Остановка планировщика постов
        from services.post_scheduler import post_scheduler
        await post_scheduler.stop_scheduler()
        
        await db.close()
        logger.info("Database connection closed")
        logger.info("Bot shutdown completed")
    except Exception as e:
        logger.error("Shutdown error: %s", e)

async def main():
    """Главная функция"""
    shutdown_event = asyncio.Event()
    
    try:
        # Обработчики сигналов для graceful shutdown
        def signal_handler(signum, _frame):
            logger.info("Received signal %s, initiating graceful shutdown...", signum)
            shutdown_event.set()
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Инициализация
        await on_startup()
        
        # Запуск бота
        logger.info("Starting bot...")
        
        # Создаем задачу для polling
        polling_task = asyncio.create_task(dp.start_polling(bot))
        
        # Ждем сигнала завершения или ошибки
        try:
            await asyncio.wait_for(shutdown_event.wait(), timeout=None)
            logger.info("Shutdown signal received, stopping bot...")
        except asyncio.TimeoutError:
            logger.info("Bot running normally...")
        except Exception as e:
            logger.error("Error during polling: %s", e)
            raise
        finally:
            # Останавливаем polling
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                logger.info("Bot polling stopped")
        
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
