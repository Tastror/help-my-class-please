@echo off

cd /d "%~dp0"
cd "../client"

rem : [class] is your python environment
call conda activate [class]

rem : [myclass.json] is your class.json
python .\helpMyClassPlease.py -j "..\config\[myclass.json]"
