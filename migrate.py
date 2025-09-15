#!/usr/bin/env python3
"""Скрипт для управления миграциями CtrlBot."""

import asyncio
import sys
import os
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent))

from alembic.config import Config
from alembic import command
from database import db
from config import config


async def init_database():
    """Инициализация базы данных."""
    print("🔧 Инициализация базы данных...")
    await db.connect()
    print("✅ База данных подключена")


async def close_database():
    """Закрытие соединения с базой данных."""
    await db.close()
    print("✅ Соединение с базой данных закрыто")


def run_alembic_command(cmd, *args):
    """Выполнение команды Alembic."""
    alembic_cfg = Config("alembic.ini")
    # Обновляем URL из конфигурации
    alembic_cfg.set_main_option(
        "sqlalchemy.url",
        f"postgresql://{config.DB_USER}:{config.DB_PASSWORD}@{config.DB_HOST}:{config.DB_PORT}/{config.DB_NAME}"
    )
    
    if cmd == "upgrade":
        command.upgrade(alembic_cfg, *args)
    elif cmd == "downgrade":
        command.downgrade(alembic_cfg, *args)
    elif cmd == "revision":
        # Обрабатываем аргументы для revision
        if "--autogenerate" in args:
            command.revision(alembic_cfg, "--autogenerate", *[arg for arg in args if arg != "--autogenerate"])
        else:
            command.revision(alembic_cfg, *args)
    elif cmd == "current":
        command.current(alembic_cfg, *args)
    elif cmd == "history":
        command.history(alembic_cfg, *args)
    elif cmd == "heads":
        command.heads(alembic_cfg, *args)
    else:
        print(f"❌ Неизвестная команда: {cmd}")


async def main():
    """Главная функция."""
    if len(sys.argv) < 2:
        print("""
🚀 CtrlBot Migration Manager

Использование:
    python migrate.py <команда> [аргументы]

Команды:
    init                    - Инициализация базы данных
    upgrade [revision]      - Применить миграции (по умолчанию: head)
    downgrade [revision]    - Откатить миграции (по умолчанию: -1)
    revision [message]      - Создать новую миграцию
    current                 - Показать текущую ревизию
    history                 - Показать историю миграций
    heads                   - Показать головные ревизии

Примеры:
    python migrate.py init
    python migrate.py upgrade
    python migrate.py revision "Add user table"
    python migrate.py downgrade -1
        """)
        return

    command_name = sys.argv[1]
    args = sys.argv[2:]

    try:
        if command_name == "init":
            await init_database()
            print("✅ База данных инициализирована")
        else:
            # Для остальных команд сначала подключаемся к БД
            await init_database()
            
            if command_name == "upgrade":
                revision = args[0] if args else "head"
                print(f"⬆️ Применение миграций до ревизии: {revision}")
                run_alembic_command("upgrade", revision)
                print("✅ Миграции применены")
                
            elif command_name == "downgrade":
                revision = args[0] if args else "-1"
                print(f"⬇️ Откат миграций до ревизии: {revision}")
                run_alembic_command("downgrade", revision)
                print("✅ Миграции откачены")
                
            elif command_name == "revision":
                message = args[0] if args else "Auto migration"
                print(f"📝 Создание новой миграции: {message}")
                run_alembic_command("revision", "--autogenerate", "-m", message)
                print("✅ Миграция создана")
                
            elif command_name == "current":
                print("📊 Текущая ревизия:")
                run_alembic_command("current")
                
            elif command_name == "history":
                print("📚 История миграций:")
                run_alembic_command("history")
                
            elif command_name == "heads":
                print("🎯 Головные ревизии:")
                run_alembic_command("heads")
                
            else:
                print(f"❌ Неизвестная команда: {command_name}")
                return

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        sys.exit(1)
    finally:
        await close_database()


if __name__ == "__main__":
    asyncio.run(main())
