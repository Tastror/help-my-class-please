@echo off

set pwd=%~dp0
if not "%pwd:~-1,1%"=="\" set pwd=%pwd%\

for /f "tokens=2*" %%a in ('reg query "HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders" /v Desktop') do set desktopPath=%%b
if not "%desktopPath:~-1,1%"=="\" set desktopPath=%desktopPath%\

mkdir "%pwd%user-config"

set linkFilePath=%desktopPath%HMCP.lnk
set iconFilePath=%pwd%resource\ico\normal.ico

set targetFilePath_original=%pwd%resource\config\run-hmcp.bat
set targetFilePath=%pwd%user-config\run-hmcp.bat
set jsonFilePath_original=%pwd%resource\config\hmcp.json
set jsonFilePath=%pwd%user-config\hmcp.json

set vbsFilePath=%pwd%tmp.vbs

if not exist "%targetFilePath%" copy "%targetFilePath_original%" "%targetFilePath%"
if not exist "%jsonFilePath%" copy "%jsonFilePath_original%" "%jsonFilePath%"

echo set oWS = WScript.CreateObject("WScript.Shell") > "%vbsFilePath%"
echo set oLink = oWS.CreateShortcut("%linkFilePath%") >> "%vbsFilePath%"
echo oLink.TargetPath = "%targetFilePath%" >> "%vbsFilePath%"
echo oLink.IconLocation = "%iconFilePath%, 0" >> "%vbsFilePath%""
echo oLink.Save >> "%vbsFilePath%"

cscript //nologo "%vbsFilePath%"
del "%vbsFilePath%" /f /q
