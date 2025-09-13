#!/usr/bin/env python3
"""
Скрипт установки зависимостей для CtrlBot
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Выполняет команду и выводит результат"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - успешно")
            return True
        else:
            print(f"❌ {description} - ошибка:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ {description} - исключение: {e}")
        return False

def check_python_version():
    """Проверяет версию Python"""
    print("🐍 Проверка версии Python...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - подходит")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - нужна версия 3.10+")
        return False

def install_dependencies():
    """Устанавливает зависимости"""
    print("\n📦 Установка зависимостей...")
    
    # Проверяем, есть ли requirements.txt
    if not os.path.exists('requirements.txt'):
        print("❌ Файл requirements.txt не найден!")
        return False
    
    # Устанавливаем зависимости
    success = run_command(
        f"{sys.executable} -m pip install -r requirements.txt",
        "Установка зависимостей из requirements.txt"
    )
    
    return success

def create_directories():
    """Создает необходимые директории"""
    print("\n📁 Создание директорий...")
    
    directories = [
        'logs',
        'temp',
        'exports',
        'uploads'
    ]
    
    for directory in directories:
        if not os.path.exists(directory):
            try:
                os.makedirs(directory)
                print(f"✅ Создана директория: {directory}")
            except Exception as e:
                print(f"❌ Ошибка создания {directory}: {e}")
        else:
            print(f"✅ Директория уже существует: {directory}")

def check_env_file():
    """Проверяет наличие .env файла"""
    print("\n🔧 Проверка конфигурации...")
    
    if os.path.exists('.env'):
        print("✅ Файл .env найден")
        return True
    elif os.path.exists('env.example'):
        print("⚠️  Файл .env не найден, но есть env.example")
        print("Скопируйте env.example в .env и заполните настройки")
        return False
    else:
        print("❌ Файлы конфигурации не найдены")
        return False

def main():
    """Главная функция установки"""
    print("🚀 CtrlBot - Установка зависимостей\n")
    
    # Проверяем версию Python
    if not check_python_version():
        return False
    
    # Создаем директории
    create_directories()
    
    # Проверяем конфигурацию
    env_ok = check_env_file()
    
    # Устанавливаем зависимости
    deps_ok = install_dependencies()
    
    print("\n" + "="*50)
    if deps_ok:
        print("🎉 Зависимости установлены успешно!")
        if not env_ok:
            print("⚠️  Не забудьте настроить .env файл")
        print("\nСледующие шаги:")
        print("1. Настройте .env файл")
        print("2. Запустите: python test_config.py")
        print("3. Запустите бота: python bot.py")
    else:
        print("❌ Ошибки при установке зависимостей")
    
    return deps_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
