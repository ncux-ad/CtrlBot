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
from utils.cron_parser import parse_cron_to_human
from database import db

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
        
        # Получаем все напоминания
        all_reminders = await reminder_service.get_all_reminders()
        
        # Формируем сообщение
        status_text = "🟢 Работает" if status else "🔴 Остановлен"
        
        reminders_text = ""
        if all_reminders:
            reminders_text = "\n\n*Активные напоминания:*\n"
            for reminder in all_reminders[:5]:  # Показываем только первые 5
                channel_title = reminder.get('channel_title', 'Неизвестный канал')
                schedule_cron = reminder.get('schedule_cron', 'Не указано')
                schedule_human = parse_cron_to_human(schedule_cron) if schedule_cron != 'Не указано' else 'Не указано'
                enabled = "✅" if reminder.get('enabled') else "❌"
                reminders_text += f"• {enabled} {channel_title}: {schedule_human}\n"
        else:
            reminders_text = "\n\n*Нет активных напоминаний*"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои напоминания", callback_data="my_reminders")],
            [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="reminder_settings")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
        
        await message.answer(
            f"⏰ *Управление напоминаниями*\n\n"
            f"*Статус планировщика:* {status_text}\n"
            f"*Всего напоминаний:* {len(all_reminders)}"
            f"{reminders_text}",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error("Failed to show reminders menu: %s", e)
        await message.answer(
            "❌ *Ошибка загрузки напоминаний*\n\n"
            "Попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_menu_keyboard()
        )

@router.callback_query(F.data == "my_reminders", admin_filter)
async def callback_my_reminders(callback: CallbackQuery):
    """Просмотр напоминаний пользователя"""
    try:
        reminders = await reminder_service.get_all_reminders()
        
        if not reminders:
            await callback.message.edit_text(
                "📋 *Все напоминания*\n\n"
                "Нет активных напоминаний.\n\n"
                "Создайте новое напоминание, используя кнопку ниже.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_reminders")]
                ])
            )
        else:
            reminders_text = "📋 *Все напоминания*\n\n"
            for i, reminder in enumerate(reminders, 1):
                channel_title = reminder.get('channel_title', 'Неизвестный канал')
                schedule_cron = reminder.get('schedule_cron', 'Не указано')
                schedule_human = parse_cron_to_human(schedule_cron) if schedule_cron != 'Не указано' else 'Не указано'
                enabled = "✅" if reminder.get('enabled') else "❌"
                reminders_text += f"{i}. {enabled} *{channel_title}*\n"
                reminders_text += f"   📅 {schedule_human}\n"
                reminders_text += f"   ⚙️ `{schedule_cron}`\n\n"
            
            # Создаем клавиатуру с кнопками удаления
            keyboard_buttons = []
            for i, reminder in enumerate(reminders[:10]):  # Максимум 10 напоминаний
                keyboard_buttons.append([
                    InlineKeyboardButton(
                        text=f"❌ Удалить {i+1}",
                        callback_data=f"delete_reminder_{reminder['id']}"
                    )
                ])
            
            keyboard_buttons.append([InlineKeyboardButton(text="🔙 Назад", callback_data="manage_reminders")])
            
            await callback.message.edit_text(
                reminders_text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons),
                parse_mode="Markdown"
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error("Failed to show user reminders: %s", e)
        await callback.answer("❌ Ошибка загрузки напоминаний", show_alert=True)

