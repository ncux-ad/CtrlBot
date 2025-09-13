@echo off
chcp 65001 >nul
echo Запускаем CtrlBot в режиме разработки с hot-reload...
docker-compose -f docker-compose.dev.yml up --build -d
echo.
echo Готово! Теперь изменения в коде применяются автоматически.
echo Логи: docker-compose -f docker-compose.dev.yml logs -f ctrlbot
pause
