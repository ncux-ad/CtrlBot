"""
@file: handlers/admin.py
@description: Админские команды и управление
@dependencies: services/tags.py, utils/keyboards.py, utils/filters.py
@created: 2025-09-13
"""

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from utils.filters import IsConfigAdminFilter
from utils.logging import get_logger
from config import config

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()

async def safe_callback_answer(callback: CallbackQuery, text: str = None):
    """Безопасный ответ на callback с обработкой ошибок"""
    try:
        await callback.answer(text=text)
    except TelegramBadRequest as e:
        if "query is too old" in str(e) or "response timeout expired" in str(e):
            logger.warning("Callback query expired, ignoring: %s", e)
        else:
            logger.warning("Failed to answer callback: %s", e)
    except Exception as e:
        logger.warning("Unexpected error answering callback: %s", e)

@router.message(Command("start"), admin_filter)
async def cmd_start(message: Message):
    """Обработчик команды /start - только для админов"""
    logger.info("Start command received from user %s", message.from_user.id)
    logger.info("Admin access granted for user %s", message.from_user.id)
    
    await message.answer(
        "👑 *Админ панель CtrlBot*\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="view_posts")],
            [InlineKeyboardButton(text="📢 Проверить отложенные", callback_data="check_scheduled_posts")],
            [InlineKeyboardButton(text="🔧 Исправить статусы", callback_data="fix_post_status")],
            [InlineKeyboardButton(text="🤖 AI помощник", callback_data="ai_functions")],
            [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
            [InlineKeyboardButton(text="📚 Управление сериями", callback_data="manage_series")],
            [InlineKeyboardButton(text="⏰ Напоминания", callback_data="manage_reminders")],
            [InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
            [InlineKeyboardButton(text="⚙️ Настройки канала", callback_data="channel_settings")],
            [InlineKeyboardButton(text="🔗 Получить ID канала", callback_data="get_channel_id")]
        ])
    )

@router.message(Command("admin"), admin_filter)
async def cmd_admin(message: Message):
    """Главная админ панель"""
    await message.answer(
        "👑 *Админ панель CtrlBot*\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
        ])
    )

@router.message(Command("ping"))
async def cmd_ping(message: Message):
    """Обработчик команды /ping"""
    await message.answer("🏓 Pong! Бот работает.")

# Обработчики кнопок клавиатуры (оставляем только для совместимости)
@router.message(F.text == "📝 Новый пост", admin_filter)
async def btn_new_post(message: Message, state: FSMContext):
    """Обработчик кнопки 'Новый пост' - перенаправляем на inline меню"""
    await message.answer(
        "📝 **Создание нового поста**\n\n"
        "Отправьте текст поста в формате Markdown.\n"
        "Можно использовать *жирный*, _курсив_, `код` и другие\n"
        "элементы.\n\n"
        "👇👇👇\n"
        "**В поле ввода наберите пост**\n"
        "(желательно Ctrl+C и Ctrl+V для сохранения форматирования!)"
    )

@router.message(F.text == "🤖 AI помощник")
async def btn_ai_helper(message: Message):
    """Обработчик кнопки 'AI помощник' - перенаправляем на inline меню"""
    await message.answer(
        "🤖 *AI помощник*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 AI функции", callback_data="ai_functions")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(F.text == "🏷️ Теги")
