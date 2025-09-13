#!/bin/bash
echo "🧪 Запуск тестовой версии CtrlBot (без БД)"
echo

# Активация виртуального окружения
source venv/bin/activate

# Проверка конфигурации
echo "🔧 Проверка конфигурации..."
python test_config.py
if [ $? -ne 0 ]; then
    echo "❌ Ошибка конфигурации!"
    exit 1
fi

echo
echo "🧪 Запуск тестового бота..."
python bot_test.py
