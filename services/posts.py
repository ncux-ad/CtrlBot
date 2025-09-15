# Service: posts

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
import logging

from database import db
from config import config

logger = logging.getLogger(__name__)

class PostService:
    """Сервис для работы с постами"""
    
    async def create_post(self, channel_id: int, title: Optional[str], 
                         body_md: str, user_id: int, series_id: Optional[int] = None,
                         scheduled_at: Optional[datetime] = None, tag_ids: Optional[List[int]] = None) -> int:
        """Создает новый пост"""
        try:
            # Определяем статус
            status = 'scheduled' if scheduled_at else 'draft'
            
            query = """
                INSERT INTO posts (channel_id, title, body_md, status, series_id, scheduled_at, created_at, updated_at)
                VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                RETURNING id
            """
            post_id = await db.fetch_val(query, channel_id, title, body_md, status, series_id, scheduled_at)
            
            # Добавляем теги если есть
            if tag_ids:
                from services.tags import tag_service
                for tag_id in tag_ids:
                    await tag_service.add_tag_to_post(post_id, tag_id)
                
                # Обновляем кеш тегов
                await tag_service.update_post_tags_cache(post_id)
            
            # Если есть серия, увеличиваем номер
            if series_id:
                from services.series import series_service
                await series_service.increment_series_number(series_id)
            
            logger.info("Post created: %s for channel %s by user %s (series: %s, tags: %s)", 
                       post_id, channel_id, user_id, series_id, tag_ids)
            return post_id
        except Exception as e:
            logger.error("Failed to create post: %s", e)
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
            return dict(result) if result else None
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
            query = """
                UPDATE posts 
                SET status = 'published', 
                    published_at = NOW(),
                    message_id = $2,
                    updated_at = NOW()
                WHERE id = $1
            """
            await db.execute(query, post_id, message_id)
            logger.info("Post %s published with message_id %s", post_id, message_id)
            return True
        except Exception as e:
            logger.error("Failed to publish post %s: %s", post_id, e)
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
    
    async def get_all_posts(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Получение всех постов"""
        try:
            query = """
                SELECT p.*, c.title as channel_title
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                ORDER BY p.created_at DESC
                LIMIT $1 OFFSET $2
            """
            posts = await db.fetch_all(query, limit, offset)
            return [dict(post) for post in posts]
        except Exception as e:
            logger.error("Failed to get all posts: %s", e)
            return []
    
    async def cancel_scheduled_post(self, post_id: int) -> bool:
        """Отмена запланированного поста"""
        try:
            # Проверяем, что пост существует и запланирован
            post = await db.fetch_one(
                "SELECT id, status FROM posts WHERE id = $1", post_id
            )
            
            if not post:
                logger.warning("Post %s not found", post_id)
                return False
            
            if post['status'] != 'scheduled':
                logger.warning("Post %s is not scheduled (status: %s)", post_id, post['status'])
                return False
            
            # Меняем статус на черновик
            await db.execute(
                "UPDATE posts SET status = 'draft', scheduled_at = NULL WHERE id = $1",
                post_id
            )
            
            logger.info("Cancelled scheduled post %s", post_id)
            return True
            
        except Exception as e:
            logger.error("Failed to cancel scheduled post %s: %s", post_id, e)
            return False
    
    async def retry_failed_post(self, post_id: int) -> bool:
        """Повторная попытка публикации неудачного поста"""
        try:
            # Проверяем, что пост существует и имеет статус failed
            post = await db.fetch_one(
                "SELECT id, status FROM posts WHERE id = $1", post_id
            )
            
            if not post:
                logger.warning("Post %s not found", post_id)
                return False
            
            if post['status'] != 'failed':
                logger.warning("Post %s is not failed (status: %s)", post_id, post['status'])
                return False
            
            # Меняем статус на черновик для повторной попытки
            await db.execute(
                "UPDATE posts SET status = 'draft' WHERE id = $1",
                post_id
            )
            
            logger.info("Retrying failed post %s", post_id)
            return True
            
        except Exception as e:
            logger.error("Failed to retry post %s: %s", post_id, e)
            return False
    
    async def update_scheduled_time(self, post_id: int, new_scheduled_at: datetime) -> bool:
        """Обновление времени публикации запланированного поста"""
        try:
            # Проверяем, что пост существует и запланирован
            post = await db.fetch_one(
                "SELECT id, status FROM posts WHERE id = $1", post_id
            )
            
            if not post:
                logger.warning("Post %s not found", post_id)
                return False
            
            if post['status'] != 'scheduled':
                logger.warning("Post %s is not scheduled (status: %s)", post_id, post['status'])
                return False
            
            # Обновляем время публикации
            await db.execute(
                "UPDATE posts SET scheduled_at = $1 WHERE id = $2",
                new_scheduled_at, post_id
            )
            
            logger.info("Updated scheduled time for post %s to %s", post_id, new_scheduled_at)
            return True
            
        except Exception as e:
            logger.error("Failed to update scheduled time for post %s: %s", post_id, e)
            return False
    
    async def publish_scheduled_posts(self) -> List[Dict[str, Any]]:
        """Публикация запланированных постов (вызывается планировщиком)"""
        try:
            # Получаем посты, которые нужно опубликовать
            now = datetime.now(timezone.utc)
            posts = await db.fetch_all(
                """
                SELECT p.*, c.tg_channel_id, c.title as channel_title
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                WHERE p.status = 'scheduled' 
                AND p.scheduled_at <= $1
                ORDER BY p.scheduled_at ASC
                """,
                now
            )
            
            published_posts = []
            
            for post in posts:
                try:
                    # Здесь должна быть логика публикации через PostPublisher
                    # Пока просто меняем статус на published
                    await db.execute(
                        "UPDATE posts SET status = 'published', published_at = NOW() WHERE id = $1",
                        post['id']
                    )
                    
                    published_posts.append(dict(post))
                    logger.info("Published scheduled post %s", post['id'])
                    
                except Exception as e:
                    logger.error("Failed to publish post %s: %s", post['id'], e)
                    # Меняем статус на failed
                    await db.execute(
                        "UPDATE posts SET status = 'failed' WHERE id = $1",
                        post['id']
                    )
            
            logger.info("Published %s scheduled posts", len(published_posts))
            return published_posts
            
        except Exception as e:
            logger.error("Failed to publish scheduled posts: %s", e)
            return []

# Глобальный экземпляр сервиса
post_service = PostService()
