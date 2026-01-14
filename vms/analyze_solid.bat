@echo off
echo ========================================
echo Analise SOLID com Pylint
echo ========================================
echo.

echo [1/5] Analisando modulo Admin...
venv\Scripts\pylint src\admin --disable=C0114,C0115,C0116 --max-line-length=120

echo.
echo [2/5] Analisando modulo Cidades...
venv\Scripts\pylint src\cidades --disable=C0114,C0115,C0116 --max-line-length=120

echo.
echo [3/5] Analisando modulo Cameras...
venv\Scripts\pylint src\cameras --disable=C0114,C0115,C0116 --max-line-length=120

echo.
echo [4/5] Analisando modulo Streaming...
venv\Scripts\pylint src\streaming --disable=C0114,C0115,C0116 --max-line-length=120

echo.
echo [5/5] Analisando modulo LPR...
venv\Scripts\pylint src\lpr --disable=C0114,C0115,C0116 --max-line-length=120

echo.
echo ========================================
echo Analise Completa!
echo ========================================
pause
