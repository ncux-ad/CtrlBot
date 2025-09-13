@echo off
echo 🐍 Управление виртуальным окружением CtrlBot
echo.

:menu
echo Выберите действие:
echo 1. Создать виртуальное окружение
echo 2. Активировать виртуальное окружение
echo 3. Установить зависимости
echo 4. Запустить тестовый бот
echo 5. Запустить основной бот
echo 6. Деактивировать окружение
echo 7. Выход
echo.

set /p choice="Введите номер (1-7): "

if "%choice%"=="1" goto create_venv
if "%choice%"=="2" goto activate_venv
if "%choice%"=="3" goto install_deps
if "%choice%"=="4" goto run_test
if "%choice%"=="5" goto run_main
if "%choice%"=="6" goto deactivate_venv
if "%choice%"=="7" goto exit
goto menu

:create_venv
echo.
echo 🔧 Создание виртуального окружения...
python -m venv venv
if %errorlevel% neq 0 (
    echo ❌ Ошибка создания виртуального окружения!
    pause
    goto menu
)
echo ✅ Виртуальное окружение создано!
echo.
goto menu

:activate_venv
echo.
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat
echo ✅ Виртуальное окружение активировано!
echo.
goto menu

:install_deps
echo.
echo 📦 Установка зависимостей...
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки зависимостей!
    pause
    goto menu
)
echo ✅ Зависимости установлены!
echo.
goto menu

:run_test
echo.
echo 🧪 Запуск тестового бота...
call venv\Scripts\activate.bat
python bot_test.py
echo.
goto menu

:run_main
echo.
echo 🚀 Запуск основного бота...
call venv\Scripts\activate.bat
python bot.py
echo.
goto menu

:deactivate_venv
echo.
echo 🔧 Деактивация виртуального окружения...
deactivate
echo ✅ Виртуальное окружение деактивировано!
echo.
goto menu

:exit
echo.
echo 👋 До свидания!
pause
exit /b 0
