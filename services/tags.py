# Service: tags

from typing import List, Optional, Dict, Any
import logging

from database import db

logger = logging.getLogger(__name__)

class TagService:
    """Сервис для работы с тегами"""
    
    async def create_tag(self, channel_id: int, name: str, kind: str = 'regular') -> int:
        """Создает новый тег"""
        try:
            query = """
                INSERT INTO tags (channel_id, name, kind)
                VALUES ($1, $2, $3)
                ON CONFLICT (channel_id, name) DO UPDATE SET
                    kind = EXCLUDED.kind,
                    id = tags.id
                RETURNING id
            """
            tag_id = await db.fetch_val(query, channel_id, name, kind)
            logger.info("Tag created/updated: %s (%s) for channel %s", name, kind, channel_id)
            return tag_id
        except Exception as e:
            logger.error("Failed to create tag %s: %s", name, e)
            raise
    
    async def get_tags_by_channel(self, channel_id: int, kind: Optional[str] = None) -> List[Dict[str, Any]]:
        """Получает теги канала"""
        try:
            where_clause = "WHERE channel_id = $1"
            params = [channel_id]
            
            if kind:
                where_clause += " AND kind = $2"
                params.append(kind)
            
            query = f"""
                SELECT * FROM tags 
                {where_clause}
                ORDER BY name ASC
            """
            results = await db.fetch_all(query, *params)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get tags for channel %s: %s", channel_id, e)
            raise
    
    async def get_tag(self, tag_id: int) -> Optional[Dict[str, Any]]:
        """Получает тег по ID"""
        try:
            query = "SELECT * FROM tags WHERE id = $1"
            result = await db.fetch_one(query, tag_id)
            return dict(result) if result else None
        except Exception as e:
            logger.error("Failed to get tag %s: %s", tag_id, e)
            raise
    
    async def update_tag(self, tag_id: int, name: Optional[str] = None, 
                        kind: Optional[str] = None) -> bool:
        """Обновляет тег"""
        try:
            updates = []
            params = []
            param_count = 1
            
            if name is not None:
                updates.append(f"name = ${param_count}")
                params.append(name)
                param_count += 1
            
            if kind is not None:
                updates.append(f"kind = ${param_count}")
                params.append(kind)
                param_count += 1
            
            if not updates:
                return True
            
            params.append(tag_id)
            
            query = f"""
                UPDATE tags 
                SET {', '.join(updates)}
                WHERE id = ${param_count}
            """
            
            await db.execute(query, *params)
            logger.info("Tag %s updated", tag_id)
            return True
        except Exception as e:
            logger.error("Failed to update tag %s: %s", tag_id, e)
            raise
    
    async def delete_tag(self, tag_id: int) -> bool:
        """Удаляет тег"""
        try:
            query = "DELETE FROM tags WHERE id = $1"
            await db.execute(query, tag_id)
            logger.info("Tag %s deleted", tag_id)
            return True
        except Exception as e:
            logger.error("Failed to delete tag %s: %s", tag_id, e)
            raise
    
    async def add_tag_to_post(self, post_id: int, tag_id: int) -> bool:
        """Добавляет тег к посту"""
        try:
            query = """
                INSERT INTO post_tags (post_id, tag_id)
                VALUES ($1, $2)
                ON CONFLICT (post_id, tag_id) DO NOTHING
            """
            await db.execute(query, post_id, tag_id)
            logger.info("Tag %s added to post %s", tag_id, post_id)
            return True
        except Exception as e:
            logger.error("Failed to add tag %s to post %s: %s", tag_id, post_id, e)
            raise
    
    async def remove_tag_from_post(self, post_id: int, tag_id: int) -> bool:
        """Удаляет тег из поста"""
        try:
            query = "DELETE FROM post_tags WHERE post_id = $1 AND tag_id = $2"
            await db.execute(query, post_id, tag_id)
            logger.info("Tag %s removed from post %s", tag_id, post_id)
            return True
        except Exception as e:
            logger.error("Failed to remove tag %s from post %s: %s", tag_id, post_id, e)
            raise
    
    async def get_post_tags(self, post_id: int) -> List[Dict[str, Any]]:
        """Получает теги поста"""
        try:
            query = """
                SELECT t.* FROM tags t
                JOIN post_tags pt ON t.id = pt.tag_id
                WHERE pt.post_id = $1
                ORDER BY t.name ASC
            """
            results = await db.fetch_all(query, post_id)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get tags for post %s: %s", post_id, e)
            raise
    
    async def update_post_tags_cache(self, post_id: int) -> bool:
        """Обновляет кеш тегов поста"""
        try:
            # Получаем теги поста
            tags = await self.get_post_tags(post_id)
            tag_names = [tag['name'] for tag in tags]
            
            # Обновляем кеш
            query = "UPDATE posts SET tags_cache = $1 WHERE id = $2"
            await db.execute(query, tag_names, post_id)
            
            logger.info("Tags cache updated for post %s: %s", post_id, tag_names)
            return True
        except Exception as e:
            logger.error("Failed to update tags cache for post %s: %s", post_id, e)
            raise
    
    async def validate_tag_name(self, name: str) -> tuple[bool, str]:
        """Валидирует название тега"""
        if not name or not name.strip():
            return False, "Название тега не может быть пустым"
        
        if len(name) > 50:
            return False, "Название тега слишком длинное (максимум 50 символов)"
        
        # Проверяем на недопустимые символы
        if any(char in name for char in ['#', '@', ' ', '\n', '\t']):
            return False, "Название тега содержит недопустимые символы"
        
        return True, ""
    
    async def get_all_tags(self) -> List[Dict[str, Any]]:
        """Получение всех тегов с количеством постов"""
        try:
            query = """
                SELECT 
                    t.*,
                    COUNT(pt.post_id) as posts_count
                FROM tags t
                LEFT JOIN post_tags pt ON t.id = pt.tag_id
                GROUP BY t.id, t.channel_id, t.name, t.kind, t.created_at
                ORDER BY t.name ASC
            """
            results = await db.fetch_all(query)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get all tags: %s", e)
            return []

# Глобальный экземпляр сервиса
tag_service = TagService()
