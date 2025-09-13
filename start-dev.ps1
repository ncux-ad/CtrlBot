# Запуск CtrlBot в режиме разработки
Write-Host "🚀 Запуск CtrlBot в режиме разработки..." -ForegroundColor Green
docker-compose -f docker-compose.dev.yml --env-file .env up -d
Write-Host "✅ Контейнеры запущены!" -ForegroundColor Green
Write-Host "📋 Для просмотра логов: .\logs-dev.ps1" -ForegroundColor Yellow
