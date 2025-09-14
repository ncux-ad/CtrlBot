"""
@file: handlers/posts.py
@description: Обработчики для создания и управления постами
@dependencies: services/posts.py, utils/keyboards.py, utils/states.py
@created: 2025-09-13
"""

import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, ParseMode
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

# Удалены сложные импорты форматирования - используем KISS принцип

from services.posts import post_service
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
        "📝 *Создание нового поста*\n\n"
        "Отправьте текст поста в формате Markdown\\.\n"
        "Можно использовать *жирный*, _курсив_, `код` и другие\n"
        "элементы.\n\n"
        "👇👇👇\n"
        "*В поле ввода наберите пост*\n"
        "\\(желательно Ctrl\\+C и Ctrl\\+V для сохранения форматирования!\\)"
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
        keyboard = [[InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]]
    
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
                [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
        "👑 *Админ-панель*\n\n"
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
    from datetime import datetime, timedelta
    
    scheduled_at = datetime.now() + timedelta(hours=1)
    await state.update_data(scheduled_at=scheduled_at)
    await state.set_state(PostCreationStates.confirm)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* {scheduled_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_tomorrow_morning", StateFilter(PostCreationStates.schedule))
async def callback_schedule_tomorrow_morning(callback: CallbackQuery, state: FSMContext):
    """Планирование на завтра утром"""
    from datetime import datetime, timedelta
    
    tomorrow = datetime.now() + timedelta(days=1)
    scheduled_at = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    await state.update_data(scheduled_at=scheduled_at)
    await state.set_state(PostCreationStates.confirm)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* {scheduled_at.strftime('%d.%m.%Y %H:%M')}\n"
        f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
        f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
        reply_markup=get_confirmation_keyboard("publish")
    )
    await callback.answer()

@router.callback_query(F.data == "schedule_tomorrow_evening", StateFilter(PostCreationStates.schedule))
async def callback_schedule_tomorrow_evening(callback: CallbackQuery, state: FSMContext):
    """Планирование на завтра вечером"""
    from datetime import datetime, timedelta
    
    tomorrow = datetime.now() + timedelta(days=1)
    scheduled_at = tomorrow.replace(hour=21, minute=0, second=0, microsecond=0)
    await state.update_data(scheduled_at=scheduled_at)
    await state.set_state(PostCreationStates.confirm)
    
    data = await state.get_data()
    post_text = data.get('post_text', '')
    
    await callback.message.edit_text(
        f"✅ *Подтверждение публикации:*\n\n"
        f"📝 *Текст:*\n{post_text}\n\n"
        f"⏰ *Время:* {scheduled_at.strftime('%d.%m.%Y %H:%M')}\n"
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
    from datetime import datetime, timedelta
    import re
    
    time_text = message.text.strip().lower()
    
    try:
        scheduled_at = None
        
        # Парсим различные форматы времени
        if re.match(r'^\d{1,2}:\d{2}$', time_text):
            # Формат: 15:30
            hour, minute = map(int, time_text.split(':'))
            today = datetime.now()
            scheduled_at = today.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Если время уже прошло сегодня, планируем на завтра
            if scheduled_at <= datetime.now():
                scheduled_at += timedelta(days=1)
                
        elif time_text.startswith('завтра'):
            # Формат: завтра 15:30
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_text)
            if time_match:
                hour, minute = map(int, time_match.groups())
                tomorrow = datetime.now() + timedelta(days=1)
                scheduled_at = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
            else:
                raise ValueError("Неверный формат времени")
                
        elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}\s+\d{1,2}:\d{2}$', time_text):
            # Формат: 25.12.2024 15:30
            date_time = datetime.strptime(time_text, '%d.%m.%Y %H:%M')
            scheduled_at = date_time
            
        else:
            raise ValueError("Неверный формат времени")
        
        # Проверяем, что время в будущем
        if scheduled_at <= datetime.now():
            await message.answer(
                "❌ *Время должно быть в будущем!*\n\n"
                "Попробуйте указать время заново:",
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
            f"⏰ *Время:* {scheduled_at.strftime('%d.%m.%Y %H:%M')}\n"
            f"🏷️ *Теги:* {len(data.get('selected_tags', []))} выбрано\n"
            f"📚 *Серия:* {'Да' if data.get('series_id') else 'Нет'}",
            reply_markup=get_confirmation_keyboard("publish")
        )
        
    except Exception as e:
        logger.error(f"Ошибка парсинга времени '{time_text}': {e}")
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

