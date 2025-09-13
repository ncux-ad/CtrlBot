#!/bin/bash

# CtrlBot Installation Script for Linux
# This script installs CtrlBot as a systemd service

set -e

echo "🚀 Installing CtrlBot..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo -e "${RED}This script should not be run as root${NC}"
   exit 1
fi

# Configuration
BOT_USER="ctrlbot"
BOT_HOME="/opt/ctrlbot"
SERVICE_FILE="ctrlbot.service"

echo -e "${YELLOW}Step 1: Creating user and directories...${NC}"

# Create user if doesn't exist
if ! id "$BOT_USER" &>/dev/null; then
    sudo useradd -r -s /bin/false -d "$BOT_HOME" "$BOT_USER"
    echo "✅ User $BOT_USER created"
else
    echo "✅ User $BOT_USER already exists"
fi

# Create directories
sudo mkdir -p "$BOT_HOME"
sudo mkdir -p "$BOT_HOME/logs"
sudo mkdir -p "$BOT_HOME/data"
sudo chown -R "$BOT_USER:$BOT_USER" "$BOT_HOME"

echo -e "${YELLOW}Step 2: Copying files...${NC}"

# Copy application files
sudo cp -r . "$BOT_HOME/"
sudo chown -R "$BOT_USER:$BOT_USER" "$BOT_HOME"

echo -e "${YELLOW}Step 3: Setting up Python environment...${NC}"

# Create virtual environment
cd "$BOT_HOME"
sudo -u "$BOT_USER" python3 -m venv venv
sudo -u "$BOT_USER" venv/bin/pip install -r requirements.txt

echo -e "${YELLOW}Step 4: Installing systemd service...${NC}"

# Copy service file
sudo cp "deploy/$SERVICE_FILE" "/etc/systemd/system/"
sudo systemctl daemon-reload
sudo systemctl enable ctrlbot

echo -e "${YELLOW}Step 5: Setting up log rotation...${NC}"

# Create logrotate configuration
sudo tee /etc/logrotate.d/ctrlbot > /dev/null <<EOF
$BOT_HOME/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 $BOT_USER $BOT_USER
    postrotate
        systemctl reload ctrlbot > /dev/null 2>&1 || true
    endscript
}
EOF

echo -e "${YELLOW}Step 6: Setting up firewall (if ufw is available)...${NC}"

# Configure firewall if ufw is available
if command -v ufw &> /dev/null; then
    sudo ufw allow out 443/tcp  # HTTPS for API calls
    sudo ufw allow out 5432/tcp # PostgreSQL
    echo "✅ Firewall configured"
fi

echo -e "${GREEN}Installation completed!${NC}"
echo ""
echo "Next steps:"
echo "1. Copy your .env file to $BOT_HOME/"
echo "2. Configure PostgreSQL database"
echo "3. Start the service: sudo systemctl start ctrlbot"
echo "4. Check status: sudo systemctl status ctrlbot"
echo "5. View logs: sudo journalctl -u ctrlbot -f"
echo ""
echo "Service management commands:"
echo "  sudo systemctl start ctrlbot    # Start service"
echo "  sudo systemctl stop ctrlbot     # Stop service"
echo "  sudo systemctl restart ctrlbot  # Restart service"
echo "  sudo systemctl status ctrlbot   # Check status"
echo "  sudo journalctl -u ctrlbot -f   # View logs"
