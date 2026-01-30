# =============================================================================
# RemoteCam - Install Virtual Camera (Windows)
# =============================================================================
# This script helps set up a virtual webcam on Windows
# Run as Administrator
# =============================================================================

$ErrorActionPreference = "Stop"

Write-Host "========================================"  -ForegroundColor Green
Write-Host "  RemoteCam - Virtual Camera Setup"  -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Green

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Host "Warning: This script should be run as Administrator" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Virtual Camera Options for Windows:" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. OBS Virtual Camera (Recommended - Easy)" -ForegroundColor Green
Write-Host "   - Download OBS Studio: https://obsproject.com/download" 
Write-Host "   - Install OBS, it includes a virtual camera"
Write-Host "   - Use OBS to capture RemoteCam stream and output to virtual cam"
Write-Host ""

Write-Host "2. Unity Capture (DirectShow - Advanced)" -ForegroundColor Yellow
Write-Host "   - GitHub: https://github.com/schellingb/UnityCapture"
Write-Host "   - Provides a DirectShow virtual camera"
Write-Host "   - Can be controlled programmatically"
Write-Host ""

Write-Host "3. akvcam (Open Source DirectShow)" -ForegroundColor Yellow
Write-Host "   - GitHub: https://github.com/AkVirtualCamera/akvcam"
Write-Host "   - Requires manual driver installation"
Write-Host ""

# Check if FFmpeg is installed
Write-Host "Checking for FFmpeg..." -ForegroundColor Cyan
$ffmpegPath = Get-Command ffmpeg -ErrorAction SilentlyContinue

if ($ffmpegPath) {
    Write-Host "FFmpeg found at: $($ffmpegPath.Source)" -ForegroundColor Green
} else {
    Write-Host "FFmpeg not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installing FFmpeg via winget..." -ForegroundColor Yellow
    
    try {
        winget install Gyan.FFmpeg
        Write-Host "FFmpeg installed successfully!" -ForegroundColor Green
    } catch {
        Write-Host "Failed to install FFmpeg automatically." -ForegroundColor Red
        Write-Host "Please download from: https://ffmpeg.org/download.html" -ForegroundColor Yellow
        Write-Host "Or install via Chocolatey: choco install ffmpeg" -ForegroundColor Yellow
    }
}

# Check if OBS is installed
Write-Host ""
Write-Host "Checking for OBS Studio..." -ForegroundColor Cyan

$obsPath = @(
    "${env:ProgramFiles}\obs-studio\bin\64bit\obs64.exe",
    "${env:ProgramFiles(x86)}\obs-studio\bin\64bit\obs64.exe"
)

$obsFound = $false
foreach ($path in $obsPath) {
    if (Test-Path $path) {
        Write-Host "OBS Studio found at: $path" -ForegroundColor Green
        $obsFound = $true
        break
    }
}

if (-not $obsFound) {
    Write-Host "OBS Studio not found." -ForegroundColor Yellow
    Write-Host "Download from: https://obsproject.com/download" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================"  -ForegroundColor Green
Write-Host "  Setup Instructions:"  -ForegroundColor Green
Write-Host "========================================"  -ForegroundColor Green
Write-Host ""
Write-Host "Option A: Using OBS Virtual Camera" -ForegroundColor Cyan
Write-Host "  1. Open OBS Studio"
Write-Host "  2. Add a 'Browser' source with RemoteCam URL"
Write-Host "  3. Or add a 'VLC Video Source' for MJPEG stream"
Write-Host "  4. Click 'Start Virtual Camera' in OBS"
Write-Host "  5. Select 'OBS Virtual Camera' in Zoom/Meet/Teams"
Write-Host ""
Write-Host "Option B: Using FFmpeg + Python Script" -ForegroundColor Cyan
Write-Host "  1. Run remotecam_to_webcam.bat or .py"
Write-Host "  2. Script captures stream and sends to virtual camera"
Write-Host ""
Write-Host "========================================"  -ForegroundColor Green
