#!/bin/bash
echo "🚀 Запуск CtrlBot в виртуальном окружении"
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
echo "🚀 Запуск бота..."
python bot.py
