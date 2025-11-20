@echo off
REM Jarvis AI Assistant - Windows Deployment Script
REM This script installs and configures Jarvis as a Windows service

setlocal enabledelayedexpansion

echo ========================================
echo Jarvis AI Assistant - Windows Deployment
echo ========================================

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo This script must be run as Administrator
    pause
    exit /b 1
)

REM Configuration
set APP_NAME=JarvisAI
set APP_DIR=C:\Jarvis
set SERVICE_NAME=JarvisAI

echo [1/6] Creating application directory...
if not exist "%APP_DIR%" mkdir "%APP_DIR%"
if not exist "%APP_DIR%\logs" mkdir "%APP_DIR%\logs"
if not exist "%APP_DIR%\data" mkdir "%APP_DIR%\data"

echo [2/6] Copying application files...
xcopy /E /I /Y . "%APP_DIR%"

echo [3/6] Installing Python dependencies...
cd /d "%APP_DIR%"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pywin32 python-dotenv

echo [4/6] Setting up environment configuration...
if not exist "%APP_DIR%\.env" (
    copy .env.example "%APP_DIR%\.env"
    echo.
    echo Please edit %APP_DIR%\.env with your API keys
    echo.
)

echo [5/6] Installing Windows service...
python deployment\jarvis-windows-service.py install

echo [6/6] Configuring service...
sc config %SERVICE_NAME% start= auto
sc description %SERVICE_NAME% "Jarvis AI Assistant with Enhanced Features"

REM Start the service
echo Starting Jarvis service...
net start %SERVICE_NAME%

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo ✅ Jarvis AI Assistant deployed successfully!
    echo ========================================
    echo.
    echo Service Status: Running
    echo Application Directory: %APP_DIR%
    echo Service Name: %SERVICE_NAME%
    echo.
    echo Useful Commands:
    echo   • Start Service: net start %SERVICE_NAME%
    echo   • Stop Service: net stop %SERVICE_NAME%
    echo   • Restart Service: net stop %SERVICE_NAME% && net start %SERVICE_NAME%
    echo   • Check Status: sc query %SERVICE_NAME%
    echo   • View Logs: type "%APP_DIR%\logs\jarvis.log"
    echo.
    echo Don't forget to:
    echo   1. Edit %APP_DIR%\.env with your API keys
    echo   2. Restart service: net stop %SERVICE_NAME% && net start %SERVICE_NAME%
    echo.
) else (
    echo.
    echo ❌ Failed to start Jarvis service
    echo Please check the Windows Event Viewer for error details
    echo.
)

echo Deployment complete. Press any key to exit...
pause > nul