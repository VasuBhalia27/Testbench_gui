@echo off
echo Running J-Link erase script...

"C:\Program Files\SEGGER\JLink_V936\JLink.exe" -CommandFile erase_psoc.jlink > jlink_log.txt 2>&1

type jlink_log.txt

findstr /C:"Erasing done." jlink_log.txt >nul
if %errorlevel%==0 (
    echo.
    echo ==========================================
    echo Device erased successfully.
    echo ==========================================
    goto end
)

findstr /C:"Failed to preserve target RAM" jlink_log.txt >nul
if %errorlevel%==0 (
    echo.
    echo ==========================================
    echo Device is already erased or blank.
    echo ==========================================
    goto end
)

findstr /C:"Cannot connect to the probe/programmer" jlink_log.txt >nul
if %errorlevel%==0 (
    echo.
    echo ==========================================
    echo ERROR: J-Link probe not connected.
    echo ==========================================
    goto end
)

echo.
echo ==========================================
echo Unknown error occurred.
echo Check J-Link log.
echo ==========================================

:end
pause