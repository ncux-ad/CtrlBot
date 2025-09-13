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
                         body_md: str, user_id: int) -> int:
        """Создает новый пост"""
        try:
            query = """
                INSERT INTO posts (channel_id, title, body_md, status, created_at, updated_at)
                VALUES ($1, $2, $3, 'draft', NOW(), NOW())
                RETURNING id
            """
            post_id = await db.fetch_val(query, channel_id, title, body_md)
            logger.info("Post created: %s for channel %s by user %s", post_id, channel_id, user_id)
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

# Глобальный экземпляр сервиса
post_service = PostService()
