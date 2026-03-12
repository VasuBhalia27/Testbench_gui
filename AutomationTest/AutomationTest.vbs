' Silent launcher for SmartBU Test Automation GUI.
' Double-click this file instead of the .bat to start the GUI
' without any CMD/console window appearing in the background.
'
' Uses pythonw.exe (the no-console Python variant) so no black
' window ever appears.  Any startup errors are written to
' AutomationTest_error.log in the same folder so they are
' not silently swallowed.

Dim fso, scriptDir, projectRoot, logPath, cmd
Dim wsh : Set wsh = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' This file lives in the AutomationTest sub-folder.
' The project root (one level up) is where the automation package lives.
scriptDir   = fso.GetParentFolderName(WScript.ScriptFullName)
projectRoot = fso.GetParentFolderName(scriptDir)
wsh.CurrentDirectory = projectRoot

logPath = scriptDir & "\AutomationTest_error.log"
cmd = "pythonw -m AutomationScripts.core.gui_automation"

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
