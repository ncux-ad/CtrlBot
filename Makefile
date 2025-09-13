# CtrlBot Development Commands

.PHONY: start stop restart logs clean

start:
	@echo "🚀 Запуск CtrlBot в режиме разработки..."
	docker-compose -f docker-compose.dev.yml --env-file .env up -d
	@echo "✅ Контейнеры запущены!"

stop:
	@echo "🛑 Остановка CtrlBot..."
	docker-compose -f docker-compose.dev.yml down
	@echo "✅ Контейнеры остановлены!"

restart: stop start
	@echo "🔄 CtrlBot перезапущен!"

logs:
	@echo "📋 Просмотр логов CtrlBot..."
	docker-compose -f docker-compose.dev.yml logs ctrlbot -f

logs-tail:
	@echo "📋 Последние 50 строк логов..."
	docker-compose -f docker-compose.dev.yml logs ctrlbot --tail=50

clean:
	@echo "🧹 Очистка контейнеров и volumes..."
	docker-compose -f docker-compose.dev.yml down -v
	docker system prune -f
	@echo "✅ Очистка завершена!"

help:
	@echo "Доступные команды:"
	@echo "  make start      - Запустить CtrlBot"
	@echo "  make stop       - Остановить CtrlBot"
	@echo "  make restart    - Перезапустить CtrlBot"
	@echo "  make logs       - Просмотр логов (live)"
	@echo "  make logs-tail  - Последние 50 строк логов"
	@echo "  make clean      - Очистить все контейнеры и volumes"
	@echo "  make help       - Показать эту справку"
