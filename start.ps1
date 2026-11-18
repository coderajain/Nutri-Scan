# ===================================================
# NutriScan v1.0 - Unified Start Script (PowerShell)
# ===================================================
$root = $PSScriptRoot

Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "           Starting NutriScan v1.0                 " -ForegroundColor Cyan
Write-Host "===================================================" -ForegroundColor Cyan

Write-Host "`n[1/2] Launching FastAPI Backend (:8000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; Write-Host '--- NutriScan Backend (FastAPI) ---' -ForegroundColor Cyan; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "[2/2] Launching React Frontend (:3000)..." -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\frontend'; Write-Host '--- NutriScan Frontend (Vite) ---' -ForegroundColor Cyan; npm run dev"

Write-Host "`n===================================================" -ForegroundColor Cyan
Write-Host "Both services launched successfully in new windows!" -ForegroundColor Green
Write-Host "  * Frontend UI: http://localhost:3000" -ForegroundColor Yellow
Write-Host "  * Backend API: http://localhost:8000/api/v1/health" -ForegroundColor Yellow
Write-Host "  * API Docs:    http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "===================================================`n" -ForegroundColor Cyan
