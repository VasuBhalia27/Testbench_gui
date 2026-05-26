@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo   SmartBU Auto Install / Checks
echo ========================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0install_prerequisites.ps1" %*
set "RC=%ERRORLEVEL%"
if %RC% neq 0 (
  echo.
  echo Auto install finished with errors.
) else (
  echo.
  echo Auto install finished successfully.
)

echo.
pause
exit /b %RC%
