# Makefile для ControllerBot-лайт 2.0

# Переменные окружения
PYTHON=python3
VENV=venv
ACTIVATE=. $(VENV)/bin/activate

# Установка зависимостей
install:
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE) && pip install -r requirements.txt

# Запуск бота
run:
	$(ACTIVATE) && $(PYTHON) bot.py

# Тесты
test:
	$(ACTIVATE) && pytest -v

# Бэкап БД
backup:
	./deploy/backup_postgres.sh

# Форматирование кода
format:
	$(ACTIVATE) && black .

# Линтинг
lint:
	$(ACTIVATE) && ruff check .

# Очистка venv и кеша
clean:
	rm -rf $(VENV) __pycache__ .pytest_cache
