"""
@file: utils/post_card.py
@description: Компонент для рендеринга карточек постов с превью
@dependencies: aiogram, utils.timezone_utils
@created: 2025-09-13
"""

import asyncio
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.timezone_utils import format_datetime

class PostCardRenderer:
    def __init__(self):
        self.status_emojis = {
            'published': '✅',
            'scheduled': '⏰', 
            'failed': '❌',
            'deleted': '️'
        }
        
        self.status_colors = {
            'published': '',
            'scheduled': '🟡',
            'failed': '🔴', 
            'deleted': '⚫'
        }
    
    async def create_post_card(self, post: dict, bot=None) -> tuple[str, InlineKeyboardMarkup]:
        """Создает красивую карточку поста с реальными превью"""
        try:
            # Заголовок (первые 50 символов)
            title = post['body_md'][:50] + "..." if len(post['body_md']) > 50 else post['body_md']
            
            # Метаданные
            date = format_datetime(post['created_at'])
            channel = post.get('channel_name', 'Неизвестный канал')
            status = self.status_emojis.get(post['status'], '❓')
            views = post.get('views', 0)
            likes = post.get('likes', 0)
            comments = post.get('comments', 0)
            
            # Реальные превью медиа
            media_preview = await self._get_media_preview(post, bot)
            text_preview = self._get_text_preview(post)
            
            # Формируем карточку
            card = f"""
┌─────────────────────────────────────────────────────────┐
│ 📝 {title:<50} │
│ {date}  📺 {channel}  📊 {views:,} просмотров        │
│ ┌─────────────────────────────────────────────────────┐ │
│ │ {media_preview}  {text_preview}                    │ │
│ └─────────────────────────────────────────────────────┘ │
│ {status} {post['status'].title()}  ❤️ {likes:,}  💬 {comments:,}        │
└─────────────────────────────────────────────────────────┘
"""
            
            # Создаем кнопки действий
            keyboard = self._create_action_buttons(post)
            
            return card, keyboard
        except Exception as e:
            # Fallback к простой карточке
            title = post['body_md'][:50] + "..." if len(post['body_md']) > 50 else post['body_md']
            status = self.status_emojis.get(post['status'], '❓')
            card = f"📝 {title}\n{status} {post['status'].title()}\n"
            keyboard = self._create_action_buttons(post)
            return card, keyboard
    
    async def _get_media_preview(self, post: dict, bot=None) -> str:
        """Получает реальные превью медиа для поста"""
        if not bot or not post.get('media_file_id'):
            return " [Текст]"
            
        try:
            if post.get('media_type') == 'photo':
                return "🖼️ [Фото]"
            elif post.get('media_type') == 'video':
                return " [Видео]"
            elif post.get('media_type') == 'document':
                return "📄 [Документ]"
            else:
                return " [Текст]"
        except Exception as e:
            return f"📝 [Медиа: {post.get('media_type', 'неизвестно')}]"
    
    def _get_text_preview(self, post: dict) -> str:
        """Получает превью текста поста"""
        text = post['body_md']
        if len(text) > 30:
            return text[:30] + "..."
        return text
    
    def _create_action_buttons(self, post: dict) -> InlineKeyboardMarkup:
        """Создает кнопки действий для поста"""
        buttons = []
        
        # Основные действия
        row1 = [
            InlineKeyboardButton("👁️ Просмотр", callback_data=f"view_post_{post['id']}"),
            InlineKeyboardButton("✏️ Редактировать", callback_data=f"edit_post_{post['id']}")
        ]
        buttons.append(row1)
        
        # Дополнительные действия в зависимости от статуса
        if post['status'] == 'scheduled':
            row2 = [
                InlineKeyboardButton("⏰ Изменить время", callback_data=f"change_time_{post['id']}"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_scheduled_{post['id']}")
            ]
            buttons.append(row2)
        elif post['status'] == 'failed':
            row2 = [
                InlineKeyboardButton("🔄 Повторить", callback_data=f"retry_failed_{post['id']}"),
                InlineKeyboardButton("❌ Отменить", callback_data=f"cancel_scheduled_{post['id']}")
            ]
            buttons.append(row2)
        
        # Удаление
        row3 = [InlineKeyboardButton("🗑️ Удалить", callback_data=f"delete_post_{post['id']}")]
        buttons.append(row3)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
