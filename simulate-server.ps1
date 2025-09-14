# Simulate Server Environment Script
# This script mimics the server deployment process

Write-Host "🚀 Starting Zimmer Platform Simulation..." -ForegroundColor Green

# Check if PM2 is installed globally
Write-Host "📋 Checking PM2 installation..." -ForegroundColor Yellow
try {
    $pm2Version = pm2 --version
    Write-Host "✅ PM2 is installed: $pm2Version" -ForegroundColor Green
} catch {
    Write-Host "❌ PM2 not found. Installing PM2 globally..." -ForegroundColor Red
    npm install -g pm2
}

# Stop any existing PM2 processes
Write-Host "🛑 Stopping existing PM2 processes..." -ForegroundColor Yellow
pm2 delete all 2>$null

# Build all frontend applications
Write-Host "🔨 Building frontend applications..." -ForegroundColor Yellow

# Build user panel
Write-Host "  📱 Building user panel..." -ForegroundColor Cyan
Set-Location zimmer_user_panel
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ User panel build failed!" -ForegroundColor Red
    exit 1
}
Set-Location ..

# Build admin dashboard
Write-Host "  🎛️ Building admin dashboard..." -ForegroundColor Cyan
Set-Location zimmermanagement/zimmer-admin-dashboard
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Admin dashboard build failed!" -ForegroundColor Red
    exit 1
}
Set-Location ../..

# Start all services with PM2
Write-Host "🚀 Starting all services with PM2..." -ForegroundColor Yellow
pm2 start ecosystem.config.js

# Show status
Write-Host "📊 Service Status:" -ForegroundColor Green
pm2 status

Write-Host "`n🌐 Services are now running:" -ForegroundColor Green
Write-Host "  🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  👤 User Panel: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  🎛️ Admin Dashboard: http://localhost:3001" -ForegroundColor Cyan

Write-Host "`n📝 Useful commands:" -ForegroundColor Yellow
Write-Host "  pm2 status          - Check service status" -ForegroundColor White
Write-Host "  pm2 logs            - View all logs" -ForegroundColor White
Write-Host "  pm2 logs [app-name] - View specific app logs" -ForegroundColor White
Write-Host "  pm2 restart all     - Restart all services" -ForegroundColor White
Write-Host "  pm2 stop all        - Stop all services" -ForegroundColor White
Write-Host "  pm2 delete all      - Delete all services" -ForegroundColor White

Write-Host "`n✅ Server simulation started successfully!" -ForegroundColor Green
