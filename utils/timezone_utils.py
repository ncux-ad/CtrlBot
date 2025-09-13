"""
Утилиты для работы с таймзонами
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import pytz
from config import config

logger = logging.getLogger(__name__)

# Получаем таймзону из конфигурации
TIMEZONE = pytz.timezone(config.TIMEZONE)

def get_now() -> datetime:
    """Получает текущее время в настроенной таймзоне"""
    return datetime.now(TIMEZONE)

def get_utc_now() -> datetime:
    """Получает текущее время в UTC"""
    return datetime.now(pytz.UTC)

def to_timezone(dt: datetime, target_tz: str = None) -> datetime:
    """Конвертирует datetime в указанную таймзону"""
    if target_tz is None:
        target_tz = config.TIMEZONE
    
    if dt.tzinfo is None:
        # Если время без таймзоны, считаем его локальным
        dt = TIMEZONE.localize(dt)
    
    target_timezone = pytz.timezone(target_tz)
    return dt.astimezone(target_timezone)

def to_utc(dt: datetime) -> datetime:
    """Конвертирует datetime в UTC"""
    if dt.tzinfo is None:
        # Если время без таймзоны, считаем его локальным
        dt = TIMEZONE.localize(dt)
    
    return dt.astimezone(pytz.UTC)

def parse_time_input(time_text: str) -> Optional[datetime]:
    """
    Парсит введенное пользователем время в datetime с учетом таймзоны
    
    Поддерживаемые форматы:
    - 15:30 - сегодня в 15:30
    - завтра 15:30 - завтра в 15:30  
    - 25.12.2024 15:30 - конкретная дата
    """
    import re
    
    time_text = time_text.strip().lower()
    scheduled_at = None
    
    try:
        if re.match(r'^\d{1,2}:\d{2}$', time_text):
            # Формат: 15:30
            hour, minute = map(int, time_text.split(':'))
            now = get_now()
            today = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            
            # Если время уже прошло сегодня, планируем на завтра
            if today <= now:
                scheduled_at = today + timedelta(days=1)
                logger.info(f"Время {hour:02d}:{minute:02d} уже прошло, планируем на завтра: {scheduled_at}")
            else:
                scheduled_at = today
                logger.info(f"Планируем на сегодня: {scheduled_at}")
                
        elif time_text.startswith('завтра'):
            # Формат: завтра 15:30
            time_match = re.search(r'(\d{1,2}):(\d{2})', time_text)
            if time_match:
                hour, minute = map(int, time_match.groups())
                tomorrow = get_now() + timedelta(days=1)
                scheduled_at = tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)
                
        elif re.match(r'^\d{1,2}\.\d{1,2}\.\d{4}\s+\d{1,2}:\d{2}$', time_text):
            # Формат: 25.12.2024 15:30
            date_time = datetime.strptime(time_text, '%d.%m.%Y %H:%M')
            scheduled_at = TIMEZONE.localize(date_time)
            
        else:
            logger.warning(f"Неизвестный формат времени: {time_text}")
            return None
            
        # Проверяем, что время в будущем
        if scheduled_at <= get_now():
            logger.warning(f"Время {scheduled_at} уже прошло")
            return None
            
        return scheduled_at
        
    except Exception as e:
        logger.error(f"Ошибка парсинга времени '{time_text}': {e}")
        return None

def format_datetime(dt: datetime, format_str: str = '%d.%m.%Y %H:%M') -> str:
    """Форматирует datetime в строку с учетом таймзоны"""
    if dt.tzinfo is None:
        # Если время без таймзоны, считаем его локальным
        dt = TIMEZONE.localize(dt)
    
    # Конвертируем в локальную таймзону для отображения
    local_dt = dt.astimezone(TIMEZONE)
    result = local_dt.strftime(format_str)
    logger.info(f"format_datetime: {dt} -> {local_dt} -> {result}")
    return result

def get_tomorrow_morning(hour: int = 9, minute: int = 0) -> datetime:
    """Получает завтрашнее утро в указанное время"""
    tomorrow = get_now() + timedelta(days=1)
    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

def get_tomorrow_evening(hour: int = 21, minute: int = 0) -> datetime:
    """Получает завтрашний вечер в указанное время"""
    tomorrow = get_now() + timedelta(days=1)
    return tomorrow.replace(hour=hour, minute=minute, second=0, microsecond=0)

def get_in_hours(hours: int) -> datetime:
    """Получает время через указанное количество часов"""
    return get_now() + timedelta(hours=hours)
