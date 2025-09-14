# Start Admin Dashboard Service
Write-Host "🚀 Starting Zimmer Admin Dashboard..." -ForegroundColor Green

Set-Location zimmermanagement/zimmer-admin-dashboard
$env:NODE_ENV = "production"
$env:PORT = "3001"
$env:NEXT_PUBLIC_API_URL = "http://localhost:8000"
npm start