@router.callback_query(F.data == "create_reminder", admin_filter)
async def callback_create_reminder(callback: CallbackQuery):
    """Создание напоминания"""
    try:
        # Получаем список каналов для выбора
        channels = await reminder_service.get_available_channels()
        
        if not channels:
            await callback.message.edit_text(
                "❌ *Нет доступных каналов*\n\n"
                "Сначала добавьте канал в настройки бота.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_reminders")]
                ])
            )
        else:
            text = "➕ *Создание напоминания*\n\n"
            text += "Выберите канал для напоминания:\n\n"
            
            keyboard = []
            for channel in channels:
                keyboard.append([InlineKeyboardButton(
                    text=f"📢 {channel.get('title', 'Канал')}",
                    callback_data=f"select_channel_{channel['id']}"
                )])
            
            keyboard.append([InlineKeyboardButton(text="🔙 Назад", callback_data="manage_reminders")])
            
            await callback.message.edit_text(
                text,
                reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
            )
    except Exception as e:
        logger.error(f"Error in create_reminder: {e}")
        await callback.message.edit_text(
            "❌ *Ошибка создания напоминания*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_reminders")]
            ])
        )
    await callback.answer()

@router.callback_query(F.data == "reminder_settings", admin_filter)
async def callback_reminder_settings(callback: CallbackQuery):
    """Настройки напоминаний"""
    try:
        status = await reminder_service.get_scheduler_status()
        scheduler_info = await reminder_service.get_scheduler_info()
        
        await callback.message.edit_text(
            "⚙️ *Настройки напоминаний*\n\n"
            f"*Статус планировщика:* {'🟢 Работает' if status else '🔴 Остановлен'}\n"
            f"*Задач в очереди:* {scheduler_info['jobs_count']}\n\n"
            "*Стандартные напоминания:*\n"
            "• 12:00 - Ежедневное напоминание\n"
            "• 21:00 - Ежедневное напоминание\n\n"
            "Эти напоминания отправляются всем администраторам.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="manage_reminders")]
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
        
        success = await reminder_service.delete_reminder(reminder_id)
        
        if success:
            await callback.answer("✅ Напоминание удалено", show_alert=True)
            # Обновляем список напоминаний
            await callback_my_reminders(callback)
        else:
            await callback.answer("❌ Не удалось удалить напоминание", show_alert=True)
            
    except Exception as e:
        logger.error("Failed to delete reminder: %s", e)
        await callback.answer("❌ Ошибка удаления напоминания", show_alert=True)

@router.callback_query(F.data.startswith("select_channel_"), admin_filter)
async def callback_select_channel(callback: CallbackQuery):
    """Выбор канала для создания напоминания"""
    try:
        channel_id = int(callback.data.split("_")[-1])
        
        # Получаем информацию о канале
        channel = await db.fetch_one(
            "SELECT id, title, tg_channel_id FROM channels WHERE id = $1", 
            channel_id
        )
        
        if not channel:
            await callback.message.edit_text(
                "❌ *Канал не найден*\n\nПопробуйте выбрать другой канал.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
                ])
            )
            await callback.answer()
            return
        
        # Показываем форму создания напоминания
        await callback.message.edit_text(
            f"➕ *Создание напоминания*\n\n"
            f"📢 *Канал:* {channel['title']}\n\n"
            f"Выберите время напоминания:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🌅 12:00 (полдень)", callback_data=f"set_time_{channel_id}_12:00")],
                [InlineKeyboardButton(text="🌆 21:00 (вечер)", callback_data=f"set_time_{channel_id}_21:00")],
                [InlineKeyboardButton(text="⏰ Другое время", callback_data=f"custom_time_{channel_id}")],
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error("Error in callback_select_channel: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка выбора канала*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data.startswith("set_time_"), admin_filter)
async def callback_set_time(callback: CallbackQuery):
    """Установка времени напоминания"""
    try:
        # Парсим данные: set_time_{channel_id}_{time}
        parts = callback.data.split("_")
        channel_id = int(parts[2])
        time_str = parts[3]
        
        # Создаем напоминание
        cron_expression = f"0 {time_str.split(':')[1]} {time_str.split(':')[0]} * *"
        
        success = await reminder_service.create_reminder(
            channel_id=channel_id,
            kind="daily",
            schedule_cron=cron_expression,
            enabled=True
        )
        
        if success:
            await callback.message.edit_text(
                f"✅ *Напоминание создано*\n\n"
                f"⏰ *Время:* {time_str}\n"
                f"🔄 *Расписание:* Ежедневно\n\n"
                f"Напоминание будет отправляться каждый день в указанное время.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад к напоминаниям", callback_data="manage_reminders")]
                ])
            )
        else:
            await callback.message.edit_text(
                "❌ *Ошибка создания напоминания*\n\nПопробуйте позже.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
                ])
            )
        
        await callback.answer()
        
    except Exception as e:
        logger.error("Error in callback_set_time: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка установки времени*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data.startswith("custom_time_"), admin_filter)
async def callback_custom_time(callback: CallbackQuery):
    """Настройка пользовательского времени"""
    try:
        channel_id = int(callback.data.split("_")[-1])
        
        await callback.message.edit_text(
            "⏰ *Пользовательское время*\n\n"
            "Для создания напоминания с пользовательским временем отправьте сообщение в формате:\n\n"
            "`/create_reminder {channel_id} {cron_expression}`\n\n"
            "Примеры cron выражений:\n"
            "• `0 9 * * 1-5` - каждый будний день в 9:00\n"
            "• `0 18 * * 0` - каждое воскресенье в 18:00\n"
            "• `0 12 1 * *` - 1 числа каждого месяца в 12:00\n\n"
            f"ID канала: `{channel_id}`",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error("Error in callback_custom_time: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка настройки времени*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="create_reminder")]
            ])
        )
        await callback.answer()

