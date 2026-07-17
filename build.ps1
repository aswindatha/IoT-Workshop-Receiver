# Build script for the IoT Workshop Receiver (Windows / Linux)
#
# Usage (PowerShell):
#   .\build.ps1
#
# Usage (bash / Linux):
#   bash build.sh
#
# Produces dist/IoT-Workshop-Receiver/ with the executable.

param(
    [switch]$Clean
)

$ErrorActionPreference = "Stop"

Write-Host "==> Installing dependencies" -ForegroundColor Cyan
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller

if ($Clean) {
    Write-Host "==> Cleaning previous build artifacts" -ForegroundColor Yellow
    if (Test-Path build) { Remove-Item -Recurse -Force build }
    if (Test-Path dist)  { Remove-Item -Recurse -Force dist }
}

Write-Host "==> Building executable with PyInstaller" -ForegroundColor Cyan
pyinstaller --noconfirm receiver.spec

Write-Host "==> Done. Output: dist/IoT-Workshop-Receiver/" -ForegroundColor Green
