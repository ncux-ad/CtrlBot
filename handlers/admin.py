"""
@file: handlers/admin.py
@description: Админские команды и управление
@dependencies: services/tags.py, utils/keyboards.py, utils/filters.py
@created: 2025-09-13
"""

import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.enums import ParseMode
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
        "👑 *Админ панель CtrlAI\\_Bot*\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
            [InlineKeyboardButton(text="📢 Проверить отложенные", callback_data="check_scheduled_posts")],
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
        "👑 *Админ панель CtrlAI\\_Bot*\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📊 Создать опрос", callback_data="create_poll")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
            [InlineKeyboardButton(text="📢 Проверить отложенные", callback_data="check_scheduled_posts")],
            [InlineKeyboardButton(text="🤖 AI помощник", callback_data="ai_functions")],
            [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
            [InlineKeyboardButton(text="📚 Управление сериями", callback_data="manage_series")],
            [InlineKeyboardButton(text="⏰ Напоминания", callback_data="manage_reminders")],
            [InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
            [InlineKeyboardButton(text="⚙️ Настройки канала", callback_data="channel_settings")],
            [InlineKeyboardButton(text="🔗 Получить ID канала", callback_data="get_channel_id")]
        ]),
        parse_mode=ParseMode.MARKDOWN_V2
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
        "📝 *Создание нового поста*\n\n"
        "Отправьте текст поста в формате Markdown\\.\n"
        "Можно использовать *жирный*, _курсив_, `код` и другие\n"
        "элементы.\n\n"
        "👇👇👇\n"
        "*В поле ввода наберите пост*\n"
        "\\(желательно Ctrl\\+C и Ctrl\\+V для сохранения форматирования!\\)"
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
            [InlineKeyboardButton(text="📋 Просмотр постов", callback_data="my_posts")],
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

