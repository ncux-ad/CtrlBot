#!/bin/bash

# CtrlBot Monitoring Script
# This script monitors the bot and sends alerts if needed

set -e

# Configuration
BOT_NAME="CtrlBot"
LOG_FILE="/opt/ctrlbot/logs/monitor.log"
ALERT_EMAIL="admin@example.com"  # Change this to your email
TELEGRAM_ALERT_CHAT_ID=""  # Optional: Telegram chat for alerts

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Log function
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Check if service is running
check_service() {
    if systemctl is-active --quiet ctrlbot; then
        log "✅ Service is running"
        return 0
    else
        log "❌ Service is not running"
        return 1
    fi
}

# Check if bot is responding
check_bot_response() {
    # This would require implementing a health endpoint
    # For now, we'll check if the process is running
    if pgrep -f "python.*bot.py" > /dev/null; then
        log "✅ Bot process is running"
        return 0
    else
        log "❌ Bot process is not running"
        return 1
    fi
}

# Check disk space
check_disk_space() {
    local usage=$(df /opt/ctrlbot | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$usage" -lt 90 ]; then
        log "✅ Disk usage: ${usage}%"
        return 0
    else
        log "❌ Disk usage critical: ${usage}%"
        return 1
    fi
}

# Check log file size
check_log_size() {
    local log_size=$(du -m /opt/ctrlbot/logs | tail -1 | awk '{print $1}')
    if [ "$log_size" -lt 100 ]; then
        log "✅ Log size: ${log_size}MB"
        return 0
    else
        log "⚠️ Log size large: ${log_size}MB"
        return 1
    fi
}

# Send alert
send_alert() {
    local message="$1"
    log "🚨 ALERT: $message"
    
    # Send email alert
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "CtrlBot Alert" "$ALERT_EMAIL"
    fi
    
    # Send Telegram alert (if configured)
    if [ -n "$TELEGRAM_ALERT_CHAT_ID" ] && [ -n "$BOT_TOKEN" ]; then
        curl -s -X POST "https://api.telegram.org/bot$BOT_TOKEN/sendMessage" \
            -d chat_id="$TELEGRAM_ALERT_CHAT_ID" \
            -d text="🚨 CtrlBot Alert: $message" > /dev/null
    fi
}

# Restart service if needed
restart_service() {
    log "🔄 Restarting service..."
    systemctl restart ctrlbot
    sleep 5
    
    if check_service; then
        log "✅ Service restarted successfully"
        send_alert "CtrlBot service was restarted successfully"
    else
        log "❌ Failed to restart service"
        send_alert "CRITICAL: Failed to restart CtrlBot service"
    fi
}

# Main monitoring function
main() {
    log "🔍 Starting monitoring check..."
    
    local issues=0
    
    # Check service status
    if ! check_service; then
        ((issues++))
        restart_service
    fi
    
    # Check bot response
    if ! check_bot_response; then
        ((issues++))
        send_alert "CtrlBot is not responding"
    fi
    
    # Check disk space
    if ! check_disk_space; then
        ((issues++))
        send_alert "Disk space critical on CtrlBot server"
    fi
    
    # Check log size
    if ! check_log_size; then
        ((issues++))
        # Rotate logs
        log "🔄 Rotating logs..."
        /usr/sbin/logrotate -f /etc/logrotate.d/ctrlbot
    fi
    
    # Summary
    if [ $issues -eq 0 ]; then
        log "✅ All checks passed"
    else
        log "⚠️ $issues issues found"
    fi
    
    log "🏁 Monitoring check completed"
}

# Run monitoring
main "$@"
