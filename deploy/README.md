# 🚀 CtrlBot Deployment Guide

This guide covers different deployment options for CtrlBot.

## 📋 Prerequisites

### Required
- Python 3.11+
- PostgreSQL 12+
- Telegram Bot Token
- YandexGPT API Key (optional)

### Optional
- Docker & Docker Compose
- systemd (Linux)
- NSSM (Windows)

## 🐧 Linux Deployment (systemd)

### 1. Quick Install
```bash
# Make install script executable
chmod +x deploy/install.sh

# Run installation
./deploy/install.sh
```

### 2. Manual Setup
```bash
# Create user
sudo useradd -r -s /bin/false -d /opt/ctrlbot ctrlbot

# Create directories
sudo mkdir -p /opt/ctrlbot/{logs,data}
sudo chown -R ctrlbot:ctrlbot /opt/ctrlbot

# Copy files
sudo cp -r . /opt/ctrlbot/
sudo chown -R ctrlbot:ctrlbot /opt/ctrlbot

# Install service
sudo cp deploy/ctrlbot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable ctrlbot
```

### 3. Configuration
```bash
# Copy and edit configuration
sudo cp env.example /opt/ctrlbot/.env
sudo nano /opt/ctrlbot/.env

# Start service
sudo systemctl start ctrlbot
```

### 4. Service Management
```bash
# Start/Stop/Restart
sudo systemctl start ctrlbot
sudo systemctl stop ctrlbot
sudo systemctl restart ctrlbot

# Check status
sudo systemctl status ctrlbot

# View logs
sudo journalctl -u ctrlbot -f
```

## 🐳 Docker Deployment

### 1. Quick Deploy
```bash
# Make deploy script executable
chmod +x deploy/docker-deploy.sh

# Run deployment
./deploy/docker-deploy.sh
```

### 2. Manual Setup
```bash
# Create .env file
cp env.example .env
# Edit .env with your settings

# Start services
docker-compose up -d

# Check status
docker-compose ps
```

### 3. Management
```bash
# View logs
docker-compose logs -f ctrlbot

# Restart bot
docker-compose restart ctrlbot

# Stop all services
docker-compose down

# Update and restart
docker-compose pull
docker-compose up -d
```

## 🪟 Windows Deployment

### 1. PowerShell Install
```powershell
# Run as Administrator
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\deploy\install-windows.ps1
```

### 2. Manual Setup
```powershell
# Create service directory
New-Item -ItemType Directory -Path "C:\CtrlBot" -Force

# Copy files
Copy-Item -Path ".\*" -Destination "C:\CtrlBot" -Recurse

# Setup Python environment
cd C:\CtrlBot
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Install as Windows Service (using NSSM)
# Download NSSM from https://nssm.cc/
nssm install CtrlBot "C:\CtrlBot\venv\Scripts\python.exe" "C:\CtrlBot\bot.py"
nssm start CtrlBot
```

## 🔧 Configuration

### Environment Variables
```env
# Required
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
DB_PASSWORD=your_strong_password

# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ctrlbot_db
DB_USER=ctrlbot

# AI (Optional)
YANDEX_API_KEY=your_yandex_api_key
YANDEX_FOLDER_ID=your_folder_id

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/bot.log
LOG_ERROR_FILE=logs/errors.log
TIMEZONE=Europe/Moscow
```

### Database Setup
```sql
-- Create database
CREATE DATABASE ctrlbot_db;

-- Create user
CREATE USER ctrlbot WITH PASSWORD 'your_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ctrlbot_db TO ctrlbot;
```

## 📊 Monitoring

### Health Check
```bash
# Run health check
python deploy/healthcheck.py

# Check specific components
python -c "from services.ai import ai_service; print(ai_service.check_api_status())"
```

### Monitoring Script
```bash
# Setup monitoring
chmod +x deploy/monitor.sh

# Run monitoring
./deploy/monitor.sh

# Setup cron job for regular monitoring
echo "*/5 * * * * /opt/ctrlbot/deploy/monitor.sh" | crontab -
```

### Log Management
```bash
# View logs
tail -f /opt/ctrlbot/logs/bot.log
tail -f /opt/ctrlbot/logs/errors.log

# Log rotation (automatic with systemd)
sudo journalctl -u ctrlbot --since "1 hour ago"
```

## 🔒 Security

### Linux Security
```bash
# Set proper permissions
sudo chown -R ctrlbot:ctrlbot /opt/ctrlbot
sudo chmod 600 /opt/ctrlbot/.env
sudo chmod 755 /opt/ctrlbot

# Firewall rules
sudo ufw allow out 443/tcp  # HTTPS for API calls
sudo ufw allow out 5432/tcp # PostgreSQL
```

### Docker Security
```yaml
# Use non-root user in Dockerfile
USER ctrlbot

# Limit resources
deploy:
  resources:
    limits:
      memory: 512M
      cpus: '0.5'
```

## 🚨 Troubleshooting

### Common Issues

#### Service won't start
```bash
# Check logs
sudo journalctl -u ctrlbot -n 50

# Check configuration
python test_config.py

# Check database connection
psql -h localhost -U ctrlbot -d ctrlbot_db
```

#### Bot not responding
```bash
# Check if process is running
ps aux | grep python

# Check network connectivity
curl -s https://api.telegram.org/bot$BOT_TOKEN/getMe

# Restart service
sudo systemctl restart ctrlbot
```

#### Database connection issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database exists
sudo -u postgres psql -l | grep ctrlbot

# Test connection
python -c "from database import db; import asyncio; asyncio.run(db.connect())"
```

### Log Analysis
```bash
# Search for errors
grep -i error /opt/ctrlbot/logs/bot.log

# Monitor in real-time
tail -f /opt/ctrlbot/logs/bot.log | grep -i error

# Check specific time range
grep "2025-09-13 10:" /opt/ctrlbot/logs/bot.log
```

## 📈 Performance Tuning

### Database Optimization
```sql
-- Create indexes for better performance
CREATE INDEX idx_posts_created_at ON posts(created_at);
CREATE INDEX idx_posts_status ON posts(status);
CREATE INDEX idx_reminders_scheduled_time ON reminders(scheduled_time);
```

### System Optimization
```bash
# Increase file limits
echo "ctrlbot soft nofile 65536" >> /etc/security/limits.conf
echo "ctrlbot hard nofile 65536" >> /etc/security/limits.conf

# Optimize PostgreSQL
# Edit /etc/postgresql/*/main/postgresql.conf
shared_buffers = 256MB
effective_cache_size = 1GB
```

## 🔄 Updates

### Systemd Update
```bash
# Stop service
sudo systemctl stop ctrlbot

# Backup current version
sudo cp -r /opt/ctrlbot /opt/ctrlbot.backup

# Update code
sudo cp -r . /opt/ctrlbot/
sudo chown -R ctrlbot:ctrlbot /opt/ctrlbot

# Start service
sudo systemctl start ctrlbot
```

### Docker Update
```bash
# Pull latest images
docker-compose pull

# Restart services
docker-compose up -d

# Clean up old images
docker system prune -f
```

## 📞 Support

For issues and questions:
1. Check logs first
2. Run health check
3. Check this documentation
4. Create an issue on GitHub
