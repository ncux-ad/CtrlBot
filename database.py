# Database connection

import logging
from typing import Optional, List, Any
from contextlib import asynccontextmanager

import asyncpg
from asyncpg import Pool

from config import config

logger = logging.getLogger(__name__)

class Database:
    """Менеджер подключения к PostgreSQL"""
    
    def __init__(self):
        self.pool: Optional[Pool] = None
    
    async def connect(self) -> None:
        """Создает пул подключений к БД"""
        try:
            self.pool = await asyncpg.create_pool(
                host=config.DB_HOST,
                port=config.DB_PORT,
                database=config.DB_NAME,
                user=config.DB_USER,
                password=config.DB_PASSWORD,
                min_size=1,
                max_size=10,
                command_timeout=60
            )
            logger.info("Database connection pool created")
        except Exception as e:
            logger.error("Failed to connect to database: %s", e)
            raise
    
    async def close(self) -> None:
        """Закрывает пул подключений"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection pool closed")
    
    @asynccontextmanager
    async def get_connection(self):
        """Контекстный менеджер для получения подключения"""
        if not self.pool:
            raise RuntimeError("Database not connected")
        
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args) -> str:
        """Выполняет SQL запрос без возврата данных"""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch_one(self, query: str, *args) -> Optional[asyncpg.Record]:
        """Выполняет запрос и возвращает одну запись"""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    async def fetch_all(self, query: str, *args) -> List[asyncpg.Record]:
        """Выполняет запрос и возвращает все записи"""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetch_val(self, query: str, *args) -> Any:
        """Выполняет запрос и возвращает одно значение"""
        async with self.get_connection() as conn:
            return await conn.fetchval(query, *args)
    
    async def init_schema(self) -> None:
        """Инициализирует схему БД из schema.sql"""
        try:
            # Читаем схему из файла
            with open('deploy/schema.sql', 'r', encoding='utf-8') as f:
                schema_sql = f.read()
            
            # Выполняем схему
            await self.execute(schema_sql)
            logger.info("Database schema initialized")
        except Exception as e:
            logger.error("Failed to initialize schema: %s", e)
            raise

# Глобальный экземпляр БД
db = Database()
