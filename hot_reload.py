#!/usr/bin/env python3
"""
Hot-reload скрипт для CtrlBot
Автоматически перезапускает бота при изменении файлов
"""

import os
import sys
import time
import subprocess
import signal
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class BotReloadHandler(FileSystemEventHandler):
    def __init__(self):
        self.bot_process = None
        self.restart_bot()
    
    def restart_bot(self):
        """Перезапускает бота"""
        if self.bot_process:
            print("🔄 Перезапускаем бота...")
            self.bot_process.terminate()
            self.bot_process.wait()
        
        print("🚀 Запускаем бота...")
        self.bot_process = subprocess.Popen([sys.executable, "bot.py"])
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # Игнорируем временные файлы
        if event.src_path.endswith(('.pyc', '.pyo', '.log', '.tmp')):
            return
        
        # Игнорируем файлы в логах
        if '/logs/' in event.src_path or '\\logs\\' in event.src_path:
            return
        
        print(f"📝 Изменен файл: {event.src_path}")
        time.sleep(0.5)  # Небольшая задержка для завершения записи
        self.restart_bot()

def main():
    print("🔥 Hot-reload для CtrlBot запущен!")
    print("📁 Отслеживаем изменения в: /app")
    print("⏹️  Нажмите Ctrl+C для остановки")
    
    event_handler = BotReloadHandler()
    observer = Observer()
    observer.schedule(event_handler, "/app", recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⏹️  Останавливаем hot-reload...")
        observer.stop()
        if event_handler.bot_process:
            event_handler.bot_process.terminate()
            event_handler.bot_process.wait()
    
    observer.join()
    print("✅ Hot-reload остановлен")

if __name__ == "__main__":
    main()
