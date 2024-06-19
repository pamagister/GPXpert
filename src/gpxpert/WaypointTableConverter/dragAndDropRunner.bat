@echo off

if [%1] == [] goto help

for %%a in (%*) do (
python "%~0/../client.py" %%a -vv
)

pause

:help
echo Usage:
echo    dragAndDropRunner.bat fileToConvert.txt
echo or
echo    Drag and drop text file on this bat file