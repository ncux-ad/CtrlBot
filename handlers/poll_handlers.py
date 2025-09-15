# Handlers: Poll Creation
# Обработчики для создания опросов

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.enums import ParseMode

from utils.states import PollCreationStates
from utils.logging import get_logger
from services.publisher import publisher
from database import db

logger = get_logger(__name__)
router = Router()

@router.message(PollCreationStates.enter_question)
async def process_poll_question(message: Message, state: FSMContext):
    """Обработка ввода вопроса опроса"""
    question = message.text.strip()
    
    if not question:
        await message.answer("❌ Вопрос не может быть пустым. Попробуйте еще раз:")
        return
    
    if len(question) > 300:
        await message.answer("❌ Вопрос слишком длинный (максимум 300 символов). Попробуйте еще раз:")
        return
    
    # Сохраняем вопрос
    await state.update_data(question=question)
    
    # Переходим к вводу вариантов ответов
    await state.set_state(PollCreationStates.enter_options)
    await message.answer(
        "📋 **Введите варианты ответов**\n\n"
        "Отправьте варианты ответов, каждый с новой строки:\n\n"
        "Пример:\n"
        "Python\n"
        "JavaScript\n"
        "Java\n"
        "C++\n\n"
        "Минимум 2 варианта, максимум 10.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )

@router.message(PollCreationStates.enter_options)
async def process_poll_options(message: Message, state: FSMContext):
    """Обработка ввода вариантов ответов"""
    options_text = message.text.strip()
    
    if not options_text:
        await message.answer("❌ Варианты ответов не могут быть пустыми. Попробуйте еще раз:")
        return
    
    # Разбиваем на варианты
    options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
    
    if len(options) < 2:
        await message.answer("❌ Минимум 2 варианта ответа. Попробуйте еще раз:")
        return
    
    if len(options) > 10:
        await message.answer("❌ Максимум 10 вариантов ответа. Попробуйте еще раз:")
        return
    
    # Проверяем длину каждого варианта
    for i, option in enumerate(options):
        if len(option) > 100:
            await message.answer(f"❌ Вариант {i+1} слишком длинный (максимум 100 символов). Попробуйте еще раз:")
            return
    
    # Сохраняем варианты
    await state.update_data(options=options)
    
    # Переходим к настройкам опроса
    await state.set_state(PollCreationStates.poll_settings)
    await message.answer(
        "⚙️ **Настройки опроса**\n\n"
        "Выберите тип опроса:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📊 Обычный опрос", callback_data="poll_type_regular")],
            [InlineKeyboardButton(text="🧠 Викторина", callback_data="poll_type_quiz")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )

