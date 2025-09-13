"""
@file: utils/pagination.py
@description: Централизованная система пагинации для больших списков
@created: 2025-09-13
"""

from typing import List, Dict, Any, Optional, Tuple
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from utils.logging import get_logger

logger = get_logger(__name__)

class PaginationManager:
    """Менеджер пагинации для больших списков"""
    
    def __init__(self, items_per_page: int = 10, max_pages: int = 100):
        self.items_per_page = items_per_page
        self.max_pages = max_pages
    
    def get_page_info(self, total_items: int, current_page: int = 1) -> Dict[str, Any]:
        """Получает информацию о странице"""
        total_pages = max(1, (total_items + self.items_per_page - 1) // self.items_per_page)
        current_page = max(1, min(current_page, total_pages))
        
        start_index = (current_page - 1) * self.items_per_page
        end_index = min(start_index + self.items_per_page, total_items)
        
        return {
            'current_page': current_page,
            'total_pages': total_pages,
            'total_items': total_items,
            'start_index': start_index,
            'end_index': end_index,
            'has_previous': current_page > 1,
            'has_next': current_page < total_pages,
            'items_on_page': end_index - start_index
        }
    
    def get_page_items(self, items: List[Any], current_page: int = 1) -> Tuple[List[Any], Dict[str, Any]]:
        """Получает элементы для текущей страницы"""
        page_info = self.get_page_info(len(items), current_page)
        page_items = items[page_info['start_index']:page_info['end_index']]
        return page_items, page_info
    
    def create_pagination_keyboard(
        self, 
        page_info: Dict[str, Any], 
        callback_prefix: str,
        additional_buttons: Optional[List[List[InlineKeyboardButton]]] = None
    ) -> InlineKeyboardMarkup:
        """Создает клавиатуру пагинации"""
        keyboard = []
        
        # Кнопки навигации
        nav_buttons = []
        
        if page_info['has_previous']:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️", 
                callback_data=f"{callback_prefix}_page_{page_info['current_page'] - 1}"
            ))
        
        # Информация о странице
        nav_buttons.append(InlineKeyboardButton(
            text=f"{page_info['current_page']}/{page_info['total_pages']}", 
            callback_data="pagination_info"
        ))
        
        if page_info['has_next']:
            nav_buttons.append(InlineKeyboardButton(
                text="➡️", 
                callback_data=f"{callback_prefix}_page_{page_info['current_page'] + 1}"
            ))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Дополнительные кнопки
        if additional_buttons:
            keyboard.extend(additional_buttons)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    def create_posts_pagination_keyboard(
        self,
        page_info: Dict[str, Any],
        posts: List[Dict[str, Any]],
        callback_prefix: str = "posts"
    ) -> InlineKeyboardMarkup:
        """Создает клавиатуру пагинации для постов с кнопками управления"""
        keyboard = []
        
        # Кнопки для каждого поста на странице
        for i, post in enumerate(posts, page_info['start_index'] + 1):
            post_buttons = []
            
            # Кнопка просмотра
            post_buttons.append(InlineKeyboardButton(
                text=f"👁️ {i}", 
                callback_data=f"view_post_{post['id']}"
            ))
            
            # Кнопка удаления (только для не удаленных)
            if post['status'] != 'deleted':
                post_buttons.append(InlineKeyboardButton(
                    text=f"🗑️ {i}", 
                    callback_data=f"delete_post_{post['id']}"
                ))
            
            keyboard.append(post_buttons)
        
        # Кнопки навигации
        nav_buttons = []
        
        if page_info['has_previous']:
            nav_buttons.append(InlineKeyboardButton(
                text="⬅️", 
                callback_data=f"{callback_prefix}_page_{page_info['current_page'] - 1}"
            ))
        
        nav_buttons.append(InlineKeyboardButton(
            text=f"{page_info['current_page']}/{page_info['total_pages']}", 
            callback_data="pagination_info"
        ))
        
        if page_info['has_next']:
            nav_buttons.append(InlineKeyboardButton(
                text="➡️", 
                callback_data=f"{callback_prefix}_page_{page_info['current_page'] + 1}"
            ))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        # Общие кнопки
        keyboard.append([
            InlineKeyboardButton(text="📝 Создать пост", callback_data="create_post"),
            InlineKeyboardButton(text="🔙 Назад в админ-панель", callback_data="main_menu")
        ])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Глобальный экземпляр
pagination_manager = PaginationManager(items_per_page=10, max_pages=100)

def get_pagination_manager() -> PaginationManager:
    """Получает глобальный экземпляр менеджера пагинации"""
    return pagination_manager
