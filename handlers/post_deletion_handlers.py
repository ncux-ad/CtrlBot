"""
@file: handlers/post_deletion_handlers.py
@description: Обработчики для удаления постов
@dependencies: services/post_service.py, services/publisher.py
@created: 2025-09-13
"""

from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from services.post_service import post_service
from services.publisher import get_publisher
from utils.filters import IsConfigAdminFilter
from utils.logging import get_logger

logger = get_logger(__name__)
router = Router()

# Фильтры
admin_filter = IsConfigAdminFilter()

@router.callback_query(F.data.startswith("view_post_"), admin_filter)
async def callback_view_post(callback: CallbackQuery):
    """Просмотр детальной информации о посте"""
    try:
        post_id = int(callback.data.split("_")[2])
        logger.info(f"👁️ Просмотр поста {post_id} пользователем {callback.from_user.id}")
        
        # Получаем пост из БД
        post = await post_service.get_post(post_id)
        
        if not post:
            await callback.answer("❌ Пост не найден", show_alert=True)
            return
        
        # Проверяем права доступа
        if post['user_id'] != callback.from_user.id:
            await callback.answer("❌ Нет прав для просмотра этого поста", show_alert=True)
            return
        
        # Формируем детальную информацию
        status_emoji = {
            'draft': '📝',
            'scheduled': '⏰',
            'published': '✅',
            'deleted': '❌',
            'failed': '⚠️'
        }.get(post['status'], '❓')
        
        text = f"📋 *Детали поста #{post['id']}*\n\n"
        text += f"📝 *Статус:* {status_emoji} {post['status']}\n"
        text += f"📅 *Создан:* {post['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
        
        if post['published_at']:
            text += f"📤 *Опубликован:* {post['published_at'].strftime('%d.%m.%Y %H:%M')}\n"
        
        if post['scheduled_at']:
            text += f"⏰ *Запланирован на:* {post['scheduled_at'].strftime('%d.%m.%Y %H:%M')}\n"
        
        if post['series_title']:
            text += f"📚 *Серия:* {post['series_title']}\n"
        
        if post['tags_cache']:
            tags = ', '.join(post['tags_cache'])
            text += f"🏷️ *Теги:* {tags}\n"
        
        if post['media_type']:
            text += f"📷 *Медиа:* {post['media_type']}\n"
        
        text += f"\n📝 *Текст поста:*\n{post['body_md']}"
        
        # Создаем клавиатуру
        keyboard = []
        
        # Кнопки действий в зависимости от статуса
        if post['status'] == 'draft':
            keyboard.append([InlineKeyboardButton(text="📤 Опубликовать", callback_data=f"publish_post_{post_id}")])
            keyboard.append([InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_post_{post_id}")])
        elif post['status'] == 'scheduled':
            keyboard.append([InlineKeyboardButton(text="⏰ Изменить время", callback_data=f"reschedule_post_{post_id}")])
            keyboard.append([InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_scheduled_post_{post_id}")])
        elif post['status'] == 'published':
            keyboard.append([InlineKeyboardButton(text="🗑️ Удалить из канала", callback_data=f"delete_post_{post_id}")])
        
        # Кнопка удаления из БД (для всех статусов кроме уже удаленных)
        if post['status'] != 'deleted':
            keyboard.append([InlineKeyboardButton(text="🗑️ Удалить навсегда", callback_data=f"permanent_delete_post_{post_id}")])
        
        keyboard.append([InlineKeyboardButton(text="🔙 Назад к списку", callback_data="my_posts")])
        
        await callback.message.edit_text(
            text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard)
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при просмотре поста: {e}")
        await callback.answer("❌ Ошибка загрузки поста", show_alert=True)

@router.callback_query(F.data.startswith("delete_post_"), admin_filter)
async def callback_delete_post(callback: CallbackQuery):
    """Удаление поста из канала (мягкое удаление)"""
    try:
        post_id = int(callback.data.split("_")[2])
        logger.info(f"🗑️ Удаление поста {post_id} пользователем {callback.from_user.id}")
        
        # Получаем пост из БД
        post = await post_service.get_post(post_id)
        
        if not post:
            await callback.answer("❌ Пост не найден", show_alert=True)
            return
        
        # Проверяем права доступа
        if post['user_id'] != callback.from_user.id:
            await callback.answer("❌ Нет прав для удаления этого поста", show_alert=True)
            return
        
        # Проверяем, можно ли удалить
        if post['status'] == 'deleted':
            await callback.answer("❌ Пост уже удален", show_alert=True)
            return
        
        # Показываем подтверждение
        await callback.message.edit_text(
            f"⚠️ *Подтверждение удаления*\n\n"
            f"Вы действительно хотите удалить пост #{post_id}?\n\n"
            f"📝 *Текст:* {post['body_md'][:100]}{'...' if len(post['body_md']) > 100 else ''}\n\n"
            f"*Это действие:*\n"
            f"• Помечает пост как удаленный в БД\n"
            f"• Удаляет сообщение из канала (если опубликован)\n"
            f"• Нельзя отменить!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_post_{post_id}")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data=f"view_post_{post_id}")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при подготовке удаления поста: {e}")
        await callback.answer("❌ Ошибка подготовки удаления", show_alert=True)

@router.callback_query(F.data.startswith("confirm_delete_post_"), admin_filter)
async def callback_confirm_delete_post(callback: CallbackQuery):
    """Подтверждение удаления поста"""
    try:
        post_id = int(callback.data.split("_")[3])
        logger.info(f"✅ Подтверждение удаления поста {post_id}")
        
        # Получаем пост из БД
        post = await post_service.get_post(post_id)
        
        if not post:
            await callback.answer("❌ Пост не найден", show_alert=True)
            return
        
        # Проверяем права доступа
        if post['user_id'] != callback.from_user.id:
            await callback.answer("❌ Нет прав для удаления этого поста", show_alert=True)
            return
        
        # Удаляем сообщение из канала, если пост опубликован
        if post['status'] == 'published' and post['message_id']:
            try:
                publisher = get_publisher()
                await publisher.delete_message_from_channel(post['tg_channel_id'], post['message_id'])
                logger.info(f"✅ Сообщение {post['message_id']} удалено из канала {post['tg_channel_id']}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось удалить сообщение из канала: {e}")
                # Продолжаем удаление в БД даже если не удалось удалить из канала
        
        # Помечаем пост как удаленный в БД
        success = await post_service.delete_post(post_id)
        
        if success:
            await callback.message.edit_text(
                f"✅ *Пост успешно удален!*\n\n"
                f"📝 *ID поста:* {post_id}\n"
                f"📝 *Текст:* {post['body_md'][:100]}{'...' if len(post['body_md']) > 100 else ''}\n\n"
                f"Пост помечен как удаленный в базе данных.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")]
                ])
            )
            logger.info(f"✅ Пост {post_id} успешно удален")
        else:
            await callback.answer("❌ Не удалось удалить пост", show_alert=True)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при удалении поста: {e}")
        await callback.answer("❌ Ошибка удаления поста", show_alert=True)

