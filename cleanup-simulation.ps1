# Cleanup Simulation Script
# This script stops and cleans up the simulated server environment

Write-Host "🧹 Cleaning up Zimmer Platform Simulation..." -ForegroundColor Yellow

# Stop all PM2 processes
Write-Host "🛑 Stopping all PM2 processes..." -ForegroundColor Yellow
pm2 delete all 2>$null

# Clear PM2 logs
Write-Host "🗑️ Clearing PM2 logs..." -ForegroundColor Yellow
pm2 flush

# Remove log files
Write-Host "📁 Removing log files..." -ForegroundColor Yellow
if (Test-Path "logs") {
    Remove-Item -Recurse -Force logs
    Write-Host "✅ Log files removed" -ForegroundColor Green
}

Write-Host "✅ Cleanup completed!" -ForegroundColor Green
