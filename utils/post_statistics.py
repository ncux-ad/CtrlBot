"""
@file: utils/post_statistics.py
@description: Компонент для расчета и форматирования статистики постов
@dependencies: datetime, typing
@created: 2025-09-13
"""

from datetime import datetime, timedelta
from typing import Dict, List

class PostStatistics:
    def __init__(self):
        pass
    
    async def calculate_weekly_stats(self, posts: List[Dict]) -> Dict:
        """Рассчитывает еженедельную статистику"""
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        # Фильтруем посты за неделю
        weekly_posts = [p for p in posts if p['created_at'] >= week_ago]
        
        # Общая статистика
        total_posts = len(weekly_posts)
        published = len([p for p in weekly_posts if p['status'] == 'published'])
        scheduled = len([p for p in weekly_posts if p['status'] == 'scheduled'])
        failed = len([p for p in weekly_posts if p['status'] == 'failed'])
        
        # Статистика по просмотрам
        total_views = sum(p.get('views', 0) for p in weekly_posts)
        total_likes = sum(p.get('likes', 0) for p in weekly_posts)
        total_comments = sum(p.get('comments', 0) for p in weekly_posts)
        
        # Топ постов
        top_posts = sorted(weekly_posts, key=lambda x: x.get('views', 0), reverse=True)[:5]
        
        return {
            'period': 'Неделя',
            'total_posts': total_posts,
            'published': published,
            'scheduled': scheduled,
            'failed': failed,
            'total_views': total_views,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'top_posts': top_posts
        }
    
    def format_weekly_stats(self, stats: Dict) -> str:
        """Форматирует еженедельную статистику для отправки"""
        message = f"""
📊 **ЕЖЕНЕДЕЛЬНАЯ СТАТИСТИКА**
Период: {stats['period']}

📝 **ПОСТЫ:**
• Всего: {stats['total_posts']}
• Опубликовано: {stats['published']}
• Отложено: {stats['scheduled']}
• Неудачных: {stats['failed']}

📈 **ВЗАИМОДЕЙСТВИЕ:**
• Просмотры: {stats['total_views']:,}
• Лайки: {stats['total_likes']:,}
• Комментарии: {stats['total_comments']:,}

🏆 **ТОП ПОСТОВ:**
"""
        
        for i, post in enumerate(stats['top_posts'], 1):
            title = post['body_md'][:30] + "..." if len(post['body_md']) > 30 else post['body_md']
            views = post.get('views', 0)
            message += f"{i}. {title} - {views:,} просмотров\n"
        
        return message
