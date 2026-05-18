@echo off
REM Debug launcher for automation with motor/LED logging enabled.
REM Run this file by double-clicking or from PowerShell when you want log files.

REM Navigate to the project root (parent of this file's folder)
cd /d "%~dp0.."

REM Enable debug logging for motor and LED test modules.
set MOTOR_DEBUG=1
set LED_DEBUG=1

echo Running automation in debug mode with MOTOR_DEBUG=1 and LED_DEBUG=1
echo Debug log files will be written to the branch root:
echo   %cd%\motor_debug.log
echo   %cd%\led_debug.log

python -m AutomationScripts.core.gui_automation

pause
