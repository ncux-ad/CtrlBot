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
    
    async def publish_poll(
        self,
        chat_id: int,
        question: str,
        options: List[str],
        is_anonymous: bool = True,
        type: str = "regular",
        allows_multiple_answers: bool = False,
        correct_option_id: Optional[int] = None,
        explanation: Optional[str] = None,
        explanation_entities: Optional[List[MessageEntity]] = None,
        open_period: Optional[int] = None,
        close_date: Optional[int] = None,
        is_closed: bool = False,
        disable_notification: bool = False,
        protect_content: bool = False,
        reply_to_message_id: Optional[int] = None,
        allow_sending_without_reply: bool = False,
        reply_markup: Optional[InlineKeyboardMarkup] = None
    ) -> Optional[Message]:
        """
        Публикует опрос в канал
        
        Args:
            chat_id: ID канала/чата
            question: Вопрос опроса
            options: Список вариантов ответов (2-10)
            is_anonymous: Анонимный опрос
            type: Тип опроса (regular, quiz)
            allows_multiple_answers: Разрешить несколько ответов
            correct_option_id: ID правильного ответа (для quiz)
            explanation: Объяснение (для quiz)
            explanation_entities: Entities для объяснения
            open_period: Время жизни опроса в секундах
            close_date: Время закрытия (Unix timestamp)
            is_closed: Закрыт ли опрос
            disable_notification: Отключить уведомления
            protect_content: Защитить контент
            reply_to_message_id: Ответ на сообщение
            allow_sending_without_reply: Разрешить отправку без ответа
            reply_markup: Inline клавиатура
            
        Returns:
            Message объект или None при ошибке
        """
        try:
            logger.info(f"📊 Публикуем опрос в канал {chat_id}")
            logger.info(f"❓ Вопрос: {question}")
            logger.info(f"📋 Вариантов: {len(options)}")
            logger.info(f"🔒 Анонимный: {is_anonymous}")
            logger.info(f"📝 Тип: {type}")
            
            message = await self.bot.send_poll(
                chat_id=chat_id,
                question=question,
                options=options,
                is_anonymous=is_anonymous,
                type=type,
                allows_multiple_answers=allows_multiple_answers,
                correct_option_id=correct_option_id,
                explanation=explanation,
                explanation_entities=explanation_entities,
                open_period=open_period,
                close_date=close_date,
                is_closed=is_closed,
                disable_notification=disable_notification,
                protect_content=protect_content,
                reply_to_message_id=reply_to_message_id,
                allow_sending_without_reply=allow_sending_without_reply,
                reply_markup=reply_markup
            )
            
            logger.info(f"✅ Опрос опубликован: ID {message.message_id}")
            return message
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации опроса: {e}")
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
                    first_success['message_id']
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
            media_data = post_data.get('media_data')
            
            # Если есть медиа, отправляем медиа с подписью
            if media_data:
                logger.info(f"📷 Отправляем медиа: {media_data['type']}")
                return await self._send_media_with_caption(
                    channel_id, 
                    media_data, 
                    text, 
                    entities
                )
            
            # Если есть entities, используем их
            if entities:
                return await self._send_with_entities(channel_id, text, entities)
            
            # Иначе пытаемся определить форматирование
            return await self._send_with_auto_formatting(channel_id, text)
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации в канал {channel_id}: {e}")
            return None
    
    async def _send_media_with_caption(
        self, 
        chat_id: int, 
        media_data: Dict[str, Any], 
        caption: str = "", 
        caption_entities: Optional[List] = None
    ) -> Optional[Message]:
        """Отправляет медиа с подписью"""
        try:
            media_type = media_data.get('type')
            file_id = media_data.get('file_id')
            
            if not media_type or not file_id:
                logger.error("❌ Неполные данные медиа")
                return None
            
            # Преобразуем entities для caption
            caption_entities_list = None
            if caption_entities:
                from utils.entities import entities_from_dict
                caption_entities_list = entities_from_dict(caption_entities)
            
            # Отправляем медиа в зависимости от типа
            if media_type == "photo":
                return await self.bot.send_photo(
                    chat_id=chat_id,
                    photo=file_id,
                    caption=caption,
                    caption_entities=caption_entities_list
                )
            elif media_type == "video":
                return await self.bot.send_video(
                    chat_id=chat_id,
                    video=file_id,
                    caption=caption,
                    caption_entities=caption_entities_list
                )
            elif media_type == "document":
                return await self.bot.send_document(
                    chat_id=chat_id,
                    document=file_id,
                    caption=caption,
                    caption_entities=caption_entities_list
                )
            elif media_type == "voice":
                return await self.bot.send_voice(
                    chat_id=chat_id,
                    voice=file_id,
                    caption=caption,
                    caption_entities=caption_entities_list
                )
            elif media_type == "audio":
                return await self.bot.send_audio(
                    chat_id=chat_id,
                    audio=file_id,
                    caption=caption,
                    caption_entities=caption_entities_list
                )
            elif media_type == "video_note":
                return await self.bot.send_video_note(
                    chat_id=chat_id,
                    video_note=file_id
                )
            else:
                logger.error(f"❌ Неподдерживаемый тип медиа: {media_type}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Ошибка отправки медиа {media_type}: {e}")
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
    
    async def delete_message_from_channel(self, channel_id: int, message_id: int) -> bool:
        """Удаляет сообщение из канала"""
        try:
            await self.bot.delete_message(chat_id=channel_id, message_id=message_id)
            logger.info(f"✅ Сообщение {message_id} удалено из канала {channel_id}")
            return True
        except Exception as e:
            error_msg = str(e)
            if "message to delete not found" in error_msg:
                logger.warning(f"⚠️ Сообщение {message_id} уже удалено из канала {channel_id}")
                return True  # Считаем успешным, если сообщение уже удалено
            else:
                logger.error(f"❌ Ошибка удаления сообщения {message_id} из канала {channel_id}: {e}")
                return False

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
