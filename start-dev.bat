@echo off
echo 🚀 Запуск CtrlBot в режиме разработки...
docker-compose -f docker-compose.dev.yml --env-file .env up -d
echo ✅ Контейнеры запущены!
echo 📋 Для просмотра логов: docker-compose -f docker-compose.dev.yml logs ctrlbot -f
pause
