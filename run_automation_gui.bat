@echo off
REM --------------------------------------------
REM Simple launcher for the automation GUI
REM Double‑click this batch file to open the standalone
REM automation interface.  No repository knowledge
REM or additional arguments are required.

REM You must have Python installed and available on your
REM PATH.  If you use a virtual environment, activate it
REM first or adjust the "python" command below accordingly.

REM prefer module invocation to ensure package imports work correctly
python -m automation.core.gui_automation

REM keep window open so any errors are visible
pause
