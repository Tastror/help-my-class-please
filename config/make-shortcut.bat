@REM @echo off

set pwd=%~dp0

for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop') do set desktopPath=%%b

set linkFilePath=%desktopPath%\HMCP.lnk
set targetFilePath=%pwd%\class-shortcut.bat
set iconFilePath=%pwd%\..\img\ico.ico

set vbsFilePath=%pwd%\tmp.vbs

echo set oWS = WScript.CreateObject("WScript.Shell") > "%vbsFilePath%"
echo set oLink = oWS.CreateShortcut("%linkFilePath%") >> "%vbsFilePath%"
echo oLink.TargetPath = "%targetFilePath%" >> "%vbsFilePath%"
echo oLink.IconLocation = "%iconFilePath%, 0" >> "%vbsFilePath%""
echo oLink.Save >> "%vbsFilePath%"

cscript //nologo "%vbsFilePath%"
del "%vbsFilePath%" /f /q
