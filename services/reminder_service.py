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
            
            # Загружаем напоминания из базы данных
            await self.load_reminders_from_db()
            
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
    
    async def load_reminders_from_db(self):
        """Загрузка напоминаний из базы данных"""
        try:
            # Получаем все активные напоминания
            reminders = await db.fetch_all(
                "SELECT * FROM reminders WHERE enabled = true"
            )
            
            if not reminders:
                # Если нет напоминаний в БД, создаем стандартные
                await self.create_default_reminders()
                reminders = await db.fetch_all(
                    "SELECT * FROM reminders WHERE enabled = true"
                )
            
            # Добавляем каждое напоминание в планировщик
            for reminder in reminders:
                await self._add_reminder_to_scheduler(reminder)
            
            logger.info(f"Loaded {len(reminders)} reminders from database")
            
        except Exception as e:
            logger.error("Failed to load reminders from database: %s", e)
            raise
    
    async def create_default_reminders(self):
        """Создание стандартных напоминаний в базе данных"""
        try:
            # Получаем первый канал
            channel = await db.fetch_one("SELECT id FROM channels LIMIT 1")
            if not channel:
                logger.warning("No channels found, cannot create default reminders")
                return
            
            # Создаем стандартные напоминания
            default_reminders = [
                {
                    'channel_id': channel['id'],
                    'kind': 'daily',
                    'schedule_cron': '0 12 * * *',  # 12:00 каждый день
                    'enabled': True
                },
                {
                    'channel_id': channel['id'],
                    'kind': 'daily',
                    'schedule_cron': '0 21 * * *',  # 21:00 каждый день
                    'enabled': True
                }
            ]
            
            for reminder_data in default_reminders:
                await db.execute(
                    """
                    INSERT INTO reminders (channel_id, kind, schedule_cron, enabled)
                    VALUES ($1, $2, $3, $4)
                    """,
                    reminder_data['channel_id'],
                    reminder_data['kind'],
                    reminder_data['schedule_cron'],
                    reminder_data['enabled']
                )
            
            logger.info("Default reminders created in database")
            
        except Exception as e:
            logger.error("Failed to create default reminders: %s", e)
            raise
    
    async def _add_reminder_to_scheduler(self, reminder):
        """Добавление напоминания в планировщик"""
        try:
            job_id = f"reminder_{reminder['id']}"
            
            # Парсим cron выражение
            cron_parts = reminder['schedule_cron'].split()
            if len(cron_parts) != 5:
                logger.error(f"Invalid cron expression: {reminder['schedule_cron']}")
                return
            
            minute, hour, day, month, day_of_week = cron_parts
            
            # Создаем задачу в планировщике
            self.scheduler.add_job(
                self._send_reminder,
                CronTrigger(
                    minute=int(minute),
                    hour=int(hour),
                    day=int(day) if day != '*' else None,
                    month=int(month) if month != '*' else None,
                    day_of_week=int(day_of_week) if day_of_week != '*' else None,
                    timezone=config.TIMEZONE
                ),
                id=job_id,
                name=f"Напоминание {reminder['id']}",
                replace_existing=True,
                args=[reminder['id']]  # Передаем ID напоминания
            )
            
            logger.info(f"Added reminder {reminder['id']} to scheduler: {reminder['schedule_cron']}")
            
        except Exception as e:
            logger.error(f"Failed to add reminder {reminder['id']} to scheduler: %s", e)
    
    async def _send_reminder(self, reminder_id):
        """Отправка напоминания по ID"""
        try:
            if not self.bot:
                logger.warning("Bot not set, cannot send reminder")
                return
            
            # Получаем данные напоминания
            reminder = await db.fetch_one(
                "SELECT * FROM reminders WHERE id = $1 AND enabled = true",
                reminder_id
            )
            
            if not reminder:
                logger.warning(f"Reminder {reminder_id} not found or disabled")
                return
            
            # Получаем данные канала
            channel = await db.fetch_one(
                "SELECT * FROM channels WHERE id = $1",
                reminder['channel_id']
            )
            
            if not channel:
                logger.warning(f"Channel {reminder['channel_id']} not found")
                return
            
            # Отправляем напоминание
            message = f"⏰ *Напоминание*\n\nВремя публиковать контент в канал {channel['title']}!"
            
            # Отправляем всем администраторам
            for admin_id in config.ADMIN_IDS:
                try:
                    await self.bot.send_message(
                        chat_id=admin_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.error(f"Failed to send reminder to admin {admin_id}: %s", e)
            
            logger.info(f"Sent reminder {reminder_id} to admins")
            
        except Exception as e:
            logger.error(f"Failed to send reminder {reminder_id}: %s", e)
    
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
    
    async def create_reminder(self, channel_id: int, kind: str, 
                            schedule_cron: str = None) -> bool:
        """Создание напоминания"""
        try:
            # Сохраняем в БД
            reminder_id = await db.fetch_val(
                """
                INSERT INTO reminders (channel_id, kind, schedule_cron, enabled, created_at)
                VALUES ($1, $2, $3, $4, $5)
                RETURNING id
                """,
                channel_id, kind, schedule_cron, True, datetime.now()
            )
            
            # Добавляем задачу в планировщик, если есть cron расписание
            if schedule_cron:
                job_id = f"reminder_{reminder_id}"
                
                # Парсим cron расписание (простая реализация)
                if schedule_cron == "0 12 * * *":  # 12:00 каждый день
                    self.scheduler.add_job(
                        self._send_daily_reminder,
                        CronTrigger(hour=12, minute=0, timezone=config.TIMEZONE),
                        id=job_id,
                        name=f"Reminder {kind} for channel {channel_id}",
                        replace_existing=True
                    )
                elif schedule_cron == "0 21 * * *":  # 21:00 каждый день
                    self.scheduler.add_job(
                        self._send_daily_reminder,
                        CronTrigger(hour=21, minute=0, timezone=config.TIMEZONE),
                        id=job_id,
                        name=f"Reminder {kind} for channel {channel_id}",
                        replace_existing=True
                    )
            
            logger.info("Reminder created: %s for channel %s", kind, channel_id)
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
    
    
    async def get_scheduler_status(self) -> bool:
        """Получение статуса планировщика"""
        try:
            return self.scheduler.running
        except Exception as e:
            logger.error("Failed to get scheduler status: %s", e)
            return False
    
    async def get_all_reminders(self) -> List[Dict[str, Any]]:
        """Получение всех напоминаний"""
        try:
            # Получаем из БД (используем существующую схему)
            reminders = await db.fetch_all(
                """
                SELECT r.*, c.title as channel_title
                FROM reminders r
                LEFT JOIN channels c ON r.channel_id = c.id
                WHERE r.enabled = true
                ORDER BY r.created_at ASC
                """
            )
            
            return [dict(reminder) for reminder in reminders]
            
        except Exception as e:
            logger.error("Failed to get all reminders: %s", e)
            return []
    
    async def get_scheduler_info(self) -> Dict[str, Any]:
        """Получение подробной информации о планировщике"""
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
            logger.error("Failed to get scheduler info: %s", e)
            return {"running": False, "jobs_count": 0, "jobs": []}
    
    async def create_reminder(self, channel_id: int, kind: str, schedule_cron: str) -> int:
        """Создание нового напоминания"""
        try:
            # Проверяем, что канал существует
            channel = await db.fetch_one("SELECT id FROM channels WHERE id = $1", channel_id)
            if not channel:
                raise ValueError(f"Channel {channel_id} not found")
            
            # Создаем напоминание в БД
            reminder_id = await db.fetch_val(
                """
                INSERT INTO reminders (channel_id, kind, schedule_cron, enabled)
                VALUES ($1, $2, $3, $4)
                RETURNING id
                """,
                channel_id, kind, schedule_cron, True
            )
            
            # Получаем созданное напоминание
            reminder = await db.fetch_one(
                "SELECT * FROM reminders WHERE id = $1", reminder_id
            )
            
            # Добавляем в планировщик
            await self._add_reminder_to_scheduler(reminder)
            
            logger.info(f"Created reminder {reminder_id} for channel {channel_id}")
            return reminder_id
            
        except Exception as e:
            logger.error(f"Failed to create reminder: %s", e)
            raise
    
    async def update_reminder(self, reminder_id: int, schedule_cron: str = None, enabled: bool = None) -> bool:
        """Обновление напоминания"""
        try:
            # Получаем текущее напоминание
            reminder = await db.fetch_one(
                "SELECT * FROM reminders WHERE id = $1", reminder_id
            )
            if not reminder:
                raise ValueError(f"Reminder {reminder_id} not found")
            
            # Обновляем в БД
            update_fields = []
            params = []
            param_count = 1
            
            if schedule_cron is not None:
                update_fields.append(f"schedule_cron = ${param_count}")
                params.append(schedule_cron)
                param_count += 1
            
            if enabled is not None:
                update_fields.append(f"enabled = ${param_count}")
                params.append(enabled)
                param_count += 1
            
            if update_fields:
                params.append(reminder_id)
                await db.execute(
                    f"UPDATE reminders SET {', '.join(update_fields)} WHERE id = ${param_count}",
                    *params
                )
            
            # Удаляем из планировщика
            job_id = f"reminder_{reminder_id}"
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass  # Задача может не существовать
            
            # Если напоминание включено, добавляем обратно
            if enabled is None or enabled:
                updated_reminder = await db.fetch_one(
                    "SELECT * FROM reminders WHERE id = $1", reminder_id
                )
                await self._add_reminder_to_scheduler(updated_reminder)
            
            logger.info(f"Updated reminder {reminder_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update reminder {reminder_id}: %s", e)
            raise
    
    async def delete_reminder(self, reminder_id: int) -> bool:
        """Удаление напоминания"""
        try:
            # Удаляем из планировщика
            job_id = f"reminder_{reminder_id}"
            try:
                self.scheduler.remove_job(job_id)
            except:
                pass  # Задача может не существовать
            
            # Удаляем из БД
            await db.execute("DELETE FROM reminders WHERE id = $1", reminder_id)
            
            logger.info(f"Deleted reminder {reminder_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete reminder {reminder_id}: %s", e)
            raise

    async def get_available_channels(self) -> List[Dict[str, Any]]:
        """Получить список доступных каналов для создания напоминаний"""
        try:
            query = """
                SELECT id, title, tg_channel_id 
                FROM channels 
                WHERE enabled = true 
                ORDER BY title
            """
            channels = await db.fetch_all(query)
            
            return [
                {
                    'id': channel['id'],
                    'title': channel['title'],
                    'tg_channel_id': channel['tg_channel_id']
                }
                for channel in channels
            ]
            
        except Exception as e:
            logger.error(f"Failed to get available channels: %s", e)
            return []

# Глобальный экземпляр сервиса
reminder_service = ReminderService()
