#!/bin/bash
echo "🛠️ Настройка CtrlBot"
echo

# Создание виртуального окружения если его нет
if [ ! -d "venv" ]; then
    echo "📦 Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка создания виртуального окружения!"
        exit 1
    fi
fi

# Активация виртуального окружения
echo "🔧 Активация виртуального окружения..."
source venv/bin/activate

# Обновление pip
echo "📦 Обновление pip..."
python -m pip install --upgrade pip

# Установка зависимостей
echo "📦 Установка зависимостей..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "❌ Ошибка установки зависимостей!"
    exit 1
fi

# Проверка конфигурации
echo "🔧 Проверка конфигурации..."
python test_config.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка конфигурации!"
    echo "Проверьте файл .env"
    exit 1
fi

echo
echo "✅ Настройка завершена успешно!"
echo
echo "Доступные команды:"
echo "  ./start.sh      - Запуск бота (требует PostgreSQL)"
echo "  ./start_test.sh - Запуск тестовой версии (без БД)"
echo "  python test_config.py - Проверка конфигурации"
echo
