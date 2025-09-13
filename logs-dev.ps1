# Просмотр логов CtrlBot
Write-Host "📋 Просмотр логов CtrlBot..." -ForegroundColor Green
docker-compose -f docker-compose.dev.yml logs ctrlbot -f
