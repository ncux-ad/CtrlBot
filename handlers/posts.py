"""
@file: handlers/posts.py
@description: Обработчики для создания и управления постами
@dependencies: services/posts.py, utils/keyboards.py, utils/states.py
@created: 2025-09-13
"""

import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

# Удалены сложные импорты форматирования - используем KISS принцип

from services.posts import post_service
from services.tags import tag_service
from utils.keyboards import (
    get_main_menu_keyboard,
    get_post_actions_keyboard,
    get_tags_keyboard,
    get_series_keyboard,
    get_schedule_keyboard,
    get_confirmation_keyboard
)
from utils.states import PostCreationStates
from utils.filters import IsConfigAdminFilter, PostTextFilter
from utils.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()
text_filter = PostTextFilter()

def convert_markdown_to_telegram(text: str) -> str:
    """Конвертирует стандартный Markdown в Telegram MarkdownV2"""
    logger.info(f"🔄 convert_markdown_to_telegram: входной текст: '{text}'")
    
    # Исправляем незакрытые блоки кода
    # Если есть ``` без закрытия, добавляем ```
    triple_backticks_count = text.count('```')
    if triple_backticks_count % 2 == 1:
        text += '```'
        logger.info("🔄 Исправлен незакрытый блок кода")
    
    # Сначала обрабатываем блоки кода - они не должны конвертироваться
    code_blocks = []
    code_pattern = r'```([^`]*?)```'
    code_matches = re.findall(code_pattern, text, re.DOTALL)
    for i, code_content in enumerate(code_matches):
        placeholder = f"__CODE_BLOCK_{i}__"
        code_blocks.append(code_content)
        text = text.replace(f"```{code_content}```", placeholder)
    
    # Обрабатываем одиночные блоки кода
    single_backticks = []
    single_code_pattern = r'`([^`]+)`'
    single_matches = re.findall(single_code_pattern, text)
    for i, code_content in enumerate(single_matches):
        placeholder = f"__SINGLE_CODE_{i}__"
        single_backticks.append(code_content)
        text = text.replace(f"`{code_content}`", placeholder)
    
    # Конвертируем одинарные маркеры в правильные для Telegram MarkdownV2
    # *жирный* -> **жирный** (жирный)
    before_bold = text
    text = re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)', r'**\1**', text)
    if before_bold != text:
        logger.info(f"🔄 Конвертация жирного: '{before_bold}' -> '{text}'")
    
    # _курсив_ -> *курсив* (курсив, НЕ подчеркивание!)
    before_italic = text
    text = re.sub(r'(?<![a-zA-Z0-9])_([^_]+)_(?![a-zA-Z0-9])', r'*\1*', text)
    if before_italic != text:
        logger.info(f"🔄 Конвертация курсива: '{before_italic}' -> '{text}'")
    
    # Экранируем специальные символы для MarkdownV2
    # Символы, которые нужно экранировать: _ * [ ] ( ) ~ ` > # + - = | { } . !
    before_escape = text
    escape_chars = r'\_\*\[\]\(\)~`>#\+\-=|{}\.!'
    for char in escape_chars:
        if char not in ['*', '_', '[', ']', '(', ')', '`']:  # Не экранируем маркеры форматирования
            text = text.replace(char, f'\\{char}')
    
    if before_escape != text:
        logger.info(f"🔄 Экранирование: '{before_escape}' -> '{text}'")
    
    # Восстанавливаем блоки кода
    for i, code_content in enumerate(code_blocks):
        placeholder = f"__CODE_BLOCK_{i}__"
        text = text.replace(placeholder, f"```{code_content}```")
    
    for i, code_content in enumerate(single_backticks):
        placeholder = f"__SINGLE_CODE_{i}__"
        text = text.replace(placeholder, f"`{code_content}`")
    
    logger.info(f"🔄 convert_markdown_to_telegram: результат: '{text}'")
    return text

def escape_markdown(text: str) -> str:
    """Экранирует специальные символы Telegram Markdown"""
    # Символы, которые нужно экранировать в Telegram Markdown
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

# Удалена сложная функция конвертации форматирования - используем KISS принцип