@router.callback_query(F.data == "manage_reminders", admin_filter)
async def callback_manage_reminders(callback: CallbackQuery):
    """Главное меню напоминаний"""
    try:
        # Получаем статус планировщика
        status = await reminder_service.get_scheduler_status()
        
        # Получаем все напоминания
        all_reminders = await reminder_service.get_all_reminders()
        
        # Формируем сообщение
        status_text = "🟢 Работает" if status else "🔴 Остановлен"
        
        reminders_text = ""
        if all_reminders:
            reminders_text = "\n\n*Активные напоминания:*\n"
            for reminder in all_reminders[:5]:  # Показываем только первые 5
                channel_title = reminder.get('channel_title', 'Неизвестный канал')
                schedule_cron = reminder.get('schedule_cron', 'Не указано')
                schedule_human = parse_cron_to_human(schedule_cron) if schedule_cron != 'Не указано' else 'Не указано'
                enabled = "✅" if reminder.get('enabled') else "❌"
                reminders_text += f"• {enabled} {channel_title}: {schedule_human}\n"
        else:
            reminders_text = "\n\n*Нет активных напоминаний*"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Мои напоминания", callback_data="my_reminders")],
            [InlineKeyboardButton(text="➕ Создать напоминание", callback_data="create_reminder")],
            [InlineKeyboardButton(text="⚙️ Настройки", callback_data="reminder_settings")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
        
        await callback.message.edit_text(
            f"⏰ *Управление напоминаниями*\n\n"
            f"*Статус планировщика:* {status_text}\n"
            f"*Всего напоминаний:* {len(all_reminders)}"
            f"{reminders_text}",
            reply_markup=keyboard,
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error("Error in callback_manage_reminders: %s", e)
        await callback.message.edit_text(
            "❌ *Ошибка загрузки напоминаний*\n\nПопробуйте позже.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
            ])
        )
    
    await callback.answer()

@router.callback_query(F.data == "back_to_admin", admin_filter)
async def callback_back_to_admin(callback: CallbackQuery):
    """Возврат в админ-панель"""
    await callback.message.edit_text(
        "👑 *Админ панель CtrlAI_Bot*\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()

@router.message(Command("ping"))
async def cmd_ping(message: Message):
    """Проверка работоспособности бота"""
    await message.answer(
        "🏓 *Pong!*\n\n"
        "Бот работает нормально.\n"
        f"Время ответа: < 1 секунды"
    )
