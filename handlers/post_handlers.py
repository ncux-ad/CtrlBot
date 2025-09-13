"""
@file: handlers/post_handlers.py
@description: Обработчики для создания и управления постами
@dependencies: services/post_service.py, utils/keyboards.py, utils/states.py
@created: 2025-09-13
"""

import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

# Удалены сложные импорты форматирования - используем KISS принцип

from services.post_service import post_service
from services.tags import tag_service
from services.series import series_service
from utils.keyboards import (
    get_main_menu_keyboard,
    get_post_actions_keyboard,
    get_tags_keyboard,
    get_series_keyboard,
    get_schedule_keyboard,
    get_confirmation_keyboard
)
from utils.timezone_utils import format_datetime
from utils.states import PostCreationStates
from utils.filters import IsConfigAdminFilter, PostTextFilter
from utils.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()
text_filter = PostTextFilter()

# Убраны функции парсинга - возвращаемся к простому созданию поста

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
        "📝 **Создание нового поста**\n\n"
        "Отправьте текст поста - любой текст, который хотите опубликовать.\n\n"
        "💡 *Поддерживается Markdown форматирование:*\n"
        "• *жирный* → **жирный**\n"
        "• _курсив_ → __курсив__\n"
        "• `код` → `код`\n"
        "• [ссылка](url) → [ссылка](url)\n\n"
        "✅ *Можно копировать из Obsidian, .md файлов и других редакторов!*",
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
        logger.info("🔄 Редактируем сообщение")
        await callback.message.edit_text(
            f"👁️ *Предпросмотр поста:*\n\n{post_text}",
            reply_markup=get_post_actions_keyboard()
        )
        logger.info("✅ Сообщение отредактировано успешно")
    except Exception as e:
        logger.warning(f"❌ Не удалось отредактировать сообщение: {e}")
        # Если не удалось отредактировать, отправляем новое сообщение
        logger.info("📤 Отправляем новое сообщение")
        await callback.message.answer(
            f"👁️ *Предпросмотр поста:*\n\n{post_text}",
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
📝 *Пример Markdown форматирования:*

*Это жирный текст*
_Это курсивный текст_
`Это моноширинный код`

```блок кода
function hello() {
    console.log("Привет!");
}
```

[Ссылка на сайт](https://example.com)

*Списки:*
• Первый пункт
• Второй пункт
• Третий пункт

*Нумерованный список:*
1. Первый
2. Второй  
3. Третий

*Цитата:*
> Это цитата
> может быть многострочной

*Эмодзи:* 😀 🚀 💡 📝 ✅ ❌
    """
    
    # Если есть сохраненный текст поста, показываем кнопку "Назад к посту"
    if post_text:
        keyboard = [[InlineKeyboardButton(text="🔙 Назад к посту", callback_data="back_to_preview")]]
    else:
        keyboard = [[InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]]
    
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
            "❌ *Текст поста не найден*\n\n"
            "Создайте новый пост командой /new_post",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
    else:
        await state.set_state(PostCreationStates.preview)
        await callback.message.answer(
            f"👁️ *Предпросмотр поста:*\n\n{post_text}",
            reply_markup=get_post_actions_keyboard()
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_admin")
async def callback_back_to_admin_from_example(callback: CallbackQuery, state: FSMContext):
    """Возврат в админ-панель из примера Markdown"""
    await state.clear()
    await callback.message.answer(
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
    await callback.answer()

@router.callback_query(F.data == "schedule_post", StateFilter(PostCreationStates.preview))
async def callback_schedule_post(callback: CallbackQuery, state: FSMContext):
    """Переход к планированию поста"""
    await state.set_state(PostCreationStates.schedule)
    await callback.message.edit_text(
        "📅 *Планирование публикации:*\n\n"
        "Выберите когда опубликовать пост:",
        reply_markup=get_schedule_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "add_tags", StateFilter(PostCreationStates.preview))
async def callback_add_tags(callback: CallbackQuery, state: FSMContext):
    """Переход к добавлению тегов"""
    try:
        # Получаем ID канала из конфигурации
        from config import config
        channel_ids = getattr(config, 'CHANNEL_IDS', [])
        
        if not channel_ids:
            await callback.answer("❌ Каналы не настроены!", show_alert=True)
            return
        
        # Получаем теги для первого канала
        channel_id = channel_ids[0]
        tags = await tag_service.get_tags_by_channel(channel_id)
        
        if not tags:
            await callback.message.edit_text(
                "🏷️ *Теги не найдены*\n\n"
                "Сначала создайте теги в админ-панели.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад к посту", callback_data="back_to_preview")]
                ])
            )
        else:
            await state.set_state(PostCreationStates.add_tags)
            await callback.message.edit_text(
                "🏷️ *Выберите теги для поста:*\n\n"
                "Отметьте нужные теги и нажмите 'Готово'",
                reply_markup=get_tags_keyboard(tags)
            )
        
    except Exception as e:
        logger.error(f"Ошибка при получении тегов: {e}")
        await callback.answer("❌ Ошибка загрузки тегов", show_alert=True)
    
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
    
    try:
        # Получаем ID канала из конфигурации
        from config import config
        channel_ids = getattr(config, 'CHANNEL_IDS', [])
        
        if not channel_ids:
            await callback.answer("❌ Каналы не настроены!", show_alert=True)
            return
        
        # Получаем серии для первого канала
        channel_id = channel_ids[0]
        series = await series_service.get_series_by_channel(channel_id)
        
        if not series:
            await callback.message.edit_text(
                "📚 *Серии не найдены*\n\n"
                "Сначала создайте серии в админ-панели.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад к посту", callback_data="back_to_preview")]
                ])
            )
        else:
            await callback.message.edit_text(
                "📚 *Выберите серию для поста:*\n\n"
                "Пост будет автоматически пронумерован в выбранной серии.",
                reply_markup=get_series_keyboard(series)
            )
        
    except Exception as e:
        logger.error(f"Ошибка при получении серий: {e}")
        await callback.answer("❌ Ошибка загрузки серий", show_alert=True)
    
    await callback.answer()

@router.callback_query(F.data.startswith("select_series_"), StateFilter(PostCreationStates.choose_series))
async def callback_select_series(callback: CallbackQuery, state: FSMContext):
    """Выбор серии"""
    series_id = int(callback.data.split("_")[2])
    await state.update_data(series_id=series_id)
    
    # Переходим к планированию
    await state.set_state(PostCreationStates.schedule)
    await callback.message.edit_text(
        "📅 *Планирование публикации:*\n\n"
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
        "📅 *Планирование публикации:*\n\n"
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
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* Сейчас\n"
        f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_hour", StateFilter(PostCreationStates.schedule))
async def callback_schedule_hour(callback: CallbackQuery, state: FSMContext):
    """Планирование через час"""
    from utils.timezone_utils import get_in_hours
    
    logger.info("⏰ Планирование через час")
    scheduled_at = get_in_hours(1)
    logger.info(f"📅 Запланировано на: {scheduled_at}")
    
    await state.update_data(scheduled_at=scheduled_at)
    await state.set_state(PostCreationStates.confirm)
    logger.info("✅ FSM состояние обновлено: confirm")
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* {format_datetime(scheduled_at)}\n"
        f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_tomorrow_morning", StateFilter(PostCreationStates.schedule))
async def callback_schedule_tomorrow_morning(callback: CallbackQuery, state: FSMContext):
    """Планирование на завтра утром"""
    from utils.timezone_utils import get_tomorrow_morning
    
    scheduled_at = get_tomorrow_morning(9, 0)
    await state.update_data(scheduled_at=scheduled_at)
    await state.set_state(PostCreationStates.confirm)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* {format_datetime(scheduled_at)}\n"
        f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_tomorrow_evening", StateFilter(PostCreationStates.schedule))
async def callback_schedule_tomorrow_evening(callback: CallbackQuery, state: FSMContext):
    """Планирование на завтра вечером"""
    from utils.timezone_utils import get_tomorrow_evening
    
    scheduled_at = get_tomorrow_evening(21, 0)
    await state.update_data(scheduled_at=scheduled_at)
    await state.set_state(PostCreationStates.confirm)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* {format_datetime(scheduled_at)}\n"
        f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_custom", StateFilter(PostCreationStates.schedule))
async def callback_schedule_custom(callback: CallbackQuery, state: FSMContext):
    """Планирование с указанием времени"""
    await state.set_state(PostCreationStates.enter_time)
    
    await callback.message.edit_text(
        "📅 *Укажите время публикации:*\n\n"
        "Отправьте время в формате:\n"
        "• `15:30` - сегодня в 15:30\n"
        "• `завтра 15:30` - завтра в 15:30\n"
        "• `25.12.2024 15:30` - конкретная дата\n\n"
        "Или нажмите 'Отменить' для возврата к выбору времени.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_schedule")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_schedule", StateFilter(PostCreationStates.schedule))
async def callback_cancel_schedule(callback: CallbackQuery, state: FSMContext):
    """Отмена планирования"""
    await state.set_state(PostCreationStates.preview)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"👁️ *Предпросмотр поста:*\n\n{post_text}",
        reply_markup=get_post_actions_keyboard()
    )
    await callback.answer()

@router.message(StateFilter(PostCreationStates.enter_time))
async def process_time_input(message: Message, state: FSMContext):
    """Обработка ввода времени"""
    from utils.timezone_utils import parse_time_input
    
    time_text = message.text.strip()
    
    try:
        scheduled_at = parse_time_input(time_text)
        
        if not scheduled_at:
            await message.answer(
                "❌ *Неверный формат времени!*\n\n"
                "Используйте один из форматов:\n"
                "• `15:30` - сегодня в 15:30\n"
                "• `завтра 15:30` - завтра в 15:30\n"
                "• `25.12.2024 15:30` - конкретная дата\n\n"
                "Попробуйте еще раз:",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_schedule")]
                ])
            )
            return
        
        # Сохраняем время и переходим к подтверждению
        await state.update_data(scheduled_at=scheduled_at)
        await state.set_state(PostCreationStates.confirm)
        
        data = await state.get_data()
        post_text = data.get('post_text', '')
        
        await message.answer(
            f"✅ *Подтверждение публикации:*\n\n"
            f"📝 *Текст:*\n{post_text}\n\n"
            f"⏰ *Время:* {format_datetime(scheduled_at)}\n"
            f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
            f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
            reply_markup=get_confirmation_keyboard("publish")
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга времени '{time_text}': {e}")
        await message.answer(
            "❌ *Ошибка обработки времени!*\n\n"
            "Попробуйте указать время в одном из форматов:\n"
            "• `15:30` - сегодня в 15:30\n"
            "• `завтра 15:30` - завтра в 15:30\n"
            "• `25.12.2024 15:30` - конкретная дата\n\n"
            "Попробуйте еще раз:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_schedule")]
            ])
        )

@router.callback_query(F.data == "confirm_publish", StateFilter(PostCreationStates.confirm))
async def callback_confirm_publish(callback: CallbackQuery, state: FSMContext):
    """Подтверждение публикации"""
    logger.info("=== НАЧАЛО СОЗДАНИЯ ПОСТА ===")
    
    data = await state.get_data()
    logger.info(f"📊 FSM данные: {data}")
    
    try:
        # Получаем данные из FSM
        post_text = data.get('post_text', '')
        selected_tags = data.get('selected_tags', [])
        series_id = data.get('series_id')
        scheduled_at = data.get('scheduled_at')
        entities = data.get('entities', [])
        
        logger.info(f"📝 Текст поста: '{post_text}'")
        logger.info(f"🏷️ Выбранные теги: {selected_tags}")
        logger.info(f"📚 ID серии: {series_id}")
        logger.info(f"⏰ Запланировано на: {scheduled_at}")
        logger.info(f"🎨 Entities: {len(entities) if entities else 0}")
        
        # Получаем ID канала из конфигурации
        from config import config
        channel_ids = getattr(config, 'CHANNEL_IDS', [])
        logger.info(f"📢 Настроенные каналы: {channel_ids}")
        
        if not channel_ids:
            await callback.message.edit_text(
                "❌ *Каналы не настроены*\n\n"
                "Сначала настройте каналы для публикации."
            )
            await callback.answer()
            return
        
        # Создаем пост в БД
        logger.info("💾 Создаем пост в базе данных")
        post_id = await post_service.create_post(
            tg_channel_id=channel_ids[0],  # Используем первый канал
            title=None,  # Пока без заголовка
            body_md=post_text,
            user_id=callback.from_user.id,
            series_id=series_id,
            scheduled_at=scheduled_at,
            tag_ids=selected_tags,
            entities=entities
        )
        logger.info(f"✅ Пост создан с ID: {post_id}")
        
        # Формируем сообщение о результате
        result_text = f"✅ *Пост успешно создан!*\n\n"
        result_text += f"📝 *ID поста:* {post_id}\n"
        result_text += f"📝 *Текст:* {post_text[:100]}{'...' if len(post_text) > 100 else ''}\n"
        
        if series_id:
            result_text += f"📚 *Серия:* {series_id}\n"
        
        if selected_tags:
            result_text += f"🏷️ *Теги:* {len(selected_tags)} шт.\n"
        
        if scheduled_at:
            result_text += f"📅 *Запланирован на:* {format_datetime(scheduled_at)}\n"
        else:
            result_text += f"📅 *Статус:* Черновик\n"
        
        # Создаем клавиатуру с действиями
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать новый пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")]
        ])
        
        await callback.message.edit_text(result_text, reply_markup=keyboard)
        
        # Сбрасываем состояние
        await state.clear()
        
    except Exception as e:
        logger.error("❌ Ошибка создания поста: %s", e)
        logger.error("📊 Данные FSM на момент ошибки: %s", data)
        await callback.message.edit_text(
            "❌ *Ошибка создания поста*\n\n"
            "Попробуйте еще раз или обратитесь к администратору."
        )
    
    await callback.answer()

@router.callback_query(F.data == "my_posts")
async def callback_my_posts(callback: CallbackQuery):
    """Просмотр постов пользователя"""
    try:
        logger.info(f"📋 Просмотр постов пользователя {callback.from_user.id}")
        
        # Получаем посты пользователя
        posts = await post_service.get_user_posts(callback.from_user.id, limit=10)
        
        if not posts:
            await callback.message.edit_text(
                "📋 *Мои посты*\n\n"
                "У вас пока нет постов.\n"
                "Создайте первый пост командой /new_post",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")]
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
        keyboard.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_my_posts: {e}")
        await callback.message.edit_text(
            f"❌ *Ошибка загрузки постов*\n\n{str(e)}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data == "load_more_posts")
async def callback_load_more_posts(callback: CallbackQuery):
    """Загрузка дополнительных постов"""
    try:
        logger.info(f"📄 Загрузка дополнительных постов для пользователя {callback.from_user.id}")
        
        # Получаем offset из FSM или используем 10 по умолчанию
        data = await callback.message.get_state()
        offset = 10  # Пока простое решение
        
        # Получаем посты пользователя
        posts = await post_service.get_user_posts(callback.from_user.id, limit=10, offset=offset)
        
        if not posts:
            await callback.answer("📭 Больше постов нет", show_alert=True)
            return
        
        # Формируем список постов
        text = "📋 *Мои посты (продолжение)*\n\n"
        
        for i, post in enumerate(posts, offset + 1):
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
        keyboard.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Error in callback_load_more_posts: {e}")
        await callback.answer("❌ Ошибка загрузки постов", show_alert=True)

@router.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await state.clear()
    await callback.message.edit_text(
        "🏠 *Главное меню*\n\n"
        "Выберите действие:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post")],
            [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "cancel_publish", StateFilter(PostCreationStates.confirm))
async def callback_cancel_publish(callback: CallbackQuery, state: FSMContext):
    """Отмена публикации"""
    await state.clear()
    await callback.message.edit_text(
        "❌ *Создание поста отменено*\n\n"
        "Используйте /new_post для создания нового поста."
    )
    await callback.answer()

@router.callback_query(F.data == "post_advanced")
async def callback_post_advanced(callback: CallbackQuery, state: FSMContext):
    """Дополнительные действия с постом"""
    from utils.keyboards import get_post_advanced_keyboard
    
    try:
        await callback.message.edit_text(
            "⚙️ *Дополнительные действия*\n\n"
            "Выберите дополнительное действие:",
            reply_markup=get_post_advanced_keyboard()
        )
    except Exception as e:
        logger.warning("Failed to edit message in post_advanced: %s", e)
    await callback.answer()

@router.callback_query(F.data == "back_to_post")
async def callback_back_to_post(callback: CallbackQuery, state: FSMContext):
    """Возврат к основному меню поста"""
    from utils.keyboards import get_post_actions_keyboard
    
    try:
        await callback.message.edit_text(
            "📝 **Создание нового поста**\n\n"
            "Отправьте текст поста в формате Markdown.\n"
            "Можно использовать *жирный*, _курсив_, `код` и другие элементы.",
            reply_markup=get_post_actions_keyboard()
        )
    except Exception as e:
        logger.warning("Failed to edit message in back_to_post: %s", e)
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
                "❌ *Каналы не настроены*\n\n"
                "Сначала настройте каналы для публикации:\n"
                "1. Перейдите в админ-панель\n"
                "2. Нажмите '🔗 Получить ID канала'\n"
                "3. Перешлите сообщение из канала",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
            await callback.answer()
            return
        
        # Используем PostPublisher для публикации
        from services.publisher import get_publisher
        
        # Получаем entities из FSM
        data = await state.get_data()
        entities = data.get('entities', [])
        
        post_data = {
            'id': None,  # Для простой публикации ID не нужен
            'body_md': post_text,
            'entities': entities
        }
        
        publisher = get_publisher()
        results = await publisher.publish_post(post_data, channel_ids, update_db=False)
        
        published_channels = [result['channel_id'] for result in results['success']]
        failed_channels = [(result['channel_id'], result['error']) for result in results['failed']]
        
        # Формируем сообщение о результате
        if published_channels:
            result_text = f"✅ *Пост успешно опубликован!*\n\n"
            result_text += f"📝 *Текст:*\n{post_text}\n\n"
            result_text += f"📢 *Опубликовано в каналы:* {len(published_channels)}\n"
            
            if failed_channels:
                result_text += f"❌ *Ошибки:* {len(failed_channels)} каналов\n"
        else:
            result_text = "❌ *Не удалось опубликовать пост*\n\n"
            result_text += f"📝 *Текст:*\n{post_text}\n\n"
            result_text += "Проверьте права бота в каналах."
        
        await callback.message.edit_text(
            result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
        
        # TODO: Сохранить пост в БД
        # post_id = await post_service.create_post(...)
        
        # Сбрасываем состояние
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to publish post: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка публикации поста*\n\n"
            "Попробуйте еще раз или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
    
    await callback.answer()

@router.callback_query(F.data == "cancel_post")
async def callback_cancel_post(callback: CallbackQuery, state: FSMContext):
    """Отмена создания поста"""
    await state.clear()
    try:
        await callback.message.edit_text(
            "❌ *Создание поста отменено*\n\n"
            "Используйте кнопки ниже для навигации:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
    except Exception as e:
        logger.warning("Failed to edit message in cancel_post: %s", e)
    await callback.answer()

@router.message(Command("my_posts"), admin_filter)
async def cmd_my_posts(message: Message):
    """Команда просмотра постов"""
    try:
        # Получаем посты пользователя
        posts = await post_service.get_user_posts(message.from_user.id, limit=10)
        
        if not posts:
            await message.answer(
                "📋 *Мои посты*\n\n"
                "У вас пока нет постов.\n"
                "Создайте первый пост командой /new_post",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
                ])
            )
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
        keyboard.append([InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")])
        
        await message.answer(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        
    except Exception as e:
        logger.error(f"Ошибка при получении постов: {e}")
        await message.answer(
            "❌ *Ошибка загрузки постов*\n\n"
            "Попробуйте еще раз или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Команда помощи"""
    help_text = """
🤖 *CtrlBot - Помощь*

*Основные команды:*
/new_post - Создать новый пост
/my_posts - Мои посты
/help - Эта справка

*Для администраторов:*
/admin - Админ панель
/config - Настройки

*Markdown форматирование:*
*жирный* - жирный текст
_курсив_ - курсивный текст
`код` - моноширинный код
```блок кода``` - блок кода
[ссылка](url) - ссылка

*Поддержка:*
Если у вас есть вопросы, обратитесь к администратору.
    """
    
    await message.answer(
        help_text, 
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(StateFilter(PostCreationStates.enter_text))
async def process_any_post_message(message: Message, state: FSMContext):
    """Обработчик для создания поста с извлечением entities"""
    logger.info("=== НАЧАЛО ОБРАБОТКИ СООБЩЕНИЯ ===")
    
    # Получаем текст из сообщения
    if message.text:
        text = message.text.strip()
        entities = message.entities
        logger.info(f"📝 Получен текст: '{text}'")
        logger.info(f"📏 Длина текста: {len(text)} символов")
        logger.info(f"🎨 Entities: {len(entities) if entities else 0}")
    elif message.caption:
        text = message.caption.strip()
        entities = message.caption_entities
        logger.info(f"📝 Получен caption: '{text}'")
        logger.info(f"📏 Длина caption: {len(text)} символов")
        logger.info(f"🎨 Caption entities: {len(entities) if entities else 0}")
    else:
        logger.warning("❌ Сообщение не содержит текста")
        await message.answer("❌ *Не удалось получить текст*\n\nСообщение не содержит текста.")
        return
    
    # Валидация текста
    logger.info("🔍 Начинаем валидацию текста")
    is_valid, error_msg = await post_service.validate_post_text(text)
    if not is_valid:
        logger.warning(f"❌ Валидация не прошла: {error_msg}")
        await message.answer(f"❌ {error_msg}")
        return
    logger.info("✅ Валидация прошла успешно")
    
    # Сохраняем текст и entities
    logger.info("💾 Сохраняем текст и entities в FSM state")
    await state.update_data(post_text=text, entities=entities)
    await state.set_state(PostCreationStates.preview)
    logger.info("✅ FSM state обновлен")
    
    # Показываем простой предпросмотр
    logger.info("👁️ Отправляем предпросмотр")
    await message.answer(
        f"👁️ *Предпросмотр поста:*\n\n{text}",
        reply_markup=get_post_actions_keyboard()
    )
    logger.info("✅ Предпросмотр отправлен успешно")
    
    logger.info("=== КОНЕЦ ОБРАБОТКИ СООБЩЕНИЯ ===")

@router.message()
async def handle_unknown(message: Message):
    """Обработка неизвестных сообщений"""
    await message.answer(
        "❓ *Неизвестная команда*\n\n"
        "Используйте /help для просмотра доступных команд.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
    )
