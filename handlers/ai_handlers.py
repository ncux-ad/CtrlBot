"""
@file: handlers/ai_handlers.py
@description: Обработчики AI функций (YandexGPT)
@dependencies: services/ai_service.py, utils/keyboards.py, utils/filters.py
@created: 2025-09-13
"""

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from services.ai_service import ai_service
from utils.keyboards import get_main_menu_keyboard
from utils.filters import IsConfigAdminFilter
from utils.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()

@router.message(Command("ai"), admin_filter)
async def cmd_ai(message: Message):
    """Главное меню AI функций"""
    try:
        # Проверяем статус API
        status = await ai_service.check_api_status()
        
        status_emoji = "🟢" if status["status"] == "working" else "🔴"
        status_text = f"{status_emoji} {status['message']}"
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🏷️ Подсказки тегов", callback_data="ai_suggest_tags")],
            [InlineKeyboardButton(text="✂️ Сократить текст", callback_data="ai_shorten_text")],
            [InlineKeyboardButton(text="🎨 Изменить стиль", callback_data="ai_change_style")],
            [InlineKeyboardButton(text="📝 Улучшить текст", callback_data="ai_improve_text")],
            [InlineKeyboardButton(text="📄 Создать аннотацию", callback_data="ai_annotation")],
            [InlineKeyboardButton(text="🔧 Настройки AI", callback_data="ai_settings")],
            [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="back_to_admin")]
        ])
        
        await message.answer(
            f"🤖 *AI помощник CtrlBot*\n\n"
            f"*Статус:* {status_text}\n\n"
            f"Выберите функцию:",
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error("Failed to show AI menu: %s", e)
        await message.answer(
            "❌ *Ошибка загрузки AI функций*\n\n"
            "Попробуйте позже или обратитесь к администратору.",
            reply_markup=get_main_menu_keyboard()
        )

@router.callback_query(F.data == "ai_suggest_tags", admin_filter)
async def callback_ai_suggest_tags(callback: CallbackQuery):
    """Подсказки тегов"""
    await callback.message.edit_text(
        "🏷️ *Подсказки тегов*\n\n"
        "Отправьте текст поста, и я предложу релевантные теги.\n\n"
        "Просто напишите текст поста в следующем сообщении.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="ai")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "ai_shorten_text", admin_filter)
async def callback_ai_shorten_text(callback: CallbackQuery):
    """Сокращение текста"""
    await callback.message.edit_text(
        "✂️ *Сокращение текста*\n\n"
        "Отправьте текст, который нужно сократить.\n\n"
        "Просто напишите текст в следующем сообщении.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="ai")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "ai_change_style", admin_filter)
async def callback_ai_change_style(callback: CallbackQuery):
    """Изменение стиля текста"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📰 Официальный", callback_data="style_formal")],
        [InlineKeyboardButton(text="😊 Неформальный", callback_data="style_casual")],
        [InlineKeyboardButton(text="📺 Новостной", callback_data="style_news")],
        [InlineKeyboardButton(text="💼 Маркетинговый", callback_data="style_marketing")],
        [InlineKeyboardButton(text="🔧 Технический", callback_data="style_technical")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="ai")]
    ])
    
    await callback.message.edit_text(
        "🎨 *Изменение стиля текста*\n\n"
        "Выберите стиль для вашего текста:",
        reply_markup=keyboard
    )
    await callback.answer()

@router.callback_query(F.data == "ai_improve_text", admin_filter)
async def callback_ai_improve_text(callback: CallbackQuery):
    """Улучшение текста"""
    await callback.message.edit_text(
        "📝 *Улучшение текста*\n\n"
        "Отправьте текст для улучшения (исправление ошибок, улучшение стиля).\n\n"
        "Просто напишите текст в следующем сообщении.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="ai")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "ai_annotation", admin_filter)
async def callback_ai_annotation(callback: CallbackQuery):
    """Создание аннотации"""
    await callback.message.edit_text(
        "📄 *Создание аннотации*\n\n"
        "Отправьте текст поста, и я создам краткую аннотацию.\n\n"
        "Просто напишите текст в следующем сообщении.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="ai")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "ai_settings", admin_filter)
async def callback_ai_settings(callback: CallbackQuery):
    """Настройки AI"""
    try:
        status = await ai_service.check_api_status()
        
        await callback.message.edit_text(
            f"🔧 *Настройки AI*\n\n"
            f"*Статус API:* {status['message']}\n\n"
            f"*Доступные функции:*\n"
            f"• Подсказки тегов\n"
            f"• Сокращение текста\n"
            f"• Изменение стиля\n"
            f"• Улучшение текста\n"
            f"• Создание аннотаций\n\n"
            f"*Настройка:*\n"
            f"• YANDEX_API_KEY: {'✅ Настроен' if ai_service.api_key else '❌ Не настроен'}\n"
            f"• YANDEX_FOLDER_ID: {'✅ Настроен' if ai_service.folder_id else '❌ Не настроен'}",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 Назад", callback_data="ai")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error("Failed to show AI settings: %s", e)
        await callback.answer("❌ Ошибка загрузки настроек", show_alert=True)

@router.callback_query(F.data.startswith("style_"), admin_filter)
async def callback_style_selected(callback: CallbackQuery):
    """Выбран стиль для изменения текста"""
    style = callback.data.split("_")[1]
    style_names = {
        "formal": "официальный",
        "casual": "неформальный", 
        "news": "новостной",
        "marketing": "маркетинговый",
        "technical": "технический"
    }
    
    await callback.message.edit_text(
        f"🎨 *Изменение стиля на {style_names.get(style, style)}*\n\n"
        f"Отправьте текст, который нужно переписать в {style_names.get(style, style)} стиле.\n\n"
        f"Просто напишите текст в следующем сообщении.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Назад", callback_data="ai_change_style")]
        ])
    )
    await callback.answer()

@router.message(admin_filter)
async def handle_ai_text_processing(message: Message):
    """Обработка текста для AI функций"""
    try:
        text = message.text.strip()
        if not text or len(text) < 10:
            await message.answer("❌ Текст слишком короткий. Минимум 10 символов.")
            return
        
        # Простая эвристика для определения типа запроса
        # В реальном приложении это должно быть через FSM состояния
        
        # Если текст содержит ключевые слова для тегов
        if any(word in text.lower() for word in ["теги", "тег", "метки", "категории"]):
            await process_tag_suggestion(message, text)
        # Если текст очень длинный - предлагаем сократить
        elif len(text) > 500:
            await process_text_shortening(message, text)
        # Иначе - улучшаем текст
        else:
            await process_text_improvement(message, text)
            
    except Exception as e:
        logger.error("Failed to process AI text: %s", e)
        await message.answer("❌ Ошибка обработки текста. Попробуйте еще раз.")

async def process_tag_suggestion(message: Message, text: str):
    """Обработка запроса на подсказки тегов"""
    try:
        await message.answer("🤖 Анализирую текст и предлагаю теги...")
        
        tags = await ai_service.suggest_tags(text)
        
        if tags:
            tags_text = ", ".join([f"#{tag}" for tag in tags])
            await message.answer(
                f"🏷️ *Предлагаемые теги:*\n\n{tags_text}\n\n"
                f"Используйте эти теги для вашего поста!"
            )
        else:
            await message.answer("❌ Не удалось предложить теги. Проверьте настройки AI.")
            
    except Exception as e:
        logger.error("Failed to process tag suggestion: %s", e)
        await message.answer("❌ Ошибка при предложении тегов.")

async def process_text_shortening(message: Message, text: str):
    """Обработка запроса на сокращение текста"""
    try:
        await message.answer("✂️ Сокращаю текст...")
        
        shortened = await ai_service.shorten_text(text, max_length=200)
        
        await message.answer(
            f"✂️ *Сокращенный текст:*\n\n{shortened}\n\n"
            f"*Исходная длина:* {len(text)} символов\n"
            f"*Новая длина:* {len(shortened)} символов"
        )
        
    except Exception as e:
        logger.error("Failed to process text shortening: %s", e)
        await message.answer("❌ Ошибка при сокращении текста.")

async def process_text_improvement(message: Message, text: str):
    """Обработка запроса на улучшение текста"""
    try:
        await message.answer("📝 Улучшаю текст...")
        
        improved = await ai_service.improve_text(text)
        
        await message.answer(
            f"📝 *Улучшенный текст:*\n\n{improved}\n\n"
            f"*Исходный текст:*\n{text}"
        )
        
    except Exception as e:
        logger.error("Failed to process text improvement: %s", e)
        await message.answer("❌ Ошибка при улучшении текста.")

@router.callback_query(F.data == "back_to_admin", admin_filter)
async def callback_back_to_admin(callback: CallbackQuery):
    """Возврат в админ-панель"""
    await callback.message.edit_text(
        "👑 *Админ панель CtrlBot*\n\n"
        "Выберите действие:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