@router.message(Command("new_post"), admin_filter)
async def cmd_new_post(message: Message, state: FSMContext):
    """Команда создания нового поста"""
    await state.set_state(PostCreationStates.enter_text)
    await message.answer(
        "📝 <b>Создание нового поста</b>\n\n"
        "Отправьте текст поста - любой текст, который хотите опубликовать.\n\n"
        "💡 <b>Поддерживается Markdown форматирование:</b>\n"
        "• *жирный* → **жирный**\n"
        "• _курсив_ → __курсив__\n"
        "• `код` → `код`\n"
        "• [ссылка](url) → [ссылка](url)\n\n"
        "✅ <b>Можно копировать из Obsidian, .md файлов и других редакторов!</b>",
        reply_markup=get_post_actions_keyboard()
    )

# Удален - заменен универсальным обработчиком

# Удален - заменен универсальным обработчиком

# Удален - заменен универсальным обработчиком

@router.callback_query(F.data == "preview_post", StateFilter(PostCreationStates.preview))
async def callback_preview_post(callback: CallbackQuery, state: FSMContext):
    """Повторный показ предпросмотра"""
    logger.info("=== ПОВТОРНЫЙ ПРЕДПРОСМОТР ===")
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    logger.info(f"📝 Текст для предпросмотра: '{post_text}'")
    
    try:
        logger.info("🔄 Редактируем сообщение с parse_mode='MarkdownV2'")
        # Экранируем HTML теги для MarkdownV2
        preview_text = f"👁️ *Предпросмотр поста:*\n\n{post_text}"
        await callback.message.edit_text(
            preview_text,
            parse_mode="MarkdownV2",
            reply_markup=get_post_actions_keyboard()
        )
        logger.info("✅ Сообщение отредактировано успешно")
    except Exception as e:
        logger.warning(f"❌ Не удалось отредактировать сообщение: {e}")
        # Если не удалось отредактировать, отправляем новое сообщение
        logger.info("📤 Отправляем новое сообщение с parse_mode='MarkdownV2'")
        preview_text = f"👁️ *Предпросмотр поста:*\n\n{post_text}"
        await callback.message.answer(
            preview_text,
            parse_mode="MarkdownV2",
            reply_markup=get_post_actions_keyboard()
        )
        logger.info("✅ Новое сообщение отправлено")
    await callback.answer()