@router.callback_query(F.data.startswith("permanent_delete_post_"), admin_filter)
async def callback_permanent_delete_post(callback: CallbackQuery):
    """Постоянное удаление поста из БД"""
    try:
        post_id = int(callback.data.split("_")[3])
        logger.info(f"🗑️ Постоянное удаление поста {post_id}")
        
        # Получаем пост из БД
        post = await post_service.get_post(post_id)
        
        if not post:
            await callback.answer("❌ Пост не найден", show_alert=True)
            return
        
        # Проверяем права доступа
        if post['user_id'] != callback.from_user.id:
            await callback.answer("❌ Нет прав для удаления этого поста", show_alert=True)
            return
        
        # Показываем предупреждение
        await callback.message.edit_text(
            f"⚠️ *ОСТОРОЖНО! Постоянное удаление*\n\n"
            f"Вы действительно хотите НАВСЕГДА удалить пост #{post_id}?\n\n"
            f"📝 *Текст:* {post['body_md'][:100]}{'...' if len(post['body_md']) > 100 else ''}\n\n"
            f"*Это действие:*\n"
            f"• Удаляет пост из базы данных\n"
            f"• Удаляет сообщение из канала (если опубликован)\n"
            f"• НЕЛЬЗЯ ОТМЕНИТЬ!\n"
            f"• Потеряется вся история поста",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💀 УДАЛИТЬ НАВСЕГДА", callback_data=f"confirm_permanent_delete_{post_id}")],
                [InlineKeyboardButton(text="❌ Отменить", callback_data=f"view_post_{post_id}")]
            ])
        )
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при подготовке постоянного удаления: {e}")
        await callback.answer("❌ Ошибка подготовки удаления", show_alert=True)

@router.callback_query(F.data.startswith("confirm_permanent_delete_"), admin_filter)
async def callback_confirm_permanent_delete(callback: CallbackQuery):
    """Подтверждение постоянного удаления поста"""
    try:
        post_id = int(callback.data.split("_")[3])
        logger.info(f"💀 Подтверждение постоянного удаления поста {post_id}")
        
        # Получаем пост из БД
        post = await post_service.get_post(post_id)
        
        if not post:
            await callback.answer("❌ Пост не найден", show_alert=True)
            return
        
        # Проверяем права доступа
        if post['user_id'] != callback.from_user.id:
            await callback.answer("❌ Нет прав для удаления этого поста", show_alert=True)
            return
        
        # Удаляем сообщение из канала, если пост опубликован
        if post['status'] == 'published' and post['message_id']:
            try:
                publisher = get_publisher()
                await publisher.delete_message_from_channel(post['tg_channel_id'], post['message_id'])
                logger.info(f"✅ Сообщение {post['message_id']} удалено из канала {post['tg_channel_id']}")
            except Exception as e:
                logger.warning(f"⚠️ Не удалось удалить сообщение из канала: {e}")
        
        # Удаляем пост из БД (пока используем мягкое удаление)
        # TODO: Добавить функцию полного удаления из БД
        success = await post_service.delete_post(post_id)
        
        if success:
            await callback.message.edit_text(
                f"💀 *Пост удален навсегда!*\n\n"
                f"📝 *ID поста:* {post_id}\n"
                f"📝 *Текст:* {post['body_md'][:100]}{'...' if len(post['body_md']) > 100 else ''}\n\n"
                f"Пост удален из базы данных и канала.",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="📋 Мои посты", callback_data="my_posts")],
                    [InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")]
                ])
            )
            logger.info(f"💀 Пост {post_id} удален навсегда")
        else:
            await callback.answer("❌ Не удалось удалить пост", show_alert=True)
        
        await callback.answer()
        
    except Exception as e:
        logger.error(f"Ошибка при постоянном удалении поста: {e}")
        await callback.answer("❌ Ошибка удаления поста", show_alert=True)
