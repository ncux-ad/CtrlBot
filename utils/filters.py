# Utils: filters

from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from typing import List
from config import config

class IsAdminFilter(BaseFilter):
    """Фильтр для проверки админских прав"""
    
    def __init__(self, admin_ids: List[int]):
        self.admin_ids = admin_ids
    
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

class IsChannelFilter(BaseFilter):
    """Фильтр для сообщений из каналов"""
    
    async def __call__(self, message: Message) -> bool:
        return message.chat.type in ['channel', 'supergroup']

class IsPrivateFilter(BaseFilter):
    """Фильтр для приватных сообщений"""
    
    async def __call__(self, message: Message) -> bool:
        return message.chat.type == 'private'

class PostTextFilter(BaseFilter):
    """Фильтр для текста поста (не команды)"""
    
    async def __call__(self, message: Message) -> bool:
        return (
            message.text is not None 
            and not message.text.startswith('/')
            and len(message.text.strip()) > 0
        )

class CallbackDataFilter(BaseFilter):
    """Фильтр для callback данных"""
    
    def __init__(self, prefix: str):
        self.prefix = prefix
    
    async def __call__(self, callback: CallbackQuery) -> bool:
        return callback.data and callback.data.startswith(self.prefix)

class TagCallbackFilter(CallbackDataFilter):
    """Фильтр для callback тегов"""
    
    def __init__(self):
        super().__init__("toggle_tag_")

class SeriesCallbackFilter(CallbackDataFilter):
    """Фильтр для callback серий"""
    
    def __init__(self):
        super().__init__("select_series_")

class ScheduleCallbackFilter(CallbackDataFilter):
    """Фильтр для callback планирования"""
    
    def __init__(self):
        super().__init__("schedule_")

class AdminCallbackFilter(CallbackDataFilter):
    """Фильтр для админских callback"""
    
    def __init__(self):
        super().__init__("manage_")

class IsConfigAdminFilter(BaseFilter):
    """Фильтр для проверки админских прав из конфигурации"""
    
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in config.ADMIN_IDS
