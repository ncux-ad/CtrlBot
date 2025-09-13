#!/usr/bin/env python3
"""
CtrlBot Health Check Script
Checks the health of the bot and its dependencies
"""

import asyncio
import aiohttp
import sys
import os
from datetime import datetime
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config import config
from database import db
from services.ai import ai_service
from services.reminders import reminder_service

class HealthChecker:
    """Health checker for CtrlBot"""
    
    def __init__(self):
        self.checks = []
        self.overall_status = True
    
    def add_check(self, name: str, check_func):
        """Add a health check"""
        self.checks.append((name, check_func))
    
    async def run_checks(self):
        """Run all health checks"""
        print(f"🏥 CtrlBot Health Check - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for name, check_func in self.checks:
            try:
                result = await check_func()
                status = "✅" if result else "❌"
                print(f"{status} {name}")
                
                if not result:
                    self.overall_status = False
                    
            except Exception as e:
                print(f"❌ {name} - Error: {e}")
                self.overall_status = False
        
        print("=" * 60)
        overall_status = "✅ HEALTHY" if self.overall_status else "❌ UNHEALTHY"
        print(f"Overall Status: {overall_status}")
        
        return self.overall_status

# Health check functions
async def check_config():
    """Check configuration"""
    try:
        config.validate()
        return True
    except Exception:
        return False

async def check_database():
    """Check database connection"""
    try:
        await db.connect()
        await db.close()
        return True
    except Exception:
        return False

async def check_telegram_api():
    """Check Telegram API"""
    try:
        async with aiohttp.ClientSession() as session:
            url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/getMe"
            async with session.get(url, timeout=10) as response:
                return response.status == 200
    except Exception:
        return False

async def check_yandex_api():
    """Check YandexGPT API"""
    try:
        status = await ai_service.check_api_status()
        return status["status"] == "working"
    except Exception:
        return False

async def check_scheduler():
    """Check reminder scheduler"""
    try:
        from services.reminders import reminder_service
        status = await reminder_service.get_scheduler_status()
        print(f"Scheduler status: {status}")
        return status["running"]
    except Exception as e:
        print(f"Scheduler check error: {e}")
        return False

async def check_logs():
    """Check log files"""
    try:
        log_file = Path(config.LOG_FILE)
        error_file = Path(config.LOG_ERROR_FILE)
        
        # Check if log files exist and are writable
        log_file.parent.mkdir(parents=True, exist_ok=True)
        error_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Try to write to log files
        with open(log_file, 'a') as f:
            f.write("")
        with open(error_file, 'a') as f:
            f.write("")
        
        return True
    except Exception:
        return False

async def check_disk_space():
    """Check available disk space"""
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free // (1024**3)
        return free_gb > 1  # At least 1GB free
    except Exception:
        return True  # Skip on Windows or if check fails

async def main():
    """Main health check function"""
    checker = HealthChecker()
    
    # Add all checks
    checker.add_check("Configuration", check_config)
    checker.add_check("Database Connection", check_database)
    checker.add_check("Telegram API", check_telegram_api)
    checker.add_check("YandexGPT API", check_yandex_api)
    checker.add_check("Reminder Scheduler", check_scheduler)
    checker.add_check("Log Files", check_logs)
    checker.add_check("Disk Space", check_disk_space)
    
    # Run checks
    healthy = await checker.run_checks()
    
    # Exit with appropriate code
    sys.exit(0 if healthy else 1)

if __name__ == "__main__":
    asyncio.run(main())
