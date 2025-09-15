# Utils: keyboards

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from typing import List

def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Админ-панель бота"""
    keyboard = [
        [KeyboardButton(text="📝 Новый пост"), KeyboardButton(text="📋 Мои посты")],
        [KeyboardButton(text="🤖 AI помощник"), KeyboardButton(text="⏰ Напоминания")],
        [KeyboardButton(text="🏷️ Теги"), KeyboardButton(text="📊 Серии")],
        [KeyboardButton(text="⚙️ Настройки"), KeyboardButton(text="📈 Статистика")]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_post_actions_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для действий с постом"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="publish_post")],
        [InlineKeyboardButton(text="📅 Запланировать", callback_data="schedule_post")],
        [InlineKeyboardButton(text="⚙️ Дополнительно", callback_data="post_advanced")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_post")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_post_advanced_keyboard() -> InlineKeyboardMarkup:
    """Расширенная клавиатура для дополнительных действий с постом"""
    keyboard = [
        [InlineKeyboardButton(text="👁️ Предпросмотр", callback_data="preview_post")],
        [InlineKeyboardButton(text="📝 Пример Markdown", callback_data="markdown_example")],
        [InlineKeyboardButton(text="🏷️ Добавить теги", callback_data="add_tags")],
        [InlineKeyboardButton(text="🔙 Назад к посту", callback_data="back_to_post")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_tags_keyboard(tags: List[dict], selected_tags: List[int] = None) -> InlineKeyboardMarkup:
    """Клавиатура для выбора тегов"""
    if selected_tags is None:
        selected_tags = []
    
    keyboard = []
    for tag in tags:
        tag_id = tag['id']
        tag_name = tag['name']
        is_selected = tag_id in selected_tags
        emoji = "✅" if is_selected else "⚪"
        keyboard.append([InlineKeyboardButton(
            text=f"{emoji} {tag_name}", 
            callback_data=f"toggle_tag_{tag_id}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="✅ Готово", callback_data="tags_done")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_series_keyboard(series: List[dict]) -> InlineKeyboardMarkup:
    """Клавиатура для выбора серии"""
    keyboard = []
    for s in series:
        keyboard.append([InlineKeyboardButton(
            text=f"📚 {s['title']} (#{s['next_number']})", 
            callback_data=f"select_series_{s['id']}"
        )])
    
    keyboard.append([InlineKeyboardButton(text="➕ Новая серия", callback_data="create_series")])
    keyboard.append([InlineKeyboardButton(text="⏭️ Пропустить", callback_data="skip_series")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_schedule_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для планирования публикации"""
    keyboard = [
        [InlineKeyboardButton(text="🚀 Сейчас", callback_data="schedule_now")],
        [InlineKeyboardButton(text="⏰ Через час", callback_data="schedule_hour")],
        [InlineKeyboardButton(text="📅 Завтра утром", callback_data="schedule_tomorrow_morning")],
        [InlineKeyboardButton(text="📅 Завтра вечером", callback_data="schedule_tomorrow_evening")],
        [InlineKeyboardButton(text="📝 Указать время", callback_data="schedule_custom")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_schedule")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для админских функций"""
    keyboard = [
        [InlineKeyboardButton(text="📢 Настройки канала", callback_data="channel_settings")],
        [InlineKeyboardButton(text="🏷️ Управление тегами", callback_data="manage_tags")],
        [InlineKeyboardButton(text="📚 Управление сериями", callback_data="manage_series")],
        [InlineKeyboardButton(text="⏰ Напоминания", callback_data="manage_reminders")],
        [InlineKeyboardButton(text="📊 Экспорт", callback_data="export_data")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_admin")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    keyboard = [
        [InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}")],
        [InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
