# Service: Post Publisher
# Централизованный сервис для публикации постов в Telegram каналы

from typing import List, Optional, Dict, Any
from aiogram import Bot
from aiogram.types import Message, MessageEntity, InlineKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest

from utils.logging import get_logger
from database import db

logger = get_logger(__name__)

class PostPublisher:
    """Централизованный сервис для публикации постов"""
    
    def __init__(self, bot: Bot):
        self.bot = bot
        self.max_retries = 3
        self.retry_delay = 1.0
    
    async def publish_text(
        self, 
        chat_id: int, 
        text: str, 
        entities: Optional[List[MessageEntity]] = None,
        parse_mode: Optional[ParseMode] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """
        Публикует текстовое сообщение с правильным форматированием
        
        Args:
            chat_id: ID канала/чата
            text: Текст сообщения
            entities: Telegram entities для форматирования
            parse_mode: Режим парсинга (если entities не указаны)
            reply_markup: Inline клавиатура
            
        Returns:
            Message объект или None при ошибке
        """
        try:
            logger.info(f"📤 Публикуем текст в канал {chat_id}")
            logger.info(f"📝 Длина текста: {len(text)} символов")
            logger.info(f"🎨 Entities: {len(entities) if entities else 0}")
            logger.info(f"🔧 Parse mode: {parse_mode}")
            
            # Определяем лучший способ отправки
            if entities:
                # Используем entities для точного форматирования
                logger.info("🎯 Используем entities для форматирования")
                message = await self._send_with_entities(
                    chat_id, text, entities, reply_markup
                )
            elif parse_mode:
                # Используем указанный parse_mode
                logger.info(f"🔧 Используем parse_mode: {parse_mode}")
                message = await self._send_with_parse_mode(
                    chat_id, text, parse_mode, reply_markup
                )
            else:
                # Пытаемся определить форматирование автоматически
                logger.info("🔍 Автоопределение форматирования")
                message = await self._send_with_auto_formatting(
                    chat_id, text, reply_markup
                )
            
            if message:
                logger.info(f"✅ Сообщение успешно отправлено: ID {message.message_id}")
            else:
                logger.error("❌ Не удалось отправить сообщение")
            
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации текста в канал {chat_id}: {e}")
            return None
    
    async def publish_media(
        self,
        chat_id: int,
        media_type: str,
        media_file_id: str,
        caption: Optional[str] = None,
        caption_entities: Optional[List[MessageEntity]] = None,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """
        Публикует медиа с подписью
        
        Args:
            chat_id: ID канала/чата
            media_type: Тип медиа (photo, video, document, etc.)
            media_file_id: ID файла в Telegram
            caption: Подпись к медиа
            caption_entities: Entities для подписи
            reply_markup: Inline клавиатура
            
        Returns:
            Message объект или None при ошибке
        """
        try:
            logger.info(f"📤 Публикуем {media_type} в канал {chat_id}")
            
            # Выбираем метод отправки в зависимости от типа медиа
            if media_type == "photo":
                message = await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=media_file_id,
                    caption=caption,
                    caption_entities=caption_entities,
                    reply_markup=reply_markup
                )
            elif media_type == "video":
                message = await self.bot.send_video(
                    chat_id=chat_id,
                    video=media_file_id,
                    caption=caption,
                    caption_entities=caption_entities,
                    reply_markup=reply_markup
                )
            elif media_type == "document":
                message = await self.bot.send_document(
                    chat_id=chat_id,
                    document=media_file_id,
                    caption=caption,
                    caption_entities=caption_entities,
                    reply_markup=reply_markup
                )
            else:
                logger.error(f"❌ Неподдерживаемый тип медиа: {media_type}")
                return None
            
            logger.info(f"✅ Медиа успешно отправлено: ID {message.message_id}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации медиа в канал {chat_id}: {e}")
            return None
    
    async def publish_copy(
        self,
        chat_id: int,
        from_chat_id: int,
        message_id: int,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """
        Копирует сообщение из другого чата (сохраняет все форматирование)
        
        Args:
            chat_id: ID целевого канала/чата
            from_chat_id: ID исходного чата
            message_id: ID исходного сообщения
            reply_markup: Inline клавиатура
            
        Returns:
            Message объект или None при ошибке
        """
        try:
            logger.info(f"📋 Копируем сообщение {message_id} из чата {from_chat_id} в {chat_id}")
            
            message = await self.bot.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=message_id,
                reply_markup=reply_markup
            )
            
            logger.info(f"✅ Сообщение успешно скопировано: ID {message.message_id}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка копирования сообщения: {e}")
            return None
    
    async def publish_post(
        self,
        post_data: Dict[str, Any],
        channel_ids: List[int],
        update_db: bool = True
    ) -> Dict[str, Any]:
        """
        Публикует пост в несколько каналов
        
        Args:
            post_data: Данные поста (id, body_md, entities, etc.)
            channel_ids: Список ID каналов для публикации
            update_db: Обновлять ли БД после публикации
            
        Returns:
            Результат публикации с деталями
        """
        logger.info(f"📤 Публикуем пост {post_data.get('id')} в {len(channel_ids)} каналов")
        
        results = {
            'success': [],
            'failed': [],
            'total_channels': len(channel_ids),
            'success_count': 0,
            'failed_count': 0
        }
        
        for channel_id in channel_ids:
            try:
                # Пытаемся опубликовать в канал
                message = await self._publish_to_channel(post_data, channel_id)
                
                if message:
                    results['success'].append({
                        'channel_id': channel_id,
                        'message_id': message.message_id,
                        'message': message
                    })
                    results['success_count'] += 1
                    logger.info(f"✅ Пост опубликован в канал {channel_id}")
                else:
                    results['failed'].append({
                        'channel_id': channel_id,
                        'error': 'Не удалось отправить сообщение'
                    })
                    results['failed_count'] += 1
                    logger.error(f"❌ Не удалось опубликовать в канал {channel_id}")
                
            except Exception as e:
                results['failed'].append({
                    'channel_id': channel_id,
                    'error': str(e)
                })
                results['failed_count'] += 1
                logger.error(f"❌ Ошибка публикации в канал {channel_id}: {e}")
        
        # Обновляем БД если нужно
        if update_db and results['success_count'] > 0:
            try:
                # Берем первый успешный message_id для БД
                first_success = results['success'][0]
                await self._update_post_in_db(
                    post_data['id'], 
                    first_success['message_id'],
                    results['success_count']
                )
                logger.info(f"✅ БД обновлена для поста {post_data['id']}")
            except Exception as e:
                logger.error(f"❌ Ошибка обновления БД: {e}")
        
        logger.info(f"📊 Результат публикации: {results['success_count']}/{results['total_channels']} успешно")
        return results
    
    async def _publish_to_channel(self, post_data: Dict[str, Any], channel_id: int) -> Optional[Message]:
        """Публикует пост в конкретный канал"""
        try:
            text = post_data.get('body_md', '')
            entities = post_data.get('entities')
            
            # Если есть entities, используем их
            if entities:
                return await self._send_with_entities(channel_id, text, entities)
            
            # Иначе пытаемся определить форматирование
            return await self._send_with_auto_formatting(channel_id, text)
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации в канал {channel_id}: {e}")
            return None
    
    async def _send_with_entities(
        self, 
        chat_id: int, 
        text: str, 
        entities: List[MessageEntity],
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """Отправляет сообщение с entities (наиболее точный способ)"""
        try:
            return await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                entities=entities,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки с entities: {e}")
            return None
    
    async def _send_with_parse_mode(
        self, 
        chat_id: int, 
        text: str, 
        parse_mode: ParseMode,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """Отправляет сообщение с указанным parse_mode"""
        try:
            return await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                reply_markup=reply_markup
            )
        except Exception as e:
            logger.error(f"❌ Ошибка отправки с parse_mode {parse_mode}: {e}")
            return None
    
    async def _send_with_auto_formatting(
        self, 
        chat_id: int, 
        text: str,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """Автоматически определяет форматирование и отправляет сообщение"""
        try:
            # Проверяем, есть ли Markdown форматирование
            if self._has_markdown_formatting(text):
                logger.info("🔍 Обнаружено Markdown форматирование")
                return await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    parse_mode=ParseMode.MARKDOWN_V2,
                    reply_markup=reply_markup
                )
            else:
                logger.info("📄 Отправляем как обычный текст")
                return await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup
                )
        except TelegramBadRequest as e:
            if "can't parse entities" in str(e).lower():
                logger.warning("⚠️ Ошибка парсинга Markdown, отправляем как обычный текст")
                return await self.bot.send_message(
                    chat_id=chat_id,
                    text=text,
                    reply_markup=reply_markup
                )
            else:
                raise
        except Exception as e:
            logger.error(f"❌ Ошибка автоформатирования: {e}")
            return None
    
    def _has_markdown_formatting(self, text: str) -> bool:
        """Проверяет, содержит ли текст Markdown форматирование"""
        markdown_indicators = ['*', '_', '`', '[', ']', '(', ')']
        return any(indicator in text for indicator in markdown_indicators)
    
    async def _update_post_in_db(self, post_id: int, message_id: int):
        """Обновляет пост в БД после публикации"""
        try:
            query = """
                UPDATE posts 
                SET status = 'published', 
                    published_at = NOW(),
                    message_id = $2,
                    updated_at = NOW()
                WHERE id = $1
            """
            await db.execute(query, post_id, message_id)
            logger.info(f"✅ Пост {post_id} обновлен в БД (message_id: {message_id})")
        except Exception as e:
            logger.error(f"❌ Ошибка обновления поста {post_id} в БД: {e}")
            raise

# Глобальный экземпляр (будет инициализирован в bot.py)
publisher = None

def get_publisher() -> PostPublisher:
    """Получает экземпляр PostPublisher"""
    if publisher is None:
        raise RuntimeError("PostPublisher не инициализирован. Вызовите init_publisher() в bot.py")
    return publisher

def init_publisher(bot: Bot) -> PostPublisher:
    """Инициализирует PostPublisher с ботом"""
    global publisher
    publisher = PostPublisher(bot)
    logger.info("✅ PostPublisher инициализирован")
    return publisher
