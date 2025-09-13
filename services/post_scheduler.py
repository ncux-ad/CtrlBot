"""
Сервис для планирования публикации отложенных постов
"""
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from services.post_service import post_service

logger = logging.getLogger(__name__)

class PostScheduler:
    """Планировщик для публикации отложенных постов"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': AsyncIOExecutor()},
            job_defaults={'coalesce': False, 'max_instances': 1}
        )
        self.bot = None
        self.is_running = False
    
    def set_bot(self, bot):
        """Устанавливает экземпляр бота"""
        self.bot = bot
        logger.info("Bot instance set for post scheduler")
    
    async def start_scheduler(self):
        """Запускает планировщик"""
        if self.is_running:
            logger.warning("Post scheduler already running")
            return
        
        try:
            if not self.bot:
                logger.error("Bot instance not set for post scheduler")
                return
            
            # Добавляем задачу проверки отложенных постов каждую минуту
            self.scheduler.add_job(
                self._check_and_publish_posts,
                trigger=IntervalTrigger(minutes=1),
                id='publish_scheduled_posts',
                name='Publish Scheduled Posts',
                replace_existing=True
            )
            
            self.scheduler.start()
            self.is_running = True
            logger.info("✅ Post scheduler started - checking every minute")
            
        except Exception as e:
            logger.error(f"Failed to start post scheduler: {e}")
            raise
    
    async def stop_scheduler(self):
        """Останавливает планировщик"""
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
            self.is_running = False
            logger.info("Post scheduler stopped")
        except Exception as e:
            logger.error(f"Failed to stop post scheduler: {e}")
    
    async def _check_and_publish_posts(self):
        """Проверяет и публикует отложенные посты"""
        try:
            logger.info("🔍 Проверяем отложенные посты...")
            
            if not self.bot:
                logger.error("Bot instance not available for publishing")
                return
            
            # Публикуем посты
            published_count = await post_service.publish_scheduled_posts(self.bot)
            
            if published_count > 0:
                logger.info(f"📢 Опубликовано {published_count} отложенных постов")
            else:
                logger.debug("📭 Нет постов для публикации")
                
        except Exception as e:
            logger.error(f"Error in post scheduler: {e}")
    
    async def get_scheduler_status(self) -> dict:
        """Получает статус планировщика"""
        try:
            jobs = self.scheduler.get_jobs()
            return {
                "running": self.scheduler.running,
                "is_running": self.is_running,
                "jobs_count": len(jobs),
                "bot_available": self.bot is not None
            }
        except Exception as e:
            logger.error(f"Failed to get scheduler status: {e}")
            return {"error": str(e)}

# Глобальный экземпляр планировщика
post_scheduler = PostScheduler()
