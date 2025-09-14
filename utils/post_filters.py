"""
@file: utils/post_filters.py
@description: Компонент для фильтрации и сортировки постов
@dependencies: aiogram, datetime
@created: 2025-09-13
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta

class PostFilters:
    def __init__(self):
        self.date_filters = {
            'today': 'Сегодня',
            'week': 'Неделя', 
            'month': 'Месяц',
            'all': 'Все время'
        }
        
        self.status_filters = {
            'all': 'Все',
            'published': 'Опубликованные',
            'scheduled': 'Отложенные',
            'failed': 'Неудачные',
            'deleted': 'Удаленные'
        }
        
        self.sort_options = {
            'date_desc': 'По дате (новые)',
            'date_asc': 'По дате (старые)',
            'status': 'По статусу',
            'channel': 'По каналу',
            'views': 'По просмотрам'
        }
    
    def create_filters_keyboard(self, current_filters: dict = None) -> InlineKeyboardMarkup:
        """Создает клавиатуру фильтров"""
        if not current_filters:
            current_filters = {
                'date': 'all',
                'status': 'all', 
                'sort': 'date_desc'
            }
        
        buttons = []
        
        # Фильтры по дате
        date_row = []
        for key, label in self.date_filters.items():
            emoji = "✅" if current_filters.get('date') == key else "⚪"
            date_row.append(InlineKeyboardButton(
                f"{emoji} {label}", 
                callback_data=f"filter_date_{key}"
            ))
        buttons.append(date_row)
        
        # Фильтры по статусу
        status_row = []
        for key, label in self.status_filters.items():
            emoji = "✅" if current_filters.get('status') == key else "⚪"
            status_row.append(InlineKeyboardButton(
                f"{emoji} {label}", 
                callback_data=f"filter_status_{key}"
            ))
        buttons.append(status_row)
        
        # Сортировка
        sort_row = []
        for key, label in self.sort_options.items():
            emoji = "✅" if current_filters.get('sort') == key else "⚪"
            sort_row.append(InlineKeyboardButton(
                f"{emoji} {label}", 
                callback_data=f"filter_sort_{key}"
            ))
        buttons.append(sort_row)
        
        # Кнопки управления
        control_row = [
            InlineKeyboardButton("🔍 Поиск", callback_data="search_posts"),
            InlineKeyboardButton("📊 Статистика", callback_data="weekly_stats"),
            InlineKeyboardButton("☑️ Выбрать все", callback_data="select_all_posts")
        ]
        buttons.append(control_row)
        
        return InlineKeyboardMarkup(inline_keyboard=buttons)
    
    def apply_filters(self, posts: list, filters: dict) -> list:
        """Применяет фильтры к списку постов"""
        filtered_posts = posts.copy()
        
        # Фильтр по дате
        if filters.get('date') != 'all':
            now = datetime.now()
            if filters['date'] == 'today':
                start_date = now.replace(hour=0, minute=0, second=0, microsecond=0)
                filtered_posts = [p for p in filtered_posts if p['created_at'] >= start_date]
            elif filters['date'] == 'week':
                start_date = now - timedelta(days=7)
                filtered_posts = [p for p in filtered_posts if p['created_at'] >= start_date]
            elif filters['date'] == 'month':
                start_date = now - timedelta(days=30)
                filtered_posts = [p for p in filtered_posts if p['created_at'] >= start_date]
        
        # Фильтр по статусу
        if filters.get('status') != 'all':
            filtered_posts = [p for p in filtered_posts if p['status'] == filters['status']]
        
        # Сортировка
        if filters.get('sort') == 'date_desc':
            filtered_posts.sort(key=lambda x: x['created_at'], reverse=True)
        elif filters.get('sort') == 'date_asc':
            filtered_posts.sort(key=lambda x: x['created_at'])
        elif filters.get('sort') == 'status':
            filtered_posts.sort(key=lambda x: x['status'])
        elif filters.get('sort') == 'views':
            filtered_posts.sort(key=lambda x: x.get('views', 0), reverse=True)
        
        return filtered_posts
