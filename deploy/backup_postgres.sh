#!/bin/bash
# backup_postgres.sh — скрипт для бэкапа PostgreSQL
# Сохраняет дампы в /var/backups/postgres/

BACKUP_DIR=/var/backups/postgres
DATE=$(date +%Y-%m-%d_%H-%M-%S)
FILENAME=$BACKUP_DIR/controllerbot_$DATE.sql.gz

mkdir -p $BACKUP_DIR

pg_dump -h localhost -U controllerbot controllerbot_db | gzip > $FILENAME

# Хранить не больше 14 дней
find $BACKUP_DIR -type f -mtime +14 -delete