async def btn_tags(message: Message):
    """Обработчик кнопки 'Теги' - перенаправляем на inline меню"""
    await message.answer(
        "🏷️ *Управление тегами*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(F.text == "⚙️ Настройки")
async def btn_settings(message: Message):
    """Обработчик кнопки 'Настройки' - перенаправляем на inline меню"""
    await message.answer(
        "⚙️ *Настройки*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Настройки канала", callback_data="channel_settings")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(F.text == "📋 Мои посты")
async def btn_my_posts(message: Message):
    """Обработчик кнопки 'Мои посты' - перенаправляем на inline меню"""
    await message.answer(
        "📋 *Мои посты*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Просмотр постов", callback_data="view_posts")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(F.text == "⏰ Напоминания")
async def btn_reminders(message: Message):
    """Обработчик кнопки 'Напоминания' - перенаправляем на inline меню"""
    await message.answer(
        "⏰ *Напоминания*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏰ Управление напоминаниями", callback_data="manage_reminders")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(F.text == "📊 Серии")
async def btn_series(message: Message):
    """Обработчик кнопки 'Серии' - перенаправляем на inline меню"""
    await message.answer(
        "📊 *Серии*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Управление сериями", callback_data="manage_series")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(F.text == "📈 Статистика")
async def btn_statistics(message: Message):
    """Обработчик кнопки 'Статистика' - перенаправляем на inline меню"""
    await message.answer(
        "📈 *Статистика*\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(Command("config"), admin_filter)
async def cmd_config(message: Message):
    """Показ конфигурации"""
    config_info = f"""
⚙️ *Конфигурация CtrlBot*

*Основные настройки:*
• Логирование: {config.LOG_LEVEL}
• Макс. длина поста: {config.MAX_POST_LENGTH}
• Мин. тегов: {config.MIN_TAGS_REQUIRED}
• Часовой пояс: {config.TIMEZONE}

*База данных:*
• Хост: {config.DB_HOST}:{config.DB_PORT}
• База: {config.DB_NAME}
• Пользователь: {config.DB_USER}

*AI интеграция:*
• YandexGPT: {'✅ Настроено' if config.YANDEX_API_KEY else '❌ Не настроено'}
• Папка: {config.YANDEX_FOLDER_ID or 'Не указана'}

*Каналы:*
• Настроено каналов: {len(config.CHANNEL_IDS) if hasattr(config, 'CHANNEL_IDS') else 0}
• ID каналов: {config.CHANNEL_IDS if hasattr(config, 'CHANNEL_IDS') else 'Не настроено'}

*Администраторы:*
• Количество: {len(config.ADMIN_IDS)}
• Ваш ID: {message.from_user.id if message.from_user else 'Неизвестно'}
    """
    
    await message.answer(config_info)

@router.message(F.forward_from_chat, admin_filter)
async def handle_forwarded_message(message: Message):
    """Обработка пересланных сообщений для получения ID канала"""
    if message.forward_from_chat and message.forward_from_chat.type in ['channel', 'supergroup']:
        channel_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title or "Неизвестный канал"
        
        try:
            # Проверяем права бота в канале
            bot_member = await message.bot.get_chat_member(channel_id, message.bot.id)
            
            if bot_member.status in ['administrator', 'creator']:
                # Проверяем права на отправку сообщений
                can_post = bot_member.can_post_messages if hasattr(bot_member, 'can_post_messages') else True
                
                if can_post:
                    # Сохраняем ID канала в конфигурацию
                    if not hasattr(config, 'CHANNEL_IDS'):
                        config.CHANNEL_IDS = []
                    
                    if channel_id not in config.CHANNEL_IDS:
                        config.CHANNEL_IDS.append(channel_id)
                        
                        # Сохраняем в .env файл
                        await save_channel_id_to_env(channel_id)
                        
                        await message.answer(
                            f"✅ *Канал успешно настроен!*\n\n"
                            f"📢 *Канал:* {channel_title}\n"
                            f"🆔 *ID:* `{channel_id}`\n"
                            f"🤖 *Права бота:* ✅ Администратор\n"
                            f"📝 *Публикация:* ✅ Разрешена\n\n"
                            f"Теперь бот может публиковать посты в этот канал!",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                            ])
                        )
                    else:
                        await message.answer(
                            f"ℹ️ *Канал уже настроен*\n\n"
                            f"📢 *Канал:* {channel_title}\n"
                            f"🆔 *ID:* `{channel_id}`\n\n"
                            f"Канал уже добавлен в список для публикации.",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                            ])
                        )
                else:
                    await message.answer(
                        f"❌ *Недостаточно прав*\n\n"
                        f"📢 *Канал:* {channel_title}\n"
                        f"🆔 *ID:* `{channel_id}`\n\n"
                        f"Бот добавлен как администратор, но не может публиковать сообщения.\n"
                        f"Проверьте права бота в настройках канала.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                        ])
                    )
            else:
                await message.answer(
                    f"❌ *Бот не является администратором*\n\n"
                    f"📢 *Канал:* {channel_title}\n"
                    f"🆔 *ID:* `{channel_id}`\n\n"
                    f"Добавьте бота в канал как администратора с правами на публикацию.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                    ])
                )
                
        except Exception as e:
            logger.error("Error checking channel permissions: %s", e)
            await message.answer(
                f"❌ *Ошибка проверки канала*\n\n"
                f"Не удалось проверить права бота в канале.\n"
                f"Убедитесь, что бот добавлен как администратор.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )

async def save_channel_id_to_env(channel_id: int):
    """Сохранение ID канала в .env файл"""
    try:
        env_file = ".env"
        
        # Читаем существующий .env файл
        env_content = ""
        if os.path.exists(env_file):
            with open(env_file, 'r', encoding='utf-8') as f:
                env_content = f.read()
        
        # Обновляем или добавляем CHANNEL_IDS
        if "CHANNEL_IDS=" in env_content:
            # Заменяем существующую строку
            import re
            pattern = r"CHANNEL_IDS=.*"
            replacement = f"CHANNEL_IDS={channel_id}"
            env_content = re.sub(pattern, replacement, env_content)
        else:
            # Добавляем новую строку
            env_content += f"\nCHANNEL_IDS={channel_id}\n"
        
        # Записываем обновленный .env файл
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
            
        logger.info("Channel ID %s saved to .env file", channel_id)
        
    except Exception as e:
        logger.error("Failed to save channel ID to .env: %s", e)

@router.callback_query(F.data == "channel_settings", admin_filter)
async def callback_channel_settings(callback: CallbackQuery):
    """Настройки канала"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "📢 *Настройки канала*\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будут настройки канала.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in channel_settings: %s", e)
    await callback.answer()

@router.callback_query(F.data == "manage_tags", admin_filter)
async def callback_manage_tags(callback: CallbackQuery):
    """Управление тегами"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "🏷️ *Управление тегами*\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет управление тегами.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in manage_tags: %s", e)
    await callback.answer()

@router.callback_query(F.data == "manage_series", admin_filter)
async def callback_manage_series(callback: CallbackQuery):
    """Управление сериями"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "📚 *Управление сериями*\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет управление сериями.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in manage_series: %s", e)
    await callback.answer()

@router.callback_query(F.data == "manage_reminders", admin_filter)
async def callback_manage_reminders(callback: CallbackQuery):
    """Управление напоминаниями"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "⏰ *Управление напоминаниями*\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет управление напоминаниями.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in manage_reminders: %s", e)
    await callback.answer()

@router.callback_query(F.data == "export_data", admin_filter)
async def callback_export_data(callback: CallbackQuery):
    """Экспорт данных"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "📊 *Экспорт данных*\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет экспорт данных.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in export_data: %s", e)
    await callback.answer()


@router.callback_query(F.data == "back_to_admin", admin_filter)
async def callback_back_to_admin(callback: CallbackQuery):
    """Возврат в админ-панель"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "👑 *Админ панель CtrlBot*\n\n"
                "Выберите действие:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="📋 Мои посты", callback_data="view_posts")],
                    [InlineKeyboardButton(text="📢 Проверить отложенные", callback_data="check_scheduled_posts")],
                    [InlineKeyboardButton(text="🔧 Исправить статусы", callback_data="fix_post_status")],
                    [InlineKeyboardButton(text="🤖 AI помощник", callback_data="ai_functions")],
                    [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
                    [InlineKeyboardButton(text="📚 Управление сериями", callback_data="manage_series")],
                    [InlineKeyboardButton(text="⏰ Напоминания", callback_data="manage_reminders")],
                    [InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
                    [InlineKeyboardButton(text="⚙️ Настройки канала", callback_data="channel_settings")],
                    [InlineKeyboardButton(text="🔗 Получить ID канала", callback_data="get_channel_id")]
                ])
            )
    except Exception as e:
        # Если сообщение не изменилось, просто отвечаем на callback
        logger.warning("Failed to edit message in back_to_admin: %s", e)
        await safe_callback_answer(callback)

