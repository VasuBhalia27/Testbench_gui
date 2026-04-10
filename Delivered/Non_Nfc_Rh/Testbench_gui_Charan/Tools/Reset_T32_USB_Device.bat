@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

echo -----------------------------------------------------------
echo Lauterbach TRACE32 USB reset helper
echo -----------------------------------------------------------
echo This script must be run as Administrator.
echo If it is not elevated, right-click and choose "Run as administrator".
echo.

powershell -NoProfile -Command "If (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) { Write-Error 'Administrator privileges are required'; exit 1 }"
if errorlevel 1 (
    echo.
    echo ERROR: Administrator privileges are required. Run this script as Administrator.
    pause
    exit /b 1
)

echo Stopping any existing TRACE32/T32 processes first...
for /f "tokens=1" %%P in ('tasklist ^| findstr /i "t32 trace"') do (
    if not "%%P"=="" (
        taskkill /F /IM %%P /T >nul 2>&1
    )
)
echo Checking for Lauterbach PODBUS USB device...
powershell -NoProfile -ExecutionPolicy Bypass -Command "Set-StrictMode -Off; $devices = Get-PnpDevice | Where-Object { $_.FriendlyName -like '*Lauterbach*' -or $_.FriendlyName -like '*TRACE32*' -or $_.FriendlyName -like '*PODBUS*' -or ($_.HardwareID -ne $null -and ($_.HardwareID | Where-Object { $_ -like '*VID_0897*' })) }; if (-not $devices) { Write-Host 'No Lauterbach USB device found.'; exit 2 }; Write-Host 'Found device:'; $devices | Select-Object FriendlyName, Status, InstanceId; foreach ($dev in $devices) { Disable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }; Start-Sleep -Seconds 5; foreach ($dev in $devices) { Enable-PnpDevice -InstanceId $dev.InstanceId -Confirm:$false -ErrorAction SilentlyContinue }; Start-Sleep -Seconds 5; foreach ($dev in $devices) { try { $parent = (Get-PnpDeviceProperty -InstanceId $dev.InstanceId -KeyName 'DEVPKEY_Device_Parent').Data; if ($parent) { Write-Host 'Resetting parent device:' $parent; Disable-PnpDevice -InstanceId $parent -Confirm:$false -ErrorAction SilentlyContinue; Start-Sleep -Seconds 3; Enable-PnpDevice -InstanceId $parent -Confirm:$false -ErrorAction SilentlyContinue; Start-Sleep -Seconds 3 } } catch { } }; Write-Host 'Device reset complete.'"

if errorlevel 2 (
    echo.
    echo ERROR: Lauterbach device not found. Check cable and device manager.
    pause
    exit /b 2
)

echo.
echo Reset finished. Please retry Connect Trace32 in the GUI.
pause
