@echo off
chcp 65001 >nul 2>&1
set PYTHONIOENCODING=utf-8
title MAHABHARATA SYSTEM - Starting...
cd /d "c:\Users\vinay\Desktop\mahabharata-system"

echo.
echo  ================================================
echo   🕉️  MAHABHARATA SYSTEM - Auto Start
echo  ================================================
echo.

:: Wait for network and Ollama to be ready
echo [STARTUP] Waiting for system to settle...
timeout /t 10 /nobreak >nul

:: Start Ollama if not running
echo [STARTUP] Checking Ollama...
tasklist /FI "IMAGENAME eq ollama.exe" 2>NUL | find /I "ollama.exe" >NUL
if %ERRORLEVEL% NEQ 0 (
    echo [STARTUP] Starting Ollama...
    start "" "ollama" serve
    timeout /t 5 /nobreak >nul
) else (
    echo [STARTUP] Ollama already running.
)

:: Wait for Ollama API to respond
echo [STARTUP] Waiting for Ollama API...
:wait_ollama
curl -s http://localhost:11434/api/version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    timeout /t 2 /nobreak >nul
    goto wait_ollama
)
echo [STARTUP] Ollama API ready!

:: Start the MAHABHARATA system
echo [STARTUP] Launching MAHABHARATA SYSTEM...
echo.

:: Open the dashboard in default browser after a short delay
start "" cmd /c "timeout /t 15 /nobreak >nul && start http://localhost:8000"

:: Start the main system (this will block and keep running)
python main.py
