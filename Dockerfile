FROM python:3.11-slim

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Создаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем Python зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем исходный код
COPY . .

# Создаем директории и пользователя
RUN mkdir -p /app/logs /app/data && \
    useradd -m -u 1000 botuser && \
    chown -R botuser:botuser /app
USER botuser

# Открываем порт для healthcheck
EXPOSE 8000

# Команда запуска (по умолчанию - обычный режим)
CMD ["python", "bot.py"]