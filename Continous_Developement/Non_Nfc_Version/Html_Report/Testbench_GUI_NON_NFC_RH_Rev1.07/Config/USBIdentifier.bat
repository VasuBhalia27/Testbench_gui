@echo off
echo ========================================
echo    USB Device Scanner for Lauterbach
echo ========================================
echo.

echo Step 1: List all USB devices (with debugger CONNECTED)
echo ------------------------------------------------------
wmic path Win32_USBControllerDevice get Dependent > %temp%\usb_all.txt
echo USB devices found (first 20 lines):
echo.
type %temp%\usb_all.txt | findstr /i "usb" > %temp%\usb_filtered.txt
type %temp%\usb_filtered.txt | more
echo.
echo ------------------------------------------------------
echo.

echo Step 2: Search for common debugger identifiers...
echo ------------------------------------------------------
echo Searching for 'lauterbach'...
wmic path Win32_USBControllerDevice get Dependent | findstr /i "lauterbach"
if %errorlevel% equ 0 (echo [FOUND] via 'lauterbach') else (echo [NOT FOUND] via 'lauterbach')
echo.

echo Searching for 'trace32'...
wmic path Win32_USBControllerDevice get Dependent | findstr /i "trace32"
if %errorlevel% equ 0 (echo [FOUND] via 'trace32') else (echo [NOT FOUND] via 'trace32')
echo.

echo Searching for 'debug'...
wmic path Win32_USBControllerDevice get Dependent | findstr /i "debug"
if %errorlevel% equ 0 (echo [FOUND] via 'debug') else (echo [NOT FOUND] via 'debug')
echo.

echo Searching for 'VID_1366' (common Lauterbach VID)...
wmic path Win32_USBControllerDevice get Dependent | findstr /i "VID_1366"
if %errorlevel% equ 0 (echo [FOUND] via VID_1366) else (echo [NOT FOUND] via VID_1366)
echo.

echo Searching for 'VID_0403' (FTDI common)...
wmic path Win32_USBControllerDevice get Dependent | findstr /i "VID_0403"
if %errorlevel% equ 0 (echo [FOUND] via VID_0403) else (echo [NOT FOUND] via VID_0403)
echo.

echo ------------------------------------------------------
echo.

echo Step 3: Show all USB device details in readable format
echo ------------------------------------------------------
powershell "Get-PnpDevice | Where-Object {$_.Class -eq 'USB'} | Format-Table FriendlyName, Status -AutoSize"
echo.

echo Step 4: Check Device Manager via command line
echo ------------------------------------------------------
pnputil /enum-devices | findstr /i "lauterbach trace32 debug" > %temp%\pnputil.txt
type %temp%\pnputil.txt
echo.

echo.
echo ------------------------------------------------------
echo Step 5: If nothing found above, here's a complete list
echo of all USB-related devices (save to file for analysis)
echo ------------------------------------------------------
wmic path Win32_USBControllerDevice get Dependent > %temp%\usb_complete.txt
echo Complete list saved to: %temp%\usb_complete.txt
echo You can open this file in Notepad and search manually
echo.
echo Notepad %temp%\usb_complete.txt
echo.

pause