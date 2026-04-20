@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo   SmartBU Auto Install / Checks
echo ========================================
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0install_prerequisites.ps1"
if errorlevel 1 (
  echo.
  echo Auto install finished with errors.
) else (
  echo.
  echo Auto install finished successfully.
)

echo.
pause
