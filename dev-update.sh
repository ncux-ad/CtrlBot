#!/bin/bash
# Скрипт для быстрого обновления кода (без пересборки)

echo "⚡ Быстрое обновление кода CtrlBot"

# Проверяем, что контейнер запущен
if ! docker ps | grep -q ctrlbot; then
    echo "❌ Контейнер не запущен. Запускаем..."
    docker-compose up -d
    sleep 5
fi

# Перезапускаем только бота (код уже смонтирован)
echo "🔄 Перезапускаем бота..."
docker-compose restart ctrlbot

# Ждем запуска
echo "⏳ Ждем запуска..."
sleep 3

# Проверяем статус
echo "📊 Статус:"
docker-compose ps ctrlbot

echo "✅ Готово! Код обновлен за секунды!"
echo "📝 Логи: docker logs ctrlbot -f"
