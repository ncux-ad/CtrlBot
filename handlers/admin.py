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
    logger.info("Start command received from admin %s", message.from_user.id)
    await message.answer(
        "👑 <b>Админ панель CtrlBot</b>\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="view_posts")],
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
        "👑 <b>Админ панель CtrlBot</b>\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
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
        "📝 <b>Создание нового поста</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "🤖 AI помощник")
async def btn_ai_helper(message: Message):
    """Обработчик кнопки 'AI помощник' - перенаправляем на inline меню"""
    await message.answer(
        "🤖 <b>AI помощник</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🤖 AI функции", callback_data="ai_functions")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "🏷️ Теги")
async def btn_tags(message: Message):
    """Обработчик кнопки 'Теги' - перенаправляем на inline меню"""
    await message.answer(
        "🏷️ <b>Управление тегами</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "⚙️ Настройки")
async def btn_settings(message: Message):
    """Обработчик кнопки 'Настройки' - перенаправляем на inline меню"""
    await message.answer(
        "⚙️ <b>Настройки</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📢 Настройки канала", callback_data="channel_settings")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "📋 Мои посты")
async def btn_my_posts(message: Message):
    """Обработчик кнопки 'Мои посты' - перенаправляем на inline меню"""
    await message.answer(
        "📋 <b>Мои посты</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Просмотр постов", callback_data="view_posts")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "⏰ Напоминания")
async def btn_reminders(message: Message):
    """Обработчик кнопки 'Напоминания' - перенаправляем на inline меню"""
    await message.answer(
        "⏰ <b>Напоминания</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏰ Управление напоминаниями", callback_data="manage_reminders")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "📊 Серии")
async def btn_series(message: Message):
    """Обработчик кнопки 'Серии' - перенаправляем на inline меню"""
    await message.answer(
        "📊 <b>Серии</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 Управление сериями", callback_data="manage_series")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(F.text == "📈 Статистика")
async def btn_statistics(message: Message):
    """Обработчик кнопки 'Статистика' - перенаправляем на inline меню"""
    await message.answer(
        "📈 <b>Статистика</b>\n\n"
        "Используйте кнопки ниже для навигации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Экспорт данных", callback_data="export_data")],
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(Command("config"), admin_filter)
async def cmd_config(message: Message):
    """Показ конфигурации"""
    config_info = f"""
⚙️ <b>Конфигурация CtrlBot</b>

<b>Основные настройки:</b>
• Логирование: {config.LOG_LEVEL}
• Макс. длина поста: {config.MAX_POST_LENGTH}
• Мин. тегов: {config.MIN_TAGS_REQUIRED}
• Часовой пояс: {config.TIMEZONE}

<b>База данных:</b>
• Хост: {config.DB_HOST}:{config.DB_PORT}
• База: {config.DB_NAME}
• Пользователь: {config.DB_USER}

<b>AI интеграция:</b>
• YandexGPT: {'✅ Настроено' if config.YANDEX_API_KEY else '❌ Не настроено'}
• Папка: {config.YANDEX_FOLDER_ID or 'Не указана'}

<b>Каналы:</b>
• Настроено каналов: {len(config.CHANNEL_IDS) if hasattr(config, 'CHANNEL_IDS') else 0}
• ID каналов: {config.CHANNEL_IDS if hasattr(config, 'CHANNEL_IDS') else 'Не настроено'}

<b>Администраторы:</b>
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
                            f"✅ <b>Канал успешно настроен!</b>\n\n"
                            f"📢 <b>Канал:</b> {channel_title}\n"
                            f"🆔 <b>ID:</b> <code>{channel_id}</code>\n"
                            f"🤖 <b>Права бота:</b> ✅ Администратор\n"
                            f"📝 <b>Публикация:</b> ✅ Разрешена\n\n"
                            f"Теперь бот может публиковать посты в этот канал!",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                            ])
                        )
                    else:
                        await message.answer(
                            f"ℹ️ <b>Канал уже настроен</b>\n\n"
                            f"📢 <b>Канал:</b> {channel_title}\n"
                            f"🆔 <b>ID:</b> <code>{channel_id}</code>\n\n"
                            f"Канал уже добавлен в список для публикации.",
                            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                            ])
                        )
                else:
                    await message.answer(
                        f"❌ <b>Недостаточно прав</b>\n\n"
                        f"📢 <b>Канал:</b> {channel_title}\n"
                        f"🆔 <b>ID:</b> <code>{channel_id}</code>\n\n"
                        f"Бот добавлен как администратор, но не может публиковать сообщения.\n"
                        f"Проверьте права бота в настройках канала.",
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                        ])
                    )
            else:
                await message.answer(
                    f"❌ <b>Бот не является администратором</b>\n\n"
                    f"📢 <b>Канал:</b> {channel_title}\n"
                    f"🆔 <b>ID:</b> <code>{channel_id}</code>\n\n"
                    f"Добавьте бота в канал как администратора с правами на публикацию.",
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                    ])
                )
                
        except Exception as e:
            logger.error("Error checking channel permissions: %s", e)
            await message.answer(
                f"❌ <b>Ошибка проверки канала</b>\n\n"
                f"Не удалось проверить права бота в канале.\n"
                f"Убедитесь, что бот добавлен как администратор.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
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
                "📢 <b>Настройки канала</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будут настройки канала.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
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
                "🏷️ <b>Управление тегами</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет управление тегами.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
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
                "📚 <b>Управление сериями</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет управление сериями.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
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
                "⏰ <b>Управление напоминаниями</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет управление напоминаниями.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
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
                "📊 <b>Экспорт данных</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет экспорт данных.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in export_data: %s", e)
    await callback.answer()

@router.callback_query(F.data == "back_to_main", admin_filter)
async def callback_back_to_main(callback: CallbackQuery):
    """Возврат в главное меню"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "👑 <b>Админ панель CtrlBot</b>\n\n"
                "Выберите действие:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="📋 Мои посты", callback_data="view_posts")],
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
        logger.warning("Failed to edit message in back_to_main: %s", e)
        await safe_callback_answer(callback)