@router.callback_query(F.data == "confirm_publish", StateFilter(PostCreationStates.confirm))
async def callback_confirm_publish(callback: CallbackQuery, state: FSMContext):
    """Подтверждение публикации"""
    data = await state.get_data()
    
    try:
        # Получаем данные из FSM
        post_text = data.get('post_text', '')
        selected_tags = data.get('selected_tags', [])
        series_id = data.get('series_id')
        scheduled_at = data.get('scheduled_at')
        
        # Получаем ID канала из конфигурации
        from config import config
        channel_ids = getattr(config, 'CHANNEL_IDS', [])
        
        if not channel_ids:
            await callback.message.edit_text(
                "❌ *Каналы не настроены*\n\n"
                "Сначала настройте каналы для публикации."
            )
            await callback.answer()
            return
        
        # Создаем пост в БД
        post_id = await post_service.create_post(
            channel_id=channel_ids[0],  # Используем первый канал
            title=None,  # Пока без заголовка
            body_md=post_text,
            user_id=callback.from_user.id,
            series_id=series_id,
            scheduled_at=scheduled_at,
            tag_ids=selected_tags
        )
        
        # Формируем сообщение о результате
        result_text = f"✅ *Пост успешно создан!*\n\n"
        result_text += f"📝 *ID поста:* {post_id}\n"
        result_text += f"📝 *Текст:* {post_text[:100]}{'...' if len(post_text) > 100 else ''}\n"
        
        if series_id:
            result_text += f"📚 *Серия:* {series_id}\n"
        
        if selected_tags:
            result_text += f"🏷️ *Теги:* {len(selected_tags)} шт.\n"
        
        if scheduled_at:
            result_text += f"📅 *Запланирован на:* {scheduled_at.strftime('%d.%m.%Y %H:%M')}\n"
        else:
            result_text += f"📅 *Статус:* Черновик\n"
        
        await callback.message.edit_text(result_text)
        
        # Сбрасываем состояние
        await state.clear()
        
    except Exception as e:
        logger.error("Failed to create post: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка создания поста*\n\n"
            "Попробуйте еще раз или обратитесь к администратору."
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
                    [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
                
                # Отправляем пост в канал как есть
                sent_message = await callback.bot.send_message(
                    chat_id=channel_id,
                    text=post_text
                )

                
                published_channels.append(channel_id)
                logger.info(f"✅ Пост успешно опубликован в канал {channel_id}")
                logger.info(f"📨 ID сообщения: {sent_message.message_id}")
                
            except Exception as e:
                failed_channels.append((channel_id, str(e)))
                logger.error(f"❌ Ошибка публикации в канал {channel_id}: {e}")
        
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
                [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
                [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
                [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
                    [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
                text += f"   📅 {post['scheduled_at'].strftime('%d.%m.%Y %H:%M')}\n"
            
            text += f"   📅 {post['created_at'].strftime('%d.%m.%Y %H:%M')}\n\n"
        
        # Добавляем кнопки
        keyboard = []
        if len(posts) >= 10:
            keyboard.append([InlineKeyboardButton(text="📄 Показать еще", callback_data="load_more_posts")])
        keyboard.append([InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")])
        
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
                [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
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
            [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
        ])
    )

@router.message(StateFilter(PostCreationStates.enter_text))
async def process_any_post_message(message: Message, state: FSMContext):
    """Простой обработчик для создания поста - без парсинга"""
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
    
    # Сохраняем текст как есть
    logger.info("💾 Сохраняем текст в FSM state")
    await state.update_data(post_text=text)
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
            [InlineKeyboardButton(text="👑 Админ-панель", callback_data="back_to_admin")]
        ])
    )
