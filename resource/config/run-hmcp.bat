@echo off

cd /d "%~dp0"
cd "..\src"

@REM "hmcp" is your python environment, you may need to change it
call conda activate hmcp

@REM "hmcp.json" is your hmcp.json, you must modify it !!!
python .\helpMyClassPlease.py -j "..\user-config\hmcp.json"
