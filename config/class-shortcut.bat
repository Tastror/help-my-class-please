@echo off

cd /d "%~dp0"
cd "../client"

@REM "class" is your python environment, you may need to change it
call conda activate class

@REM "my-class.json" is your class.json, you must modify it !!!
python .\helpMyClassPlease.py -j "..\config\my-class.json"
