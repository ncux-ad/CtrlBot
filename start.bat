@echo off
echo 🚀 Запуск CtrlBot в виртуальном окружении
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
echo 🚀 Запуск бота...
python bot.py

pause
