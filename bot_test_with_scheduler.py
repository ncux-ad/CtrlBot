#!/usr/bin/env python3
"""
Тестовая версия CtrlBot с планировщиком напоминаний (без БД)
Для проверки функциональности напоминаний
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

# Фильтры
admin_filter = IsConfigAdminFilter()

# Простые обработчики для тестирования
@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "🚀 <b>CtrlBot запущен!</b>\n\n"
        "Это тестовая версия с планировщиком напоминаний.\n"
        "Основные функции будут доступны после настройки PostgreSQL.\n\n"
        "Используйте /reminders для управления напоминаниями."
    )

@dp.message(Command("ping"))
async def cmd_ping(message: Message):
    """Обработчик команды /ping"""
    await message.answer("🏓 Pong! Бот работает.")

@dp.message(Command("admin"), admin_filter)
async def cmd_admin(message: Message):
    """Обработчик команды /admin (только для админов)"""
    await message.answer(
        f"👑 <b>Админ панель</b>\n\n"
        f"ID: {message.from_user.id}\n"
        f"Имя: {message.from_user.first_name}\n"
        f"Админов в системе: {len(config.ADMIN_IDS)}\n\n"
        f"Используйте /reminders для управления напоминаниями."
    )

@dp.message(Command("config"), admin_filter)
async def cmd_config(message: Message):
    """Обработчик команды /config (только для админов)"""
    await message.answer(
        f"⚙️ <b>Конфигурация</b>\n\n"
        f"Логирование: {config.LOG_LEVEL}\n"
        f"Макс. длина поста: {config.MAX_POST_LENGTH}\n"
        f"Мин. тегов: {config.MIN_TAGS_REQUIRED}\n"
        f"Часовой пояс: {config.TIMEZONE}\n"
        f"AI настроен: {'Да' if config.YANDEX_API_KEY else 'Нет'}\n\n"
        f"Планировщик: Включен (тестовый режим)"
    )

@dp.message(Command("reminders"), admin_filter)
async def cmd_reminders(message: Message):
    """Обработчик команды /reminders (только для админов)"""
    try:
        from services.reminders import reminder_service
        status = await reminder_service.get_scheduler_status()
        
        status_text = "🟢 Работает" if status["running"] else "🔴 Остановлен"
        jobs_text = f"Задач в очереди: {status['jobs_count']}"
        
        await message.answer(
            f"⏰ <b>Управление напоминаниями</b>\n\n"
            f"<b>Статус планировщика:</b> {status_text}\n"
            f"<b>{jobs_text}</b>\n\n"
            f"<b>Стандартные напоминания:</b>\n"
            f"• 12:00 - Ежедневное напоминание\n"
            f"• 21:00 - Ежедневное напоминание\n\n"
            f"Эти напоминания отправляются всем администраторам.\n\n"
            f"<b>В тестовом режиме БД недоступна,</b>\n"
            f"поэтому пользовательские напоминания не сохраняются."
        )
        
    except Exception as e:
        logger.error("Failed to show reminders: %s", e)
        await message.answer(
            "❌ <b>Ошибка загрузки напоминаний</b>\n\n"
            "Попробуйте позже или обратитесь к администратору."
        )

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>CtrlBot - Помощь</b>

<b>Основные команды:</b>
/start - Запуск бота
/ping - Проверка работоспособности
/help - Эта справка

<b>Для администраторов:</b>
/admin - Админ панель
/config - Настройки
/reminders - Управление напоминаниями

<b>Поддержка:</b>
Если у вас есть вопросы, обратитесь к администратору.
    """
    await message.answer(help_text)

@dp.message(Command("myid"))
async def cmd_myid(message: Message):
    """Обработчик команды /myid"""
    await message.answer(
        f"🆔 <b>Ваш ID:</b> {message.from_user.id}\n"
        f"👤 <b>Имя:</b> {message.from_user.first_name}\n"
        f"👑 <b>Админ:</b> {'Да' if message.from_user.id in config.ADMIN_IDS else 'Нет'}"
    )

@dp.message()
async def handle_text(message: Message):
    """Обработчик текстовых сообщений"""
    if message.text:
        await message.answer(
            f"📝 <b>Получено сообщение:</b>\n\n"
            f"Длина: {len(message.text)} символов\n"
            f"От: {message.from_user.first_name}\n"
            f"ID: {message.from_user.id}\n\n"
            f"Используйте /help для просмотра команд."
        )

async def on_startup():
    """Инициализация при запуске"""
    try:
        # Валидация конфигурации
        config.validate()
        logger.info("Configuration validated")
        
        # Инициализация планировщика напоминаний
        from services.reminders import reminder_service
        reminder_service.set_bot(bot)
        await reminder_service.start_scheduler()
        
        logger.info("Test bot with scheduler startup completed")
        
    except Exception as e:
        logger.error("Startup failed: %s", e)
        raise

async def on_shutdown():
    """Очистка при завершении"""
    try:
        # Остановка планировщика напоминаний
        from services.reminders import reminder_service
        await reminder_service.stop_scheduler()
        
        logger.info("Test bot shutdown completed")
        
    except Exception as e:
        logger.error("Shutdown failed: %s", e)

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
        logger.info("Starting test bot with scheduler...")
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
