# Service: export

from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json

from database import db

logger = logging.getLogger(__name__)

class ExportService:
    """Сервис для экспорта данных"""
    
    async def export_posts_to_json(self, channel_id: Optional[int] = None, 
                                 limit: int = 100) -> Dict[str, Any]:
        """Экспорт постов в JSON формат"""
        try:
            where_clause = ""
            params = []
            
            if channel_id:
                where_clause = "WHERE p.channel_id = $1"
                params.append(channel_id)
            
            query = f"""
                SELECT 
                    p.*,
                    c.title as channel_title
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT ${len(params) + 1}
            """
            params.append(limit)
            
            posts = await db.fetch_all(query, *params)
            
            # Конвертируем посты в словари и обрабатываем datetime
            posts_data = []
            for post in posts:
                post_dict = dict(post)
                # Конвертируем все datetime объекты в строки
                for key, value in post_dict.items():
                    if isinstance(value, datetime):
                        post_dict[key] = value.isoformat()
                posts_data.append(post_dict)
            
            export_data = {
                "export_info": {
                    "created_at": datetime.now().isoformat(),
                    "total_posts": len(posts),
                    "channel_id": channel_id
                },
                "posts": posts_data
            }
            
            return export_data
            
        except Exception as e:
            logger.error("Failed to export posts to JSON: %s", e)
            raise
    
    async def export_posts_to_markdown(self, channel_id: Optional[int] = None, 
                                     limit: int = 100) -> str:
        """Экспорт постов в Markdown формат"""
        try:
            where_clause = ""
            params = []
            
            if channel_id:
                where_clause = "WHERE p.channel_id = $1"
                params.append(channel_id)
            
            query = f"""
                SELECT 
                    p.*,
                    c.title as channel_title
                FROM posts p
                LEFT JOIN channels c ON p.channel_id = c.id
                {where_clause}
                ORDER BY p.created_at DESC
                LIMIT ${len(params) + 1}
            """
            params.append(limit)
            
            posts = await db.fetch_all(query, *params)
            
            markdown = f"# Экспорт постов\n\n"
            markdown += f"**Дата экспорта:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n"
            markdown += f"**Всего постов:** {len(posts)}\n\n"
            
            if channel_id:
                channel = posts[0] if posts else None
                if channel:
                    markdown += f"**Канал:** {channel['channel_title']}\n\n"
            
            markdown += "---\n\n"
            
            for i, post in enumerate(posts, 1):
                markdown += f"## Пост #{i}\n\n"
                markdown += f"**ID:** {post['id']}\n"
                markdown += f"**Статус:** {post['status']}\n"
                markdown += f"**Создан:** {post['created_at'].strftime('%d.%m.%Y %H:%M')}\n"
                
                if post['scheduled_at']:
                    markdown += f"**Запланирован:** {post['scheduled_at'].strftime('%d.%m.%Y %H:%M')}\n"
                
                if post['published_at']:
                    markdown += f"**Опубликован:** {post['published_at'].strftime('%d.%m.%Y %H:%M')}\n"
                
                markdown += f"**Канал:** {post['channel_title']}\n\n"
                
                if post.get('text'):
                    markdown += f"**Текст:**\n{post['text']}\n\n"
                
                if post.get('tags_cache'):
                    tags = post['tags_cache'] if isinstance(post['tags_cache'], list) else []
                    if tags:
                        markdown += f"**Теги:** {', '.join(tags)}\n\n"
                
                markdown += "---\n\n"
            
            return markdown
            
        except Exception as e:
            logger.error("Failed to export posts to Markdown: %s", e)
            raise
    
    async def get_export_stats(self, channel_id: Optional[int] = None) -> Dict[str, Any]:
        """Получение статистики для экспорта"""
        try:
            where_clause = ""
            params = []
            
            if channel_id:
                where_clause = "WHERE channel_id = $1"
                params.append(channel_id)
            
            # Общая статистика
            stats_query = f"""
                SELECT 
                    COUNT(*) as total_posts,
                    COUNT(CASE WHEN status = 'published' THEN 1 END) as published_posts,
                    COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_posts,
                    COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_posts,
                    COUNT(CASE WHEN status = 'deleted' THEN 1 END) as deleted_posts
                FROM posts
                {where_clause}
            """
            
            stats = await db.fetch_one(stats_query, *params)
            
            # Статистика по каналам
            channels_query = """
                SELECT 
                    c.title,
                    COUNT(p.id) as posts_count
                FROM channels c
                LEFT JOIN posts p ON c.id = p.channel_id
                GROUP BY c.id, c.title
                ORDER BY posts_count DESC
            """
            
            channels = await db.fetch_all(channels_query)
            
            return {
                "total_posts": stats['total_posts'],
                "published_posts": stats['published_posts'],
                "scheduled_posts": stats['scheduled_posts'],
                "draft_posts": stats['draft_posts'],
                "deleted_posts": stats['deleted_posts'],
                "channels": [dict(channel) for channel in channels]
            }
            
        except Exception as e:
            logger.error("Failed to get export stats: %s", e)
            raise

# Глобальный экземпляр сервиса
export_service = ExportService()
