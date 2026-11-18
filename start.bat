@echo off
title NutriScan Launcher
echo ===================================================
echo           Starting NutriScan v1.0
echo ===================================================
echo [1/2] Launching FastAPI Backend on http://localhost:8000...
start "NutriScan Backend (FastAPI)" cmd /k "cd /d %~dp0backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

echo [2/2] Launching React Frontend on http://localhost:3000...
start "NutriScan Frontend (Vite)" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ===================================================
echo Services are starting in separate terminal windows!
echo - Frontend:  http://localhost:3000
echo - Backend:   http://localhost:8000/api/v1/health
echo - API Docs:  http://localhost:8000/docs
echo ===================================================
echo.
pause