# Новые callback обработчики для inline навигации
@router.callback_query(F.data == "create_post", admin_filter)
async def callback_create_post(callback: CallbackQuery, state: FSMContext):
    """Создание нового поста"""
    from utils.states import PostCreationStates
    from utils.keyboards import get_post_actions_keyboard
    
    # Проверяем, есть ли привязанные каналы
    from database import db
    channels = await db.fetch_all("SELECT id, tg_channel_id, title FROM channels")
    
    if not channels:
        # Нет каналов - показываем инструкцию
        await callback.message.edit_text(
            "🔗 *Сначала привяжите канал!*\n\n"
            "Для создания постов нужно привязать канал:\n\n"
            "1️⃣ *Добавьте бота в канал как администратора*\n"
            "   • Права: отправка сообщений\n"
            "   • Редактирование сообщений\n\n"
            "2️⃣ *Перешлите любое сообщение из канала боту*\n"
            "   • Я автоматически определю ID канала\n"
            "   • Сохраню настройки\n\n"
            "3️⃣ *Готово!* Можете создавать посты\n\n"
            "💡 _Перешлите сообщение из канала прямо сейчас_",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔄 Проверить снова", callback_data="create_post")],
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
        await callback.answer()
        return
    
    # Есть каналы - переходим к созданию поста
    await state.set_state(PostCreationStates.enter_text)
    try:
        if callback.message:
            await callback.message.edit_text(
                "📝 **Создание нового поста**\n\n"
                "Отправьте текст поста в формате Markdown.\n"
                "Можно использовать *жирный*, _курсив_, `код` и другие\n"
                "элементы.\n\n"
                "👇👇👇\n"
                "**В поле ввода наберите пост**\n"
                "(желательно Ctrl+C и Ctrl+V для сохранения форматирования!)"
            )
    except Exception as e:
        logger.warning("Failed to edit message in create_post: %s", e)
    await callback.answer()

@router.callback_query(F.data == "ai_functions", admin_filter)
async def callback_ai_functions(callback: CallbackQuery):
    """AI функции"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "🤖 *AI помощник CtrlBot*\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет AI помощник с YandexGPT.\n\n"
                "Планируемые функции:\n"
                "• Подсказки тегов на основе текста\n"
                "• Сокращение длинных текстов\n"
                "• Изменение стиля текста\n"
                "• Улучшение грамматики и стиля\n"
                "• Создание аннотаций",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in ai_functions: %s", e)
    await callback.answer()

@router.callback_query(F.data == "view_posts", admin_filter)
async def callback_view_posts(callback: CallbackQuery):
    """Просмотр постов пользователя"""
    try:
        from services.post_service import post_service
        from utils.timezone_utils import format_datetime
        
        logger.info(f"📋 Просмотр постов пользователя {callback.from_user.id}")
        
        # Проверяем, есть ли привязанные каналы
        from database import db
        channels = await db.fetch_all("SELECT id, tg_channel_id, title FROM channels")
        
        if not channels:
            await callback.message.edit_text(
                "🔗 *Сначала привяжите канал!*\n\n"
                "Для просмотра постов нужно привязать канал:\n\n"
                "1️⃣ *Добавьте бота в канал как администратора*\n"
                "   • Права: отправка сообщений\n"
                "   • Редактирование сообщений\n\n"
                "2️⃣ *Перешлите любое сообщение из канала боту*\n"
                "   • Я автоматически определю ID канала\n"
                "   • Сохраню настройки\n\n"
                "3️⃣ *Готово!* Можете создавать и просматривать посты\n\n"
                "💡 _Перешлите сообщение из канала прямо сейчас_",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Проверить снова", callback_data="view_posts")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
            await callback.answer()
            return
        
        # Получаем посты пользователя
        posts = await post_service.get_user_posts(callback.from_user.id, limit=10)
        
        if not posts:
            await callback.message.edit_text(
                "📋 *Мои посты*\n\n"
                "У вас пока нет постов.\n"
                "Создайте первый пост командой /new_post",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
            await callback.answer()
            return
        
        # Формируем список постов
        text = "📋 *Мои посты*\n\n"
        
        for i, post in enumerate(posts, 1):
            status_emoji = {
                'draft': '📝',
                'scheduled': '⏰',
                'published': '✅',
                'deleted': '❌'
            }.get(post['status'], '❓')
            
            text += f"{i}. {status_emoji} *#{post['id']}*\n"
            text += f"   📝 {post['body_md'][:50]}{'...' if len(post['body_md']) > 50 else ''}\n"
            
            if post['series_title']:
                text += f"   📚 {post['series_title']}\n"
            
            if post['tags_cache']:
                tags = ', '.join(post['tags_cache'][:3])
                text += f"   🏷️ {tags}\n"
            
            if post['scheduled_at']:
                text += f"   ⏰ {format_datetime(post['scheduled_at'])}\n"
            
            text += f"   📅 {format_datetime(post['created_at'])}\n\n"
        
        # Добавляем кнопки
        keyboard = []
        if len(posts) >= 10:
            keyboard.append([InlineKeyboardButton(text="📄 Показать еще", callback_data="load_more_posts")])
        keyboard.append([InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")])
        keyboard.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_view_posts: {e}")
        await callback.message.edit_text(
            f"❌ *Ошибка загрузки постов*\n\n{str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data == "get_channel_id", admin_filter)
async def callback_get_channel_id(callback: CallbackQuery):
    """Получение ID канала"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "🔗 *Получение ID канала*\n\n"
                "Для настройки публикации постов:\n\n"
                "1️⃣ *Добавьте бота в канал как администратора*\n"
                "   • Права: отправка сообщений\n"
                "   • Редактирование сообщений\n\n"
                "2️⃣ *Перешлите любое сообщение из канала боту*\n"
                "   • Я автоматически определю ID канала\n"
                "   • Сохраню настройки\n\n"
                "3️⃣ *Готово!* Бот сможет публиковать посты\n\n"
                "💡 _Перешлите сообщение из канала прямо сейчас_",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in get_channel_id: %s", e)
    await callback.answer()

@router.message(F.forward_from_chat.type == "channel")
async def handle_channel_forward(message: Message):
    """Обработка пересылки сообщений из каналов"""
    try:
        channel_id = message.forward_from_chat.id
        channel_title = message.forward_from_chat.title or "Без названия"
        
        logger.info(f"📢 Получено сообщение из канала: {channel_id} ({channel_title})")
        
        # Проверяем, есть ли канал в БД
        from database import db
        existing_channel = await db.fetch_one("""
            SELECT id, tg_channel_id, title 
            FROM channels 
            WHERE tg_channel_id = $1
        """, channel_id)
        
        if existing_channel:
            await message.answer(
                f"✅ *Канал уже настроен!*\n\n"
                f"📢 *Канал:* {channel_title}\n"
                f"🆔 *ID:* `{channel_id}`\n\n"
                f"Бот уже может публиковать посты в этот канал.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
        else:
            # Добавляем канал в БД
            await db.execute("""
                INSERT INTO channels (tg_channel_id, title, created_at)
                VALUES ($1, $2, NOW())
            """, channel_id, channel_title)
            
            logger.info(f"✅ Канал {channel_id} ({channel_title}) добавлен в БД")
            
            await message.answer(
                f"🎉 *Канал успешно добавлен!*\n\n"
                f"📢 *Канал:* {channel_title}\n"
                f"🆔 *ID:* `{channel_id}`\n\n"
                f"Теперь бот может публиковать посты в этот канал!\n\n"
                f"💡 _Хотите создать первый пост?_",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
            
    except Exception as e:
        logger.error(f"Error handling channel forward: {e}")
        await message.answer(
            f"❌ *Ошибка добавления канала*\n\n{str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )

@router.callback_query(F.data == "check_scheduled_posts", admin_filter)
async def check_scheduled_posts(callback: CallbackQuery):
    """Проверка и публикация отложенных постов"""
    try:
        from services.post_scheduler import post_scheduler
        from services.post_service import post_service
        
        logger.info("🔍 Ручная проверка отложенных постов")
        
        # Получаем статус планировщика
        status = await post_scheduler.get_scheduler_status()
        
        if not status.get('bot_available'):
            await callback.message.edit_text(
                "❌ *Планировщик недоступен*\n\n"
                "Бот не инициализирован для публикации постов.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
            await callback.answer()
            return
        
        # Получаем отложенные посты
        scheduled_posts = await post_service.get_scheduled_posts()
        
        if not scheduled_posts:
            await callback.message.edit_text(
                "📭 *Нет отложенных постов*\n\n"
                "Все посты опубликованы или нет запланированных публикаций.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
        else:
            # Публикуем посты
            published_count = await post_service.publish_scheduled_posts(callback.bot)
            
            result_text = f"📢 *Проверка отложенных постов*\n\n"
            result_text += f"📋 *Найдено:* {len(scheduled_posts)} постов\n"
            result_text += f"✅ *Опубликовано:* {published_count} постов\n\n"
            
            if published_count < len(scheduled_posts):
                result_text += f"❌ *Ошибок:* {len(scheduled_posts) - published_count} постов\n"
            
            await callback.message.edit_text(
                result_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔄 Проверить снова", callback_data="check_scheduled_posts")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in check_scheduled_posts: {e}")
        await callback.message.edit_text(
            f"❌ *Ошибка проверки постов*\n\n{str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
        await callback.answer()


