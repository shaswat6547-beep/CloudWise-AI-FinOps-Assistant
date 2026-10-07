@echo off
title CloudWise - AI FinOps Assistant

cd /d "C:\Users\shasw\OneDrive\Desktop\Cloudwise"

echo Starting CloudWise Dashboard...
start "CloudWise Dashboard" cmd /k python frontend\app.py

timeout /t 3 /nobreak >nul

echo Starting CloudWise AI...
start "CloudWise AI" cmd /k python frontend\chat.py

timeout /t 5 /nobreak >nul

start http://127.0.0.1:7860

echo.
echo ==========================================
echo       CloudWise is now running!
echo ==========================================
echo Dashboard: http://127.0.0.1:7860
echo AI Chat:   http://127.0.0.1:7861
echo ==========================================