@router.callback_query(F.data.startswith("poll_type_"), PollCreationStates.poll_settings)
async def callback_poll_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа опроса"""
    poll_type = callback.data.split("_")[2]  # regular или quiz
    
    await state.update_data(poll_type=poll_type)
    
    if poll_type == "quiz":
        # Для викторины нужно выбрать правильный ответ
        data = await state.get_data()
        options = data.get('options', [])
        
        keyboard = []
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(
                text=f"✅ {option}" if i == 0 else option,
                callback_data=f"correct_option_{i}"
            )])
        keyboard.append([InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")])
        
        await callback.message.edit_text(
            "🎯 **Выберите правильный ответ**\n\n"
            "Отметьте правильный вариант для викторины:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
    else:
        # Обычный опрос - переходим к дополнительным настройкам
        await callback.message.edit_text(
            "⚙️ **Дополнительные настройки**\n\n"
            "Выберите дополнительные опции:",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔒 Анонимный опрос", callback_data="poll_anonymous_true")],
                [InlineKeyboardButton(text="👤 Публичный опрос", callback_data="poll_anonymous_false")],
                [InlineKeyboardButton(text="📝 Один ответ", callback_data="poll_multiple_false")],
                [InlineKeyboardButton(text="📝 Несколько ответов", callback_data="poll_multiple_true")],
                [InlineKeyboardButton(text="✅ Готово", callback_data="poll_preview")],
                [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
            ])
        )
    
    await callback.answer()

@router.callback_query(F.data.startswith("correct_option_"), PollCreationStates.poll_settings)
async def callback_correct_option(callback: CallbackQuery, state: FSMContext):
    """Выбор правильного ответа для викторины"""
    option_index = int(callback.data.split("_")[2])
    
    await state.update_data(correct_option_id=option_index)
    
    # Переходим к дополнительным настройкам
    await callback.message.edit_text(
        "⚙️ **Дополнительные настройки**\n\n"
        "Выберите дополнительные опции:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔒 Анонимный опрос", callback_data="poll_anonymous_true")],
            [InlineKeyboardButton(text="👤 Публичный опрос", callback_data="poll_anonymous_false")],
            [InlineKeyboardButton(text="✅ Готово", callback_data="poll_preview")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data.startswith("poll_"), PollCreationStates.poll_settings)
async def callback_poll_settings(callback: CallbackQuery, state: FSMContext):
    """Обработка настроек опроса"""
    setting = callback.data.split("_")[1]  # anonymous, multiple, preview
    value = callback.data.split("_")[2]    # true, false, или пусто для preview
    
    if setting == "anonymous":
        await state.update_data(is_anonymous=value == "true")
    elif setting == "multiple":
        await state.update_data(allows_multiple_answers=value == "true")
    elif setting == "preview":
        # Переходим к предпросмотру
        await state.set_state(PollCreationStates.preview)
        await callback_poll_preview(callback, state)
        return
    
    # Обновляем кнопки
    data = await state.get_data()
    is_anonymous = data.get('is_anonymous', True)
    allows_multiple = data.get('allows_multiple_answers', False)
    
    await callback.message.edit_text(
        "⚙️ **Дополнительные настройки**\n\n"
        f"🔒 Анонимный: {'✅' if is_anonymous else '❌'}\n"
        f"📝 Несколько ответов: {'✅' if allows_multiple else '❌'}\n\n"
        "Выберите дополнительные опции:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔒 Анонимный опрос", callback_data="poll_anonymous_true")],
            [InlineKeyboardButton(text="👤 Публичный опрос", callback_data="poll_anonymous_false")],
            [InlineKeyboardButton(text="📝 Один ответ", callback_data="poll_multiple_false")],
            [InlineKeyboardButton(text="📝 Несколько ответов", callback_data="poll_multiple_true")],
            [InlineKeyboardButton(text="✅ Готово", callback_data="poll_preview")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "poll_preview", PollCreationStates.preview)
async def callback_poll_preview(callback: CallbackQuery, state: FSMContext):
    """Предпросмотр опроса"""
    data = await state.get_data()
    
    question = data.get('question', '')
    options = data.get('options', [])
    poll_type = data.get('poll_type', 'regular')
    is_anonymous = data.get('is_anonymous', True)
    allows_multiple = data.get('allows_multiple_answers', False)
    correct_option_id = data.get('correct_option_id')
    
    # Формируем текст предпросмотра
    preview_text = f"📊 **Предпросмотр опроса**\n\n"
    preview_text += f"❓ **Вопрос:** {question}\n\n"
    preview_text += f"📋 **Варианты ответов:**\n"
    for i, option in enumerate(options):
        if poll_type == "quiz" and i == correct_option_id:
            preview_text += f"✅ {option}\n"
        else:
            preview_text += f"• {option}\n"
    
    preview_text += f"\n⚙️ **Настройки:**\n"
    preview_text += f"• Тип: {'Викторина' if poll_type == 'quiz' else 'Обычный опрос'}\n"
    preview_text += f"• Анонимный: {'Да' if is_anonymous else 'Нет'}\n"
    if poll_type == "regular":
        preview_text += f"• Несколько ответов: {'Да' if allows_multiple else 'Нет'}\n"
    
    await callback.message.edit_text(
        preview_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📅 Запланировать", callback_data="poll_schedule")],
            [InlineKeyboardButton(text="🚀 Опубликовать сейчас", callback_data="poll_publish_now")],
            [InlineKeyboardButton(text="✏️ Изменить", callback_data="poll_edit")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "poll_publish_now", PollCreationStates.preview)
async def callback_poll_publish_now(callback: CallbackQuery, state: FSMContext):
    """Публикация опроса сейчас"""
    data = await state.get_data()
    
    # Получаем каналы
    channels = await db.fetch_all("SELECT id, tg_channel_id, title FROM channels")
    
    if not channels:
        await callback.answer("❌ Нет доступных каналов!")
        return
    
    # Публикуем в первый канал (можно расширить для выбора)
    channel = channels[0]
    channel_id = channel['tg_channel_id']
    
    try:
        # Публикуем опрос
        message = await publisher.publish_poll(
            chat_id=channel_id,
            question=data.get('question', ''),
            options=data.get('options', []),
            is_anonymous=data.get('is_anonymous', True),
            type=data.get('poll_type', 'regular'),
            allows_multiple_answers=data.get('allows_multiple_answers', False),
            correct_option_id=data.get('correct_option_id'),
        )
        
        if message:
            await callback.message.edit_text(
                "✅ **Опрос опубликован!**\n\n"
                f"📺 Канал: {channel['title']}\n"
                f"📊 ID сообщения: {message.message_id}",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
                ])
            )
            await callback.answer("✅ Опрос опубликован!")
        else:
            await callback.message.edit_text(
                "❌ **Ошибка публикации опроса**\n\n"
                "Попробуйте позже или обратитесь к администратору.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
                ])
            )
            await callback.answer("❌ Ошибка публикации!")
    
    except Exception as e:
        logger.error(f"Error publishing poll: {e}")
        await callback.message.edit_text(
            "❌ **Ошибка публикации опроса**\n\n"
            "Попробуйте позже или обратитесь к администратору.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
            ])
        )
        await callback.answer("❌ Ошибка публикации!")
    
    # Очищаем состояние
    await state.clear()

@router.callback_query(F.data == "poll_edit", PollCreationStates.preview)
async def callback_poll_edit(callback: CallbackQuery, state: FSMContext):
    """Редактирование опроса"""
    await state.set_state(PollCreationStates.enter_question)
    await callback.message.edit_text(
        "✏️ **Редактирование опроса**\n\n"
        "Отправьте новый вопрос для опроса:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )
    await callback.answer()

@router.callback_query(F.data == "poll_schedule", PollCreationStates.preview)
async def callback_poll_schedule(callback: CallbackQuery, state: FSMContext):
    """Планирование опроса"""
    await state.set_state(PollCreationStates.schedule)
    await callback.message.edit_text(
        "📅 **Планирование опроса**\n\n"
        "Выберите время публикации:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="⏰ Через час", callback_data="poll_schedule_hour")],
            [InlineKeyboardButton(text="🌅 Завтра утром (09:00)", callback_data="poll_schedule_tomorrow_morning")],
            [InlineKeyboardButton(text="🌆 Завтра вечером (21:00)", callback_data="poll_schedule_tomorrow_evening")],
            [InlineKeyboardButton(text="📅 Выбрать время", callback_data="poll_schedule_custom")],
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )
    await callback.answer()

# Обработчики планирования (упрощенные версии)
@router.callback_query(F.data == "poll_schedule_hour", PollCreationStates.schedule)
async def callback_poll_schedule_hour(callback: CallbackQuery, state: FSMContext):
    """Планирование на час вперед"""
    from datetime import datetime, timedelta
    
    scheduled_time = datetime.now() + timedelta(hours=1)
    await state.update_data(scheduled_at=scheduled_time)
    
    await callback.message.edit_text(
        f"⏰ **Опрос запланирован на {scheduled_time.strftime('%d.%m.%Y %H:%M')}**\n\n"
        "Опрос будет опубликован автоматически в указанное время.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
        ])
    )
    await callback.answer("✅ Опрос запланирован!")
    await state.clear()

@router.callback_query(F.data == "poll_schedule_tomorrow_morning", PollCreationStates.schedule)
async def callback_poll_schedule_tomorrow_morning(callback: CallbackQuery, state: FSMContext):
    """Планирование на завтра утром"""
    from datetime import datetime, timedelta
    
    tomorrow = datetime.now() + timedelta(days=1)
    scheduled_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
    await state.update_data(scheduled_at=scheduled_time)
    
    await callback.message.edit_text(
        f"🌅 **Опрос запланирован на завтра утром ({scheduled_time.strftime('%d.%m.%Y %H:%M')})**\n\n"
        "Опрос будет опубликован автоматически в указанное время.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
        ])
    )
    await callback.answer("✅ Опрос запланирован!")
    await state.clear()

@router.callback_query(F.data == "poll_schedule_tomorrow_evening", PollCreationStates.schedule)
async def callback_poll_schedule_tomorrow_evening(callback: CallbackQuery, state: FSMContext):
    """Планирование на завтра вечером"""
    from datetime import datetime, timedelta
    
    tomorrow = datetime.now() + timedelta(days=1)
    scheduled_time = tomorrow.replace(hour=21, minute=0, second=0, microsecond=0)
    await state.update_data(scheduled_at=scheduled_time)
    
    await callback.message.edit_text(
        f"🌆 **Опрос запланирован на завтра вечером ({scheduled_time.strftime('%d.%m.%Y %H:%M')})**\n\n"
        "Опрос будет опубликован автоматически в указанное время.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
        ])
    )
    await callback.answer("✅ Опрос запланирован!")
    await state.clear()

@router.callback_query(F.data == "poll_schedule_custom", PollCreationStates.schedule)
async def callback_poll_schedule_custom(callback: CallbackQuery, state: FSMContext):
    """Выбор произвольного времени"""
    await state.set_state(PollCreationStates.enter_time)
    await callback.message.edit_text(
        "📅 **Выберите время публикации**\n\n"
        "Отправьте время в формате ДД.ММ.ГГГГ ЧЧ:ММ\n\n"
        "Пример: 20.12.2024 15:30",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_admin")]
        ])
    )
    await callback.answer()

@router.message(PollCreationStates.enter_time)
async def process_poll_time_input(message: Message, state: FSMContext):
    """Обработка ввода времени для опроса"""
    from datetime import datetime
    
    try:
        time_str = message.text.strip()
        scheduled_time = datetime.strptime(time_str, '%d.%m.%Y %H:%M')
        
        # Проверяем, что время в будущем
        if scheduled_time <= datetime.now():
            await message.answer("❌ Время должно быть в будущем. Попробуйте еще раз:")
            return
        
        await state.update_data(scheduled_at=scheduled_time)
        
        await message.answer(
            f"✅ **Опрос запланирован на {scheduled_time.strftime('%d.%m.%Y %H:%M')}**\n\n"
            "Опрос будет опубликован автоматически в указанное время.",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🔙 В админ-панель", callback_data="back_to_admin")]
            ])
        )
        await state.clear()
        
    except ValueError:
        await message.answer("❌ Неверный формат времени. Используйте ДД.ММ.ГГГГ ЧЧ:ММ\n\nПример: 20.12.2024 15:30")
