@echo off
echo =============================================
echo  M-Track Automation - Setup and Run
echo =============================================

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH.
    pause
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo Setup complete!
echo.
echo USAGE:
echo   Step 1 - Discover form fields (run once to see what fields are in the form):
echo     python mtrack_automation.py --discover
echo.
echo   Step 2 - Edit config.json and fill in the field_mapping section
echo.
echo   Step 3 - Test with a dry run (reads sheet, no browser):
echo     python mtrack_automation.py --dry-run
echo.
echo   Step 4 - Run with 1 row first to verify:
echo     python mtrack_automation.py --rows 1
echo.
echo   Step 5 - Run all rows:
echo     python mtrack_automation.py
echo.
pause
