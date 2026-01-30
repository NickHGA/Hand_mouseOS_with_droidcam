@echo off
REM =============================================================================
REM RemoteCam - Stream to Virtual Webcam (Windows)
REM =============================================================================
REM This script captures the MJPEG stream from RemoteCam
REM Requires: FFmpeg, OBS Virtual Camera or similar
REM =============================================================================

setlocal EnableDelayedExpansion

REM Configuration - Edit these values
set PHONE_IP=192.168.1.100
set PHONE_PORT=8080
set STREAM_ENDPOINT=/video
set WIDTH=640
set HEIGHT=480
set FPS=30

REM Build stream URL
set STREAM_URL=http://%PHONE_IP%:%PHONE_PORT%%STREAM_ENDPOINT%

echo ========================================
echo   RemoteCam to Virtual Webcam
echo ========================================
echo.
echo Stream URL:   %STREAM_URL%
echo Resolution:   %WIDTH%x%HEIGHT%
echo Framerate:    %FPS% fps
echo ========================================
echo.

REM Check if FFmpeg is available
where ffmpeg >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: FFmpeg not found in PATH
    echo.
    echo Please install FFmpeg:
    echo   Option 1: winget install Gyan.FFmpeg
    echo   Option 2: choco install ffmpeg
    echo   Option 3: Download from https://ffmpeg.org/download.html
    echo.
    pause
    exit /b 1
)

echo FFmpeg found. Testing connection to RemoteCam...
echo.

REM Test connection using curl or PowerShell
powershell -Command "try { Invoke-WebRequest -Uri '%STREAM_URL%' -TimeoutSec 5 -Method Head | Out-Null; Write-Host 'RemoteCam is reachable' -ForegroundColor Green } catch { Write-Host 'Cannot reach RemoteCam!' -ForegroundColor Red; exit 1 }"
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Make sure:
    echo   1. RemoteCam is running on your phone
    echo   2. Phone and PC are on the same network
    echo   3. IP address is correct ^(%PHONE_IP%^)
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   METHOD 1: Preview Only ^(no virtual cam^)
echo ========================================
echo.
echo Starting FFplay preview window...
echo Press Q in the video window to close it
echo.

REM Start FFplay for preview
start /B ffplay -fflags nobuffer -flags low_delay -framedrop -i "%STREAM_URL%" -window_title "RemoteCam Preview"

echo.
echo ========================================
echo   METHOD 2: Using OBS Virtual Camera
echo ========================================
echo.
echo To use as a virtual webcam:
echo   1. Open OBS Studio
echo   2. Add a Media Source with URL: %STREAM_URL%
echo   3. Click "Start Virtual Camera" in OBS
echo   4. Select "OBS Virtual Camera" in your app
echo.
echo Press any key to exit...
pause >nul
