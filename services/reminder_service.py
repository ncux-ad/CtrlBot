"""
@file: services/reminders.py
@description: Сервис для управления напоминаниями
@dependencies: database.py, config.py
@created: 2025-09-13
"""

from datetime import datetime, time, timedelta
from typing import List, Optional, Dict, Any
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor

from database import db
from config import config
from utils.logging import get_logger

logger = get_logger(__name__)

class ReminderService:
    """Сервис для управления напоминаниями"""
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler(
            jobstores={'default': MemoryJobStore()},
            executors={'default': AsyncIOExecutor()},
            job_defaults={
                'coalesce': False,
                'max_instances': 3
            }
        )
        self.bot = None  # Будет установлен при инициализации
    
    def set_bot(self, bot):
        """Установка экземпляра бота для отправки уведомлений"""
        self.bot = bot
    
    async def start_scheduler(self):
        """Запуск планировщика"""
        try:
            self.scheduler.start()
            logger.info("Reminder scheduler started")
            
            # Добавляем стандартные напоминания
            await self.add_default_reminders()
            
        except Exception as e:
            logger.error("Failed to start scheduler: %s", e)
            raise
    
    async def stop_scheduler(self):
        """Остановка планировщика"""
        try:
            self.scheduler.shutdown()
            logger.info("Reminder scheduler stopped")
        except Exception as e:
            logger.error("Failed to stop scheduler: %s", e)
    
    async def add_default_reminders(self):
        """Добавление стандартных напоминаний (12:00 и 21:00)"""
        try:
            # Напоминание в 12:00
            self.scheduler.add_job(
                self._send_daily_reminder,
                CronTrigger(hour=12, minute=0, timezone=config.TIMEZONE),
                id='daily_reminder_12',
                name='Ежедневное напоминание 12:00',
                replace_existing=True
            )
            
            # Напоминание в 21:00
            self.scheduler.add_job(
                self._send_daily_reminder,
                CronTrigger(hour=21, minute=0, timezone=config.TIMEZONE),
                id='daily_reminder_21',
                name='Ежедневное напоминание 21:00',
                replace_existing=True
            )
            
            logger.info("Default reminders added: 12:00 and 21:00")
            
        except Exception as e:
            logger.error("Failed to add default reminders: %s", e)
    
    async def _send_daily_reminder(self):
        """Отправка ежедневного напоминания"""
        if not self.bot:
            logger.warning("Bot not set, cannot send reminder")
            return
        
        try:
            # Получаем список админов
            admin_ids = config.ADMIN_IDS
            
            # Формируем сообщение
            current_time = datetime.now().strftime("%H:%M")
            message = (
                f"⏰ *Напоминание {current_time}*\n\n"
                f"Время создать пост для канала!\n\n"
                f"Используйте /new_post для создания нового поста."
            )
            
            # Отправляем всем админам
            for admin_id in admin_ids:
                try:
                    await self.bot.send_message(admin_id, message)
                    logger.info("Reminder sent to admin %s", admin_id)
                except Exception as e:
                    logger.error("Failed to send reminder to admin %s: %s", admin_id, e)
            
        except Exception as e:
            logger.error("Failed to send daily reminder: %s", e)
    
    async def create_reminder(self, user_id: int, message: str, 
                            scheduled_time: datetime, reminder_type: str = "custom") -> bool:
        """Создание пользовательского напоминания"""
        try:
            # Добавляем задачу в планировщик
            job_id = f"reminder_{user_id}_{int(scheduled_time.timestamp())}"
            
            self.scheduler.add_job(
                self._send_custom_reminder,
                DateTrigger(run_date=scheduled_time),
                args=[user_id, message],
                id=job_id,
                name=f"Custom reminder for user {user_id}",
                replace_existing=True
            )
            
            # Сохраняем в БД (если подключена)
            try:
                await db.execute(
                    """
                    INSERT INTO reminders (user_id, message, scheduled_time, type, created_at)
                    VALUES ($1, $2, $3, $4, $5)
                    """,
                    user_id, message, scheduled_time, reminder_type, datetime.now()
                )
            except Exception as e:
                logger.warning("Failed to save reminder to DB: %s", e)
            
            logger.info("Custom reminder created for user %s at %s", user_id, scheduled_time)
            return True
            
        except Exception as e:
            logger.error("Failed to create reminder: %s", e)
            return False
    
    async def _send_custom_reminder(self, user_id: int, message: str):
        """Отправка пользовательского напоминания"""
        if not self.bot:
            logger.warning("Bot not set, cannot send custom reminder")
            return
        
        try:
            await self.bot.send_message(user_id, f"⏰ *Напоминание*\n\n{message}")
            logger.info("Custom reminder sent to user %s", user_id)
        except Exception as e:
            logger.error("Failed to send custom reminder to user %s: %s", user_id, e)
    
    async def get_user_reminders(self, user_id: int) -> List[Dict[str, Any]]:
        """Получение напоминаний пользователя"""
        try:
            # Получаем из БД
            reminders = await db.fetch_all(
                """
                SELECT id, message, scheduled_time, type, created_at
                FROM reminders
                WHERE user_id = $1 AND scheduled_time > $2
                ORDER BY scheduled_time ASC
                """,
                user_id, datetime.now()
            )
            
            return [dict(reminder) for reminder in reminders]
            
        except Exception as e:
            logger.error("Failed to get user reminders: %s", e)
            return []
    
    async def delete_reminder(self, reminder_id: int, user_id: int) -> bool:
        """Удаление напоминания"""
        try:
            # Удаляем из БД
            result = await db.execute(
                "DELETE FROM reminders WHERE id = $1 AND user_id = $2",
                reminder_id, user_id
            )
            
            if result:
                # Пытаемся удалить из планировщика
                try:
                    self.scheduler.remove_job(f"reminder_{user_id}_{reminder_id}")
                except:
                    pass  # Задача могла уже выполниться
                
                logger.info("Reminder %s deleted for user %s", reminder_id, user_id)
                return True
            else:
                logger.warning("Reminder %s not found for user %s", reminder_id, user_id)
                return False
                
        except Exception as e:
            logger.error("Failed to delete reminder: %s", e)
            return False
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Получение статуса планировщика"""
        try:
            jobs = self.scheduler.get_jobs()
            
            return {
                "running": self.scheduler.running,
                "jobs_count": len(jobs),
                "jobs": [
                    {
                        "id": job.id,
                        "name": job.name,
                        "next_run": job.next_run_time.isoformat() if job.next_run_time else None
                    }
                    for job in jobs
                ]
            }
            
        except Exception as e:
            logger.error("Failed to get scheduler status: %s", e)
            return {"running": False, "jobs_count": 0, "jobs": []}

# Глобальный экземпляр сервиса
reminder_service = ReminderService()
