# Service: posts

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from utils.timezone_utils import to_utc
import logging

from database import db
from config import config

logger = logging.getLogger(__name__)

class PostService:
    """Сервис для работы с постами"""
    
    async def get_channel_id_by_tg_id(self, tg_channel_id: int) -> Optional[int]:
        """Получает ID канала по Telegram channel ID"""
        try:
            query = "SELECT id FROM channels WHERE tg_channel_id = $1"
            return await db.fetch_val(query, tg_channel_id)
        except Exception as e:
            logger.error("Failed to get channel ID for tg_channel_id %s: %s", tg_channel_id, e)
            return None
    
    async def create_post(self, tg_channel_id: int, title: Optional[str], 
                         body_md: str, user_id: int, series_id: Optional[int] = None,
                         scheduled_at: Optional[datetime] = None, tag_ids: Optional[List[int]] = None,
                         entities: Optional[List] = None) -> int:
        """Создает новый пост"""
        logger.info("=== НАЧАЛО СОЗДАНИЯ ПОСТА В БД ===")
        logger.info(f"📢 TG Channel ID: {tg_channel_id}")
        logger.info(f"📝 Title: {title}")
        logger.info(f"📄 Body length: {len(body_md)} chars")
        logger.info(f"👤 User ID: {user_id}")
        logger.info(f"📚 Series ID: {series_id}")
        logger.info(f"⏰ Scheduled at: {scheduled_at}")
        logger.info(f"🏷️ Tag IDs: {tag_ids}")
        logger.info(f"🎨 Entities: {len(entities) if entities else 0}")
        
        try:
            # Получаем ID канала из базы
            logger.info("🔍 Ищем ID канала в базе данных")
            channel_id = await self.get_channel_id_by_tg_id(tg_channel_id)
            if not channel_id:
                logger.error(f"❌ Канал с tg_channel_id {tg_channel_id} не найден")
                raise ValueError(f"Channel with tg_channel_id {tg_channel_id} not found")
            logger.info(f"✅ Найден channel_id: {channel_id}")
            
            # Определяем статус
            status = 'scheduled' if scheduled_at else 'draft'
            logger.info(f"📊 Статус поста: {status}")
            
            # Конвертируем время в UTC для хранения в БД
            if scheduled_at:
                scheduled_at_utc = to_utc(scheduled_at)
                logger.info(f"🕐 Время в UTC: {scheduled_at_utc}")
            else:
                scheduled_at_utc = None
                logger.info("🕐 Время не указано")
            
            # Конвертируем entities в JSON для хранения в БД
            entities_json = None
            if entities:
                from utils.entities import entities_to_json
                entities_json = entities_to_json(entities)
                logger.info(f"🎨 Entities сохранены в JSON: {len(entities_json)} символов")
            else:
                logger.info("🎨 Entities не указаны")
            
            logger.info("💾 Выполняем INSERT в таблицу posts")
            query = """
                INSERT INTO posts (channel_id, user_id, title, body_md, entities, status, series_id, scheduled_at, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
                RETURNING id
            """
            post_id = await db.fetch_val(query, channel_id, user_id, title, body_md, entities_json, status, series_id, scheduled_at_utc)
            logger.info(f"✅ Пост сохранен в БД с ID: {post_id}")
            
            # Добавляем теги если есть
            if tag_ids:
                logger.info(f"🏷️ Добавляем {len(tag_ids)} тегов к посту")
                from services.tags import tag_service
                for tag_id in tag_ids:
                    logger.info(f"🏷️ Добавляем тег ID: {tag_id}")
                    await tag_service.add_tag_to_post(post_id, tag_id)
                
                # Обновляем кеш тегов
                logger.info("🔄 Обновляем кеш тегов")
                await tag_service.update_post_tags_cache(post_id)
            else:
                logger.info("🏷️ Теги не указаны")
            
            # Если есть серия, увеличиваем номер
            if series_id:
                logger.info(f"📚 Увеличиваем номер серии: {series_id}")
                from services.series import series_service
                await series_service.increment_series_number(series_id)
            else:
                logger.info("📚 Серия не указана")
            
            logger.info("✅ ПОСТ УСПЕШНО СОЗДАН")
            logger.info("Post created: %s for channel %s by user %s (series: %s, tags: %s)", 
                       post_id, channel_id, user_id, series_id, tag_ids)
            return post_id
        except Exception as e:
            logger.error("❌ ОШИБКА СОЗДАНИЯ ПОСТА")
            logger.error("Failed to create post: %s", e)
            logger.error("📊 Параметры на момент ошибки:")
            logger.error("  - tg_channel_id: %s", tg_channel_id)
            logger.error("  - title: %s", title)
            logger.error("  - body_md length: %s", len(body_md) if body_md else 0)
            logger.error("  - user_id: %s", user_id)
            logger.error("  - series_id: %s", series_id)
            logger.error("  - scheduled_at: %s", scheduled_at)
            logger.error("  - tag_ids: %s", tag_ids)
            raise
    
    async def get_post(self, post_id: int) -> Optional[Dict[str, Any]]:
        """Получает пост по ID"""
        try:
            query = """
                SELECT p.*, c.title as channel_title, s.title as series_title
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                LEFT JOIN series s ON p.series_id = s.id
                WHERE p.id = $1
            """
            result = await db.fetch_one(query, post_id)
            if not result:
                return None
            
            post_dict = dict(result)
            
            # Восстанавливаем entities из JSON
            if post_dict.get('entities'):
                from utils.entities import entities_from_json
                post_dict['entities'] = entities_from_json(post_dict['entities'])
                logger.info(f"🎨 Восстановлено {len(post_dict['entities'])} entities для поста {post_id}")
            
            return post_dict
        except Exception as e:
            logger.error("Failed to get post %s: %s", post_id, e)
            raise
    
    async def get_user_posts(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Dict[str, Any]]:
        """Получает посты пользователя"""
        try:
            query = """
                SELECT p.*, c.title as channel_title, s.title as series_title, s.next_number
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                LEFT JOIN series s ON p.series_id = s.id
                WHERE p.user_id = $1
                ORDER BY p.created_at DESC
                LIMIT $2 OFFSET $3
            """
            results = await db.fetch_all(query, user_id, limit, offset)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get posts for user %s: %s", user_id, e)
            raise
    
    async def update_post(self, post_id: int, title: Optional[str] = None,
                         body_md: Optional[str] = None, status: Optional[str] = None,
                         scheduled_at: Optional[datetime] = None) -> bool:
        """Обновляет пост"""
        try:
            updates = []
            params = []
            param_count = 1
            
            if title is not None:
                updates.append(f"title = ${param_count}")
                params.append(title)
                param_count += 1
            
            if body_md is not None:
                updates.append(f"body_md = ${param_count}")
                params.append(body_md)
                param_count += 1
            
            if status is not None:
                updates.append(f"status = ${param_count}")
                params.append(status)
                param_count += 1
            
            if scheduled_at is not None:
                updates.append(f"scheduled_at = ${param_count}")
                params.append(scheduled_at)
                param_count += 1
            
            updates.append(f"updated_at = ${param_count}")
            params.append(datetime.now(timezone.utc))
            param_count += 1
            
            params.append(post_id)
            
            query = f"""
                UPDATE posts 
                SET {', '.join(updates)}
                WHERE id = ${param_count}
            """
            
            result = await db.execute(query, *params)
            logger.info("Post %s updated", post_id)
            return True
        except Exception as e:
            logger.error("Failed to update post %s: %s", post_id, e)
            raise
    
    async def get_posts_by_channel(self, channel_id: int, status: Optional[str] = None,
                                  limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        """Получает посты канала"""
        try:
            where_clause = "WHERE p.channel_id = $1"
            params = [channel_id]
            param_count = 1
            
            if status:
                param_count += 1
                where_clause += f" AND p.status = ${param_count}"
                params.append(status)
            
            query = f"""
                SELECT p.*, c.title as channel_title, s.title as series_title
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                LEFT JOIN series s ON p.series_id = s.id
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT ${param_count + 1} OFFSET ${param_count + 2}
            """
            params.extend([limit, offset])
            
            results = await db.fetch_all(query, *params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get posts for channel %s: %s", channel_id, e)
            raise
    
    async def get_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Получает посты для публикации"""
        try:
            query = """
                SELECT p.*, c.tg_channel_id, c.title as channel_title
                FROM posts p
                JOIN channels c ON p.channel_id = c.id
                WHERE p.status = 'scheduled' 
                AND p.scheduled_at <= NOW()
                ORDER BY p.scheduled_at ASC
            """
            results = await db.fetch_all(query)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get scheduled posts: %s", e)
            raise
    
    async def publish_post(self, post_id: int, message_id: int) -> bool:
        """Помечает пост как опубликованный"""
        try:
            logger.info(f"🔄 Обновляем статус поста {post_id} на 'published' с message_id {message_id}")
            
            query = """
                UPDATE posts 
                SET status = 'published', 
                    published_at = NOW(),
                    message_id = $2,
                    updated_at = NOW()
                WHERE id = $1
            """
            
            result = await db.execute(query, post_id, message_id)
            logger.info(f"✅ SQL UPDATE выполнен: {result}")
            
            # Проверяем, что пост действительно обновился
            updated_post = await db.fetch_one("""
                SELECT id, status, published_at, message_id 
                FROM posts 
                WHERE id = $1
            """, post_id)
            
            if updated_post:
                logger.info(f"✅ Подтверждение обновления: ID={updated_post['id']}, status={updated_post['status']}, published_at={updated_post['published_at']}, message_id={updated_post['message_id']}")
            else:
                logger.error(f"❌ Пост {post_id} не найден после обновления!")
            
            logger.info("Post %s published with message_id %s", post_id, message_id)
            return True
        except Exception as e:
            logger.error("Failed to publish post %s: %s", post_id, e)
            raise
    
    async def publish_scheduled_posts(self, bot) -> int:
        """Публикует все готовые к публикации посты"""
        logger.info("=== НАЧАЛО ПУБЛИКАЦИИ ОТЛОЖЕННЫХ ПОСТОВ ===")
        
        try:
            # Получаем посты для публикации
            scheduled_posts = await self.get_scheduled_posts()
            logger.info(f"📋 Найдено {len(scheduled_posts)} постов для публикации")
            
            if not scheduled_posts:
                logger.info("📭 Нет постов для публикации")
                return 0
            
            published_count = 0
            
            for post in scheduled_posts:
                try:
                    logger.info(f"📤 Публикуем пост ID {post['id']}: '{post['body_md'][:50]}...'")
                    
                    # Используем PostPublisher для публикации
                    from services.publisher import get_publisher
                    publisher = get_publisher()
                    
                    post_data = {
                        'id': post['id'],
                        'body_md': post['body_md'],
                        'entities': post.get('entities')  # Если есть entities
                    }
                    
                    results = await publisher.publish_post(
                        post_data, 
                        [post['tg_channel_id']], 
                        update_db=True
                    )
                    
                    if results['success_count'] > 0:
                        published_count += 1
                        logger.info(f"✅ Пост {post['id']} успешно опубликован в канал {post['tg_channel_id']}")
                    else:
                        logger.error(f"❌ Не удалось опубликовать пост {post['id']}")
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка публикации поста {post['id']}: {e}")
                    continue
            
            logger.info(f"✅ ПУБЛИКАЦИЯ ЗАВЕРШЕНА: {published_count}/{len(scheduled_posts)} постов")
            return published_count
            
        except Exception as e:
            logger.error(f"❌ Ошибка публикации отложенных постов: {e}")
            raise
    
    async def delete_post(self, post_id: int) -> bool:
        """Удаляет пост (мягкое удаление)"""
        try:
            query = """
                UPDATE posts 
                SET status = 'deleted', updated_at = NOW()
                WHERE id = $1
            """
            await db.execute(query, post_id)
            logger.info("Post %s deleted", post_id)
            return True
        except Exception as e:
            logger.error("Failed to delete post %s: %s", post_id, e)
            raise
    
    async def validate_post_text(self, text: str) -> tuple[bool, str]:
        """Валидирует текст поста"""
        if not text or not text.strip():
            return False, "Текст поста не может быть пустым"
        
        if len(text) > config.MAX_POST_LENGTH:
            return False, f"Текст поста слишком длинный (максимум {config.MAX_POST_LENGTH} символов)"
        
        return True, ""

# Глобальный экземпляр сервиса
post_service = PostService()
