"""
@file: utils/weekly_stats_scheduler.py
@description: Планировщик еженедельной статистики постов
@dependencies: apscheduler, services.post_service, utils.post_statistics
@created: 2025-09-13
"""

import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram.enums import ParseMode
from services.post_service import post_service
from utils.post_statistics import PostStatistics
from utils.logging import get_logger

logger = get_logger(__name__)

class WeeklyStatsScheduler:
    def __init__(self, bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.stats_calculator = PostStatistics()
        
    def start(self):
        """Запускает планировщик еженедельной статистики"""
        # Каждую субботу в 12:00
        self.scheduler.add_job(
            self.send_weekly_stats,
            'cron',
            day_of_week=6,  # Суббота
            hour=12,
            minute=0,
            id='weekly_stats'
        )
        self.scheduler.start()
        logger.info("📊 Еженедельная статистика запланирована на субботы в 12:00")
    
    async def send_weekly_stats(self):
        """Отправляет еженедельную статистику"""
        try:
            # Получаем все посты
            posts = await post_service.get_all_posts()
            
            # Рассчитываем статистику
            stats = await self.stats_calculator.calculate_weekly_stats(posts)
            
            # Форматируем сообщение
            message = self.stats_calculator.format_weekly_stats(stats)
            
            # Отправляем админам
            admin_ids = [439304619]  # Замените на реальные ID админов
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(admin_id, message, parse_mode=ParseMode.MARKDOWN_V2)
                    logger.info(f"📊 Еженедельная статистика отправлена админу {admin_id}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки статистики админу {admin_id}: {e}")
                    
        except Exception as e:
            logger.error(f"❌ Ошибка расчета еженедельной статистики: {e}")
    
    def stop(self):
        """Останавливает планировщик"""
        self.scheduler.shutdown()
        logger.info("📊 Планировщик еженедельной статистики остановлен")
