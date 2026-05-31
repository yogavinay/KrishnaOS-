# Register MAHABHARATA in Windows Startup
$WshShell = New-Object -ComObject WScript.Shell
$startupPath = [System.IO.Path]::Combine($env:APPDATA, "Microsoft", "Windows", "Start Menu", "Programs", "Startup", "Mahabharata.lnk")
$Shortcut = $WshShell.CreateShortcut($startupPath)
$Shortcut.TargetPath = "c:\Users\vinay\Desktop\mahabharata-system\startup_silent.vbs"
$Shortcut.WorkingDirectory = "c:\Users\vinay\Desktop\mahabharata-system"
$Shortcut.Description = "MAHABHARATA AI System - Auto Start"
$Shortcut.Save()
Write-Host "Startup shortcut created at: $startupPath"
