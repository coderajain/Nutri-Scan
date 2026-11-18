@echo off
title NutriScan Terminator
echo ===================================================
echo           Stopping NutriScan Services
echo ===================================================

echo Stopping services running on port 8000 and 3000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "') do (
    taskkill /F /PID %%a 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":3000 "') do (
    taskkill /F /PID %%a 2>nul
)

echo NutriScan stopped.
pause
