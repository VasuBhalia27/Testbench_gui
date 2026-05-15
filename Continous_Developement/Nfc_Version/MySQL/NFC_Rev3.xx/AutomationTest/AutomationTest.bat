@echo off
REM --------------------------------------------
REM Simple launcher for the automation GUI
REM Double-click this batch file to open the standalone
REM automation interface.  No repository knowledge
REM or additional arguments are required.
REM
REM This file lives in the AutomationTest sub-folder.
REM It changes directory one level up to the project root
REM so that "python -m AutomationScripts.core.gui_automation" resolves correctly.

REM You must have Python installed and available on your
REM PATH.  If you use a virtual environment, activate it
REM first or adjust the "python" command below accordingly.

REM Navigate to the project root (parent of this file's folder)
cd /d "%~dp0.."

REM prefer module invocation to ensure package imports work correctly
python -m AutomationScripts.core.gui_automation

REM keep window open so any errors are visible
pause