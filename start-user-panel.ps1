# Start User Panel Service
Write-Host "🚀 Starting Zimmer User Panel..." -ForegroundColor Green

Set-Location zimmer_user_panel
$env:NODE_ENV = "production"
$env:PORT = "3000"
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
npm start
