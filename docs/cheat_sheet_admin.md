# 🧰 Admin Cheat Sheet

## Systemd
- Статус: `sudo systemctl status controllerbot`
- Рестарт: `sudo systemctl restart controllerbot`
- Логи: `journalctl -u controllerbot -f`

## Docker
- Запуск: `docker-compose up -d --build`
- Логи: `docker-compose logs -f bot`
- БД-консоль: `docker exec -it controllerbot_db psql -U controllerbot controllerbot_db`

## PostgreSQL
- Локально: `psql -U controllerbot -h 127.0.0.1 controllerbot_db`
- Размер БД: `\l+` или `SELECT pg_size_pretty(pg_database_size('controllerbot_db'));`