@router.callback_query(F.data == "markdown_example")
async def callback_markdown_example(callback: CallbackQuery, state: FSMContext):
    """Показать пример Markdown форматирования"""
    # Проверяем, есть ли сохраненный текст поста
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    example_text = """
📝 <b>Пример Markdown форматирования:</b>

*Это жирный текст*
_Это курсивный текст_
`Это моноширинный код`

```блок кода
function hello() {
    console.log("Привет!");
}
```

[Ссылка на сайт](https://example.com)

<b>Списки:</b>
• Первый пункт
• Второй пункт
• Третий пункт

<b>Нумерованный список:</b>
1. Первый
2. Второй  
3. Третий

<b>Цитата:</b>
> Это цитата
> может быть многострочной

<b>Эмодзи:</b> 😀 🚀 💡 📝 ✅ ❌
    """
    
    # Если есть сохраненный текст поста, показываем кнопку "Назад к посту"
    if post_text:
        keyboard = [[InlineKeyboardButton(text="🔙 Назад к посту", callback_data="back_to_preview")]]
    else:
        keyboard = [[InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]]
    
    await callback.message.answer(
        example_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_preview")
async def callback_back_to_preview(callback: CallbackQuery, state: FSMContext):
    """Возврат к предпросмотру поста"""
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    if not post_text:
        await callback.message.answer(
            "❌ <b>Текст поста не найден</b>\n\n"
            "Создайте новый пост командой /new_post",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        )
    else:
        await state.set_state(PostCreationStates.preview)
        # Экранируем HTML теги для MarkdownV2
        preview_text = f"👁️ *Предпросмотр поста:*\n\n{post_text}"
        await callback.message.answer(
            preview_text,
            parse_mode="MarkdownV2",
            reply_markup=get_post_actions_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def callback_back_to_main_from_example(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню из примера Markdown"""
    await state.clear()
    await callback.message.answer(
        "🏠 <b>Главное меню</b>\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="view_posts")],
            [InlineKeyboardButton(text="🤖 AI помощник", callback_data="ai_functions")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="channel_settings")],
            [InlineKeyboardButton(text="🔗 Получить ID канала", callback_data="get_channel_id")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "add_tags", StateFilter(PostCreationStates.preview))
async def callback_add_tags(callback: CallbackQuery, state: FSMContext):
    """Переход к добавлению тегов"""
    # Получаем теги канала (пока заглушка)
    # TODO: Получать реальные теги из БД
    tags = [
        {"id": 1, "name": "новости"},
        {"id": 2, "name": "анонсы"},
        {"id": 3, "name": "объявления"},
        {"id": 4, "name": "важно"}
    ]
    
    await state.set_state(PostCreationStates.add_tags)
    await callback.message.edit_text(
        "🏷️ <b>Выберите теги для поста:</b>\n\n"
        "Отметьте нужные теги и нажмите 'Готово'",
        reply_markup=get_tags_keyboard(tags)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("toggle_tag_"), StateFilter(PostCreationStates.add_tags))
async def callback_toggle_tag(callback: CallbackQuery, state: FSMContext):
    """Переключение выбора тега"""
    tag_id = int(callback.data.split("_")[2])
    
    # Получаем текущие выбранные теги
    data = await state.get_data()
    selected_tags = data.get('selected_tags', [])
    
    # Переключаем тег
    if tag_id in selected_tags:
        selected_tags.remove(tag_id)
    else:
        selected_tags.append(tag_id)
    
    await state.update_data(selected_tags=selected_tags)
    
    # Обновляем клавиатуру
    tags = [
        {"id": 1, "name": "новости"},
        {"id": 2, "name": "анонсы"},
        {"id": 3, "name": "объявления"},
        {"id": 4, "name": "важно"}
    ]
    
    await callback.message.edit_reply_markup(
        reply_markup=get_tags_keyboard(tags, selected_tags)
    )
    await callback.answer()

@router.callback_query(F.data == "tags_done", StateFilter(PostCreationStates.add_tags))
async def callback_tags_done(callback: CallbackQuery, state: FSMContext):
    """Завершение выбора тегов"""
    data = await state.get_data()
    selected_tags = data.get('selected_tags', [])
    
    if not selected_tags:
        await callback.answer("❌ Выберите хотя бы один тег!", show_alert=True)
        return
    
    # Переходим к выбору серии
    await state.set_state(PostCreationStates.choose_series)
    
    # Получаем серии канала (пока заглушка)
    # TODO: Получать реальные серии из БД
    series = [
        {"id": 1, "title": "Еженедельные новости", "next_number": 5},
        {"id": 2, "title": "Анонсы событий", "next_number": 12}
    ]
    
    await callback.message.edit_text(
        "📚 <b>Выберите серию для поста:</b>\n\n"
        "Пост будет автоматически пронумерован в выбранной серии.",
        reply_markup=get_series_keyboard(series)
    )
    await callback.answer()

@router.callback_query(F.data.startswith("select_series_"), StateFilter(PostCreationStates.choose_series))
async def callback_select_series(callback: CallbackQuery, state: FSMContext):
    """Выбор серии"""
    series_id = int(callback.data.split("_")[2])
    await state.update_data(series_id=series_id)
    
    # Переходим к планированию
    await state.set_state(PostCreationStates.schedule)
    await callback.message.edit_text(
        "📅 <b>Планирование публикации:</b>\n\n"
        "Выберите когда опубликовать пост:",
        reply_markup=get_schedule_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "skip_series", StateFilter(PostCreationStates.choose_series))
async def callback_skip_series(callback: CallbackQuery, state: FSMContext):
    """Пропуск выбора серии"""
    await state.update_data(series_id=None)
    
    # Переходим к планированию
    await state.set_state(PostCreationStates.schedule)
    await callback.message.edit_text(
        "📅 <b>Планирование публикации:</b>\n\n"
        "Выберите когда опубликовать пост:",
        reply_markup=get_schedule_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_now", StateFilter(PostCreationStates.schedule))
async def callback_schedule_now(callback: CallbackQuery, state: FSMContext):
    """Публикация сейчас"""
    await state.update_data(scheduled_at=None)
    await state.set_state(PostCreationStates.confirm)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ <b>Подтверждение публикации:</b>\n\n"
        f"📝 <b>Текст:</b>\n{post_text}\n\n"
        f"⏰ <b>Время:</b> Сейчас\n"
        f"🏷️ <b>Теги:</b> {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 <b>Серия:</b> {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "confirm_publish", StateFilter(PostCreationStates.confirm))
async def callback_confirm_publish(callback: CallbackQuery, state: FSMContext):
    """Подтверждение публикации"""
    data = await state.get_data()
    
    try:
        # TODO: Реализовать создание поста в БД
        # post_id = await post_service.create_post(...)
        
        await callback.message.edit_text(
            "✅ <b>Пост успешно создан!</b>\n\n"
            "Пост будет опубликован в ближайшее время."
        )
        
        # Сбрасываем состояние
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to create post: %s", e)
        await callback.message.edit_text(
            "❌ <b>Ошибка создания поста</b>\n\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )
    
    await callback.answer()

@router.callback_query(F.data == "cancel_publish", StateFilter(PostCreationStates.confirm))
async def callback_cancel_publish(callback: CallbackQuery, state: FSMContext):
    """Отмена публикации"""
    await state.clear()
    await callback.message.edit_text(
        "❌ <b>Создание поста отменено</b>\n\n"
        "Используйте /new_post для создания нового поста."
    )
    await callback.answer()

@router.callback_query(F.data == "publish_post", StateFilter(PostCreationStates.preview))
async def callback_publish_post(callback: CallbackQuery, state: FSMContext):
    """Простая публикация поста"""
    logger.info("=== НАЧАЛО ПУБЛИКАЦИИ ПОСТА ===")
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    logger.info(f"📝 Получен текст для публикации: '{post_text}'")
    
    try:
        # Получаем ID каналов из конфигурации
        from config import config
        channel_ids = getattr(config, 'CHANNEL_IDS', [])
        logger.info(f"📢 Настроенные каналы: {channel_ids}")
        
        if not channel_ids:
            logger.warning("❌ Каналы не настроены")
            await callback.message.edit_text(
                "❌ <b>Каналы не настроены</b>\n\n"
                "Сначала настройте каналы для публикации:\n"
                "1. Перейдите в админ-панель\n"
                "2. Нажмите '🔗 Получить ID канала'\n"
                "3. Перешлите сообщение из канала",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
                ])
            )
            await callback.answer()
            return
        
        # Публикуем пост во все настроенные каналы
        published_channels = []
        failed_channels = []
        
        for channel_id in channel_ids:
            try:
                logger.info(f"📤 Публикуем в канал {channel_id}")
                logger.info(f"📝 Текст: '{post_text}'")
                logger.info(f"🔧 parse_mode: 'MarkdownV2'")
                
                # Отправляем пост в канал с MarkdownV2 форматированием
                sent_message = await callback.bot.send_message(
                    chat_id=channel_id,
                    text=post_text,
                    parse_mode="MarkdownV2"
                )
                
                published_channels.append(channel_id)
                logger.info(f"✅ Пост успешно опубликован в канал {channel_id}")
                logger.info(f"📨 ID сообщения: {sent_message.message_id}")
                
            except Exception as e:
                failed_channels.append((channel_id, str(e)))
                logger.error(f"❌ Ошибка публикации в канал {channel_id}: {e}")
        
        # Формируем сообщение о результате
        if published_channels:
            result_text = f"✅ <b>Пост успешно опубликован!</b>\n\n"
            result_text += f"📝 <b>Текст:</b>\n{post_text}\n\n"
            result_text += f"📢 <b>Опубликовано в каналы:</b> {len(published_channels)}\n"
            
            if failed_channels:
                result_text += f"❌ <b>Ошибки:</b> {len(failed_channels)} каналов\n"
        else:
            result_text = "❌ <b>Не удалось опубликовать пост</b>\n\n"
            result_text += f"📝 <b>Текст:</b>\n{post_text}\n\n"
            result_text += "Проверьте права бота в каналах."
        
        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        )
        
        # TODO: Сохранить пост в БД
        # post_id = await post_service.create_post(...)
        
        # Сбрасываем состояние
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to publish post: %s", e)
        await callback.message.edit_text(
            "❌ <b>Ошибка публикации поста</b>\n\n"
            "Попробуйте еще раз или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        )
    
    await callback.answer()

@router.callback_query(F.data == "cancel_post")
async def callback_cancel_post(callback: CallbackQuery, state: FSMContext):
    """Отмена создания поста"""
    await state.clear()
    try:
        await callback.message.edit_text(
            "❌ <b>Создание поста отменено</b>\n\n"
            "Используйте кнопки ниже для навигации:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
            ])
        )
    except Exception as e:
        logger.warning("Failed to edit message in cancel_post: %s", e)
    await callback.answer()

@router.message(Command("my_posts"), admin_filter)
async def cmd_my_posts(message: Message):
    """Команда просмотра постов"""
    # TODO: Реализовать получение постов из БД
    await message.answer(
        "📋 <b>Мои посты</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет список ваших постов.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда помощи"""
    help_text = """
🤖 <b>CtrlBot - Помощь</b>

<b>Основные команды:</b>
/new_post - Создать новый пост
/my_posts - Мои посты
/help - Эта справка

<b>Для администраторов:</b>
/admin - Админ панель
/config - Настройки

<b>Markdown форматирование:</b>
*жирный* - жирный текст
_курсив_ - курсивный текст
`код` - моноширинный код
```блок кода``` - блок кода
[ссылка](url) - ссылка

<b>Поддержка:</b>
Если у вас есть вопросы, обратитесь к администратору.
    """
    
    await message.answer(
        help_text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )

@router.message(StateFilter(PostCreationStates.enter_text))
async def process_any_post_message(message: Message, state: FSMContext):
    """Простой обработчик для любых сообщений при создании поста"""
    logger.info("=== НАЧАЛО ОБРАБОТКИ СООБЩЕНИЯ ===")
    
    # Получаем текст из сообщения
    if message.text:
        text = message.text.strip()
        logger.info(f"📝 Получен текст: '{text}'")
    elif message.caption:
        text = message.caption.strip()
        logger.info(f"📝 Получен caption: '{text}'")
    else:
        logger.warning("❌ Сообщение не содержит текста")
        await message.answer("❌ <b>Не удалось получить текст</b>\n\nСообщение не содержит текста.")
        return
    
    # Валидация текста
    logger.info("🔍 Начинаем валидацию текста")
    is_valid, error_msg = await post_service.validate_post_text(text)
    if not is_valid:
        logger.warning(f"❌ Валидация не прошла: {error_msg}")
        await message.answer(f"❌ {error_msg}")
        return
    logger.info("✅ Валидация прошла успешно")
    
    # Конвертируем стандартный Markdown в Telegram Markdown
    logger.info("🔄 Начинаем конвертацию Markdown")
    logger.info(f"📥 Исходный текст: '{text}'")
    converted_text = convert_markdown_to_telegram(text)
    logger.info(f"📤 Конвертированный текст: '{converted_text}'")
    
    # Сохраняем конвертированный текст
    logger.info("💾 Сохраняем текст в FSM state")
    await state.update_data(post_text=converted_text)
    await state.set_state(PostCreationStates.preview)
    logger.info("✅ FSM state обновлен")
    
    # Показываем предпросмотр с MarkdownV2 форматированием
    logger.info("👁️ Отправляем предпросмотр с parse_mode='MarkdownV2'")
    try:
        # Экранируем HTML теги для MarkdownV2
        preview_text = f"👁️ *Предпросмотр поста:*\n\n{converted_text}"
        await message.answer(
            preview_text,
            parse_mode="MarkdownV2",
            reply_markup=get_post_actions_keyboard()
        )
        logger.info("✅ Предпросмотр отправлен успешно")
    except Exception as e:
        logger.error(f"❌ Ошибка при отправке предпросмотра: {e}")
        # Fallback без форматирования
        await message.answer(
            f"👁️ Предпросмотр поста:\n\n{converted_text}",
            reply_markup=get_post_actions_keyboard()
        )
        logger.info("✅ Предпросмотр отправлен без форматирования")
    
    logger.info("=== КОНЕЦ ОБРАБОТКИ СООБЩЕНИЯ ===")

@router.message()
async def handle_unknown(message: Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "❓ <b>Неизвестная команда</b>\n\n"
        "Используйте /help для просмотра доступных команд.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏠 Главное меню", callback_data="back_to_main")]
        ])
    )
