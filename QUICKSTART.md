# 🚀 CtrlBot - Быстрый старт

## 📋 **Что нужно для запуска**

### 1. Python 3.10+
```bash
python --version
```

### 2. PostgreSQL
- Установите PostgreSQL
- Создайте базу данных
- Создайте пользователя

### 3. Telegram Bot
- Создайте бота через @BotFather
- Получите токен

## ⚡ **Быстрая установка**

### Windows
```cmd
# 1. Настройка (создает venv и устанавливает зависимости)
setup.bat

# 2. Настройте .env файл
copy env.example .env
# Отредактируйте .env файл

# 3. Запуск
start.bat          # Полная версия (требует PostgreSQL)
start_test.bat     # Тестовая версия (без БД)
```

### Linux/macOS
```bash
# 1. Настройка
./setup.sh

# 2. Настройте .env файл
cp env.example .env
# Отредактируйте .env файл

# 3. Запуск
./start.sh         # Полная версия (требует PostgreSQL)
./start_test.sh    # Тестовая версия (без БД)
```

### Менеджер виртуального окружения
```bash
# Windows
venv_manager.bat

# Linux/macOS
chmod +x venv_manager.sh
./venv_manager.sh
```

### Ручная установка
```bash
# 1. Создайте виртуальное окружение
python -m venv venv

# 2. Активируйте его
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate

# 3. Установите зависимости
pip install -r requirements.txt

# 4. Настройте .env
cp env.example .env

# 5. Проверьте настройки
python test_config.py

# 6. Запустите бота
python bot.py
```

## 🔧 **Настройка .env**

Минимальные настройки:
```env
BOT_TOKEN=1234567890:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
ADMIN_IDS=123456789,987654321
DB_PASSWORD=your_strong_password_here
```

Полные настройки см. в `env.example`

## 🗄️ **Настройка PostgreSQL**

### Создание базы данных:
```sql
CREATE DATABASE controllerbot_db;
CREATE USER controllerbot WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE controllerbot_db TO controllerbot;
```

### Настройки в .env:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=controllerbot_db
DB_USER=controllerbot
DB_PASSWORD=your_password
```

## 🚨 **Решение проблем**

### Ошибка "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### Ошибка подключения к БД
- Проверьте, что PostgreSQL запущен
- Проверьте настройки в .env
- Проверьте, что база данных создана

### Ошибка токена бота
- Проверьте BOT_TOKEN в .env
- Убедитесь, что бот не заблокирован

## 📞 **Помощь**

- Полная документация: `docs/README.md`
- Чек-лист: `CHECKLIST.md`
- Тест конфигурации: `python test_config.py`
