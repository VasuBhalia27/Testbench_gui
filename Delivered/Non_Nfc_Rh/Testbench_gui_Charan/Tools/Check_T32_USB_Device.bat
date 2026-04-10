@echo off
echo ============================================
echo  Lauterbach / TRACE32 USB Device Checker
echo ============================================
echo.
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-PnpDevice | Where-Object { $_.FriendlyName -like '*Lauterbach*' -or $_.FriendlyName -like '*TRACE32*' -or $_.FriendlyName -like '*PODBUS*' -or ($_.HardwareID -ne $null -and ($_.HardwareID | Where-Object { $_ -like '*VID_0897*' })) } | Select-Object FriendlyName, Status, InstanceId, HardwareID | Format-List"
echo.
echo ============================================
echo  All USB devices (search for T32 manually):
echo ============================================
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "Get-PnpDevice -Class USB | Select-Object FriendlyName, Status, InstanceId | Format-Table -AutoSize"
pause
