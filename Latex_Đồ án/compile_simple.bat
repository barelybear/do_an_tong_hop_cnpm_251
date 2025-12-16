@echo off
chcp 65001 > nul
cd /d "%~dp0"

REM Thêm MiKTeX vào PATH
set "PATH=%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64"

pdflatex main.tex
pdflatex main.tex
echo.
echo Biên dịch hoàn tất!
pause


