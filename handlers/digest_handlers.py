"""
@file: handlers/digest_handlers.py
@description: Обработчики дайджестов и экспорта
@dependencies: utils/keyboards.py, utils/filters.py
@created: 2025-09-13
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from utils.keyboards import get_main_menu_keyboard
from utils.filters import IsConfigAdminFilter
from utils.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()

@router.message(Command("digest"), admin_filter)
async def cmd_digest(message: Message):
    """Управление дайджестами"""
    try:
        from database import db
        
        # Получаем статистику постов за последние 7 дней
        stats_query = """
            SELECT 
                COUNT(*) as total_posts,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published_posts,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_posts,
                COUNT(CASE WHEN created_at >= NOW() - INTERVAL '7 days' THEN 1 END) as recent_posts
            FROM posts
        """
        stats = await db.fetch_one(stats_query)
        
        text = "📊 *Управление дайджестами*\n\n"
        text += f"📈 *Статистика за неделю:*\n"
        text += f"• Всего постов: {stats['total_posts']}\n"
        text += f"• Опубликовано: {stats['published_posts']}\n"
        text += f"• Запланировано: {stats['scheduled_posts']}\n"
        text += f"• За последние 7 дней: {stats['recent_posts']}\n\n"
        
        text += "🔧 *Доступные функции:*\n"
        text += "• Создание недельных дайджестов\n"
        text += "• Создание месячных дайджестов\n"
        text += "• Настройка автоматической отправки\n"
        text += "• Экспорт в Excel\n\n"
        
        text += "💡 *Использование:*\n"
        text += "Используйте админ-панель для настройки дайджестов"
        
        await message.answer(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.error("Error in cmd_digest: %s", e)
        await message.answer(
            "❌ *Ошибка загрузки статистики*\n\nПопробуйте позже",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="MarkdownV2"
        )

@router.message(Command("export"), admin_filter)
async def cmd_export(message: Message):
    """Экспорт данных"""
    try:
        from services.export import export_service
        
        # Получаем статистику для экспорта
        stats = await export_service.get_export_stats()
        
        text = "📈 *Экспорт данных*\n\n"
        text += f"📊 *Статистика:*\n"
        text += f"• Всего постов: {stats['total_posts']}\n"
        text += f"• Опубликовано: {stats['published_posts']}\n"
        text += f"• Запланировано: {stats['scheduled_posts']}\n"
        text += f"• Черновики: {stats['draft_posts']}\n"
        text += f"• Ошибки: {stats['failed_posts']}\n\n"
        
        if stats['channels']:
            text += "📺 *Каналы:*\n"
            for channel in stats['channels'][:3]:  # Показываем первые 3 канала
                text += f"• {channel['title']}: {channel['posts_count']} постов\n"
            if len(stats['channels']) > 3:
                text += f"... и еще {len(stats['channels']) - 3} каналов\n"
        
        text += "\n🔧 *Доступные форматы:*\n"
        text += "• JSON (.json)\n"
        text += "• Markdown (.md)\n"
        text += "• Excel (.xlsx) - в разработке\n"
        text += "• CSV (.csv) - в разработке\n\n"
        
        text += "💡 *Использование:*\n"
        text += "Используйте админ-панель для экспорта данных"
        
        await message.answer(
            text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="MarkdownV2"
        )
    except Exception as e:
        logger.error("Error in cmd_export: %s", e)
        await message.answer(
            "❌ *Ошибка загрузки статистики*\n\nПопробуйте позже",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="MarkdownV2"
        )
