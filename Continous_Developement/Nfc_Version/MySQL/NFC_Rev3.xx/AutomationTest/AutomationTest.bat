@echo off
REM --------------------------------------------
REM Launcher for SmartBU Testbench GUI
REM Double-click to open the full GUI application.
REM
REM Automation flow triggered by the operator:
REM   1. Scan 2D barcode with the keyboard-wedge scanner
REM      (scanner fills the field and presses Enter automatically)
REM   2. Tests start automatically when a valid 19-char barcode is detected
REM   3. PASS/FAIL shown on screen
REM   4. HTML report saved automatically (filename includes PCB serial)
REM   5. Test result inserted into MySQL database automatically
REM
REM This file lives in the AutomationTest sub-folder.
REM It changes directory one level up to the project root
REM so that all package imports (AutomationScripts, Functional) resolve correctly.
REM
REM Requirements:
REM   - Python installed and on PATH
REM   - pip install -r AutomationScripts\requirements.txt
REM   - MySQL server running with 'testbench' database and 'test_results' table
REM   - DB_CONFIG in AutomationScripts\mysql_logger.py set to correct credentials

REM Navigate to the project root (parent of this file's folder)
cd /d "%~dp0.."

REM Launch the full GUI application (includes Automation tab with MySQL integration)
python Gui_Main_Script\gui_main.py

REM keep window open so any errors are visible
pause