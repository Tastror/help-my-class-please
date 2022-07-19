@echo off

rem : this is your disk name where client directory is in
F:

rem : [YOUR-PATH] is your path to client directory
cd "\[YOUR-PATH]\help-my-class-please\client"

rem : [class] is your python environment
call conda activate [class]

rem : [myclass.json] is your class.json
python .\helpMyClassPlease.py -j "..\config\[myclass.json]"