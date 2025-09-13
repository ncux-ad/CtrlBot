@echo off
echo 🔄 Перезапуск CtrlBot...
docker-compose -f docker-compose.dev.yml --env-file .env restart
echo ✅ CtrlBot перезапущен!
pause
