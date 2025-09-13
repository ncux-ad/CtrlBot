@echo off
echo 🛠️ Настройка CtrlBot
echo.

REM Создание виртуального окружения если его нет
if not exist "venv" (
    echo 📦 Создание виртуального окружения...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ❌ Ошибка создания виртуального окружения!
        pause
        exit /b 1
    )
)

REM Активация виртуального окружения
echo 🔧 Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Обновление pip
echo 📦 Обновление pip...
python -m pip install --upgrade pip

REM Установка зависимостей
echo 📦 Установка зависимостей...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Ошибка установки зависимостей!
    pause
    exit /b 1
)

REM Проверка конфигурации
echo 🔧 Проверка конфигурации...
python test_config.py
if %errorlevel% neq 0 (
    echo ❌ Ошибка конфигурации!
    echo Проверьте файл .env
    pause
    exit /b 1
)

echo.
echo ✅ Настройка завершена успешно!
echo.
echo Доступные команды:
echo   start.bat      - Запуск бота (требует PostgreSQL)
echo   start_test.bat - Запуск тестовой версии (без БД)
echo   test_config.py - Проверка конфигурации
echo.

pause
