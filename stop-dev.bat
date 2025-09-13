@echo off
echo 🛑 Остановка CtrlBot...
docker-compose -f docker-compose.dev.yml down
echo ✅ Контейнеры остановлены!
pause
