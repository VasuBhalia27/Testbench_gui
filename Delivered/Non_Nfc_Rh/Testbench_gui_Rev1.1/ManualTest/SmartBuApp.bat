@echo off
title SmartBU Manual Test (Quick)
color 0A

echo ========================================
echo    SmartBU Manual Test - Quick Check
echo ========================================
echo.

cd /d C:\Ushin\Testbench_gui_Charan

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

:: Check Trace32
if exist "C:\T32\bin\windows64\t32marm.exe" (
    echo [OK] Trace32 found at C:\T32
) else (
    echo [WARN] Trace32 not found at default location
    echo        Expected: C:\T32\bin\windows64\t32marm.exe
)

:: Lauterbach detection - Using PnPEntity search
echo.
echo Checking Lauterbach debugger...

:: Method 1: Search by full device name (most reliable)
wmic path Win32_PnPEntity get Name | findstr /i "Lauterbach PODBUS" >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Lauterbach debugger detected (PODBUS)
) else (
    :: Method 2: Search by partial name
    wmic path Win32_PnPEntity get Name | findstr /i "Lauterbach" >nul 2>&1
    if %errorlevel% equ 0 (
        echo [OK] Lauterbach debugger detected
    ) else (
        :: Method 3: Search USB devices as fallback
        wmic path Win32_USBControllerDevice get Dependent | findstr /i "Lauterbach" >nul 2>&1
        if %errorlevel% equ 0 (
            echo [OK] Lauterbach debugger detected via USB
        ) else (
            echo [WARN] Lauterbach debugger NOT detected
            echo        Please check:
            echo          - Is the debugger plugged in?
            echo          - Is the LED on?
            echo          - Try a different USB port
            echo.
            set /p ignore="Ignore warning and continue? (y/n): "
            if /i not "!ignore!"=="y" (
                echo Exiting...
                pause
                exit /b 1
            )
        )
    )
)

:: Check Repository
echo.
if exist "C:\Ushin\Testbench_gui_Charan\SmartBU" (
    echo [OK] Repository found
) else (
    echo [WARN] Repository not found at default location
)

echo.
echo ------------------------
echo.

:: Launch GUI
echo Starting SmartBU GUI...
echo.
python Gui_Main_Script\gui_main.py

echo.
echo Application closed.
pause