# Новые callback обработчики для inline навигации
@router.callback_query(F.data == "create_post", admin_filter)
async def callback_create_post(callback: CallbackQuery, state: FSMContext):
    """Создание нового поста"""
    from utils.states import PostCreationStates
    from utils.keyboards import get_post_actions_keyboard
    
    await state.set_state(PostCreationStates.enter_text)
    try:
        if callback.message:
            await callback.message.edit_text(
                "📝 <b>Создание нового поста</b>\n\n"
                "Отправьте текст поста в формате Markdown.\n"
                "Можно использовать *жирный*, _курсив_, `код` и другие элементы.",
                reply_markup=get_post_actions_keyboard()
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
                "🤖 <b>AI помощник CtrlBot</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет AI помощник с YandexGPT.\n\n"
                "Планируемые функции:\n"
                "• Подсказки тегов на основе текста\n"
                "• Сокращение длинных текстов\n"
                "• Изменение стиля текста\n"
                "• Улучшение грамматики и стиля\n"
                "• Создание аннотаций",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in ai_functions: %s", e)
    await callback.answer()

@router.callback_query(F.data == "view_posts", admin_filter)
async def callback_view_posts(callback: CallbackQuery):
    """Просмотр постов"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "📋 <b>Мои посты</b>\n\n"
                "Функция находится в разработке.\n"
                "Скоро здесь будет список ваших постов.\n\n"
                "Планируемые функции:\n"
                "• Просмотр всех постов\n"
                "• Фильтрация по статусу\n"
                "• Редактирование постов\n"
                "• Удаление постов\n"
                "• Статистика публикаций",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in view_posts: %s", e)
    await callback.answer()

@router.callback_query(F.data == "get_channel_id", admin_filter)
async def callback_get_channel_id(callback: CallbackQuery):
    """Получение ID канала"""
    try:
        if callback.message:
            await callback.message.edit_text(
                "🔗 <b>Получение ID канала</b>\n\n"
                "Для настройки публикации постов:\n\n"
                "1️⃣ <b>Добавьте бота в канал как администратора</b>\n"
                "   • Права: отправка сообщений\n"
                "   • Редактирование сообщений\n\n"
                "2️⃣ <b>Перешлите любое сообщение из канала боту</b>\n"
                "   • Я автоматически определю ID канала\n"
                "   • Сохраню настройки\n\n"
                "3️⃣ <b>Готово!</b> Бот сможет публиковать посты\n\n"
                "💡 <i>Перешлите сообщение из канала прямо сейчас</i>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
    except Exception as e:
        logger.warning("Failed to edit message in get_channel_id: %s", e)
    await callback.answer()


