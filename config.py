# Config loader

import os
from typing import Optional, List
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

class Config:
    """Конфигурация приложения"""
    
    # Telegram Bot
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    ADMIN_IDS: List[int] = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
    
    # Database
    DB_HOST: str = os.getenv('DB_HOST', 'localhost')
    DB_PORT: int = int(os.getenv('DB_PORT', '5432'))
    DB_NAME: str = os.getenv('DB_NAME', 'controllerbot_db')
    DB_USER: str = os.getenv('DB_USER', 'controllerbot')
    DB_PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # YandexGPT
    YANDEX_API_KEY: Optional[str] = os.getenv('YANDEX_API_KEY')
    YANDEX_FOLDER_ID: Optional[str] = os.getenv('YANDEX_FOLDER_ID')
    
    # Logging
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', '/var/log/post_bot.log')
    LOG_ERROR_FILE: str = os.getenv('LOG_ERROR_FILE', '/var/log/post_bot.err')
    
    # App settings
    TIMEZONE: str = os.getenv('TIMEZONE', 'Europe/Moscow')
    MAX_POST_LENGTH: int = int(os.getenv('MAX_POST_LENGTH', '4096'))
    MIN_TAGS_REQUIRED: int = int(os.getenv('MIN_TAGS_REQUIRED', '1'))
    
    @classmethod
    def validate(cls) -> bool:
        """Проверяет обязательные настройки"""
        required = [
            cls.BOT_TOKEN,
            cls.DB_PASSWORD,
        ]
        
        missing = [field for field in required if not field]
        if missing:
            raise ValueError(f"Missing required config: {missing}")
        
        # Проверяем, что есть хотя бы один админ
        if not cls.ADMIN_IDS:
            raise ValueError("ADMIN_IDS must contain at least one user ID")
        
        return True

# Глобальный экземпляр конфигурации
config = Config()
