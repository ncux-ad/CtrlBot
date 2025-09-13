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

# Фильтры
admin_filter = IsConfigAdminFilter()

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

@dp.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🤖 <b>CtrlBot - Помощь</b>

<b>Основные команды:</b>
/start - Запуск бота
/ping - Проверка работоспособности
/myid - Показать ваш ID и статус
/reset - Сброс состояния FSM
/help - Эта справка

<b>Для администраторов:</b>
/admin - Админ панель
/config - Настройки
/new_post - Создать пост (в разработке)
/my_posts - Мои посты (в разработке)
/ai - AI помощник (в разработке)
/reminders - Напоминания (в разработке)
/digest - Дайджесты (в разработке)
/export - Экспорт данных (в разработке)

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

@dp.message(Command("reset"))
async def cmd_reset(message: Message):
    """Обработчик команды /reset"""
    await message.answer(
        "🔄 <b>Сброс состояния</b>\n\n"
        "Все состояния FSM сброшены.\n"
        "Можете начать заново!"
    )

@dp.message(Command("new_post"), admin_filter)
async def cmd_new_post(message: Message):
    """Обработчик команды /new_post (только для админов)"""
    await message.answer(
        "📝 <b>Создание нового поста</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет полноценный редактор постов с FSM.\n\n"
        "Планируемые функции:\n"
        "• Ввод текста поста\n"
        "• Предпросмотр с Markdown\n"
        "• Выбор тегов\n"
        "• Выбор серии\n"
        "• Планирование публикации\n"
        "• Подтверждение и отправка"
    )

@dp.message(Command("my_posts"), admin_filter)
async def cmd_my_posts(message: Message):
    """Обработчик команды /my_posts (только для админов)"""
    await message.answer(
        "📋 <b>Мои посты</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет список ваших постов.\n\n"
        "Планируемые функции:\n"
        "• Просмотр всех постов\n"
        "• Фильтрация по статусу\n"
        "• Редактирование постов\n"
        "• Удаление постов\n"
        "• Статистика публикаций"
    )

@dp.message(Command("reminders"), admin_filter)
async def cmd_reminders(message: Message):
    """Обработчик команды /reminders (только для админов)"""
    await message.answer(
        "⏰ <b>Управление напоминаниями</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет управление напоминаниями.\n\n"
        "Планируемые функции:\n"
        "• Настройка времени напоминаний (12:00, 21:00)\n"
        "• Включение/отключение уведомлений\n"
        "• Просмотр истории напоминаний\n"
        "• Настройка текста напоминаний"
    )

@dp.message(Command("digest"), admin_filter)
async def cmd_digest(message: Message):
    """Обработчик команды /digest (только для админов)"""
    await message.answer(
        "📊 <b>Управление дайджестами</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет управление дайджестами.\n\n"
        "Планируемые функции:\n"
        "• Создание недельных дайджестов\n"
        "• Создание месячных дайджестов\n"
        "• Настройка автоматической отправки\n"
        "• Экспорт в Excel"
    )

@dp.message(Command("ai"), admin_filter)
async def cmd_ai(message: Message):
    """Обработчик команды /ai (только для админов)"""
    await message.answer(
        "🤖 <b>AI помощник CtrlBot</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет AI помощник с YandexGPT.\n\n"
        "Планируемые функции:\n"
        "• Подсказки тегов на основе текста\n"
        "• Сокращение длинных текстов\n"
        "• Изменение стиля текста\n"
        "• Улучшение грамматики и стиля\n"
        "• Создание аннотаций"
    )

@dp.message(Command("export"), admin_filter)
async def cmd_export(message: Message):
    """Обработчик команды /export (только для админов)"""
    await message.answer(
        "📈 <b>Экспорт данных</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет экспорт данных.\n\n"
        "Планируемые форматы:\n"
        "• Markdown (.md)\n"
        "• CSV (.csv)\n"
        "• JSON (.json)"
    )

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
