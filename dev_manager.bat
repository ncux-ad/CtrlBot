@echo off
chcp 65001 >nul
echo ========================================
echo    CtrlBot Development Manager
echo ========================================
echo.

:menu
echo Выберите режим:
echo 1. Запустить в режиме разработки (hot-reload)
echo 2. Запустить в обычном режиме
echo 3. Остановить все
echo 4. Показать логи
echo 5. Войти в контейнер
echo 6. Выход
echo.
set /p choice="Введите номер (1-6): "

if "%choice%"=="1" goto dev_mode
if "%choice%"=="2" goto prod_mode
if "%choice%"=="3" goto stop
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto shell
if "%choice%"=="6" goto exit
echo Неверный выбор!
goto menu

:dev_mode
echo.
echo Запускаем в режиме разработки с hot-reload...
docker-compose -f docker-compose.dev.yml up --build -d
echo.
echo Режим разработки запущен! Изменения в коде будут автоматически применяться.
echo Логи: docker-compose -f docker-compose.dev.yml logs -f ctrlbot
goto menu

:prod_mode
echo.
echo Запускаем в обычном режиме...
docker-compose up --build -d
echo.
echo Обычный режим запущен!
goto menu

:stop
echo.
echo Останавливаем все контейнеры...
docker-compose down
docker-compose -f docker-compose.dev.yml down
echo.
echo Все остановлено!
goto menu

:logs
echo.
echo Показываем логи (Ctrl+C для выхода)...
docker-compose logs -f ctrlbot
goto menu

:shell
echo.
echo Входим в контейнер бота...
docker-compose exec ctrlbot /bin/bash
goto menu

:exit
echo.
echo До свидания!
pause
