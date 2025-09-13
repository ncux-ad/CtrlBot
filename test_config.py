#!/usr/bin/env python3
"""
Тест конфигурации CtrlBot
Проверяет, что все необходимые настройки загружены корректно
"""

import sys
import os

def test_config():
    """Тестирует загрузку конфигурации"""
    print("🔧 Тестирование конфигурации CtrlBot...")
    
    try:
        from config import config
        print("✅ Модуль config загружен")
        
        # Проверяем обязательные настройки
        required_settings = [
            ('BOT_TOKEN', config.BOT_TOKEN),
            ('DB_PASSWORD', config.DB_PASSWORD),
        ]
        
        missing = []
        for name, value in required_settings:
            if not value:
                missing.append(name)
            else:
                print(f"✅ {name}: {'*' * 8} (скрыто)")
        
        # Проверяем ADMIN_IDS отдельно
        if not config.ADMIN_IDS:
            print("❌ ADMIN_IDS: не настроено (обязательно)")
            missing.append('ADMIN_IDS')
        else:
            print(f"✅ ADMIN_IDS: {len(config.ADMIN_IDS)} админов")
        
        if missing:
            print(f"❌ Отсутствуют обязательные настройки: {', '.join(missing)}")
            return False
        
        # Проверяем опциональные настройки
        optional_settings = [
            ('YANDEX_API_KEY', config.YANDEX_API_KEY),
            ('YANDEX_FOLDER_ID', config.YANDEX_FOLDER_ID),
        ]
        
        for name, value in optional_settings:
            if value:
                print(f"✅ {name}: настроено")
            else:
                print(f"⚠️  {name}: не настроено (опционально)")
        
        print("✅ Конфигурация загружена успешно!")
        return True
        
    except ImportError as e:
        print(f"❌ Ошибка импорта: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка конфигурации: {e}")
        return False

def test_dependencies():
    """Тестирует установленные зависимости"""
    print("\n📦 Тестирование зависимостей...")
    
    dependencies = [
        ('aiogram', 'aiogram'),
        ('asyncpg', 'asyncpg'),
        ('pandas', 'pandas'),
        ('openpyxl', 'openpyxl'),
        ('python-dotenv', 'dotenv'),
    ]
    
    missing = []
    for name, module in dependencies:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - не установлен")
            missing.append(name)
    
    if missing:
        print(f"\n❌ Отсутствуют зависимости: {', '.join(missing)}")
        print("Установите их командой: pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены!")
    return True

def main():
    """Главная функция тестирования"""
    print("🚀 CtrlBot - Тест готовности к запуску\n")
    
    # Проверяем наличие .env файла
    if not os.path.exists('.env'):
        print("❌ Файл .env не найден!")
        print("Скопируйте env.example в .env и заполните настройки")
        return False
    
    print("✅ Файл .env найден")
    
    # Тестируем конфигурацию
    config_ok = test_config()
    
    # Тестируем зависимости
    deps_ok = test_dependencies()
    
    print("\n" + "="*50)
    if config_ok and deps_ok:
        print("🎉 Всё готово к запуску! Выполните: python bot.py")
    else:
        print("❌ Есть проблемы, которые нужно исправить")
    
    return config_ok and deps_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
