@echo off

cd /d "%~dp0"
cd "..\src"

@REM "class" is your python environment, you may need to change it
call conda activate class

@REM "class.json" is your class.json, you must modify it !!!
python .\helpMyClassPlease.py -j "..\user-config\class.json"
