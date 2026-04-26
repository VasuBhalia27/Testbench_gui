' Silent launcher for SmartBU Testbench GUI (NFC_OR_NON_NFC_RH_Rev2.03).
' Double-click this file to start the full GUI application without any
' CMD/console window appearing in the background.
'
' Automation flow triggered by the operator:
'   1. Scan / type 2D barcode into the "2D Scan" field
'   2. Click "Start"
'   3. All functional tests run automatically
'   4. PASS/FAIL shown on screen
'   5. HTML report saved automatically
'   6. Test result inserted into MySQL database automatically
'
' Uses pythonw.exe (the no-console Python variant) so no black
' window ever appears.  Any startup errors are written to
' AutomationTest_error.log in the same folder so they are
' not silently swallowed.
'
' Requirements:
'   - Python installed and on PATH
'   - pip install mysql-connector-python
'   - MySQL server running with testbench database and test_results table
'   - DB_CONFIG in AutomationScripts\mysql_logger.py set to correct credentials

Dim fso, scriptDir, projectRoot, logPath, cmd
Dim wsh : Set wsh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' This file lives in the AutomationTest sub-folder.
' The project root (one level up) is where all packages live.
scriptDir   = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptDir)
wsh.CurrentDirectory = projectRoot

logPath = scriptDir & "\AutomationTest_error.log"

' Launch the full GUI application (includes Automation tab with MySQL integration)
cmd = "pythonw Gui_Main_Script\gui_main.py"

' WindowStyle 0 = hidden, bWaitOnReturn False = fire-and-forget
On Error Resume Next
wsh.Run cmd, 0, False

If Err.Number <> 0 Then
    Dim ts : Set ts = fso.OpenTextFile(logPath, 8, True)
    ts.WriteLine Now & " — failed to launch: " & Err.Description
    ts.Close
End If

Set wsh = Nothing
Set fso = Nothing
