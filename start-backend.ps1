# Start Backend Service
Write-Host "🚀 Starting Zimmer Backend..." -ForegroundColor Green

# Activate virtual environment and start backend
& ".\venv\Scripts\Activate.ps1"
Set-Location zimmer-backend
python main.py
