# Start All Zimmer Platform Services
Write-Host "🚀 Starting Zimmer Platform - Simulated Server Environment" -ForegroundColor Green

# Check if all applications are built
Write-Host "📋 Checking if applications are built..." -ForegroundColor Yellow

# Check user panel build
if (-not (Test-Path "zimmer_user_panel\.next")) {
    Write-Host "❌ User panel not built. Building now..." -ForegroundColor Red
    Set-Location zimmer_user_panel
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ User panel build failed!" -ForegroundColor Red
        exit 1
    }
    Set-Location ..
}

# Check admin dashboard build
if (-not (Test-Path "zimmermanagement/zimmer-admin-dashboard/.next")) {
    Write-Host "❌ Admin dashboard not built. Building now..." -ForegroundColor Red
    Set-Location zimmermanagement/zimmer-admin-dashboard
    npm run build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Admin dashboard build failed!" -ForegroundColor Red
        exit 1
    }
    Set-Location ../..
}

Write-Host "✅ All applications are built!" -ForegroundColor Green

# Start services in separate windows
Write-Host "🚀 Starting services in separate windows..." -ForegroundColor Yellow

# Start backend
Start-Process powershell -ArgumentList "-NoExit", "-File", "start-backend.ps1" -WindowStyle Normal

# Wait a moment for backend to start
Start-Sleep -Seconds 3

# Start user panel
Start-Process powershell -ArgumentList "-NoExit", "-File", "start-user-panel.ps1" -WindowStyle Normal

# Start admin dashboard
Start-Process powershell -ArgumentList "-NoExit", "-File", "start-admin-dashboard.ps1" -WindowStyle Normal

Write-Host "`n✅ All services started in separate windows!" -ForegroundColor Green
Write-Host "`n🌐 Services are now running:" -ForegroundColor Green
Write-Host "  🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "  👤 User Panel: http://localhost:3000" -ForegroundColor Cyan
Write-Host "  🎛️ Admin Dashboard: http://localhost:3001" -ForegroundColor Cyan

Write-Host "`n📝 To stop services, close the individual PowerShell windows" -ForegroundColor Yellow
Write-Host "`n🔍 Testing connectivity..." -ForegroundColor Yellow

# Test backend connectivity
Start-Sleep -Seconds 5
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 10
    Write-Host "✅ Backend is responding: $($response.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding yet. It may still be starting..." -ForegroundColor Red
}

Write-Host "`n🎉 Server simulation environment is ready!" -ForegroundColor Green
