# Service: series

from typing import List, Optional, Dict, Any
import logging

from database import db

logger = logging.getLogger(__name__)

class SeriesService:
    """Сервис для работы с сериями"""
    
    async def create_series(self, channel_id: int, code: str, title: str) -> int:
        """Создает новую серию"""
        try:
            query = """
                INSERT INTO series (channel_id, code, title, next_number)
                VALUES ($1, $2, $3, 1)
                ON CONFLICT (channel_id, code) DO UPDATE SET
                    title = EXCLUDED.title,
                    id = series.id
                RETURNING id
            """
            series_id = await db.fetch_val(query, channel_id, code, title)
            logger.info("Series created/updated: %s (%s) for channel %s", code, title, channel_id)
            return series_id
        except Exception as e:
            logger.error("Failed to create series %s: %s", code, e)
            raise
    
    async def get_series_by_channel(self, channel_id: int) -> List[Dict[str, Any]]:
        """Получает серии канала"""
        try:
            query = """
                SELECT * FROM series 
                WHERE channel_id = $1
                ORDER BY title ASC
            """
            results = await db.fetch_all(query, channel_id)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get series for channel %s: %s", channel_id, e)
            raise
    
    async def get_series(self, series_id: int) -> Optional[Dict[str, Any]]:
        """Получает серию по ID"""
        try:
            query = "SELECT * FROM series WHERE id = $1"
            result = await db.fetch_one(query, series_id)
            return dict(result) if result else None
        except Exception as e:
            logger.error("Failed to get series %s: %s", series_id, e)
            raise
    
    async def update_series(self, series_id: int, title: Optional[str] = None, 
                           next_number: Optional[int] = None) -> bool:
        """Обновляет серию"""
        try:
            updates = []
            params = []
            param_count = 1
            
            if title is not None:
                updates.append(f"title = ${param_count}")
                params.append(title)
                param_count += 1
            
            if next_number is not None:
                updates.append(f"next_number = ${param_count}")
                params.append(next_number)
                param_count += 1
            
            if not updates:
                return True
            
            params.append(series_id)
            
            query = f"""
                UPDATE series 
                SET {', '.join(updates)}
                WHERE id = ${param_count}
            """
            
            await db.execute(query, *params)
            logger.info("Series %s updated", series_id)
            return True
        except Exception as e:
            logger.error("Failed to update series %s: %s", series_id, e)
            raise
    
    async def delete_series(self, series_id: int) -> bool:
        """Удаляет серию"""
        try:
            query = "DELETE FROM series WHERE id = $1"
            await db.execute(query, series_id)
            logger.info("Series %s deleted", series_id)
            return True
        except Exception as e:
            logger.error("Failed to delete series %s: %s", series_id, e)
            raise
    
    async def get_next_number(self, series_id: int) -> int:
        """Получает следующий номер в серии"""
        try:
            query = "SELECT next_number FROM series WHERE id = $1"
            next_number = await db.fetch_val(query, series_id)
            return next_number or 1
        except Exception as e:
            logger.error("Failed to get next number for series %s: %s", series_id, e)
            return 1
    
    async def increment_series_number(self, series_id: int) -> int:
        """Увеличивает номер серии и возвращает новый номер"""
        try:
            query = """
                UPDATE series 
                SET next_number = next_number + 1
                WHERE id = $1
                RETURNING next_number
            """
            new_number = await db.fetch_val(query, series_id)
            logger.info("Series %s number incremented to %s", series_id, new_number)
            return new_number or 1
        except Exception as e:
            logger.error("Failed to increment series %s number: %s", series_id, e)
            return 1
    
    async def validate_series_code(self, code: str) -> tuple[bool, str]:
        """Валидирует код серии"""
        if not code or not code.strip():
            return False, "Код серии не может быть пустым"
        
        if len(code) > 50:
            return False, "Код серии слишком длинный (максимум 50 символов)"
        
        # Проверяем на недопустимые символы
        if any(char in code for char in ['#', '@', ' ', '\n', '\t']):
            return False, "Код серии содержит недопустимые символы"
        
        return True, ""
    
    async def get_all_series(self) -> List[Dict[str, Any]]:
        """Получение всех серий с количеством постов"""
        try:
            query = """
                SELECT 
                    s.*,
                    COUNT(p.id) as posts_count
                FROM series s
                LEFT JOIN posts p ON s.id = p.series_id
                GROUP BY s.id, s.channel_id, s.code, s.title, s.next_number, s.created_at
                ORDER BY s.title ASC
            """
            results = await db.fetch_all(query)
            return [dict(row) for row in results]
        except Exception as e:
            logger.error("Failed to get all series: %s", e)
            return []

# Глобальный экземпляр сервиса
series_service = SeriesService()
