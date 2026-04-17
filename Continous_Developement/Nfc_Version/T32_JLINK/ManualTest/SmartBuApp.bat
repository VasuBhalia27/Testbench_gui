@echo off
setlocal EnableDelayedExpansion
title SmartBU Manual Test (Quick)
color 0A

echo ========================================
echo    SmartBU Manual Test - Quick Check
echo ========================================
echo.

set "SCRIPT_DIR=%~dp0"
set "APP_ROOT=%SCRIPT_DIR%.."
cd /d "%APP_ROOT%"

:: Quick essential checks
echo Checking prerequisites...
echo ------------------------

:: Check Python
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Python found
) else (
    echo [FAIL] Python NOT found!
    echo Please install Python and add to PATH
    pause
    exit /b 1
)

:: Check Trace32 software
if exist "C:\T32\bin\windows64\t32marm.exe" (
    echo [OK] Trace32 found at C:\T32
) else (
    echo [WARN] Trace32 not found at default location
    echo        Expected: C:\T32\bin\windows64\t32marm.exe
)

:: ---------------------------------------------------------------
:: Auto-detect connected debugger hardware (Trace32 or J-Link)
:: Sets DEBUGGER_BACKEND=trace32 or jlink for the GUI to read.
:: ---------------------------------------------------------------
echo.
echo Detecting connected debugger hardware...

set "DEBUGGER_BACKEND=none"

:: --- Check for Lauterbach / Trace32 POD ---
wmic path Win32_PnPEntity get Name 2>nul | findstr /i "Lauterbach PODBUS" >nul 2>&1
if !errorlevel! equ 0 (
    set "DEBUGGER_BACKEND=trace32"
    echo [OK] Lauterbach Trace32 POD detected
    goto :debugger_found
)
wmic path Win32_PnPEntity get Name 2>nul | findstr /i "Lauterbach" >nul 2>&1
if !errorlevel! equ 0 (
    set "DEBUGGER_BACKEND=trace32"
    echo [OK] Lauterbach Trace32 debugger detected
    goto :debugger_found
)

:: --- Check for SEGGER J-Link ---
wmic path Win32_PnPEntity get Name 2>nul | findstr /i "J-Link" >nul 2>&1
if !errorlevel! equ 0 (
    set "DEBUGGER_BACKEND=jlink"
    echo [OK] SEGGER J-Link debugger detected
    goto :debugger_found
)
wmic path Win32_PnPEntity get Name 2>nul | findstr /i "SEGGER" >nul 2>&1
if !errorlevel! equ 0 (
    set "DEBUGGER_BACKEND=jlink"
    echo [OK] SEGGER J-Link debugger detected
    goto :debugger_found
)

:: --- Neither found ---
echo [WARN] No debugger hardware detected.
echo        Please check:
echo          - Is the debugger cable plugged in?
echo          - Is the LED on the probe lit?
echo          - Try a different USB port
echo          - For Trace32: USB driver must be installed
echo          - For J-Link:  SEGGER USB driver must be installed
echo.
set /p ignore="Ignore warning and continue? (y/n): "
if /i not "!ignore!"=="y" (
    echo Exiting...
    pause
    exit /b 1
)
:: Default to trace32 if user chooses to continue without detection
set "DEBUGGER_BACKEND=trace32"

:debugger_found
echo [INFO] Debugger backend set to: %DEBUGGER_BACKEND%

:: Check Repository
echo.
if exist "%APP_ROOT%\Gui_Main_Script\gui_main.py" (
    echo [OK] GUI script found
) else (
    echo [FAIL] GUI script not found!
    echo        Expected: %APP_ROOT%\Gui_Main_Script\gui_main.py
    pause
    exit /b 1
)

echo.
echo ------------------------
echo.

:: Launch GUI
echo Starting SmartBU GUI...
echo.
python "%APP_ROOT%\Gui_Main_Script\gui_main.py"

echo.
echo Application closed.
pause