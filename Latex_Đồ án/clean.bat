@echo off
REM Clean LaTeX auxiliary files
cd /d "%~dp0"

REM Thêm MiKTeX vào PATH
set "PATH=%PATH%;C:\Program Files\MiKTeX\miktex\bin\x64"

echo Cleaning LaTeX auxiliary files...
del /Q *.aux *.bbl *.blg *.idx *.ind *.lof *.lot *.out *.toc 2>nul
del /Q *.acn *.acr *.alg *.glg *.glo *.gls *.ist 2>nul
del /Q *.fls *.fdb_latexmk *.snm *.nav *.synctex.gz 2>nul
echo Clean completed!
pause

