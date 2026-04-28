param(
    [string]$Python = "python",
    [string]$AppName = "HotkeyGuard"
)

$ErrorActionPreference = "Stop"

Write-Host "[1/4] Installing dependencies..."
& $Python -m pip install --upgrade pip
& $Python -m pip install -r requirements.txt pyinstaller

Write-Host "[2/4] Cleaning old build artifacts..."
if (Test-Path build) { Remove-Item -Recurse -Force build }
if (Test-Path dist) { Remove-Item -Recurse -Force dist }

Write-Host "[3/4] Building one-file GUI executable..."
& $Python -m PyInstaller --noconfirm --onefile --windowed --name $AppName main.py

Write-Host "[4/4] Done. Executable path: dist/$AppName.exe"
