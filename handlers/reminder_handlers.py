"""
@file: handlers/reminder_handlers.py
@description: Обработчики напоминаний и уведомлений
@dependencies: services/reminder_service.py, utils/keyboards.py, utils/filters.py
@created: 2025-09-13
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from datetime import datetime, timedelta

from services.reminder_service import reminder_service
from utils.keyboards import get_main_menu_keyboard
from utils.filters import IsConfigAdminFilter
from utils.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()

@router.message(Command("reminders"), admin_filter)
async def cmd_reminders(message: Message):
    """Управление напоминаниями"""
    try:
        # Получаем статус планировщика
        status = await reminder_service.get_scheduler_status()
        
        # Получаем напоминания пользователя
        user_reminders = await reminder_service.get_user_reminders(message.from_user.id)
        
        # Формируем сообщение
        status_text = "🟢 Работает" if status["running"] else "🔴 Остановлен"
        jobs_text = f"Задач в очереди: {status['jobs_count']}"
        
        reminders_text = ""
        if user_reminders:
            reminders_text = "\n\n<b>Ваши напоминания:</b>\n"
            for reminder in user_reminders[:5]:  # Показываем только первые 5
                time_str = reminder['scheduled_time'].strftime("%d.%m.%Y %H:%M")
                reminders_text += f"• {time_str}: {reminder['message'][:50]}...\n"
        else:
            reminders_text = "\n\n<b>У вас нет активных напоминаний</b>"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои напоминания", callback_data="my_reminders")],
            [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="reminder_settings")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
        
        await message.answer(
            f"⏰ <b>Управление напоминаниями</b>\n\n"
            f"<b>Статус планировщика:</b> {status_text}\n"
            f"<b>{jobs_text}</b>"
            f"{reminders_text}",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error("Failed to show reminders menu: %s", e)
        await message.answer(
            "❌ <b>Ошибка загрузки напоминаний</b>\n\n"
            "Попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_menu_keyboard()
        )

@router.callback_query(F.data == "my_reminders", admin_filter)
async def callback_my_reminders(callback: CallbackQuery):
    """Просмотр напоминаний пользователя"""
    try:
        reminders = await reminder_service.get_user_reminders(callback.from_user.id)
        
        if not reminders:
            await callback.message.edit_text(
                "📋 <b>Мои напоминания</b>\n\n"
                "У вас нет активных напоминаний.\n\n"
                "Создайте новое напоминание, используя кнопку ниже.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="reminders")]
                ])
            )
        else:
            reminders_text = "📋 <b>Мои напоминания</b>\n\n"
            for i, reminder in enumerate(reminders, 1):
                time_str = reminder['scheduled_time'].strftime("%d.%m.%Y %H:%M")
                reminders_text += f"{i}. <b>{time_str}</b>\n"
                reminders_text += f"   {reminder['message']}\n\n"
            
            # Создаем клавиатуру с кнопками удаления
            keyboard_buttons = []
            for i, reminder in enumerate(reminders[:10]):  # Максимум 10 напоминаний
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"❌ Удалить {i+1}",
                        callback_data=f"delete_reminder_{reminder['id']}"
                    )
                ])
            
            keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="reminders")])
            
            await callback.message.edit_text(
                reminders_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error("Failed to show user reminders: %s", e)
        await callback.answer("❌ Ошибка загрузки напоминаний", show_alert=True)

@router.callback_query(F.data == "create_reminder", admin_filter)
async def callback_create_reminder(callback: CallbackQuery):
    """Создание напоминания"""
    await callback.message.edit_text(
        "➕ <b>Создание напоминания</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет создание напоминаний.\n\n"
        "Планируемые функции:\n"
        "• Выбор даты и времени\n"
        "• Ввод текста напоминания\n"
        "• Повторяющиеся напоминания\n"
        "• Напоминания по дням недели",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="reminders")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "reminder_settings", admin_filter)
async def callback_reminder_settings(callback: CallbackQuery):
    """Настройки напоминаний"""
    try:
        status = await reminder_service.get_scheduler_status()
        
        await callback.message.edit_text(
            "⚙️ <b>Настройки напоминаний</b>\n\n"
            f"<b>Статус планировщика:</b> {'🟢 Работает' if status['running'] else '🔴 Остановлен'}\n"
            f"<b>Задач в очереди:</b> {status['jobs_count']}\n\n"
            "<b>Стандартные напоминания:</b>\n"
            "• 12:00 - Ежедневное напоминание\n"
            "• 21:00 - Ежедневное напоминание\n\n"
            "Эти напоминания отправляются всем администраторам.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="reminders")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error("Failed to show reminder settings: %s", e)
        await callback.answer("❌ Ошибка загрузки настроек", show_alert=True)

@router.callback_query(F.data.startswith("delete_reminder_"), admin_filter)
async def callback_delete_reminder(callback: CallbackQuery):
    """Удаление напоминания"""
    try:
        reminder_id = int(callback.data.split("_")[2])
        
        success = await reminder_service.delete_reminder(reminder_id, callback.from_user.id)
        
        if success:
            await callback.answer("✅ Напоминание удалено", show_alert=True)
            # Обновляем список напоминаний
            await callback_my_reminders(callback)
        else:
            await callback.answer("❌ Не удалось удалить напоминание", show_alert=True)
            
    except Exception as e:
        logger.error("Failed to delete reminder: %s", e)
        await callback.answer("❌ Ошибка удаления напоминания", show_alert=True)

@router.callback_query(F.data == "back_to_admin", admin_filter)
async def callback_back_to_admin(callback: CallbackQuery):
    """Возврат в админ-панель"""
    await callback.message.edit_text(
        "👑 <b>Админ панель CtrlBot</b>\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@router.message(Command("ping"))
async def cmd_ping(message: Message):
    """Проверка работоспособности бота"""
    await message.answer(
        "🏓 <b>Pong!</b>\n\n"
        "Бот работает нормально.\n"
        f"Время ответа: < 1 секунды"
    )
