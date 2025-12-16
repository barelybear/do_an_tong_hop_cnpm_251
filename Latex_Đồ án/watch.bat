@echo off
chcp 65001 > nul
cd /d "%~dp0"
echo.
echo ========================================
echo  LaTeX Watch Mode - Auto Compile
echo  Nhấn Ctrl+C để dừng
echo ========================================
echo.

REM Thêm MiKTeX vào PATH nếu chưa có
set "PATH=%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64"

REM Chạy latexmk với preview continuously mode
latexmk -pdf -pvc -interaction=nonstopmode -synctex=1 main.tex

