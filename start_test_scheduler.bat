@echo off
echo 🧪 Запуск тестовой версии CtrlBot с планировщиком напоминаний
echo.

REM Активация виртуального окружения
call venv\Scripts\activate.bat

REM Проверка конфигурации
echo 🔧 Проверка конфигурации...
python test_config.py
if %errorlevel% neq 0 (
    echo ❌ Ошибка конфигурации!
    pause
    exit /b 1
)

echo.
echo 🧪 Запуск тестового бота с планировщиком...
python bot_test_with_scheduler.py

pause
