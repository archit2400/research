# ResearchPilot Startup Script for PowerShell
Write-Host "========================================================" -ForegroundColor Cyan
Write-Host "  Starting ResearchPilot - Multi-Agent Academic Assistant" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan

# 1. Start FastAPI Backend in a new window
Write-Host "[1/2] Launching Backend on http://localhost:8000 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot'; python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload"

# 2. Start Vite Frontend in a new window
Write-Host "[2/2] Launching Frontend on http://localhost:5173 ..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$PSScriptRoot\frontend'; npm run dev"

Write-Host ""
Write-Host "ResearchPilot is running!" -ForegroundColor Green
Write-Host "  🌐 Open Web Dashboard: http://localhost:5173" -ForegroundColor White
Write-Host "  📚 Backend Swagger Docs: http://localhost:8000/docs" -ForegroundColor White
Write-Host "========================================================" -ForegroundColor Cyan
