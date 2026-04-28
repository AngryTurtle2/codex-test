@echo off
setlocal

set PYTHON=python
set APP_NAME=HotkeyGuard

echo [1/4] Installing dependencies...
%PYTHON% -m pip install --upgrade pip || goto :error
%PYTHON% -m pip install -r requirements.txt pyinstaller || goto :error

echo [2/4] Cleaning old build artifacts...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo [3/4] Building one-file GUI executable...
%PYTHON% -m PyInstaller --noconfirm --onefile --windowed --name %APP_NAME% main.py || goto :error

echo [4/4] Done. Executable path: dist\%APP_NAME%.exe
goto :eof

:error
echo Build failed.
exit /b 1
