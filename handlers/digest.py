"""
@file: handlers/digest.py
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
    await message.answer(
        "📊 <b>Управление дайджестами</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет управление дайджестами.\n\n"
        "Планируемые функции:\n"
        "• Создание недельных дайджестов\n"
        "• Создание месячных дайджестов\n"
        "• Настройка автоматической отправки\n"
        "• Экспорт в Excel",
        reply_markup=get_main_menu_keyboard()
    )

@router.message(Command("export"), admin_filter)
async def cmd_export(message: Message):
    """Экспорт данных"""
    await message.answer(
        "📈 <b>Экспорт данных</b>\n\n"
        "Функция находится в разработке.\n"
        "Скоро здесь будет экспорт данных.\n\n"
        "Планируемые форматы:\n"
        "• Excel (.xlsx)\n"
        "• Markdown (.md)\n"
        "• CSV (.csv)",
        reply_markup=get_main_menu_keyboard()
    )
