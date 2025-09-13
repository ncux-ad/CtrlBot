#!/bin/bash

echo "🐍 Управление виртуальным окружением CtrlBot"
echo

show_menu() {
    echo "Выберите действие:"
    echo "1. Создать виртуальное окружение"
    echo "2. Активировать виртуальное окружение"
    echo "3. Установить зависимости"
    echo "4. Запустить тестовый бот"
    echo "5. Запустить основной бот"
    echo "6. Деактивировать окружение"
    echo "7. Выход"
    echo
}

create_venv() {
    echo
    echo "🔧 Создание виртуального окружения..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка создания виртуального окружения!"
        read -p "Нажмите Enter для продолжения..."
        return
    fi
    echo "✅ Виртуальное окружение создано!"
    echo
}

activate_venv() {
    echo
    echo "🔧 Активация виртуального окружения..."
    source venv/bin/activate
    echo "✅ Виртуальное окружение активировано!"
    echo
}

install_deps() {
    echo
    echo "📦 Установка зависимостей..."
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Ошибка установки зависимостей!"
        read -p "Нажмите Enter для продолжения..."
        return
    fi
    echo "✅ Зависимости установлены!"
    echo
}

run_test() {
    echo
    echo "🧪 Запуск тестового бота..."
    source venv/bin/activate
    python bot_test.py
    echo
}

run_main() {
    echo
    echo "🚀 Запуск основного бота..."
    source venv/bin/activate
    python bot.py
    echo
}

deactivate_venv() {
    echo
    echo "🔧 Деактивация виртуального окружения..."
    deactivate
    echo "✅ Виртуальное окружение деактивировано!"
    echo
}

while true; do
    show_menu
    read -p "Введите номер (1-7): " choice
    
    case $choice in
        1) create_venv ;;
        2) activate_venv ;;
        3) install_deps ;;
        4) run_test ;;
        5) run_main ;;
        6) deactivate_venv ;;
        7) 
            echo
            echo "👋 До свидания!"
            exit 0
            ;;
        *) 
            echo "❌ Неверный выбор! Попробуйте еще раз."
            echo
            ;;
    esac
done
