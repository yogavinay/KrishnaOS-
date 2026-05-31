' MAHABHARATA SYSTEM - Silent Auto-Start on Windows Boot
' This VBS wrapper launches startup.bat without showing a command prompt window
' Place a shortcut to THIS file in your Startup folder

Set WshShell = CreateObject("WScript.Shell")
WshShell.Run """c:\Users\vinay\Desktop\mahabharata-system\startup.bat""", 0, False
Set WshShell = Nothing
