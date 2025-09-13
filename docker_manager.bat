@echo off
chcp 65001 >nul
echo ========================================
echo    CtrlBot Docker Manager
echo ========================================
echo.

:menu
echo Выберите действие:
echo 1. Собрать и запустить бота
echo 2. Остановить бота
echo 3. Перезапустить бота
echo 4. Показать логи
echo 5. Войти в контейнер
echo 6. Очистить все (ОСТОРОЖНО!)
echo 7. Выход
echo.
set /p choice="Введите номер (1-7): "

if "%choice%"=="1" goto build_and_run
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto restart
if "%choice%"=="4" goto logs
if "%choice%"=="5" goto shell
if "%choice%"=="6" goto clean
if "%choice%"=="7" goto exit
echo Неверный выбор!
goto menu

:build_and_run
echo.
echo Собираем и запускаем бота...
docker-compose up --build -d
echo.
echo Бот запущен! Проверьте логи: docker-compose logs -f ctrlbot
goto menu

:stop
echo.
echo Останавливаем бота...
docker-compose down
echo.
echo Бот остановлен!
goto menu

:restart
echo.
echo Перезапускаем бота...
docker-compose restart ctrlbot
echo.
echo Бот перезапущен!
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

:clean
echo.
echo ВНИМАНИЕ! Это удалит ВСЕ данные!
set /p confirm="Вы уверены? (yes/no): "
if not "%confirm%"=="yes" goto menu
echo.
echo Останавливаем и удаляем все...
docker-compose down -v
docker system prune -f
echo.
echo Все очищено!
goto menu

:exit
echo.
echo До свидания!
pause