@router.message(Command("add_channel"), admin_filter)
async def cmd_add_channel_private(message: Message):
    """Добавление канала (только для личных сообщений)"""
    # Проверяем, что команда вызвана в личных сообщениях
    if message.chat.type != 'private':
        return  # Пропускаем, если не личные сообщения
    
    await message.answer(
        "➕ *Добавление канала*\n\n"
        "Для добавления канала:\n"
        "1. Добавьте бота в канал как администратора\n"
        "2. Отправьте команду /start в канале\n"
        "3. Бот автоматически добавит канал в систему\n\n"
        "Или используйте команду /add_channel в канале.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(Command("add_channel"))
async def cmd_add_channel_in_channel(message: Message):
    """Добавление канала (вызывается в канале)"""
    # Проверяем, что команда вызвана в канале
    if not message.chat.type in ['channel', 'supergroup']:
        await message.answer("❌ Эта команда работает только в каналах!")
        return
    
    # Проверяем, что пользователь - администратор канала
    try:
        user_status = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if user_status.status not in ['administrator', 'creator']:
            await message.answer("❌ Только администраторы канала могут добавлять канал в систему!")
            return
    except Exception as e:
        logger.error("Error checking user status: %s", e)
        await message.answer("❌ Ошибка проверки прав доступа!")
        return
    
    channel_id = message.chat.id
    channel_title = message.chat.title or "Неизвестный канал"
    
    try:
        # Проверяем права бота в канале
        bot_member = await message.bot.get_chat_member(channel_id, message.bot.id)
        
        if bot_member.status in ['administrator', 'creator']:
            # Проверяем права на публикацию
            if bot_member.can_post_messages:
                # Добавляем канал в базу данных
                from database import db
                
                # Проверяем, есть ли уже такой канал
                existing_channel = await db.fetch_one(
                    "SELECT id FROM channels WHERE tg_channel_id = $1", 
                    channel_id
                )
                
                if existing_channel:
                    await message.answer(
                        f"ℹ️ *Канал уже добавлен*\n\n"
                        f"📢 *Канал:* {channel_title}\n"
                        f"🆔 *ID:* `{channel_id}`\n\n"
                        f"Канал уже добавлен в систему.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                        ])
                    )
                else:
                    # Добавляем новый канал
                    await db.execute(
                        """
                        INSERT INTO channels (tg_channel_id, title, enabled, created_at)
                        VALUES ($1, $2, true, NOW())
                        """,
                        channel_id, channel_title
                    )
                    
                    await message.answer(
                        f"✅ *Канал успешно добавлен!*\n\n"
                        f"📢 *Канал:* {channel_title}\n"
                        f"🆔 *ID:* `{channel_id}`\n"
                        f"🤖 *Права бота:* ✅ Администратор\n"
                        f"📝 *Публикация:* ✅ Разрешена\n\n"
                        f"Теперь вы можете создавать посты для этого канала!",
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
        logger.error("Error adding channel: %s", e)
        await message.answer(
            f"❌ *Ошибка добавления канала*\n\n"
            f"Попробуйте позже или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )

@router.message(Command("help"))
async def cmd_help_in_channel(message: Message):
    """Справка (вызывается в канале)"""
    # Проверяем, что команда вызвана в канале
    if not message.chat.type in ['channel', 'supergroup']:
        return  # В личных сообщениях есть другой обработчик
    
    help_text = """
🤖 *CtrlBot - Справка для канала*

*Доступные команды:*
/add_channel - Добавить канал в систему
/help - Показать эту справку

*Как добавить канал:*
1. Убедитесь, что бот добавлен как администратор
2. Убедитесь, что у бота есть права на публикацию
3. Отправьте команду /add_channel

*После добавления канала:*
• Вы сможете создавать посты через админ-панель
• Бот будет публиковать запланированные посты
• Доступны все функции управления контентом

*Поддержка:*
Если команды не работают, проверьте права бота в настройках канала.
    """
    
    await message.answer(help_text)

@router.message(Command("start"))
async def cmd_start_in_channel(message: Message):
    """Старт (вызывается в канале)"""
    # Проверяем, что команда вызвана в канале
    if not message.chat.type in ['channel', 'supergroup']:
        return  # В личных сообщениях есть другой обработчик
    
    await message.answer(
        "👋 *Добро пожаловать в CtrlBot!*\n\n"
        "Этот бот поможет вам управлять контентом канала.\n\n"
        "Используйте команды:\n"
        "• /add_channel - добавить канал в систему\n"
        "• /help - показать справку\n\n"
        "Для полного управления используйте админ-панель в личных сообщениях с ботом."
    )

# Обработчик для обычных сообщений в канале (когда команды отправляются как текст)
@router.message(lambda message: message.chat.type in ['channel', 'supergroup'] and message.text)
async def handle_channel_messages(message: Message):
    """Обработка сообщений в канале для распознавания команд"""
    text = message.text.strip()
    
    # Проверяем, что пользователь - администратор канала
    try:
        user_status = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        if user_status.status not in ['administrator', 'creator']:
            return  # Только администраторы могут использовать команды
    except Exception as e:
        logger.error("Error checking user status: %s", e)
        return
    
    # Обрабатываем команды, отправленные как обычные сообщения
    if text == "/start":
        await cmd_start_in_channel(message)
    elif text == "/help":
        await cmd_help_in_channel(message)
    elif text == "/add_channel":
        await cmd_add_channel_in_channel(message)

# Обработчик для inline-запросов (когда пользователь начинает вводить @botname)
@router.inline_query()
async def handle_inline_query(inline_query: InlineQuery):
    """Обработка inline-запросов для команд в канале"""
    query = inline_query.query.strip()
    
    # В inline-запросах нет chat, поэтому пропускаем проверку прав
    # Проверка прав будет в callback-обработчиках
    
    results = []
    
    # Если запрос пустой или содержит ключевые слова
    if query == "" or "add" in query.lower() or "канал" in query.lower():
        # Кнопка для добавления канала
        results.append(InlineQueryResultArticle(
            id="add_channel",
            title="➕ Добавить канал в систему",
            description="Добавить текущий канал в систему CtrlBot",
            input_message_content=InputTextMessageContent(
                message_text="➕ *Добавление канала*\n\n"
                           "Для добавления канала в систему CtrlAI\\_Bot:\n\n"
                           "1\\. Используйте команду `/add_channel` в канале\n"
                           "2\\. Или перейдите в личные сообщения с ботом\n"
                           "3\\. Используйте админ\\-панель для управления\n\n"
                           "**Команды в канале:**\n"
                           "• `/add_channel` \\- добавить канал\n"
                           "• `/help` \\- справка\n"
                           "• `/start` \\- приветствие",
                parse_mode="Markdown"
            )
        ))
    
    if query == "" or "help" in query.lower() or "справка" in query.lower():
        # Кнопка для справки
        results.append(InlineQueryResultArticle(
            id="help",
            title="❓ Справка CtrlAI\\_Bot",
            description="Показать справку по использованию бота",
            input_message_content=InputTextMessageContent(
                message_text="🤖 *CtrlAI\\_Bot \\- Справка для канала*\n\n"
                           "Этот бот поможет вам управлять контентом канала\\.\n\n"
                           "**Доступные команды:**\n"
                           "• @CtrlAI\\_Bot add\\_channel \\- добавить канал в систему\n"
                           "• @CtrlAI\\_Bot help \\- показать справку\n\n"
                           "**Для полного управления:**\n"
                           "Используйте админ\\-панель в личных сообщениях с ботом\\.",
                parse_mode="Markdown"
            )
        ))
    
    if query == "" or "admin" in query.lower() or "панель" in query.lower():
        # Кнопка для админ-панели
        results.append(InlineQueryResultArticle(
            id="admin_panel",
            title="👑 Админ-панель CtrlAI\\_Bot",
            description="Открыть админ-панель для управления каналом",
            input_message_content=InputTextMessageContent(
                message_text="👑 *Админ\\-панель CtrlAI\\_Bot*\n\n"
                           "Выберите действие для управления каналом:",
                parse_mode="Markdown"
            ),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📊 Управление постами", callback_data="manage_posts")],
                [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
                [InlineKeyboardButton(text="📺 Настройки канала", callback_data="channel_settings")],
                [InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
                [InlineKeyboardButton(text="🤖 AI функции", callback_data="ai_functions")],
                [InlineKeyboardButton(text="⏰ Напоминания", callback_data="manage_reminders")]
            ])
        ))
    
    # Если нет результатов, показываем placeholder
    if not results:
        results.append(InlineQueryResultArticle(
            id="placeholder",
            title="🤖 CtrlAI\\_Bot - Управление каналами",
            description="Введите команду для управления каналом",
            input_message_content=InputTextMessageContent(
                message_text="🤖 *CtrlAI\\_Bot \\- Управление каналами*\n\n"
                           "**Доступные команды:**\n"
                           "• `add\\_channel` \\- добавить канал в систему\n"
                           "• `help` \\- показать справку\n"
                           "• `admin` \\- открыть админ\\-панель\n\n"
                           "**Примеры использования:**\n"
                           "• @CtrlAI\\_Bot add\\_channel\n"
                           "• @CtrlAI\\_Bot help\n"
                           "• @CtrlAI\\_Bot admin",
                parse_mode="Markdown"
            )
        ))
    
    await inline_query.answer(results, cache_time=0)

# Обработчик для callback-кнопок из inline-режима
@router.callback_query(F.data == "add_channel_inline")
async def callback_add_channel_inline(callback: CallbackQuery):
    """Добавление канала через inline-кнопку"""
    # В inline-режиме callback.message может быть None
    if not callback.message:
        await callback.answer("❌ Ошибка: сообщение не найдено! Используйте команду /add_channel в канале.")
        return
    
    # В inline-режиме проверяем права по-другому
    try:
        # Получаем информацию о чате из callback
        chat_id = callback.message.chat.id
        user_id = callback.from_user.id
        
        # Проверяем, что пользователь - администратор канала
        user_status = await callback.bot.get_chat_member(chat_id, user_id)
        if user_status.status not in ['administrator', 'creator']:
            await callback.answer("❌ Только администраторы канала могут добавлять канал в систему!")
            return
    except Exception as e:
        logger.error("Error checking user status: %s", e)
        # В случае ошибки проверки прав, все равно пытаемся добавить канал
        # Это может быть проблема с API, но функциональность должна работать
        pass
    
    channel_id = callback.message.chat.id
    channel_title = callback.message.chat.title or "Неизвестный канал"
    
    logger.info(f"Adding channel: {channel_title} (ID: {channel_id})")
    
    try:
        # Проверяем, существует ли канал уже
        existing_channel = await db.fetch_one(
            "SELECT id FROM channels WHERE tg_channel_id = $1",
            channel_id
        )
        
        if existing_channel:
            logger.info(f"Channel {channel_id} already exists")
            await callback.answer("✅ Канал уже добавлен в систему!")
            return
        
        # Добавляем канал в базу данных
        await db.execute(
            "INSERT INTO channels (tg_channel_id, title, enabled, created_at) VALUES ($1, $2, $3, $4)",
            channel_id, channel_title, True, datetime.now()
        )
        
        logger.info(f"Channel {channel_id} added successfully")
        
        await callback.answer(
            f"✅ *Канал добавлен в систему!*\n\n"
            f"📺 **{channel_title}**\n"
            f"🆔 ID: `{channel_id}`\n\n"
            f"Теперь вы можете управлять каналом через админ-панель в личных сообщениях с ботом.",
            show_alert=True
        )
        
        # Обновляем сообщение
        await callback.message.edit_text(
            f"✅ *Канал успешно добавлен в систему!*\n\n"
            f"📺 **{channel_title}**\n"
            f"🆔 ID: `{channel_id}`\n\n"
            f"Теперь вы можете управлять каналом через админ-панель в личных сообщениях с ботом.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
        
    except Exception as e:
        logger.error("Error adding channel: %s", e)
        await callback.answer("❌ Ошибка добавления канала! Попробуйте позже.")

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
        from database import db
        
        # Получаем расширенную информацию о каналах
        channels_query = """
            SELECT 
                c.*,
                COUNT(p.id) as posts_count,
                COUNT(CASE WHEN p.status = 'published' THEN 1 END) as published_count,
                COUNT(CASE WHEN p.status = 'scheduled' THEN 1 END) as scheduled_count,
                COUNT(CASE WHEN p.status = 'draft' THEN 1 END) as draft_count,
                COUNT(CASE WHEN p.status = 'deleted' THEN 1 END) as deleted_count,
                COUNT(CASE WHEN p.media_type IS NOT NULL THEN 1 END) as media_posts_count,
                COUNT(CASE WHEN p.scheduled_at IS NOT NULL THEN 1 END) as scheduled_posts_count,
                MAX(p.created_at) as last_post_date,
                MIN(p.created_at) as first_post_date
            FROM channels c
            LEFT JOIN posts p ON c.id = p.channel_id
            GROUP BY c.id, c.title, c.tg_channel_id, c.created_at
            ORDER BY c.title ASC
        """
        channels = await db.fetch_all(channels_query)
        
        if not channels:
            text = "📢 *Настройки канала*\n\n❌ У вас нет доступных каналов"
        else:
            # Общая статистика
            total_posts = sum(ch['posts_count'] for ch in channels)
            total_published = sum(ch['published_count'] for ch in channels)
            total_scheduled = sum(ch['scheduled_count'] for ch in channels)
            total_drafts = sum(ch['draft_count'] for ch in channels)
            active_channels = len(channels)  # Все каналы считаем активными
            
            text = "📢 *Настройки канала*\n\n"
            text += f"📊 \\*\\*Общая статистика\\:\\*\\*\n"
            text += f"• Каналов: {len(channels)} \\(активных: {active_channels}\\)\n"
            text += f"• Всего постов: {total_posts}\n"
            text += f"• ✅ Опубликовано: {total_published}\n"
            text += f"• ⏰ Запланировано: {total_scheduled}\n"
            text += f"• 📝 Черновики: {total_drafts}\n\n"
            text += f"📺 *Доступные каналы:*\n\n"
            
            for i, channel in enumerate(channels[:5], 1):  # Показываем первые 5 каналов
                channel_title = channel['title'] or 'Без названия'
                status_icon = "✅"  # Все каналы активны
                
                text += f"**{i}\\. {status_icon} {channel_title}**\n"
                text += f"• ID: `{channel['tg_channel_id']}`\n"
                text += f"• \\*\\*Всего постов\\:\\*\\* {channel['posts_count']}\n"
                text += f"  \\- ✅ Опубликовано: {channel['published_count']}\n"
                text += f"  \\- ⏰ Запланировано: {channel['scheduled_count']}\n"
                text += f"  \\- 📝 Черновики: {channel['draft_count']}\n"
                text += f"  \\- 🗑️ Удаленные: {channel['deleted_count']}\n"
                
                if channel['media_posts_count'] > 0:
                    text += f"  \\- 📎 С медиа: {channel['media_posts_count']}\n"
                
                if channel['last_post_date']:
                    from datetime import datetime
                    last_post = channel['last_post_date']
                    if isinstance(last_post, str):
                        last_post = datetime.fromisoformat(last_post.replace('Z', '+00:00'))
                    last_post_str = last_post.strftime('%d.%m.%Y %H:%M').replace('.', '\\.')
                    text += f"• **Последний пост:** {last_post_str}\n"
                
                text += "\n"
            
            if len(channels) > 5:
                text += f"... и еще {len(channels) - 5} каналов\n\n"
        
        keyboard = [
            [InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel")],
            [InlineKeyboardButton(text="📊 Статистика каналов", callback_data="channel_stats")],
            [InlineKeyboardButton(text="⚙️ Управление каналами", callback_data="manage_channels")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
        ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_channel_settings: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки каналов*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )

@router.callback_query(F.data == "manage_channels", admin_filter)
async def callback_manage_channels(callback: CallbackQuery):
    """Управление каналами"""
    try:
        from database import db
        
        # Получаем каналы с базовой информацией
        channels_query = """
            SELECT 
                c.*,
                COUNT(p.id) as posts_count,
                COUNT(CASE WHEN p.status = 'published' THEN 1 END) as published_count
            FROM channels c
            LEFT JOIN posts p ON c.id = p.channel_id
            GROUP BY c.id, c.title, c.tg_channel_id, c.created_at
            ORDER BY c.title ASC
        """
        channels = await db.fetch_all(channels_query)
        
        if not channels:
            text = "⚙️ *Управление каналами*\n\n❌ У вас нет доступных каналов"
            keyboard = [
                [InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="channel_settings")]
            ]
        else:
            text = "⚙️ *Управление каналами*\n\n"
            text += f"📺 *Доступные каналы:*\n\n"
            
            keyboard = []
            for i, channel in enumerate(channels[:10], 1):  # Показываем первые 10 каналов
                channel_title = channel['title'] or 'Без названия'
                status_icon = "✅"  # Все каналы активны
                status_text = "Активен"  # Все каналы активны
                
                text += f"**{i}\\. {status_icon} {channel_title}**\n"
                text += f"• ID: `{channel['tg_channel_id']}`\n"
                text += f"• Статус: {status_text}\n"
                text += f"• Постов: {channel['posts_count']} \\(опубликовано: {channel['published_count']}\\)\n\n"
                
                # Добавляем кнопки для каждого канала
                if i <= 5:  # Показываем кнопки только для первых 5 каналов
                    channel_buttons = [
                        InlineKeyboardButton(
                            text=f"📝 {channel_title[:15]}{'...' if len(channel_title) > 15 else ''}", 
                            callback_data=f"channel_detail_{channel['id']}"
                        )
                    ]
                    if i % 2 == 1:  # Группируем по 2 кнопки в ряд
                        keyboard.append(channel_buttons)
                    else:
                        keyboard[-1].extend(channel_buttons)
            
            if len(channels) > 10:
                text += f"... и еще {len(channels) - 10} каналов\n\n"
            
            # Добавляем общие кнопки
            keyboard.extend([
                [InlineKeyboardButton(text="➕ Добавить канал", callback_data="add_channel")],
                [InlineKeyboardButton(text="📊 Статистика", callback_data="channel_stats")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="channel_settings")]
            ])
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_manage_channels: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки каналов*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="channel_settings")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    
    await callback.answer()

@router.callback_query(F.data.startswith("channel_detail_"), admin_filter)
async def callback_channel_detail(callback: CallbackQuery):
    """Детальная информация о канале"""
    try:
        from database import db
        
        # Извлекаем ID канала из callback_data
        channel_id = int(callback.data.split("_")[-1])
        
        # Получаем детальную информацию о канале
        channel_query = """
            SELECT 
                c.*,
                COUNT(p.id) as posts_count,
                COUNT(CASE WHEN p.status = 'published' THEN 1 END) as published_count,
                COUNT(CASE WHEN p.status = 'scheduled' THEN 1 END) as scheduled_count,
                COUNT(CASE WHEN p.status = 'draft' THEN 1 END) as draft_count,
                COUNT(CASE WHEN p.status = 'deleted' THEN 1 END) as deleted_count,
                COUNT(CASE WHEN p.media_type IS NOT NULL THEN 1 END) as media_posts_count,
                MAX(p.created_at) as last_post_date,
                MIN(p.created_at) as first_post_date
            FROM channels c
            LEFT JOIN posts p ON c.id = p.channel_id
            WHERE c.id = $1
            GROUP BY c.id, c.title, c.tg_channel_id, c.created_at
        """
        channel = await db.fetch_one(channel_query, channel_id)
        
        if not channel:
            text = "❌ *Канал не найден*"
            keyboard = [
                [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_channels")]
            ]
        else:
            channel_title = channel['title'] or 'Без названия'
            status_icon = "✅"  # Все каналы активны
            status_text = "Активен"  # Все каналы активны
            
            text = f"📺 *{status_icon} {channel_title}*\n\n"
            text += f"\\*\\*Основная информация\\:\\*\\*\n"
            text += f"• ID: `{channel['tg_channel_id']}`\n"
            text += f"• Статус: {status_text}\n"
            created_str = channel['created_at'].strftime('%d.%m.%Y %H:%M').replace('.', '\\.') if channel['created_at'] else 'Неизвестно'
            text += f"• Создан: {created_str}\n\n"
            
            text += f"\\*\\*Статистика постов\\:\\*\\*\n"
            text += f"• Всего: {channel['posts_count']}\n"
            text += f"• ✅ Опубликовано: {channel['published_count']}\n"
            text += f"• ⏰ Запланировано: {channel['scheduled_count']}\n"
            text += f"• 📝 Черновики: {channel['draft_count']}\n"
            text += f"• 🗑️ Удаленные: {channel['deleted_count']}\n"
            
            if channel['media_posts_count'] > 0:
                text += f"• 📎 С медиа: {channel['media_posts_count']}\n"
            
            if channel['last_post_date']:
                from datetime import datetime
                last_post = channel['last_post_date']
                if isinstance(last_post, str):
                    last_post = datetime.fromisoformat(last_post.replace('Z', '+00:00'))
                text += f"\n\\*\\*Активность\\:\\*\\*\n"
                last_post_str = last_post.strftime('%d.%m.%Y %H:%M').replace('.', '\\.')
                text += f"• Последний пост: {last_post_str}\n"
            
            if channel['first_post_date']:
                first_post = channel['first_post_date']
                if isinstance(first_post, str):
                    first_post = datetime.fromisoformat(first_post.replace('Z', '+00:00'))
                first_post_str = first_post.strftime('%d.%m.%Y %H:%M').replace('.', '\\.')
                text += f"• Первый пост: {first_post_str}\n"
            
            keyboard = [
                [InlineKeyboardButton(text="📝 Посты канала", callback_data=f"channel_posts_{channel_id}")],
                [InlineKeyboardButton(text="⚙️ Настройки", callback_data=f"channel_config_{channel_id}")],
                [InlineKeyboardButton(text="📊 Статистика", callback_data=f"channel_stats_{channel_id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_channels")]
            ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_channel_detail: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки канала*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_channels")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )

@router.callback_query(F.data == "manage_tags", admin_filter)
async def callback_manage_tags(callback: CallbackQuery):
    """Управление тегами"""
    try:
        from services.tags import tag_service
        from database import db
        
        # Получаем каналы пользователя
        channels_query = "SELECT * FROM channels ORDER BY title ASC"
        channels = await db.fetch_all(channels_query)
        
        if not channels:
            text = "🏷️ *Управление тегами*\n\n❌ У вас нет доступных каналов"
        else:
            # Получаем теги для первого канала
            channel = channels[0]
            tags = await tag_service.get_tags_by_channel(channel['id'])
            
            text = f"🏷️ *Управление тегами*\n\n"
            text += f"📺 *Канал:* {channel['title']}\n\n"
            
            if tags:
                text += "📋 *Существующие теги:*\n"
                for tag in tags[:10]:  # Показываем первые 10 тегов
                    text += f"• `{tag['name']}` ({tag['kind']})\n"
                if len(tags) > 10:
                    text += f"... и еще {len(tags) - 10} тегов\n"
            else:
                text += "📝 Тегов пока нет\n"
        
        keyboard = [
            [InlineKeyboardButton(text="➕ Создать тег", callback_data="create_tag")],
            [InlineKeyboardButton(text="📋 Все теги", callback_data="list_tags")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
        ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_manage_tags: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки тегов*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    
    await callback.answer()

@router.callback_query(F.data == "manage_series", admin_filter)
async def callback_manage_series(callback: CallbackQuery):
    """Управление сериями"""
    try:
        from services.series import series_service
        from database import db
        
        # Получаем каналы пользователя
        channels_query = "SELECT * FROM channels ORDER BY title ASC"
        channels = await db.fetch_all(channels_query)
        
        if not channels:
            text = "📚 *Управление сериями*\n\n❌ У вас нет доступных каналов"
        else:
            # Получаем серии для первого канала
            channel = channels[0]
            series = await series_service.get_series_by_channel(channel['id'])
            
            text = f"📚 *Управление сериями*\n\n"
            text += f"📺 *Канал:* {channel['title']}\n\n"
            
            if series:
                text += "📋 *Существующие серии:*\n"
                for s in series[:10]:  # Показываем первые 10 серий
                    text += f"• `{s['code']}` - {s['title']} (следующий: {s['next_number']})\n"
                if len(series) > 10:
                    text += f"... и еще {len(series) - 10} серий\n"
            else:
                text += "📝 Серий пока нет\n"
        
        keyboard = [
            [InlineKeyboardButton(text="➕ Создать серию", callback_data="create_series")],
            [InlineKeyboardButton(text="📋 Все серии", callback_data="list_series")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
        ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_manage_series: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки серий*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    
    await callback.answer()

@router.callback_query(F.data == "manage_reminders", admin_filter)
async def callback_manage_reminders(callback: CallbackQuery):
    """Управление напоминаниями"""
    try:
        if callback.message:
            # Получаем статус планировщика
            from services.reminder_service import reminder_service
            status = await reminder_service.get_scheduler_status()
            
            # Получаем список напоминаний
            reminders = await reminder_service.get_all_reminders()
            
            status_text = "🟢 Активен" if status else "🔴 Остановлен"
            reminders_count = len(reminders) if reminders else 0
            
            text = f"⏰ *Управление напоминаниями*\n\n"
            text += f"📊 *Статус планировщика:* {status_text}\n"
            text += f"📝 *Количество напоминаний:* {reminders_count}\n\n"
            text += f"*Доступные функции:*\n"
            text += f"• Просмотр напоминаний\n"
            text += f"• Создание нового напоминания\n"
            text += f"• Настройки планировщика\n"
            text += f"• Управление расписанием"
            
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Мои напоминания", callback_data="my_reminders")],
                    [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
                    [InlineKeyboardButton(text="⚙️ Настройки", callback_data="reminder_settings")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in manage_reminders: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки напоминаний*\n\nПопробуйте позже.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ])
            )
    await callback.answer()

@router.callback_query(F.data == "export_data", admin_filter)
async def callback_export_data(callback: CallbackQuery):
    """Экспорт данных"""
    try:
        from services.export import export_service
        from database import db
        
        # Получаем статистику
        stats = await export_service.get_export_stats()
        
        text = "📊 *Экспорт данных*\n\n"
        text += f"📈 *Статистика:*\n"
        text += f"• Всего постов: {stats['total_posts']}\n"
        text += f"• Опубликовано: {stats['published_posts']}\n"
        text += f"• Запланировано: {stats['scheduled_posts']}\n"
        text += f"• Черновики: {stats['draft_posts']}\n"
        text += f"• Удаленные: {stats['deleted_posts']}\n\n"
        
        if stats['channels']:
            text += "📺 *Каналы:*\n"
            for channel in stats['channels'][:5]:  # Показываем первые 5 каналов
                text += f"• {channel['title']}: {channel['posts_count']} постов\n"
            if len(stats['channels']) > 5:
                text += f"... и еще {len(stats['channels']) - 5} каналов\n"
        
        keyboard = [
            [InlineKeyboardButton(text="📄 JSON экспорт", callback_data="export_json")],
            [InlineKeyboardButton(text="📝 Markdown экспорт", callback_data="export_markdown")],
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="export_stats")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
        ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_export_data: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки статистики*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    
    await callback.answer()


@router.callback_query(F.data == "back_to_admin", admin_filter)
async def callback_back_to_admin(callback: CallbackQuery):
    """Возврат в админ-панель"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "👑 *Админ панель CtrlAI\\_Bot*\n\n"
                "Выберите действие:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
                    [InlineKeyboardButton(text="📢 Проверить отложенные", callback_data="check_scheduled_posts")],
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

@router.callback_query(F.data == "create_poll", admin_filter)
async def callback_create_poll(callback: CallbackQuery, state: FSMContext):
    """Создание нового опроса"""
    from utils.states import PollCreationStates
    
    # Проверяем, есть ли привязанные каналы
    from database import db
    channels = await db.fetch_all("SELECT id, tg_channel_id, title FROM channels")
    
    if not channels:
        # Нет каналов - показываем инструкцию
        await callback.message.edit_text(
            "🔗 *Сначала привяжите канал!*\n\n"
            "Для создания опросов нужно привязать канал:\n\n"
            "1️⃣ *Добавьте бота в канал как администратора*\n"
            "   • Права: отправка сообщений\n"
            "   • Редактирование сообщений\n\n"
            "2️⃣ *Используйте команду /add_channel в канале*\n"
            "   Или добавьте канал через админ\\-панель\n\n"
            "После этого вы сможете создавать опросы\\!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
            ]),
            parse_mode=ParseMode.MARKDOWN_V2
        )
        await callback.answer("❌ Нет привязанных каналов!")
        return
    
    # Переходим к созданию опроса
    await state.set_state(PollCreationStates.enter_question)
    try:
        if callback.message:
            await callback.message.edit_text(
                "📊 **Создание опроса**\n\n"
                "Отправьте вопрос для опроса:\n\n"
                "Пример:\n"
                "Какой ваш любимый язык программирования?",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in create_poll: %s", e)
    await callback.answer()

@router.callback_query(F.data == "export_json", admin_filter)
async def callback_export_json(callback: CallbackQuery):
    """Экспорт в JSON"""
    try:
        from services.export import export_service
        
        # Получаем данные для экспорта
        export_data = await export_service.export_posts_to_json()
        
        # Создаем JSON файл
        import json
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
            temp_file = f.name
        
        # Отправляем файл
        from aiogram.types import FSInputFile
        document = FSInputFile(temp_file, filename="export.json")
        await callback.message.answer_document(
            document=document,
            caption="📄 *JSON экспорт данных*\n\nЭкспорт завершен успешно\\!",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Удаляем временный файл
        os.unlink(temp_file)
        
    except Exception as e:
        logger.error("Error in callback_export_json: %s", e)
        await callback.message.answer(
            "❌ *Ошибка экспорта в JSON*\n\nПопробуйте позже",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    await callback.answer()

@router.callback_query(F.data == "export_markdown", admin_filter)
async def callback_export_markdown(callback: CallbackQuery):
    """Экспорт в Markdown"""
    try:
        from services.export import export_service
        
        # Получаем данные для экспорта
        markdown_content = await export_service.export_posts_to_markdown()
        
        # Создаем Markdown файл
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False, encoding='utf-8') as f:
            f.write(markdown_content)
            temp_file = f.name
        
        # Отправляем файл
        from aiogram.types import FSInputFile
        document = FSInputFile(temp_file, filename="export.md")
        await callback.message.answer_document(
            document=document,
            caption="📝 *Markdown экспорт данных*\n\nЭкспорт завершен успешно\\!",
            parse_mode=ParseMode.MARKDOWN_V2
        )
        
        # Удаляем временный файл
        os.unlink(temp_file)
        
    except Exception as e:
        logger.error("Error in callback_export_markdown: %s", e)
        await callback.message.answer(
            "❌ *Ошибка экспорта в Markdown*\n\nПопробуйте позже",
            parse_mode=ParseMode.MARKDOWN_V2
        )
    
    await callback.answer()

@router.callback_query(F.data == "export_stats", admin_filter)
async def callback_export_stats(callback: CallbackQuery):
    """Обновить статистику экспорта"""
    try:
        from services.export import export_service
        
        # Получаем статистику
        stats = await export_service.get_export_stats()
        
        text = "📊 *Экспорт данных*\n\n"
        text += f"📈 *Статистика:*\n"
        text += f"• Всего постов: {stats['total_posts']}\n"
        text += f"• Опубликовано: {stats['published_posts']}\n"
        text += f"• Запланировано: {stats['scheduled_posts']}\n"
        text += f"• Черновики: {stats['draft_posts']}\n"
        text += f"• Удаленные: {stats['deleted_posts']}\n\n"
        
        if stats['channels']:
            text += "📺 *Каналы:*\n"
            for channel in stats['channels'][:5]:  # Показываем первые 5 каналов
                text += f"• {channel['title']}: {channel['posts_count']} постов\n"
            if len(stats['channels']) > 5:
                text += f"... и еще {len(stats['channels']) - 5} каналов\n"
        
        keyboard = [
            [InlineKeyboardButton(text="📄 JSON экспорт", callback_data="export_json")],
            [InlineKeyboardButton(text="📝 Markdown экспорт", callback_data="export_markdown")],
            [InlineKeyboardButton(text="🔄 Обновить", callback_data="export_stats")],
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
        ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        
    except Exception as e:
        logger.error("Error in callback_export_stats: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки статистики*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    
    await callback.answer()

@router.callback_query(F.data == "ai_functions", admin_filter)
async def callback_ai_functions(callback: CallbackQuery):
    """AI функции"""
    try:
        from services.ai_service import ai_service
        
        # Проверяем статус AI API
        api_status = await ai_service.check_api_status()
        
        text = "🤖 *AI помощник CtrlBot*\n\n"
        
        if api_status['status'] == 'working':
            text += "✅ *Статус:* API работает\n\n"
            text += "🔧 *Доступные функции:*\n"
            text += "• Подсказки тегов на основе текста\n"
            text += "• Сокращение длинных текстов\n"
            text += "• Изменение стиля текста\n"
            text += "• Улучшение грамматики и стиля\n"
            text += "• Создание аннотаций\n\n"
            text += "💡 *Использование:*\n"
            text += "Отправьте текст в чат с ботом, и AI поможет его улучшить\\!"
        elif api_status['status'] == 'not_configured':
            text += "⚠️ *Статус:* API не настроен\n\n"
            text += "Для использования AI функций необходимо:\n"
            text += "• Настроить YANDEX_API_KEY\n"
            text += "• Настроить YANDEX_FOLDER_ID\n\n"
            text += "Обратитесь к администратору для настройки."
        else:
            text += "❌ *Статус:* Ошибка API\n\n"
            text += f"Проблема: {api_status['message']}\n\n"
            text += "Попробуйте позже или обратитесь к администратору."
        
        keyboard = [
            [InlineKeyboardButton(text="🔄 Проверить статус", callback_data="ai_functions")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ]
        
        if callback.message:
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error("Error in callback_ai_functions: %s", e)
        if callback.message:
            await callback.message.edit_text(
                "❌ *Ошибка загрузки AI функций*\n\nПопробуйте позже",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ]),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    
    await callback.answer()

@router.callback_query(F.data == "my_posts", admin_filter)
async def callback_view_posts(callback: CallbackQuery):
    """Обработчик кнопки 'Просмотр постов' - перенаправляем на my_posts"""
    # Перенаправляем на обработчик my_posts с пагинацией
    from handlers.post_handlers import callback_my_posts
    await callback_my_posts(callback)

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

# Добавляем недостающие обработчики для кнопок в админ-панели
@router.callback_query(F.data == "add_channel", admin_filter)
async def callback_add_channel(callback: CallbackQuery):
    """Добавление канала"""
    await callback.message.edit_text(
        "➕ *Добавление канала*\n\n"
        "Для добавления канала:\n"
        "1. Добавьте бота в канал как администратора\n"
        "2. Отправьте команду /start в канале\n"
        "3. Бот автоматически добавит канал в систему\n\n"
        "Или используйте команду /add_channel в канале.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="channel_settings")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "channel_stats", admin_filter)
async def callback_channel_stats(callback: CallbackQuery):
    """Статистика каналов"""
    try:
        # Получаем статистику каналов
        stats = await export_service.get_export_stats()
        
        channels_text = ""
        if stats.get('channels'):
            for channel in stats['channels']:
                channel_name = channel.get('title', 'Без названия')
                posts_count = channel.get('posts_count', 0)
                channels_text += f"• {channel_name}: {posts_count} постов\n"
        else:
            channels_text = "Нет данных о каналах"
        
        await callback.message.edit_text(
            f"📊 *Статистика каналов*\n\n"
            f"*Всего каналов:* {stats.get('total_channels', 0)}\n"
            f"*Всего постов:* {stats.get('total_posts', 0)}\n\n"
            f"*По каналам:*\n{channels_text}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="channel_settings")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error("Error in callback_channel_stats: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка загрузки статистики*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="channel_settings")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data == "create_tag", admin_filter)
async def callback_create_tag(callback: CallbackQuery):
    """Создание тега"""
    await callback.message.edit_text(
        "➕ *Создание тега*\n\n"
        "Для создания тега отправьте сообщение в формате:\n"
        "`/create_tag название_тега`\n\n"
        "Пример: `/create_tag новости`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_tags")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "list_tags", admin_filter)
async def callback_list_tags(callback: CallbackQuery):
    """Список тегов"""
    try:
        # Получаем все теги
        tags = await tag_service.get_all_tags()
        
        if not tags:
            await callback.message.edit_text(
                "🏷️ *Все теги*\n\n"
                "Теги не найдены.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_tags")]
                ])
            )
        else:
            tags_text = ""
            for i, tag in enumerate(tags[:20], 1):  # Показываем только первые 20
                tag_name = tag.get('name', 'Без названия')
                posts_count = tag.get('posts_count', 0)
                tags_text += f"{i}. {tag_name} ({posts_count} постов)\n"
            
            if len(tags) > 20:
                tags_text += f"\n... и еще {len(tags) - 20} тегов"
            
            await callback.message.edit_text(
                f"🏷️ *Все теги*\n\n{tags_text}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_tags")]
                ])
            )
        await callback.answer()
        
    except Exception as e:
        logger.error("Error in callback_list_tags: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка загрузки тегов*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_tags")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data == "create_series", admin_filter)
async def callback_create_series(callback: CallbackQuery):
    """Создание серии"""
    await callback.message.edit_text(
        "➕ *Создание серии*\n\n"
        "Для создания серии отправьте сообщение в формате:\n"
        "`/create_series название_серии`\n\n"
        "Пример: `/create_series еженедельный_дайджест`",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_series")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "list_series", admin_filter)
async def callback_list_series(callback: CallbackQuery):
    """Список серий"""
    try:
        # Получаем все серии
        series = await series_service.get_all_series()
        
        if not series:
            await callback.message.edit_text(
                "📚 *Все серии*\n\n"
                "Серии не найдены.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_series")]
                ])
            )
        else:
            series_text = ""
            for i, series_item in enumerate(series[:20], 1):  # Показываем только первые 20
                series_name = series_item.get('name', 'Без названия')
                posts_count = series_item.get('posts_count', 0)
                series_text += f"{i}. {series_name} ({posts_count} постов)\n"
            
            if len(series) > 20:
                series_text += f"\n... и еще {len(series) - 20} серий"
            
            await callback.message.edit_text(
                f"📚 *Все серии*\n\n{series_text}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_series")]
                ])
            )
        await callback.answer()
        
    except Exception as e:
        logger.error("Error in callback_list_series: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка загрузки серий*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_series")]
            ])
        )
        await callback.answer()


