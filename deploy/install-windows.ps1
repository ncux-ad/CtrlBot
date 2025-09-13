# CtrlBot Installation Script for Windows
# This script sets up CtrlBot as a Windows Service

param(
    [string]$ServiceName = "CtrlBot",
    [string]$InstallPath = "C:\CtrlBot",
    [string]$User = "SYSTEM"
)

Write-Host "🚀 Installing CtrlBot on Windows..." -ForegroundColor Green

# Check if running as Administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "❌ This script requires Administrator privileges!" -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ Error: .env file not found!" -ForegroundColor Red
    Write-Host "Please create .env file with required configuration:" -ForegroundColor Yellow
    Write-Host "  Copy-Item env.example .env" -ForegroundColor Yellow
    Write-Host "  # Edit .env with your settings" -ForegroundColor Yellow
    exit 1
}

Write-Host "Step 1: Creating installation directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path $InstallPath -Force | Out-Null

Write-Host "Step 2: Copying application files..." -ForegroundColor Yellow
Copy-Item -Path ".\*" -Destination $InstallPath -Recurse -Force

Write-Host "Step 3: Setting up Python environment..." -ForegroundColor Yellow
Set-Location $InstallPath
python -m venv venv
& ".\venv\Scripts\Activate.ps1"
pip install -r requirements.txt

Write-Host "Step 4: Creating Windows Service..." -ForegroundColor Yellow

# Create service script
$ServiceScript = @"
import sys
import os
sys.path.insert(0, r'$InstallPath')

import asyncio
from bot import main

if __name__ == '__main__':
    asyncio.run(main())
"@

$ServiceScript | Out-File -FilePath "$InstallPath\service_runner.py" -Encoding UTF8

# Install NSSM (Non-Sucking Service Manager) if not present
$NSSMPath = "$InstallPath\nssm.exe"
if (-not (Test-Path $NSSMPath)) {
    Write-Host "Downloading NSSM..." -ForegroundColor Yellow
    $NSSMUrl = "https://nssm.cc/release/nssm-2.24.zip"
    $NSSMZip = "$InstallPath\nssm.zip"
    Invoke-WebRequest -Uri $NSSMUrl -OutFile $NSSMZip
    Expand-Archive -Path $NSSMZip -DestinationPath "$InstallPath\nssm" -Force
    Copy-Item "$InstallPath\nssm\nssm-2.24\win64\nssm.exe" $NSSMPath
    Remove-Item "$InstallPath\nssm" -Recurse -Force
    Remove-Item $NSSMZip -Force
}

# Create Windows Service
& $NSSMPath install $ServiceName "$InstallPath\venv\Scripts\python.exe" "$InstallPath\service_runner.py"
& $NSSMPath set $ServiceName DisplayName "CtrlBot Telegram Bot"
& $NSSMPath set $ServiceName Description "CtrlBot - Telegram Bot for Channel Management"
& $NSSMPath set $ServiceName Start SERVICE_AUTO_START
& $NSSMPath set $ServiceName AppDirectory $InstallPath
& $NSSMPath set $ServiceName AppStdout "$InstallPath\logs\service.log"
& $NSSMPath set $ServiceName AppStderr "$InstallPath\logs\service_error.log"

Write-Host "Step 5: Creating log directory..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$InstallPath\logs" -Force | Out-Null

Write-Host "Step 6: Setting up log rotation..." -ForegroundColor Yellow
# Create log rotation script
$LogRotateScript = @"
# CtrlBot Log Rotation Script
`$LogPath = "$InstallPath\logs"
`$MaxSize = 10MB
`$MaxFiles = 30

Get-ChildItem "`$LogPath\*.log" | Where-Object { `$_.Length -gt `$MaxSize } | ForEach-Object {
    `$NewName = "`$(`$_.BaseName)_`$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
    Rename-Item `$_.FullName "`$LogPath\`$NewName"
}

# Keep only last 30 files
Get-ChildItem "`$LogPath\*.log" | Sort-Object CreationTime -Descending | Select-Object -Skip 30 | Remove-Item -Force
"@

$LogRotateScript | Out-File -FilePath "$InstallPath\log_rotate.ps1" -Encoding UTF8

# Create scheduled task for log rotation
$Action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-File `"$InstallPath\log_rotate.ps1`""
$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00"
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries
Register-ScheduledTask -TaskName "CtrlBot Log Rotation" -Action $Action -Trigger $Trigger -Settings $Settings -User $User | Out-Null

Write-Host "Step 7: Starting service..." -ForegroundColor Yellow
Start-Service -Name $ServiceName

Write-Host "✅ Installation completed!" -ForegroundColor Green
Write-Host ""
Write-Host "Service Information:"
Write-Host "  Name: $ServiceName"
Write-Host "  Path: $InstallPath"
Write-Host "  Status: $(Get-Service -Name $ServiceName | Select-Object -ExpandProperty Status)"
Write-Host ""
Write-Host "Management commands:"
Write-Host "  Start-Service -Name $ServiceName     # Start service"
Write-Host "  Stop-Service -Name $ServiceName      # Stop service"
Write-Host "  Restart-Service -Name $ServiceName   # Restart service"
Write-Host "  Get-Service -Name $ServiceName       # Check status"
Write-Host ""
Write-Host "Logs location: $InstallPath\logs"
Write-Host "Configuration: $InstallPath\.env"
