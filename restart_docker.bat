@echo off
chcp 65001 >nul
echo Перезапускаем CtrlBot в Docker...
docker-compose restart ctrlbot
echo Готово! Проверьте логи: docker-compose logs -f ctrlbot
