#!/bin/bash
# Скрипт для выполнения миграций в Docker контейнере

set -e

echo "🐳 CtrlBot Migration Manager (Docker)"

# Проверяем, что контейнер запущен
if ! docker ps | grep -q ctrlbot; then
    echo "❌ Контейнер ctrlbot не запущен. Запустите: docker-compose up -d"
    exit 1
fi

# Выполняем команду в контейнере
case "$1" in
    "init")
        echo "🔧 Инициализация базы данных..."
        docker exec ctrlbot python migrate.py init
        ;;
    "upgrade")
        revision=${2:-"head"}
        echo "⬆️ Применение миграций до ревизии: $revision"
        docker exec ctrlbot python migrate.py upgrade "$revision"
        ;;
    "downgrade")
        revision=${2:-"-1"}
        echo "⬇️ Откат миграций до ревизии: $revision"
        docker exec ctrlbot python migrate.py downgrade "$revision"
        ;;
    "revision")
        message=${2:-"Auto migration"}
        echo "📝 Создание новой миграции: $message"
        docker exec ctrlbot python migrate.py revision "$message"
        ;;
    "current")
        echo "📊 Текущая ревизия:"
        docker exec ctrlbot python migrate.py current
        ;;
    "history")
        echo "📚 История миграций:"
        docker exec ctrlbot python migrate.py history
        ;;
    "heads")
        echo "🎯 Головные ревизии:"
        docker exec ctrlbot python migrate.py heads
        ;;
    *)
        echo "🚀 CtrlBot Migration Manager (Docker)"
        echo ""
        echo "Использование:"
        echo "  ./docker-migrate.sh <команда> [аргументы]"
        echo ""
        echo "Команды:"
        echo "  init                    - Инициализация базы данных"
        echo "  upgrade [revision]      - Применить миграции (по умолчанию: head)"
        echo "  downgrade [revision]    - Откатить миграции (по умолчанию: -1)"
        echo "  revision [message]      - Создать новую миграцию"
        echo "  current                 - Показать текущую ревизию"
        echo "  history                 - Показать историю миграций"
        echo "  heads                   - Показать головные ревизии"
        echo ""
        echo "Примеры:"
        echo "  ./docker-migrate.sh init"
        echo "  ./docker-migrate.sh upgrade"
        echo "  ./docker-migrate.sh revision \"Add user table\""
        echo "  ./docker-migrate.sh downgrade -1"
        ;;
esac
